from pathlib import Path
import sqlite3
from typing import Iterator

DB_PATH = Path(__file__).parent / "productos.db"

_SCHEMA = """
-- Tabla de productos
CREATE TABLE IF NOT EXISTS producto (
    id         TEXT PRIMARY KEY,
    name       TEXT NOT NULL,
    size       TEXT,
    weight     REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de movimientos
CREATE TABLE IF NOT EXISTS movimiento (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    producto_id TEXT NOT NULL,
    origen      TEXT,
    destino     TEXT,
    fecha       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (producto_id) REFERENCES producto(id)
);
"""


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.executescript(_SCHEMA)
    return conn


def insert_producto(prod_id: str, name: str, size: str | None = None, weight: float | None = None) -> None:
    with get_connection() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO producto (id, name, size, weight) VALUES (?, ?, ?, ?)",
            (prod_id, name, size, weight),
        )


def insert_movimiento(prod_id: str, origen: str, destino: str) -> None:
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO movimiento (producto_id, origen, destino) VALUES (?, ?, ?)",
            (prod_id, origen, destino),
        )


def all_productos() -> Iterator[sqlite3.Row]:
    conn = get_connection()
    cur = conn.execute("SELECT * FROM producto ORDER BY created_at DESC")
    return cur.fetchall()
