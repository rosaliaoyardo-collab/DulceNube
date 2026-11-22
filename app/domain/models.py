"""Entidades y reglas puras del dominio."""
from dataclasses import dataclass
from enum import Enum

class OrderStatus(str, Enum):
    REGISTRADO = "Registrado"
    EN_PREPARACION = "En preparación"
    LISTO = "Listo para recojo"
    ENTREGADO = "Entregado"

    @classmethod
    def sequence(cls):
        return [status.value for status in cls]

@dataclass(frozen=True)
class Product:
    id: int
    name: str
    category: str
    price: float
    stock: int
    active: bool = True

    def __post_init__(self):
        if self.price < 0 or self.stock < 0:
            raise ValueError("El precio y el stock no pueden ser negativos.")

def calculate_total(items):
    """Calcula el total de (precio, cantidad) y redondea a dos decimales."""
    total = sum(float(price) * int(qty) for price, qty in items)
    return round(total, 2)
