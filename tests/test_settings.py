from haiku.rag.config import Config
from haiku.rag.store.engine import Store
from haiku.rag.store.repositories.settings import SettingsRepository


def test_settings_table_populated_on_store_init():
    """Test that settings table is populated with current config when store is initialized."""

    store = Store(":memory:")
    settings_repo = SettingsRepository(store)

    db_settings = settings_repo.get()
    config_dict = Config.model_dump(mode="json")

    assert db_settings == config_dict

    store.close()


def test_settings_save_and_retrieve():
    """Test saving and retrieving settings after config change."""
    store = Store(":memory:")
    settings_repo = SettingsRepository(store)

    original_chunk_size = Config.CHUNK_SIZE
    Config.CHUNK_SIZE = 2 * original_chunk_size

    settings_repo.save()
    retrieved_settings = settings_repo.get()
    assert retrieved_settings["CHUNK_SIZE"] == 2 * original_chunk_size

    Config.CHUNK_SIZE = original_chunk_size
    store.close()
