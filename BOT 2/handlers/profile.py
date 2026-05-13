"""
Handler para el perfil de usuario, créditos y planes.
Muestra información del usuario y permite ver detalles del plan.
"""
import logging
from datetime import datetime

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from services.database import DatabaseService
from config import PLAN_LIMITS, PLAN_HIERARCHY

logger = logging.getLogger(__name__)


async def show_profile(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Muestra el perfil del usuario: plan, créditos, estadísticas de uso.
    Se llama desde el callback 'profile' del menú principal.
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

    # Obtener estadísticas de uso
    minute_count = db.get_minute_count(user_id)
    daily_count = db.get_daily_count(user_id)
    limits = PLAN_LIMITS.get(db_user.plan, PLAN_LIMITS["FREE"])
    logs = db.get_user_logs(user_id, limit=5)

    # Construir mensaje de perfil
    profile_text = (
        f"👤 *Perfil de Usuario*\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"🆔 ID: `{db_user.id}`\n"
        f"📛 Nombre: {db_user.first_name or 'No registrado'}\n"
        f"📱 Usuario: @{db_user.username or 'No tiene'}\n\n"
        f"💎 *Plan:* {db_user.plan_emoji} {db_user.plan}\n"
        f"💰 *Créditos:* {db_user.creditos}\n\n"
        f"📊 *Uso de hoy:*\n"
        f"   • Por minuto: {minute_count}/{limits['rate_per_minute']}\n"
        f"   • Diario: {daily_count}/{limits['rate_per_day'] if limits['rate_per_day'] < 999999 else '∞'}\n\n"
    )

    if logs:
        profile_text += "📋 *Últimas consultas:*\n"
        for log in logs:
            emoji = "✅" if log["success"] else "❌"
            profile_text += f"   {emoji} `{log['command']}` (-{log['cost']}💰)\n"

    profile_text += (
        f"\n💡 *Planes disponibles:*\n"
        f"🟢 FREE: 0 créditos, 2 req/min, 10/día\n"
        f"🟡 GOLD: 50 créditos/mes, 10 req/min, 100/día\n"
        f"🔴 DIAMOND: 200 créditos/mes, 30 req/min, Ilimitado\n\n"
        f"📞 Contacta al administrador para mejorar tu plan."
    )

    keyboard = [
        [InlineKeyboardButton("⬅️ Volver al menú", callback_data="back_to_menu")],
    ]

    await query.edit_message_text(
        text=profile_text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def show_stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Muestra estadísticas generales del bot.
    Se llama desde el callback 'stats' del menú principal.
    """
    query = update.callback_query
    await query.answer()

    db = DatabaseService()
    stats = db.get_stats()

    plan_dist = stats.get("plan_distribution", {})
    plan_text = "\n".join(
        f"   {p}: {c} usuarios" for p, c in plan_dist.items()
    ) or "   Sin datos"

    top_cmds = stats.get("top_commands", [])
    top_text = "\n".join(
        f"   {i+1}. `{c['command']}` - {c['count']} consultas"
        for i, c in enumerate(top_cmds)
    ) or "   Sin datos"

    stats_text = (
        f"📊 *Estadísticas del Bot*\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"👥 *Usuarios totales:* {stats['total_users']}\n"
        f"📊 *Consultas totales:* {stats['total_queries']}\n"
        f"📅 *Consultas hoy:* {stats['today_queries']}\n\n"
        f"💎 *Distribución de planes:*\n{plan_text}\n\n"
        f"🔥 *Comandos más usados:*\n{top_text}"
    )

    keyboard = [
        [InlineKeyboardButton("⬅️ Volver al menú", callback_data="back_to_menu")],
    ]

    await query.edit_message_text(
        text=stats_text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
