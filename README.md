# Dulce Nube — Sistema de ventas, inventario y pedidos

Aplicación académica desarrollada con **Python, NiceGUI y SQLite** para la repostería Dulce Nube de Parotani, Cochabamba.

## Funcionalidades incluidas
- Acceso por roles Administrador y Vendedor.
- Catálogo visual con tarjetas, imágenes locales y búsqueda por nombre/categoría.
- Registro de ventas, carrito, comprobante y descuento transaccional del inventario.
- Inventario y alta de productos (Administrador).
- Pedidos personalizados con código y flujo Registrado → En preparación → Listo para recojo → Entregado.
- Reportes de ventas e indicadores para Administrador.
- Navegación lateral compacta: el menú queda a la izquierda y el módulo seleccionado se muestra en el área principal de la derecha.
- Al entrar a Inventario se vuelven a consultar los datos guardados; después de confirmar una venta, el stock descontado se refleja al abrir o volver a entrar al módulo.

**Alcance de esta versión:** la selección de productos se realiza manualmente por nombre; no se implementa lector ni módulo de códigos de barras. No incluye facturación electrónica, contabilidad avanzada ni pagos electrónicos.

## Tecnología y base de datos
- Python + NiceGUI: interfaz web y lógica de presentación.
- SQLite: base relacional local, sin servidor externo.
- Archivo: `data/dulcenube.db`.
- Esquema SQL: `app/infrastructure/schema.sql`.
- Adaptador y consultas: `app/infrastructure/database.py`.

La base `data/dulcenube.db` se incluye con los productos de demostración y se conserva entre ejecuciones. Al ejecutar `python main.py`, `init_db()` crea las tablas que falten y conserva los registros existentes. Las ventas confirmadas descuentan stock dentro de una transacción SQLite; si no hay existencias suficientes, la operación se cancela.

### Tablas
| Tabla | Propósito |
|---|---|
| `users` | Usuarios y roles |
| `products` | Catálogo, precio, stock e imagen |
| `sales` | Cabecera de ventas |
| `sale_items` | Detalle de productos vendidos |
| `orders` | Pedidos personalizados y estados |

## Ejecutar en Windows PowerShell
Abre PowerShell en la carpeta `DulceNube_MVP` y ejecuta:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python main.py
```

Abre `http://localhost:8080`. Mantén abierta la terminal mientras uses el sistema. En el panel, selecciona un módulo en el menú izquierdo; su información aparecerá a la derecha.

Si PowerShell bloquea la activación:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv\Scripts\Activate.ps1
```

## Usuarios de demostración
- Administrador: `admin` / `admin123`
- Vendedor: `vendedor` / `venta123`

Son credenciales simples para demostración local. No usar en producción: el siguiente endurecimiento necesario es hash de contraseñas y gestión segura de sesiones.

## Pruebas
```powershell
python -m pytest -v
```

## Ver la base de datos en Visual Studio Code
1. Abre la carpeta completa `DulceNube_MVP` en VS Code.
2. En el Explorador expande `data` y abre `dulcenube.db`.
3. Para ver tablas y filas instala la extensión **SQLite** (por ejemplo, SQLite de alexcvzz) desde Extensions.
4. Pulsa `Ctrl+Shift+P`, ejecuta `SQLite: Open Database` y selecciona `data/dulcenube.db`.
5. En la vista SQLite expande `Tables` y selecciona `users`, `products`, `sales`, `sale_items` u `orders`.

Si no aparece el archivo, verifica que abriste la carpeta raíz y no una subcarpeta. También puedes ejecutar `python -c "from app.infrastructure.database import init_db; init_db(); print('BD creada')"` desde la raíz.

## Arquitectura y responsabilidades
- `app/domain`: entidades, estados, reglas y Factory.
- `app/application`: casos de uso y validaciones.
- `app/infrastructure`: adaptador SQLite y esquema SQL.
- `app/ui`: páginas y recursos de interfaz NiceGUI.
- `assets/products`: fotografías locales del catálogo.
- `tests`: pruebas automatizadas.

Los archivos `__init__.py` identifican paquetes Python; pueden tener pocas líneas. No son módulos de lógica de negocio.

## Añadir tus propias imágenes
Copia una imagen JPG o PNG dentro de `assets/products`. En `products`, el campo `image` guarda el nombre del archivo (por ejemplo `torta_fresa.jpg`). En `app/ui/views.py`, el catálogo resuelve ese nombre dentro de la carpeta de recursos. Mantén imágenes cuadradas o recórtalas a 1:1 para que las tarjetas se vean uniformes.

## Limitaciones conocidas y seguridad
- Las contraseñas de demo se almacenan en texto plano; solo para entorno académico local.
- La app está pensada para ejecutarse localmente en el equipo de demostración.
- La tipografía externa puede usar una fuente de respaldo si no hay conexión a internet; las imágenes del catálogo son locales.
- No afirmar que las pruebas pasan hasta ejecutar PyTest en el equipo de entrega y conservar la salida real.
