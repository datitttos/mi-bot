"""
Handler para el comando /start y registro de nuevos usuarios.
Maneja el flujo de bienvenida y registro.
"""
import logging
from typing import Optional

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from services.database import DatabaseService
from models.user import User
from config import INITIAL_CREDITS, PLAN_FREE

logger = logging.getLogger(__name__)


def get_main_menu_keyboard() -> list:
    """Construye el teclado del menú principal con todas las categorías."""
    return [
        [
            InlineKeyboardButton("🏷️ RENIEC", callback_data="cat_reniec"),
            InlineKeyboardButton("⚖️ JUSTICIA", callback_data="cat_justicia"),
        ],
        [
            InlineKeyboardButton("💰 SUNAT", callback_data="cat_sunat"),
            InlineKeyboardButton("📱 TELEFONÍA", callback_data="cat_telefonia"),
        ],
        [
            InlineKeyboardButton("🛂 MIGRACIONES", callback_data="cat_migraciones"),
            InlineKeyboardButton("🏛️ SUNARP", callback_data="cat_sunarp"),
        ],
        [
            InlineKeyboardButton("💳 FINANCIERO", callback_data="cat_financiero"),
            InlineKeyboardButton("🚗 VEHÍCULOS", callback_data="cat_vehiculos"),
        ],
        [
            InlineKeyboardButton("👔 LABORAL", callback_data="cat_laboral"),
            InlineKeyboardButton("📋 PLUS GENERAL", callback_data="cat_plus"),
        ],
        [
            InlineKeyboardButton("👨‍👩‍👧‍👦 FAMILIA", callback_data="cat_familia"),
            InlineKeyboardButton("📄 ACTAS", callback_data="cat_actas"),
        ],
        [
            InlineKeyboardButton("📧 SPAM", callback_data="cat_spam"),
            InlineKeyboardButton("🧾 BAUCHERS", callback_data="cat_bauchers"),
        ],
        [
            InlineKeyboardButton("👤 Mi Perfil", callback_data="profile"),
            InlineKeyboardButton("📊 Estadísticas", callback_data="stats"),
        ],
    ]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Maneja el comando /start.
    Si el usuario no existe, lo registra automáticamente.
    Si ya existe, muestra el menú principal.
    """
    user = update.effective_user
    if not user:
        return

    db = DatabaseService()
    db_user = db.get_user(user.id)

    if not db_user:
        # Registrar nuevo usuario
        db_user = db.create_user(
            user_id=user.id,
            username=user.username,
            first_name=user.first_name,
            plan=PLAN_FREE,
            creditos=INITIAL_CREDITS[PLAN_FREE],
        )
        logger.info(f"Nuevo usuario registrado: {user.id} - @{user.username}")

        welcome_text = (
            f"👋 ¡Bienvenido *{user.first_name or 'Usuario'}*!\n\n"
            f"✅ Te has registrado exitosamente.\n"
            f"📋 Tu plan actual: *{db_user.plan}*\n"
            f"💰 Créditos: *{db_user.creditos}*\n\n"
            f"Selecciona una categoría para comenzar:"
        )
    else:
        # Actualizar último acceso
        db.update_last_active(user.id)

        welcome_text = (
            f"👋 ¡Bienvenido de nuevo *{user.first_name or 'Usuario'}*!\n\n"
            f"📋 Tu plan: *{db_user.plan_emoji} {db_user.plan}*\n"
            f"💰 Créditos disponibles: *{db_user.creditos}*\n\n"
            f"Selecciona una categoría para consultar:"
        )

    reply_markup = InlineKeyboardMarkup(get_main_menu_keyboard())

    await update.message.reply_text(
        text=welcome_text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=reply_markup,
    )
