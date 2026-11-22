"""Factory para construir comprobantes y códigos de pedidos."""
from datetime import datetime
from uuid import uuid4

class ReceiptFactory:
    @staticmethod
    def create_sale(sale_id, lines, total):
        return {
            "number": f"VTA-{int(sale_id):06d}",
            "lines": [dict(line) for line in lines],
            "total": round(float(total), 2),
            "created_at": datetime.now().strftime("%d/%m/%Y %H:%M"),
        }

    @staticmethod
    def create_order_code():
        return f"TOR-{uuid4().hex[:8].upper()}"
