"""Casos de uso: validan reglas y coordinan repositorios."""
from app.domain.factories import ReceiptFactory
from app.domain.models import OrderStatus, calculate_total

class SalesService:
    def __init__(self, repository):
        self.repository = repository

    def register_sale(self, cart):
        if not cart:
            raise ValueError("Agregue al menos un producto.")
        lines=[]
        for product_id, item in cart.items():
            qty=int(item["qty"]); price=float(item["price"])
            if qty < 1 or price < 0:
                raise ValueError("Cantidad o precio no válido.")
            if qty > int(item["stock"]):
                raise ValueError(f"Stock insuficiente para {item['name']}.")
            lines.append({"product_id":int(product_id),"name":str(item["name"]),"price":price,"qty":qty})
        total=calculate_total([(line["price"],line["qty"]) for line in lines])
        sale_id=self.repository.create_sale(lines,total)
        return ReceiptFactory.create_sale(sale_id,lines,total)

class OrderService:
    def __init__(self, repository):
        self.repository=repository

    def register_order(self, data):
        required=("customer","phone","delivery_at","decoration")
        if any(not str(data.get(key," ")).strip() for key in required):
            raise ValueError("Complete cliente, teléfono, fecha de entrega y decoración.")
        payload=dict(data); payload["code"]=ReceiptFactory.create_order_code()
        return self.repository.create_order(payload)

    def change_status(self, order_id, status):
        sequence=OrderStatus.sequence()
        if status not in sequence: raise ValueError("Estado no válido.")
        current=self.repository.get_order_by_id(order_id)
        if current is None: raise ValueError("No existe el pedido seleccionado.")
        index=sequence.index(current["status"]); target=sequence.index(status)
        if target != index+1: raise ValueError("El pedido debe avanzar un estado a la vez.")
        self.repository.update_order_status(order_id,status)
