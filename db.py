import psycopg2
from psycopg2 import pool, extras, DatabaseError
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
import traceback
from config import postgres_db, postgres_userName, postgres_password, postgres_url, postgres_port


class PostgreSQL:
    def __init__(self):
        self.connection_pool = psycopg2.pool.ThreadedConnectionPool(
            1, 5,
            database=postgres_db, 
            user=postgres_userName,
            password=postgres_password, 
            host=postgres_url, 
            port=postgres_port
        )

    @contextmanager
    def get_connection(self):
        conn = self.connection_pool.getconn()
        try:
            # Ping the connection to ensure it's alive
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
            yield conn
        except psycopg2.Error:
            self.connection_pool.putconn(conn, close=True)  # discard bad conn
            raise
        else:
            self.connection_pool.putconn(conn)

    @contextmanager
    def get_cursor(self, dict_cursor=False):
        with self.get_connection() as conn:
            cursor_class = RealDictCursor if dict_cursor else None
            cursor = conn.cursor(cursor_factory=cursor_class)
            try:
                yield conn, cursor
            finally:
                cursor.close()

    def insert(self, sql, values):
        return self._execute_write(sql, values, fetch_result=True)

    def bulk_insert(self, sql, values):
        try:
            with self.get_cursor() as (conn, cursor):
                extras.execute_values(cursor, sql, values)
                conn.commit()
        except DatabaseError:
            traceback.print_exc()
            conn.rollback()

    def select_many(self, sql, values=None):
        return self._execute_read(sql, values, many=True)

    def select_one(self, sql, value=None):
        return self._execute_read(sql, value, many=False)

    def update_delete(self, sql, values):
        return self._execute_write(sql, values, return_rowcount=True)

    def _execute_read(self, sql, values=None, many=True):
        try:
            with self.get_cursor(dict_cursor=True) as (_, cursor):
                cursor.execute(sql, values)
                return cursor.fetchall() if many else cursor.fetchone()
        except DatabaseError:
            traceback.print_exc()

    def _execute_write(self, sql, values, fetch_result=False, return_rowcount=False):
        try:
            with self.get_cursor() as (conn, cursor):
                cursor.execute(sql, values)
                result = cursor.fetchone() if fetch_result else cursor.rowcount if return_rowcount else None
                conn.commit()
                return result
        except DatabaseError:
            traceback.print_exc()
            conn.rollback()

    def __del__(self):
        self.connection_pool.closeall()
