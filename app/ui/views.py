"""Interfaz NiceGUI: acceso, catálogo, ventas, pedidos e indicadores."""
from pathlib import Path
from nicegui import ui
from app.application.use_cases import OrderService, SalesService
from app.infrastructure.database import SQLiteRepository
from app.ui import assets as _assets  # registra la ruta de imágenes locales

repo=SQLiteRepository()
ROOT=Path(__file__).resolve().parents[2]
ASSETS=ROOT/"assets"/"products"

CUSTOM_CSS="""
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@600;700&display=swap');
body { background:#fff9f6; font-family:'DM Sans',sans-serif; color:#49352f; }
.dn-brand { font-family:'Playfair Display',serif; color:#8d4055; }
.dn-card { border:1px solid #f2dfd8; border-radius:18px; box-shadow:0 8px 24px rgba(116,65,66,.07); }
.dn-product { border:1px solid #f1ded7; border-radius:18px; overflow:hidden; background:white; transition:transform .18s ease,box-shadow .18s ease; }
.dn-product:hover { transform:translateY(-3px); box-shadow:0 12px 28px rgba(116,65,66,.12); }
.dn-pill { background:#fbe8e9; color:#91465a; border-radius:999px; padding:5px 11px; font-size:12px; }
.q-btn .q-icon { font-size:18px; }
@media (max-width: 700px) { .dn-mobile-note { display:none; } }
"""

def money(value): return f"Bs {float(value):.2f}"

def register_pages():
    ui.add_head_html(f"<style>{CUSTOM_CSS}</style>", shared=True)
    session={"user":None}

    @ui.page("/")
    def login():
        with ui.column().classes("w-full min-h-screen items-center justify-center p-5 gap-5"):
            with ui.card().classes("dn-card w-full max-w-md p-8"):
                ui.label("Dulce Nube").classes("dn-brand text-4xl self-center")
                ui.label("Repostería · Ventas e inventario").classes("text-sm text-stone-500 self-center")
                ui.separator().classes("my-3")
                ui.label("Bienvenida/o").classes("text-2xl font-bold self-center")
                ui.label("Ingresa para administrar el día más dulce.").classes("text-stone-500 self-center text-sm")
                username=ui.input("Usuario").props("outlined rounded").classes("w-full mt-4")
                password=ui.input("Contraseña",password=True,password_toggle_button=True).props("outlined rounded").classes("w-full")
                def do_login():
                    user=repo.authenticate(username.value or "",password.value or "")
                    if not user: ui.notify("Usuario o contraseña incorrectos",type="negative"); return
                    session["user"]=user; ui.navigate.to("/app")
                ui.button("Ingresar",on_click=do_login).props("unelevated").classes("w-full bg-[#93475d] text-white rounded-lg py-3 mt-2")
                ui.label("Acceso de demostración académica").classes("text-xs text-stone-400 self-center mt-3")

    @ui.page("/app")
    def dashboard():
        if not session["user"]:
            ui.navigate.to("/")
            return
        user=session["user"]
        role=user["role"]
        current={"key":"catalog"}
        pages=[
            ("catalog","Catálogo","cake"),
            ("sales","Ventas","shopping_bag"),
            ("orders","Pedidos","event_note"),
            ("inventory","Inventario","inventory_2"),
        ]
        if role=="Administrador":
            pages.append(("reports","Reportes","insights"))

        with ui.column().classes("w-full min-h-screen max-w-[1600px] mx-auto p-3 md:p-6 gap-4"):
            with ui.row().classes("w-full items-center justify-between border-b border-[#f0dfd9] pb-4"):
                with ui.row().classes("items-center gap-3"):
                    ui.label("DN").classes("rounded-xl bg-[#f6dfe1] text-[#91465a] font-bold p-3")
                    with ui.column().classes("gap-0"):
                        ui.label("Dulce Nube").classes("dn-brand text-3xl")
                        ui.label(f"Panel de {role.lower()} · Repostería").classes("text-xs text-stone-500")
                with ui.row().classes("items-center gap-2"):
                    ui.label(user["username"]).classes("text-sm text-stone-500")
                    def logout():
                        session["user"]=None
                        ui.navigate.to("/")
                    ui.button("Salir",icon="logout",on_click=logout).props("outline rounded color=grey-8 dense")

            with ui.row().classes("w-full items-start gap-4 no-wrap"):
                with ui.card().classes("dn-card w-[190px] min-w-[190px] p-3 gap-2 self-stretch"):
                    ui.label("MENÚ PRINCIPAL").classes("text-[10px] font-bold tracking-widest text-stone-400 px-2 py-2")
                    menu_buttons={}
                    for key,label,icon in pages:
                        menu_buttons[key]=ui.button(label,icon=icon,on_click=lambda k=key:show_page(k)).props("flat no-caps align=left").classes("w-full justify-start rounded-xl text-sm")
                    ui.separator().classes("my-2")
                    ui.label("Dulce Nube").classes("dn-brand text-lg px-2")
                    ui.label("Gestión interna del negocio").classes("text-xs text-stone-400 px-2")
                content=ui.column().classes("flex-1 min-w-0 gap-4")

        def show_page(key):
            current["key"]=key
            for menu_key,button in menu_buttons.items():
                if menu_key==key:
                    button.props("unelevated color=primary")
                    button.classes(add="bg-[#fbe8e9] text-[#91465a]")
                else:
                    button.props("flat color=grey-8")
                    button.classes(remove="bg-[#fbe8e9] text-[#91465a]")
            content.clear()
            with content:
                if key=="catalog": catalog_view()
                elif key=="sales": sales_view()
                elif key=="orders": orders_view(role)
                elif key=="inventory": inventory_view(role)
                elif key=="reports": reports_view(role)

        show_page("catalog")

