"""Configuración de recursos estáticos de la interfaz."""
from pathlib import Path
from nicegui import app

PROJECT_ROOT=Path(__file__).resolve().parents[2]
PRODUCT_ASSETS=PROJECT_ROOT/"assets"/"products"
app.add_static_files("/product-assets",str(PRODUCT_ASSETS))
