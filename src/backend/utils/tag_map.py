import sqlite3
from pathlib import Path


class TagMap:
    """
    This is a singleton class that maps tags to item ids.
    Data is persisted in a SQLite database.
    """
    _instance = None
    _db_path = Path(__file__).parent.parent.parent.parent / "tag_mappings.db"

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TagMap, cls).__new__(cls)
            cls._instance._init_db()
        return cls._instance

    def _init_db(self):
        """Initialize the SQLite database and create the table if it doesn't exist."""
        conn = sqlite3.connect(self._db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tag_mappings (
                tag TEXT NOT NULL,
                item_id TEXT NOT NULL,
                PRIMARY KEY (tag, item_id)
            )
        """)
        conn.commit()
        conn.close()

    def _get_connection(self):
        """Get a connection to the SQLite database."""
        return sqlite3.connect(self._db_path)

    def add_tag(self, tag: str, item_id: str):
        """Add a tag-to-item_id mapping to the database."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR IGNORE INTO tag_mappings (tag, item_id) VALUES (?, ?)",
            (tag, item_id)
        )
        conn.commit()
        conn.close()

    def get_items_for_tag(self, tag: str) -> list[str]:
        """Get all item IDs associated with a specific tag."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT item_id FROM tag_mappings WHERE tag = ?",
            (tag,)
        )
        results = [row[0] for row in cursor.fetchall()]
        conn.close()
        return results

    def get_map(self) -> dict[str, list[str]]:
        """Get all tag-to-item_id mappings as a dictionary."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT tag, item_id FROM tag_mappings")

        tags_dict = {}
        for tag, item_id in cursor.fetchall():
            if tag not in tags_dict:
                tags_dict[tag] = []
            tags_dict[tag].append(item_id)

        conn.close()
        return tags_dict

    def add_tags_to_item(self, item_id: str, tags: list[str]):
        """Add multiple tags to a single item."""
        for tag in tags:
            self.add_tag(tag, item_id)