def catalog_view():
    products=repo.list_all()
    with ui.row().classes("w-full justify-between items-end"):
        with ui.column().classes("gap-0"):
            ui.label("Nuestro catálogo").classes("text-2xl font-bold")
            ui.label("Hecho con cariño, listo para compartir.").classes("text-stone-500")
        ui.label(f"{len(products)} productos").classes("dn-pill")
    search=ui.input(placeholder="Buscar un producto...").props("outlined rounded dense clearable").classes("w-full max-w-sm")
    grid=ui.grid(columns=3).classes("w-full")
    def draw():
        grid.clear()
        term=(search.value or "").lower()
        filtered=[p for p in products if term in p["name"].lower() or term in p["category"].lower()]
        with grid:
            for p in filtered:
                with ui.card().classes("dn-product p-0 w-full"):
                    image=p.get("image") or ""; path=ASSETS/image
                    if image and path.exists(): ui.image(f"/product-assets/{image}").classes("w-full h-44 object-cover")
                    else: ui.label("🍰").classes("text-6xl self-center p-8")
                    with ui.column().classes("p-4 gap-1"):
                        ui.label(p["category"]).classes("dn-pill self-start")
                        ui.label(p["name"]).classes("font-bold text-lg")
                        with ui.row().classes("w-full justify-between items-center"):
                            ui.label(money(p["price"])).classes("text-[#93475d] font-bold text-lg")
                            ui.label(f"{p['stock']} disponibles").classes("text-xs text-stone-500")
    search.on_value_change(lambda _:draw()); draw()

