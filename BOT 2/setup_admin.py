"""
Script para configurar el usuario administrador con plan DIAMOND.
Ejecutar UNA SOLA VEZ antes de iniciar el bot.
"""
import sqlite3
import os

DB_NAME = "bot_database.sqlite"
ADMIN_ID = 1591755250

def setup():
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), DB_NAME)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Crear tabla si no existe
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            plan TEXT DEFAULT 'FREE',
            creditos INTEGER DEFAULT 0,
            is_whitelisted INTEGER DEFAULT 1,
            registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS request_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            command TEXT,
            cost INTEGER DEFAULT 0,
            success INTEGER DEFAULT 1,
            error_msg TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS daily_usage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            date TEXT,
            minute_count INTEGER DEFAULT 0,
            day_count INTEGER DEFAULT 0,
            UNIQUE(user_id, date)
        )
    """)
    
    # Verificar si el usuario ya existe
    cursor.execute("SELECT id FROM users WHERE id = ?", (ADMIN_ID,))
    existing = cursor.fetchone()
    
    if existing:
        # Actualizar a DIAMOND
        cursor.execute("""
            UPDATE users 
            SET plan = 'DIAMOND', creditos = 9999, is_whitelisted = 1
            WHERE id = ?
        """, (ADMIN_ID,))
        print(f"✅ Usuario {ADMIN_ID} actualizado a DIAMOND con 9999 créditos")
    else:
        # Crear nuevo usuario DIAMOND
        cursor.execute("""
            INSERT INTO users (id, username, first_name, plan, creditos, is_whitelisted)
            VALUES (?, ?, ?, 'DIAMOND', 9999, 1)
        """, (ADMIN_ID, "admin", "Administrador"))
        print(f"✅ Usuario {ADMIN_ID} creado con plan DIAMOND y 9999 créditos")
    
    conn.commit()
    conn.close()
    print("✅ Base de datos configurada correctamente")
    print("🚀 Ahora puedes ejecutar: python main.py")

if __name__ == "__main__":
    setup()
