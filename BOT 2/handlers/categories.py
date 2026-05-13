"""
Handler para el menú de categorías de comandos.
Muestra los comandos disponibles en cada categoría según el plan del usuario.
"""
import logging
from typing import Dict

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from services.database import DatabaseService
from constants import (
    CATEGORIES,
    COMMANDS_BY_CATEGORY,
    COMMAND_COSTS,
    COMMAND_PLANS,
    COMMAND_DESCRIPTIONS,
)
from config import PLAN_LEVELS

logger = logging.getLogger(__name__)


def _build_category_text(category_key: str, user_plan: str) -> str:
    """
    Construye el texto de una categoría con todos sus comandos,
    indicando cuáles están disponibles según el plan del usuario.
    """
    category_name = CATEGORIES.get(category_key, category_key.upper())
    commands = COMMANDS_BY_CATEGORY.get(category_key, [])

    if not commands:
        return f"📌 *{category_name}*\n\nNo hay comandos disponibles en esta categoría."

    lines = [f"📌 *{category_name}*\n"]
    user_level = PLAN_LEVELS.get(user_plan, 1)

    for cmd in commands:
        cost = COMMAND_COSTS.get(cmd, 1)
        required_plan = COMMAND_PLANS.get(cmd, "FREE")
        description = COMMAND_DESCRIPTIONS.get(cmd, "")
        required_level = PLAN_LEVELS.get(required_plan, 1)

        if user_level >= required_level:
            # Comando disponible
            plan_emoji = "🟢" if required_plan == "FREE" else "🟡" if required_plan == "GOLD" else "🔴"
            lines.append(
                f"   `{cmd}` - {description}\n"
                f"   💰 {cost} créditos | {plan_emoji} {required_plan}\n"
            )
        else:
            # Comando bloqueado por plan
            lines.append(
                f"   ~~`{cmd}`~~ - {description}\n"
                f"   🔒 Requiere plan *{required_plan}*\n"
            )

    lines.append(f"\n💡 Tu plan: *{user_plan}*")
    return "\n".join(lines)


async def show_category(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Muestra los comandos de una categoría seleccionada.
    Se llama desde los callbacks 'cat_*' del menú principal.
    """
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    db = DatabaseService()
    db_user = db.get_user(user_id)

    if not db_user:
        await query.edit_message_text(
            "❌ No estás registrado. Usa /start para registrarte."
        )
        return

    # Extraer la categoría del callback data (ej: "cat_reniec" -> "reniec")
    category_key = query.data.split("_", 1)[1] if "_" in query.data else ""

    if category_key == "back":
        # Volver al menú principal
        from handlers.start import get_main_menu_keyboard
        await query.edit_message_text(
            text="Selecciona una categoría para consultar:",
            reply_markup=InlineKeyboardMarkup(get_main_menu_keyboard()),
        )
        return

    if category_key not in CATEGORIES:
        await query.edit_message_text("❌ Categoría no encontrada.")
        return

    category_text = _build_category_text(category_key, db_user.plan)

    keyboard = [
        [InlineKeyboardButton("⬅️ Volver al menú", callback_data="cat_back")],
    ]

    await query.edit_message_text(
        text=category_text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def back_to_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Vuelve al menú principal desde cualquier submenú.
    """
    query = update.callback_query
    await query.answer()

    from handlers.start import get_main_menu_keyboard

    user_id = query.from_user.id
    db = DatabaseService()
    db_user = db.get_user(user_id)

    if db_user:
        welcome_text = (
            f"👋 Menú Principal\n\n"
            f"📋 Tu plan: *{db_user.plan_emoji} {db_user.plan}*\n"
            f"💰 Créditos: *{db_user.creditos}*\n\n"
            f"Selecciona una categoría:"
        )
    else:
        welcome_text = "Selecciona una categoría:"

    await query.edit_message_text(
        text=welcome_text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(get_main_menu_keyboard()),
    )
