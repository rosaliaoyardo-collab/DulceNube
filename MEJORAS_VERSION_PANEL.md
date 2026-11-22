# Mejoras de la versión con panel lateral

- Se reemplazó la navegación superior por un menú compacto ubicado a la izquierda.
- Los módulos Catálogo, Ventas, Pedidos e Inventario se abren en el área principal de la derecha.
- El módulo Reportes aparece para el rol Administrador.
- Cada cambio de módulo vuelve a construir su vista y consulta los datos actuales de SQLite. Esto evita que la tabla de inventario permanezca mostrando el stock anterior después de registrar una venta.
- El descuento de existencias se realiza en una transacción y con una condición SQL que impide dejar stock negativo.
- Se mantienen las imágenes locales, la base de datos SQLite, los roles, los pedidos, los comprobantes y los reportes.

## Comprobación realizada en el entorno de preparación

- `python -m compileall -q .`: correcto.
- `pytest -q`: 10 pruebas aprobadas.
- No fue posible iniciar la interfaz web en el entorno de preparación porque no tiene instalado NiceGUI. En el equipo de ejecución, instalar las dependencias con `pip install -r requirements.txt` antes de ejecutar `python main.py`.
