"""
SQLite database management for the Google Maps scraping application.
"""

import sqlite3
from datetime import datetime

# Colonnes attendues (hors id) : nom -> définition SQL
SCHEMA_COLUMNS = {
    "name": "TEXT",
    "phone": "TEXT",
    "address": "TEXT",
    "category": "TEXT",
    "country": "TEXT",
    "wilaya": "TEXT",
    "has_website": "INTEGER DEFAULT 0",
    "website_url": "TEXT",
    "rating": "TEXT",
    "reviews_count": "TEXT",
    "status": "TEXT",
    "maps_url": "TEXT",
    "search_query": "TEXT",
    "scraped_at": "TEXT",
}


class Database:
    def __init__(self, db_path="results.db"):
        self.db_path = db_path
        self._init_db()
        self._migrate()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        conn = self._connect()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS results (
                id INTEGER PRIMARY KEY AUTOINCREMENT
            )
        """)
        conn.commit()
        conn.close()

    def _migrate(self):
        """Ajoute automatiquement les colonnes manquantes (mise à jour d'une base existante)."""
        conn = self._connect()
        cur = conn.cursor()
        cur.execute("PRAGMA table_info(results)")
        existing_cols = {row[1] for row in cur.fetchall()}

        for col, sqltype in SCHEMA_COLUMNS.items():
            if col not in existing_cols:
                cur.execute(f"ALTER TABLE results ADD COLUMN {col} {sqltype}")

        conn.commit()

        # Index anti-doublon (recréé si absent)
        try:
            cur.execute("""
                CREATE UNIQUE INDEX IF NOT EXISTS idx_unique_result
                ON results(name, address)
            """)
            conn.commit()
        except sqlite3.OperationalError:
            pass
        conn.close()

    def insert_result(self, data: dict):
        conn = self._connect()
        cur = conn.cursor()
        try:
            cur.execute("""
                INSERT INTO results
                (name, phone, address, category, country, wilaya, has_website,
                 website_url, rating, reviews_count, status, maps_url,
                 search_query, scraped_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data.get("name", ""),
                data.get("phone", ""),
                data.get("address", ""),
                data.get("category", ""),
                data.get("country", ""),
                data.get("wilaya", ""),
                1 if data.get("has_website") else 0,
                data.get("website_url", ""),
                data.get("rating", ""),
                data.get("reviews_count", ""),
                data.get("status", ""),
                data.get("maps_url", ""),
                data.get("search_query", ""),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            ))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()

    def get_all_results(self, only_without_website=False, wilaya=None, country=None):
        conn = self._connect()
        cur = conn.cursor()
        query = """SELECT id, name, phone, address, category, country, wilaya,
                          has_website, website_url, rating, reviews_count,
                          status, maps_url, scraped_at
                   FROM results WHERE 1=1"""
        params = []
        if only_without_website:
            query += " AND has_website = 0"
        if wilaya:
            query += " AND wilaya = ?"
            params.append(wilaya)
        if country:
            query += " AND country = ?"
            params.append(country)
        query += " ORDER BY id DESC"
        cur.execute(query, params)
        rows = cur.fetchall()
        conn.close()
        return rows

    def delete_all(self):
        conn = self._connect()
        cur = conn.cursor()
        cur.execute("DELETE FROM results")
        conn.commit()
        conn.close()

    def count(self):
        conn = self._connect()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM results")
        n = cur.fetchone()[0]
        conn.close()
        return n
