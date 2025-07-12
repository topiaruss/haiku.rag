import json
from typing import Any

from haiku.rag.store.engine import Store


class SettingsRepository:
    def __init__(self, store: Store):
        self.store = store

    def get(self) -> dict[str, Any]:
        """Get all settings from the database."""
        if self.store._connection is None:
            raise ValueError("Store connection is not available")

        cursor = self.store._connection.execute("SELECT settings FROM settings LIMIT 1")
        row = cursor.fetchone()
        if row:
            return json.loads(row[0])
        return {}

    def save(self) -> None:
        """Sync settings from the current AppConfig to database."""
        if self.store._connection is None:
            raise ValueError("Store connection is not available")

        from haiku.rag.config import Config

        settings_json = Config.model_dump_json()

        self.store._connection.execute(
            "INSERT INTO settings (id, settings) VALUES (1, ?) ON CONFLICT(id) DO UPDATE SET settings = excluded.settings",
            (settings_json,),
        )

        self.store._connection.commit()
