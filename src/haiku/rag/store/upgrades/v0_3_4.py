from collections.abc import Callable
from sqlite3 import Connection

from haiku.rag.config import Config


def add_settings_table(db: Connection) -> None:
    """Create settings table for storing current configuration"""
    db.execute("""
        CREATE TABLE settings (
            id INTEGER PRIMARY KEY DEFAULT 1,
            settings TEXT NOT NULL DEFAULT '{}'
        )
    """)

    settings_json = Config.model_dump_json()
    db.execute(
        "INSERT INTO settings (id, settings) VALUES (1, ?)",
        (settings_json,),
    )
    db.commit()


upgrades: list[tuple[str, list[Callable[[Connection], None]]]] = [
    ("0.3.4", [add_settings_table])
]
