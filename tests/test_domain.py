from app.domain.models import calculate_total, OrderStatus

def test_calculate_total():
    assert calculate_total([(10,2),(5.5,3)])==36.5

def test_order_status_sequence():
    assert OrderStatus.sequence()==["Registrado","En preparación","Listo para recojo","Entregado"]