def sales_view():
    products=repo.list_all(); cart={}
    ui.label("Nueva venta").classes("text-2xl font-bold")
    ui.label("Selecciona productos, indica cantidades y confirma el cobro.").classes("text-stone-500")
    with ui.row().classes("w-full items-start gap-5 flex-wrap"):
        with ui.card().classes("dn-card p-5 flex-1 min-w-[280px]"):
            selector=ui.select({p["id"]:f"{p['name']} · {money(p['price'])} · stock {p['stock']}" for p in products},label="Producto").props("outlined rounded use-input input-debounce=0").classes("w-full")
            qty=ui.number("Cantidad",value=1,min=1,precision=0).props("outlined rounded").classes("w-36")
            cart_area=ui.column().classes("w-full")
            total_label=ui.label("Total: Bs 0.00").classes("text-2xl font-bold text-[#93475d]")
            receipt_area=ui.column().classes("w-full")
            def refresh_cart():
                cart_area.clear(); total=sum(i["price"]*i["qty"] for i in cart.values())
                with cart_area:
                    if not cart: ui.label("Tu carrito está vacío.").classes("text-stone-400")
                    for pid,item in cart.items():
                        with ui.row().classes("w-full justify-between"):
                            ui.label(f"{item['name']} × {item['qty']}")
                            ui.label(money(item["price"]*item["qty"]))
                total_label.text=f"Total: {money(total)}"
            def add():
                p=repo.get_by_id(selector.value) if selector.value else None
                if not p: ui.notify("Selecciona un producto.",type="warning"); return
                amount=int(qty.value or 1); new_qty=cart.get(p["id"],{}).get("qty",0)+amount
                if amount<1 or new_qty>p["stock"]: ui.notify("Cantidad superior al stock disponible.",type="negative"); return
                cart[p["id"]]={"name":p["name"],"price":p["price"],"qty":new_qty,"stock":p["stock"]}; refresh_cart()
            ui.button("Añadir al carrito",icon="add_shopping_cart",on_click=add).props("unelevated").classes("bg-[#93475d] text-white rounded-lg")
            def confirm():
                try:
                    receipt=SalesService(repo).register_sale(cart); receipt_area.clear()
                    with receipt_area:
                        ui.separator(); ui.label(f"Comprobante {receipt['number']}").classes("font-bold text-lg")
                        for line in receipt["lines"]: ui.label(f"{line['name']} · {line['qty']} × {money(line['price'])}")
                        ui.label(f"TOTAL {money(receipt['total'])}").classes("text-xl font-bold text-[#93475d]")
                        ui.label(receipt["created_at"]).classes("text-xs text-stone-500")
                    ui.notify("Venta registrada y stock actualizado.",type="positive"); cart.clear(); refresh_cart()
                    products[:]=repo.list_all(); selector.options={p["id"]:f"{p['name']} · {money(p['price'])} · stock {p['stock']}" for p in products}; selector.update()
                except (ValueError,KeyError,TypeError) as error: ui.notify(str(error),type="negative")
            ui.button("Confirmar venta",icon="check_circle",on_click=confirm).props("unelevated").classes("bg-emerald-700 text-white rounded-lg w-full mt-3")
        with ui.card().classes("dn-card p-5 flex-1 min-w-[260px]"):
            ui.label("Consejo").classes("font-bold text-lg")
            ui.label("El sistema descuenta las unidades del inventario únicamente cuando confirmas la venta.").classes("text-stone-600")
            ui.label("El comprobante se genera automáticamente y queda guardado en SQLite.").classes("text-stone-600")
    refresh_cart()

def orders_view(role):
    ui.label("Pedidos personalizados").classes("text-2xl font-bold")
    ui.label("Registra los detalles de cada torta y sigue su preparación.").classes("text-stone-500")
    with ui.card().classes("dn-card p-5 w-full"):
        ui.label("Nuevo pedido").classes("text-lg font-bold")
        with ui.grid(columns=2).classes("w-full"):
            customer=ui.input("Nombre del cliente").props("outlined rounded")
            phone=ui.input("Teléfono").props("outlined rounded")
            delivery=ui.input("Entrega (AAAA-MM-DD HH:MM)").props("outlined rounded")
            decoration=ui.input("Decoración solicitada").props("outlined rounded")
            dedication=ui.input("Dedicatoria / festejado").props("outlined rounded")
            notes=ui.textarea("Observaciones").props("outlined rounded").classes("col-span-2")
        def save():
            try:
                oid=OrderService(repo).register_order({"customer":customer.value or "","phone":phone.value or "","delivery_at":delivery.value or "","decoration":decoration.value or "","dedication":dedication.value or "","notes":notes.value or ""})
                ui.notify(f"Pedido guardado. Código interno #{oid}.",type="positive"); refresh()
            except ValueError as error: ui.notify(str(error),type="negative")
        ui.button("Guardar pedido",icon="save",on_click=save).props("unelevated").classes("bg-[#93475d] text-white rounded-lg")
    status=ui.select(["Todos"]+__import__("app.domain.models",fromlist=["OrderStatus"]).OrderStatus.sequence(),value="Todos",label="Filtrar por estado").props("outlined rounded").classes("w-full max-w-xs mt-4")
    area=ui.column().classes("w-full")
    def refresh():
        area.clear()
        with area:
            rows=repo.list_orders(status.value)
            if not rows: ui.label("Todavía no hay pedidos registrados.").classes("text-stone-400")
            for order in rows:
                with ui.card().classes("dn-card p-4 w-full"):
                    with ui.row().classes("w-full justify-between items-center"):
                        ui.label(f"{order['code']} · {order['customer']}").classes("font-bold")
                        ui.label(order["status"]).classes("dn-pill")
                    ui.label(f"Entrega: {order['delivery_at']} · Contacto: {order['phone']}")
                    ui.label(f"Decoración: {order['decoration']} · Dedicatoria: {order['dedication']}")
                    if order.get("notes"): ui.label(f"Notas: {order['notes']}").classes("text-stone-500")
                    sequence=__import__("app.domain.models",fromlist=["OrderStatus"]).OrderStatus.sequence(); idx=sequence.index(order["status"])
                    if role=="Administrador" and idx<len(sequence)-1:
                        next_status=sequence[idx+1]
                        def advance(order_id=order["id"],new_status=next_status):
                            try: OrderService(repo).change_status(order_id,new_status); ui.notify("Estado actualizado.",type="positive"); refresh()
                            except ValueError as error: ui.notify(str(error),type="negative")
                        ui.button(f"Avanzar a: {next_status}",on_click=advance).props("outline rounded color=primary")
    status.on_value_change(lambda _:refresh()); refresh()

