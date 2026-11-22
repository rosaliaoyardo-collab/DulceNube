# Guía breve para la sustentación

**¿Qué base de datos usa?** SQLite, una base relacional embebida. El archivo está en `data/dulcenube.db`.

**¿Dónde se crea?** `main.py` llama a `init_db()`; esta función lee `schema.sql`, crea las tablas si no existen y carga datos de muestra solo cuando el catálogo está vacío.

**¿Qué hace el Adapter?** `SQLiteRepository` implementa los contratos de repositorio y oculta los detalles SQL a los casos de uso.

**¿Qué hace Factory?** `ReceiptFactory` construye comprobantes de venta y códigos únicos para pedidos.

**¿Por qué se usa una transacción?** Para que una venta y el descuento de stock sean una sola operación consistente. Si falla una validación, SQLite revierte los cambios.

**¿Por qué hay `__init__.py`?** Identifica directorios como paquetes importables de Python; no tiene que contener lógica.

**¿Por qué las imágenes están en `assets/products`?** Son recursos estáticos locales; el campo `products.image` guarda el nombre del archivo y la interfaz lo muestra en la tarjeta del producto.
