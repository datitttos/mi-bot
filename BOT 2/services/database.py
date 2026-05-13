"""
Servicio de Base de Datos (DAO - Data Access Object).
Patrón Singleton para manejar la conexión SQLite.
Todas las operaciones CRUD de usuarios y logs se centralizan aquí.
"""
import sqlite3
import logging
from datetime import datetime, date
from typing import Optional, Dict, List, Any
from models.user import User
from config import DB_NAME

logger = logging.getLogger(__name__)


class DatabaseService:
    """Servicio singleton de base de datos SQLite."""

    _instance: Optional['DatabaseService'] = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, db_path: str = DB_NAME):
        if self._initialized:
            return
        self._initialized = True
        self.db_path = db_path
        self._init_tables()

    def _get_connection(self) -> sqlite3.Connection:
        """Obtiene una conexión a la base de datos."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        return conn

    def _init_tables(self) -> None:
        """Inicializa las tablas de la base de datos."""
        conn = self._get_connection()
        try:
            c = conn.cursor()

            # Tabla de usuarios
            c.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    plan TEXT DEFAULT 'FREE',
                    creditos INTEGER DEFAULT 0,
                    is_whitelisted BOOLEAN DEFAULT 0,
                    registered_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_active DATETIME,
                    monthly_credits_given INTEGER DEFAULT 0,
                    referral_code TEXT UNIQUE,
                    referred_by INTEGER
                )
            """)

            # Tabla de logs de consultas
            c.execute("""
                CREATE TABLE IF NOT EXISTS logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    user_id INTEGER,
                    command TEXT,
                    cost INTEGER DEFAULT 0,
                    success BOOLEAN DEFAULT 1,
                    error_msg TEXT
                )
            """)

            # Tabla de uso diario (rate limiting)
            c.execute("""
                CREATE TABLE IF NOT EXISTS daily_usage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    date TEXT,
                    count INTEGER DEFAULT 0,
                    UNIQUE(user_id, date)
                )
            """)

            # Tabla de settings de administración
            c.execute("""
                CREATE TABLE IF NOT EXISTS admin_settings (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            """)

            conn.commit()
            logger.info("Base de datos inicializada correctamente.")
        except Exception as e:
            logger.error(f"Error inicializando base de datos: {e}")
            raise
        finally:
            conn.close()

    # ─── CRUD de Usuarios ────────────────────────────────────────────────────

    def get_user(self, user_id: int) -> Optional[User]:
        """Obtiene un usuario por su ID."""
        conn = self._get_connection()
        try:
            c = conn.cursor()
            c.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            row = c.fetchone()
            if row:
                return User(**dict(row))
            return None
        except Exception as e:
            logger.error(f"Error obteniendo usuario {user_id}: {e}")
            return None
        finally:
            conn.close()

    def create_user(
        self,
        user_id: int,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        plan: str = "FREE",
        creditos: int = 0,
    ) -> User:
        """Crea un nuevo usuario en la base de datos."""
        conn = self._get_connection()
        try:
            c = conn.cursor()
            c.execute(
                """
                INSERT OR IGNORE INTO users
                    (id, username, first_name, plan, creditos, is_whitelisted, registered_at)
                VALUES (?, ?, ?, ?, ?, 1, CURRENT_TIMESTAMP)
                """,
                (user_id, username, first_name, plan, creditos),
            )
            conn.commit()
            logger.info(f"Usuario {user_id} creado con plan {plan} y {creditos} créditos.")
            return self.get_user(user_id) or User(
                id=user_id,
                plan=plan,
                creditos=creditos,
                is_whitelisted=True,
                username=username,
                first_name=first_name,
            )
        except Exception as e:
            logger.error(f"Error creando usuario {user_id}: {e}")
            raise
        finally:
            conn.close()

    def update_user(self, user_id: int, **kwargs) -> Optional[User]:
        """Actualiza campos de un usuario."""
        conn = self._get_connection()
        try:
            c = conn.cursor()
            allowed_fields = {
                "plan", "creditos", "is_whitelisted", "username", "first_name",
                "last_active", "monthly_credits_given", "referral_code", "referred_by",
            }
            updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
            if not updates:
                return self.get_user(user_id)

            set_clause = ", ".join(f"{k} = ?" for k in updates.keys())
            values = list(updates.values()) + [user_id]

            c.execute(
                f"UPDATE users SET {set_clause} WHERE id = ?",
                values,
            )
            conn.commit()
            return self.get_user(user_id)
        except Exception as e:
            logger.error(f"Error actualizando usuario {user_id}: {e}")
            return None
        finally:
            conn.close()

    def update_last_active(self, user_id: int) -> None:
        """Actualiza el timestamp de última actividad."""
        self.update_user(user_id, last_active=datetime.now().isoformat())

    def get_all_users(self) -> List[User]:
        """Obtiene todos los usuarios registrados."""
        conn = self._get_connection()
        try:
            c = conn.cursor()
            c.execute("SELECT * FROM users ORDER BY registered_at DESC")
            return [User(**dict(row)) for row in c.fetchall()]
        except Exception as e:
            logger.error(f"Error obteniendo todos los usuarios: {e}")
            return []
        finally:
            conn.close()

    def get_user_count(self) -> int:
        """Obtiene el número total de usuarios."""
        conn = self._get_connection()
        try:
            c = conn.cursor()
            c.execute("SELECT COUNT(*) FROM users")
            return c.fetchone()[0]
        finally:
            conn.close()

    # ─── Gestión de Créditos ─────────────────────────────────────────────────

    def deduct_credits(self, user_id: int, cost: int) -> bool:
        """Descuenta créditos de un usuario. Retorna True si se pudo."""
        user = self.get_user(user_id)
        if not user or user.creditos < cost:
            return False
        self.update_user(user_id, creditos=user.creditos - cost)
        return True

    def add_credits(self, user_id: int, amount: int) -> Optional[User]:
        """Agrega créditos a un usuario."""
        user = self.get_user(user_id)
        if not user:
            return None
        return self.update_user(user_id, creditos=user.creditos + amount)

    # ─── Logs ────────────────────────────────────────────────────────────────

    def log_request(
        self,
        user_id: int,
        command: str,
        cost: int = 0,
        success: bool = True,
        error_msg: Optional[str] = None,
    ) -> None:
        """Registra una consulta en el log."""
        conn = self._get_connection()
        try:
            c = conn.cursor()
            c.execute(
                "INSERT INTO logs (user_id, command, cost, success, error_msg) VALUES (?, ?, ?, ?, ?)",
                (user_id, command, cost, success, error_msg),
            )
            conn.commit()
        except Exception as e:
            logger.error(f"Error registrando log: {e}")
        finally:
            conn.close()

    def get_user_logs(
        self,
        user_id: int,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """Obtiene los últimos logs de un usuario."""
        conn = self._get_connection()
        try:
            c = conn.cursor()
            c.execute(
                """
                SELECT timestamp, command, cost, success, error_msg
                FROM logs WHERE user_id = ?
                ORDER BY timestamp DESC LIMIT ?
                """,
                (user_id, limit),
            )
            return [dict(row) for row in c.fetchall()]
        finally:
            conn.close()

    # ─── Rate Limiting ───────────────────────────────────────────────────────

    def get_minute_count(self, user_id: int) -> int:
        """Obtiene el número de consultas en el último minuto."""
        conn = self._get_connection()
        try:
            c = conn.cursor()
            c.execute(
                """
                SELECT COUNT(*) FROM logs
                WHERE user_id = ?
                AND timestamp >= datetime('now', '-1 minute')
                """,
                (user_id,),
            )
            return c.fetchone()[0]
        finally:
            conn.close()

    def get_daily_count(self, user_id: int) -> int:
        """Obtiene el número de consultas hoy."""
        today = date.today().isoformat()
        conn = self._get_connection()
        try:
            c = conn.cursor()
            c.execute(
                """
                SELECT count FROM daily_usage
                WHERE user_id = ? AND date = ?
                """,
                (user_id, today),
            )
            row = c.fetchone()
            return row["count"] if row else 0
        finally:
            conn.close()

    def increment_daily_count(self, user_id: int) -> None:
        """Incrementa el contador diario de consultas."""
        today = date.today().isoformat()
        conn = self._get_connection()
        try:
            c = conn.cursor()
            c.execute(
                """
                INSERT INTO daily_usage (user_id, date, count) VALUES (?, ?, 1)
                ON CONFLICT(user_id, date) DO UPDATE SET count = count + 1
                """,
                (user_id, today),
            )
            conn.commit()
        finally:
            conn.close()

    # ─── Estadísticas ────────────────────────────────────────────────────────

    def get_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas generales del bot."""
        conn = self._get_connection()
        try:
            c = conn.cursor()

            c.execute("SELECT COUNT(*) FROM users")
            total_users = c.fetchone()[0]

            c.execute("SELECT COUNT(*) FROM logs")
            total_queries = c.fetchone()[0]

            c.execute("SELECT COUNT(*) FROM logs WHERE timestamp >= datetime('now', '-1 day')")
            today_queries = c.fetchone()[0]

            c.execute(
                """
                SELECT plan, COUNT(*) as count FROM users
                GROUP BY plan ORDER BY count DESC
                """
            )
            plan_distribution = {row["plan"]: row["count"] for row in c.fetchall()}

            c.execute(
                """
                SELECT command, COUNT(*) as count FROM logs
                WHERE success = 1
                GROUP BY command ORDER BY count DESC LIMIT 5
                """
            )
            top_commands = [dict(row) for row in c.fetchall()]

            return {
                "total_users": total_users,
                "total_queries": total_queries,
                "today_queries": today_queries,
                "plan_distribution": plan_distribution,
                "top_commands": top_commands,
            }
        finally:
            conn.close()