def inventory_view(role):
    ui.label("Inventario").classes("text-2xl font-bold")
    ui.label("Controla existencias, precios y catálogo de productos.").classes("text-stone-500")
    if role=="Administrador":
        with ui.expansion("Registrar un producto",icon="add_circle").classes("dn-card w-full p-3"):
            name=ui.input("Nombre del producto").props("outlined rounded")
            category=ui.input("Categoría").props("outlined rounded")
            price=ui.number("Precio (Bs)",min=0,precision=2).props("outlined rounded")
            stock=ui.number("Stock inicial",min=0,precision=0).props("outlined rounded")
            image=ui.select(["torta_chocolate.jpg","torta_vainilla.jpg","queque_marmoleado.jpg","empanada_queso.jpg","alfajor.jpg","cupcake.jpg"],label="Imagen del producto").props("outlined rounded")
            def add():
                try: repo.create_product(name.value or "",category.value or "",price.value or 0,stock.value or 0,image.value or ""); ui.notify("Producto agregado.",type="positive"); ui.navigate.to("/app")
                except (ValueError,TypeError) as error: ui.notify(str(error),type="negative")
            ui.button("Guardar producto",on_click=add).props("unelevated").classes("bg-[#93475d] text-white")
    rows=repo.list_all()
    ui.table(columns=[{"name":"name","label":"Producto","field":"name"},{"name":"category","label":"Categoría","field":"category"},{"name":"price","label":"Precio (Bs)","field":"price"},{"name":"stock","label":"Existencias","field":"stock"}],rows=rows,row_key="id").classes("w-full dn-card")

def reports_view(role):
    if role!="Administrador": ui.label("Los reportes están disponibles para el administrador."); return
    stats=repo.stats(); ui.label("Resumen del negocio").classes("text-2xl font-bold")
    with ui.grid(columns=4).classes("w-full"):
        for label,value,icon in [("Ingresos",money(stats["sales_total"]),"payments"),("Ventas",stats["sales_count"],"receipt_long"),("Productos",stats["products"],"cake"),("Pedidos pendientes",stats["pending_orders"],"event")]:
            with ui.card().classes("dn-card p-4"):
                ui.icon(icon).classes("text-2xl text-[#93475d]"); ui.label(label).classes("text-xs text-stone-500"); ui.label(str(value)).classes("text-2xl font-bold")
    ui.label("Historial de ventas").classes("text-lg font-bold mt-5")
    ui.table(columns=[{"name":"id","label":"N.º","field":"id"},{"name":"created_at","label":"Fecha","field":"created_at"},{"name":"total","label":"Total (Bs)","field":"total"}],rows=repo.list_sales(),row_key="id").classes("w-full")
    ui.label("Productos más vendidos").classes("text-lg font-bold mt-5")
    ui.table(columns=[{"name":"name","label":"Producto","field":"name"},{"name":"quantity","label":"Unidades","field":"quantity"},{"name":"revenue","label":"Ingresos (Bs)","field":"revenue"}],rows=repo.top_products(),row_key="name").classes("w-full")
