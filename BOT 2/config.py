"""
Módulo de configuración centralizada del bot.
Todas las constantes y settings se definen aquí.
"""
import os
from typing import Dict, Final
from dotenv import load_dotenv

# Cargar variables desde el archivo .env
load_dotenv()

# ─── Token del Bot de Telegram ───────────────────────────────────────────────
BOT_TOKEN: Final[str] = os.getenv("BOT_TOKEN")

# ─── Token de la API PRIMEDOX ────────────────────────────────────────────────
API_TOKEN: Final[str] = os.getenv("API_TOKEN")

# ─── URLs ────────────────────────────────────────────────────────────────────
API_BASE_URL: Final[str] = "http://212.28.190.219:4006"
API_EXECUTE_URL: Final[str] = f"{API_BASE_URL}/api/execute"
API_COMMANDS_URL: Final[str] = f"{API_BASE_URL}/api/commands"
API_HEALTH_URL: Final[str] = f"{API_BASE_URL}/health"

# ─── Base de Datos ───────────────────────────────────────────────────────────
DB_NAME: Final[str] = "bot_database.sqlite"

# ─── Marca Blanca ────────────────────────────────────────────────────────────
BOT_NAME: Final[str] = "MARINEDOX_BOT"

# ─── Admin ───────────────────────────────────────────────────────────────────
ADMIN_PASSWORD: Final[str] = os.getenv("ADMIN_PASSWORD", "SuperSecreto123")
ADMIN_IDS: list[int] = [1591755250]  # IDs de Telegram con acceso admin total

# ─── Planes de Usuario ───────────────────────────────────────────────────────
PLAN_FREE: Final[str] = "FREE"
PLAN_GOLD: Final[str] = "GOLD"
PLAN_DIAMOND: Final[str] = "DIAMOND"

PLAN_LEVELS: Final[Dict[str, int]] = {
    PLAN_FREE: 1,
    PLAN_GOLD: 2,
    PLAN_DIAMOND: 3,
}

PLAN_HIERARCHY: Final[list[str]] = [PLAN_FREE, PLAN_GOLD, PLAN_DIAMOND]

# ─── Límites por Plan ────────────────────────────────────────────────────────
PLAN_LIMITS: Final[Dict[str, Dict[str, int]]] = {
    PLAN_FREE: {
        "rate_per_minute": 2,
        "rate_per_day": 10,
        "max_credits": 50,
        "monthly_free_credits": 0,
    },
    PLAN_GOLD: {
        "rate_per_minute": 10,
        "rate_per_day": 100,
        "max_credits": 500,
        "monthly_free_credits": 50,
    },
    PLAN_DIAMOND: {
        "rate_per_minute": 30,
        "rate_per_day": 999999,
        "max_credits": 9999,
        "monthly_free_credits": 200,
    },
}

# ─── Créditos Iniciales por Plan ─────────────────────────────────────────────
INITIAL_CREDITS: Final[Dict[str, int]] = {
    PLAN_FREE: 0,
    PLAN_GOLD: 50,
    PLAN_DIAMOND: 200,
}

# ─── Timeout API (recomendado 90s para PDFs/fotos) ───────────────────────────
API_TIMEOUT: Final[int] = 90

# ─── Costo por defecto si no se encuentra el comando ─────────────────────────
DEFAULT_COST: Final[int] = 1
