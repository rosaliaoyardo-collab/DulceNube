"""Adaptador SQLite: esquema, conexión y repositorios SQL."""
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

PROJECT_ROOT=Path(__file__).resolve().parents[2]
DB_PATH=PROJECT_ROOT / "data" / "dulcenube.db"

@contextmanager
def connect():
    DB_PATH.parent.mkdir(parents=True,exist_ok=True)
    conn=sqlite3.connect(DB_PATH,timeout=15)
    conn.row_factory=sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback(); raise
    finally:
        conn.close()

def init_db():
    """Crea tablas e inserta datos de demostración solo en una BD vacía."""
    schema=(PROJECT_ROOT/"app"/"infrastructure"/"schema.sql").read_text(encoding="utf-8")
    with connect() as conn:
        conn.executescript(schema)
        conn.execute("INSERT OR IGNORE INTO users(username,password,role) VALUES(?,?,?)",("admin","admin123","Administrador"))
        conn.execute("INSERT OR IGNORE INTO users(username,password,role) VALUES(?,?,?)",("vendedor","venta123","Vendedor"))
        if conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]==0:
            sample=[
                ("Torta de chocolate","Tortas",85,8,"torta_chocolate.jpg"),
                ("Torta de vainilla","Tortas",75,6,"torta_vainilla.jpg"),
                ("Queque marmoleado","Queques",25,15,"queque_marmoleado.jpg"),
                ("Empanada de queso","Salados",5,40,"empanada_queso.jpg"),
                ("Alfajor","Galletas",4,30,"alfajor.jpg"),
                ("Cupcake","Porciones",8,24,"cupcake.jpg"),
            ]
            conn.executemany("INSERT INTO products(name,category,price,stock,image) VALUES(?,?,?,?,?)",sample)

class SQLiteRepository:
    """Adapter que implementa los puertos usando SQL parametrizado."""
    def authenticate(self,username,password):
        with connect() as conn:
            row=conn.execute("SELECT username,role FROM users WHERE username=? AND password=?",(username,password)).fetchone()
            return dict(row) if row else None

    def list_all(self):
        with connect() as conn:
            return [dict(r) for r in conn.execute("SELECT * FROM products WHERE active=1 ORDER BY name")]

    def get_by_id(self,product_id):
        with connect() as conn:
            row=conn.execute("SELECT * FROM products WHERE id=? AND active=1",(product_id,)).fetchone()
            return dict(row) if row else None

    def create_product(self,name,category,price,stock,image=""):
        name=name.strip(); category=category.strip(); price=float(price); stock=int(stock)
        if not name or not category or price<0 or stock<0: raise ValueError("Datos de producto no válidos.")
        with connect() as conn:
            conn.execute("INSERT INTO products(name,category,price,stock,image) VALUES(?,?,?,?,?)",(name,category,price,stock,image))

    def create_sale(self,lines,total):
        with connect() as conn:
            # Validación previa y descuento condicionado para evitar stock negativo.
            for line in lines:
                row=conn.execute("SELECT stock FROM products WHERE id=? AND active=1",(line["product_id"],)).fetchone()
                if row is None or row["stock"]<line["qty"]:
                    raise ValueError(f"Stock insuficiente para {line['name']}.")
            cursor=conn.execute("INSERT INTO sales(total,created_at) VALUES(?,?)",(float(total),datetime.now().isoformat(timespec="seconds")))
            sale_id=cursor.lastrowid
            for line in lines:
                updated=conn.execute(
                    "UPDATE products SET stock=stock-? WHERE id=? AND active=1 AND stock>=?",
                    (line["qty"],line["product_id"],line["qty"]),
                )
                if updated.rowcount != 1:
                    raise ValueError(f"No hay stock suficiente para {line['name']}. Actualiza la venta e inténtalo de nuevo.")
                conn.execute("INSERT INTO sale_items(sale_id,product_id,name,price,qty) VALUES(?,?,?,?,?)",(sale_id,line["product_id"],line["name"],line["price"],line["qty"]))
            return sale_id

    def create_order(self,data):
        with connect() as conn:
            cur=conn.execute("INSERT INTO orders(code,customer,phone,delivery_at,decoration,dedication,notes,status,created_at) VALUES(?,?,?,?,?,?,?,?,?)",(data["code"],data["customer"].strip(),data["phone"].strip(),data["delivery_at"].strip(),data["decoration"].strip(),data.get("dedication","").strip(),data.get("notes","").strip(),"Registrado",datetime.now().isoformat(timespec="seconds")))
            return cur.lastrowid

    def get_order_by_id(self,order_id):
        with connect() as conn:
            row=conn.execute("SELECT * FROM orders WHERE id=?",(order_id,)).fetchone()
            return dict(row) if row else None

    def list_orders(self,status=None):
        with connect() as conn:
            if status and status!="Todos": rows=conn.execute("SELECT * FROM orders WHERE status=? ORDER BY delivery_at",(status,))
            else: rows=conn.execute("SELECT * FROM orders ORDER BY delivery_at")
            return [dict(r) for r in rows]

    def update_order_status(self,order_id,status):
        with connect() as conn: conn.execute("UPDATE orders SET status=? WHERE id=?",(status,order_id))

    def list_sales(self,start_date=None,end_date=None):
        query="SELECT * FROM sales WHERE 1=1"; params=[]
        if start_date: query+=" AND date(created_at)>=date(?)"; params.append(start_date)
        if end_date: query+=" AND date(created_at)<=date(?)"; params.append(end_date)
        query+=" ORDER BY created_at DESC"
        with connect() as conn: return [dict(r) for r in conn.execute(query,params)]

    def top_products(self):
        with connect() as conn:
            return [dict(r) for r in conn.execute("SELECT name,SUM(qty) quantity,ROUND(SUM(qty*price),2) revenue FROM sale_items GROUP BY product_id,name ORDER BY quantity DESC")]

    def stats(self):
        with connect() as conn:
            return {"sales_total":conn.execute("SELECT COALESCE(SUM(total),0) FROM sales").fetchone()[0],"sales_count":conn.execute("SELECT COUNT(*) FROM sales").fetchone()[0],"products":conn.execute("SELECT COUNT(*) FROM products WHERE active=1").fetchone()[0],"stock_units":conn.execute("SELECT COALESCE(SUM(stock),0) FROM products WHERE active=1").fetchone()[0],"pending_orders":conn.execute("SELECT COUNT(*) FROM orders WHERE status!='Entregado'").fetchone()[0]}
