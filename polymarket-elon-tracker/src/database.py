"""SQLite database for persistent tweet storage."""
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


class TweetDB:
    DB_PATH = Path(__file__).parent.parent / "data" / "tracker.db"

    def __init__(self):
        self.DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.DB_PATH) as cx:
            cx.executescript("""
                CREATE TABLE IF NOT EXISTS tweets (
                    post_id    TEXT PRIMARY KEY,
                    timestamp  TEXT NOT NULL,  -- ISO UTC
                    hour       INTEGER,
                    weekday    TEXT,
                    text       TEXT,
                    likes      INTEGER DEFAULT 0,
                    rts        INTEGER DEFAULT 0,
                    replies    INTEGER DEFAULT 0,
                    views      INTEGER DEFAULT 0,
                    is_pinned  INTEGER DEFAULT 0,
                    has_media  INTEGER DEFAULT 0,
                    collected_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS meta (
                    key   TEXT PRIMARY KEY,
                    value TEXT
                );
                CREATE TABLE IF NOT EXISTS market_snapshots (
                    market_id   TEXT NOT NULL,
                    window_start TEXT NOT NULL,
                    window_end   TEXT NOT NULL,
                    target_count INTEGER,
                    count        INTEGER NOT NULL,
                    count_est    REAL,
                    updated_at    TEXT NOT NULL,
                    UNIQUE(market_id, window_start)
                );
                CREATE INDEX IF NOT EXISTS idx_tweets_timestamp ON tweets(timestamp);
            """)

    # ── tweets ──────────────────────────────────────────────────────────────

    def upsert_tweet(self, post_id: str, timestamp: str, text: str,
                     likes: int = 0, rts: int = 0, replies: int = 0,
                     views: int = 0, is_pinned: bool = False,
                     has_media: bool = False):
        try:
            dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        except Exception:
            return False

        hour = dt.hour
        weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        weekday = weekdays[dt.weekday()]
        collected_at = datetime.now(timezone.utc).isoformat()

        with sqlite3.connect(self.DB_PATH) as cx:
            cx.execute("""
                INSERT INTO tweets (post_id,timestamp,hour,weekday,text,likes,rts,replies,views,is_pinned,has_media,collected_at)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
                ON CONFLICT(post_id) DO UPDATE SET
                    text=excluded.text, likes=excluded.likes, rts=excluded.rts,
                    replies=excluded.replies, views=excluded.views
            """, (post_id, timestamp, hour, weekday, text, likes, rts,
                  replies, views, int(is_pinned), int(has_media), collected_at))
        return True

    def bulk_upsert(self, tweets: list):
        n = 0
        for t in tweets:
            ok = self.upsert_tweet(
                t["post_id"], t["timestamp"], t.get("text", ""),
                t.get("likes", 0), t.get("retweets", 0),
                t.get("replies", 0), t.get("views", 0),
                t.get("is_pinned", False), t.get("has_media", False)
            )
            if ok:
                n += 1
        return n

    def count_in_window(self, window_start: str, window_end: str) -> int:
        """Count tweets within UTC window [window_start, window_end]."""
        with sqlite3.connect(self.DB_PATH) as cx:
            cur = cx.execute("""
                SELECT COUNT(*) FROM tweets
                WHERE timestamp >= ? AND timestamp <= ?
            """, (window_start, window_end))
            row = cur.fetchone()
            return row[0] if row else 0

    def get_recent_tweets(self, hours: int = 24) -> list:
        """Get tweets from the last N hours."""
        cutoff = datetime.now(timezone.utc).isoformat()
        # naive approach: just get all sorted by timestamp desc
        with sqlite3.connect(self.DB_PATH) as cx:
            cur = cx.execute("""
                SELECT post_id,timestamp,text,hour,weekday,likes,rts,replies,views,is_pinned,has_media
                FROM tweets ORDER BY timestamp DESC
            """)
            rows = cur.fetchall()
        cutoff_dt = datetime.now(timezone.utc).replace(
            minute=0, second=0, microsecond=0
        ) - datetime.timedelta(hours=hours)
        cutoff_iso = cutoff_dt.isoformat().replace("+00:00", "Z")
        return [r for r in rows if r[1] >= cutoff_iso]

    def get_all_tweets(self) -> list:
        with sqlite3.connect(self.DB_PATH) as cx:
            cur = cx.execute("""
                SELECT post_id,timestamp,text,hour,weekday,likes,rts,replies,views,is_pinned,has_media
                FROM tweets ORDER BY timestamp DESC
            """)
            return cur.fetchall()

    def total_tweets(self) -> int:
        with sqlite3.connect(self.DB_PATH) as cx:
            cur = cx.execute("SELECT COUNT(*) FROM tweets")
            return cur.fetchone()[0]

    # ── meta ────────────────────────────────────────────────────────────────

    def get_meta(self, key: str) -> Optional[str]:
        with sqlite3.connect(self.DB_PATH) as cx:
            cur = cx.execute("SELECT value FROM meta WHERE key=?", (key,))
            r = cur.fetchone()
            return r[0] if r else None

    def set_meta(self, key: str, value: str):
        with sqlite3.connect(self.DB_PATH) as cx:
            cx.execute("INSERT INTO meta VALUES (?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                       (key, value))

    def last_collected_pid(self) -> Optional[str]:
        return self.get_meta("last_collected_pid")

    def set_last_collected_pid(self, pid: str):
        self.set_meta("last_collected_pid", pid)

    def last_collect_time(self) -> Optional[str]:
        return self.get_meta("last_collect_time")

    def set_last_collect_time(self, ts: str):
        self.set_meta("last_collect_time", ts)

    # ── market snapshots ────────────────────────────────────────────────────

    def save_market_snapshot(self, market_id, window_start, window_end,
                            target_count, count, count_est):
        with sqlite3.connect(self.DB_PATH) as cx:
            cx.execute("""
                INSERT INTO market_snapshots
                  (market_id,window_start,window_end,target_count,count,count_est,updated_at)
                VALUES (?,?,?,?,?,?,?)
                ON CONFLICT(market_id,window_start) DO UPDATE SET
                    count=excluded.count, count_est=excluded.count_est, updated_at=excluded.updated_at
            """, (market_id, window_start, window_end, target_count, count, count_est,
                  datetime.now(timezone.utc).isoformat()))
