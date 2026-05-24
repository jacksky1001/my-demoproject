import json
import sqlite3
from contextlib import closing
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict

from src.models.data_models import CheckRecord


class RecordStorageService:
    def __init__(self, db_path: str, retention_days: int):
        self.db_path = Path(db_path)
        self.retention_days = retention_days
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        with closing(sqlite3.connect(self.db_path)) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS check_records (
                    id TEXT PRIMARY KEY,
                    check_time TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    payload TEXT NOT NULL
                )
                """
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_check_records_check_time ON check_records(check_time)")
            conn.commit()

    def load_records(self) -> Dict[str, CheckRecord]:
        self.cleanup_expired()
        with closing(sqlite3.connect(self.db_path)) as conn:
            rows = conn.execute("SELECT payload FROM check_records ORDER BY check_time DESC").fetchall()
        records = {}
        for (payload,) in rows:
            record = CheckRecord.model_validate(json.loads(payload))
            records[record.id] = record
        return records

    def save_record(self, record: CheckRecord):
        payload = record.model_dump_json()
        with closing(sqlite3.connect(self.db_path)) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO check_records (id, check_time, created_at, payload)
                VALUES (?, ?, ?, ?)
                """,
                (
                    record.id,
                    record.metadata.checkTime.isoformat(),
                    record.createdAt.isoformat(),
                    payload,
                ),
            )
            conn.commit()

    def cleanup_expired(self):
        cutoff = datetime.now() - timedelta(days=self.retention_days)
        with closing(sqlite3.connect(self.db_path)) as conn:
            conn.execute("DELETE FROM check_records WHERE check_time < ?", (cutoff.isoformat(),))
            conn.commit()
