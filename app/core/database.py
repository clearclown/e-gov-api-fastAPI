"""Database connection and session management"""

import psycopg
from typing import AsyncGenerator
from contextlib import asynccontextmanager
from app.core.config import settings


class Database:
    """Database connection manager"""

    def __init__(self):
        self.connection_string = settings.database_url
        self._pool = None

    async def connect(self):
        """Initialize database connection pool"""
        # Note: For production, consider using asyncpg or psycopg3 with connection pooling
        pass

    async def disconnect(self):
        """Close database connection pool"""
        if self._pool:
            await self._pool.close()

    @asynccontextmanager
    async def get_connection(self) -> AsyncGenerator[psycopg.AsyncConnection, None]:
        """Get a database connection from the pool"""
        async with await psycopg.AsyncConnection.connect(self.connection_string) as conn:
            yield conn

    @asynccontextmanager
    async def get_cursor(self) -> AsyncGenerator[psycopg.AsyncCursor, None]:
        """Get a database cursor"""
        async with self.get_connection() as conn:
            async with conn.cursor() as cur:
                yield cur


# Global database instance
db = Database()
