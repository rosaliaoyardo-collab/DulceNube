# Arquitectura de Dulce Nube

```text
NiceGUI (app/ui)
      | invoca casos de uso
      v
Aplicación (app/application) -----> Dominio (app/domain)
      | depende de contratos/puertos
      v
Infraestructura (app/infrastructure)
      | Adapter SQLiteRepository
      v
SQLite: data/dulcenube.db
```

## Clean Architecture / Hexagonal
- **Dominio:** `Product`, `OrderStatus` y `calculate_total` contienen reglas independientes de la interfaz y la base de datos.
- **Aplicación:** `SalesService` y `OrderService` coordinan los casos de uso y validan las operaciones.
- **Puertos:** `ProductRepository`, `SalesRepository` y `OrderRepository` definen contratos mediante `Protocol`.
- **Adaptador:** `SQLiteRepository` implementa persistencia con SQLite y consultas parametrizadas.
- **UI:** NiceGUI presenta páginas y recoge entradas; no ejecuta SQL directamente.

## SOLID y patrones
- **SRP:** dominio, casos de uso, persistencia y UI tienen responsabilidades separadas.
- **DIP:** los servicios reciben un repositorio por constructor, sin crear conexiones SQL propias.
- **Factory:** `ReceiptFactory` centraliza la creación de comprobantes y códigos de pedido.
- **Adapter:** `SQLiteRepository` adapta el motor SQLite a los puertos de repositorio.
- **Transacción:** la venta y el descuento de existencias se confirman juntos; ante una excepción se revierte la operación.

## Modelo relacional
`users`; `products`; `sales` 1—N `sale_items`; `products` 1—N `sale_items`; `orders`.
