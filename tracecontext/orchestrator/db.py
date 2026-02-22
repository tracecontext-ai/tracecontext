import os
import psycopg2
from psycopg2.extras import RealDictCursor
import redis
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
            self.pg_conn = psycopg2.connect(
                os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/tracecontext"),
                cursor_factory=RealDictCursor
            )
            logger.info("Connected to PostgreSQL")
        except Exception as e:
            logger.error(f"Failed to connect to PostgreSQL: {e}")

    def _init_redis(self):
        try:
            self.redis_client = redis.Redis(
                host=os.getenv("REDIS_HOST", "localhost"),
                port=int(os.getenv("REDIS_PORT", 6379)),
                db=0
            )
            logger.info("Connected to Redis")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")

    def store_adr(self, adr_data: dict):
        with self.pg_conn.cursor() as cur:
            cur.execute(
                "INSERT INTO adrs (title, content, metadata) VALUES (%s, %s, %s)",
                (adr_data['title'], adr_data['content'], adr_data.get('metadata', {}))
            )
            self.pg_conn.commit()

    def get_session_context(self, session_id: str):
        return self.redis_client.get(f"session:{session_id}")
