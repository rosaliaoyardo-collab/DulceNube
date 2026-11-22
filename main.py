"""Punto de entrada de Dulce Nube."""
import os
from nicegui import ui
from app.infrastructure.database import init_db
from app.ui.views import register_pages

init_db()
register_pages()
# En Docker se usa DULCENUBE_HOST=0.0.0.0 para que el contenedor sea accesible desde el navegador.
ui.run(
    title="Dulce Nube | Repostería",
    host=os.getenv("DULCENUBE_HOST", "127.0.0.1"),
    port=int(os.getenv("DULCENUBE_PORT", "8080")),
    reload=False,
    favicon="🍰",
)
