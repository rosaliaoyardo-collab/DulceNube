import sqlite3
from pathlib import Path
import pytest
from app.infrastructure import database

@pytest.fixture
def isolated_db(monkeypatch, tmp_path):
    monkeypatch.setattr(database, "DB_PATH", tmp_path / "dulcenube_test.db")
    monkeypatch.setattr(database, "PROJECT_ROOT", tmp_path)
    schema_dir = tmp_path / "app" / "infrastructure"
    schema_dir.mkdir(parents=True)
    source = Path(__file__).resolve().parents[1] / "app" / "infrastructure" / "schema.sql"
    (schema_dir / "schema.sql").write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
    database.init_db()
    return database.DB_PATH

def test_init_db_and_seed(isolated_db):
    with sqlite3.connect(isolated_db) as conn:
        names = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        assert {"users", "products", "sales", "sale_items", "orders"}.issubset(names)
        assert conn.execute("SELECT COUNT(*) FROM products").fetchone()[0] == 6

def test_sale_decreases_stock(isolated_db):
    repo = database.SQLiteRepository()
    product = repo.get_by_id(1)
    repo.create_sale([{"product_id": 1, "name": product["name"], "price": product["price"], "qty": 2}], 170)
    assert repo.get_by_id(1)["stock"] == product["stock"] - 2

def test_sale_rolls_back_if_stock_is_insufficient(isolated_db):
    repo = database.SQLiteRepository()
    product = repo.get_by_id(1)
    with pytest.raises(ValueError):
        repo.create_sale([{"product_id": 1, "name": product["name"], "price": product["price"], "qty": 999}], 999)
    with sqlite3.connect(isolated_db) as conn:
        assert conn.execute("SELECT COUNT(*) FROM sales").fetchone()[0] == 0
    assert repo.get_by_id(1)["stock"] == product["stock"]
