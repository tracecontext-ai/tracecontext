"""
DatabaseManager — optional PostgreSQL + Redis persistence layer.

These connections are optional. The orchestrator runs without them,
using in-memory storage. Configure DATABASE_URL and REDIS_HOST in .env
to enable persistent storage.
"""

import os
import logging

logger = logging.getLogger(__name__)


class DatabaseManager:
    def __init__(self):
        self.pg_conn = None
        self.redis_client = None
        self._init_pg()
        self._init_redis()

    def _init_pg(self):
        try:
            import psycopg2
            from psycopg2.extras import RealDictCursor
            self.pg_conn = psycopg2.connect(
                os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/tracecontext"),
                cursor_factory=RealDictCursor,
            )
            logger.info("Connected to PostgreSQL")
        except ImportError:
            logger.debug("psycopg2 not installed — PostgreSQL disabled.")
        except Exception as e:
            logger.warning(f"PostgreSQL unavailable: {e}")

    def _init_redis(self):
        try:
            import redis as redis_lib
            self.redis_client = redis_lib.Redis(
                host=os.getenv("REDIS_HOST", "localhost"),
                port=int(os.getenv("REDIS_PORT", 6379)),
                db=0,
            )
            self.redis_client.ping()
            logger.info("Connected to Redis")
        except ImportError:
            logger.debug("redis not installed — Redis disabled.")
        except Exception as e:
            logger.warning(f"Redis unavailable: {e}")

    def store_adr(self, adr_data: dict):
        if self.pg_conn is None:
            logger.warning("store_adr called but PostgreSQL is not connected.")
            return
        with self.pg_conn.cursor() as cur:
            cur.execute(
                "INSERT INTO adrs (title, content, metadata) VALUES (%s, %s, %s)",
                (adr_data["title"], adr_data["content"], adr_data.get("metadata", {})),
            )
            self.pg_conn.commit()

    def get_session_context(self, session_id: str):
        if self.redis_client is None:
            logger.warning("get_session_context called but Redis is not connected.")
            return None
        return self.redis_client.get(f"session:{session_id}")
