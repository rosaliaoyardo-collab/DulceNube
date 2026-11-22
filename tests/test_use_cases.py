import pytest
from app.application.use_cases import SalesService, OrderService

class FakeRepo:
    def __init__(self): self.order={"id":1,"status":"Registrado"}; self.saved=None
    def create_sale(self,lines,total): self.saved=(lines,total); return 9
    def get_order_by_id(self,oid): return self.order if oid==1 else None
    def update_order_status(self,oid,status): self.order["status"]=status
    def create_order(self,data): self.saved=data; return 3

def test_sale_rejects_empty_cart():
    with pytest.raises(ValueError): SalesService(FakeRepo()).register_sale({})

def test_sale_builds_receipt():
    repo=FakeRepo(); receipt=SalesService(repo).register_sale({1:{"name":"Cupcake","price":8,"qty":2,"stock":5}})
    assert receipt["number"]=="VTA-000009" and receipt["total"]==16

def test_order_requires_fields():
    with pytest.raises(ValueError): OrderService(FakeRepo()).register_order({})

def test_order_moves_one_step():
    repo=FakeRepo(); OrderService(repo).change_status(1,"En preparación")
    assert repo.order["status"]=="En preparación"

def test_order_cannot_skip_status():
    with pytest.raises(ValueError): OrderService(FakeRepo()).change_status(1,"Entregado")
