"""
Handler de comandos de administración.
Protegidos por contraseña y por lista de ADMIN_IDS.
"""
import logging
from typing import Optional

from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from services.database import DatabaseService
from config import ADMIN_PASSWORD, ADMIN_IDS, PLAN_HIERARCHY, INITIAL_CREDITS

logger = logging.getLogger(__name__)


def _is_admin(user_id: int) -> bool:
    """Verifica si un usuario es administrador por ID."""
    return user_id in ADMIN_IDS


async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Comando /admin - Panel de administración.
    Uso: /admin <contraseña>
    Si la contraseña es correcta, muestra el panel de admin.
    """
    user_id = update.effective_user.id
    message_text = update.message.text or ""

    parts = message_text.split(maxsplit=1)
    if len(parts) < 2:
        await update.message.reply_text(
            "❌ Uso: `/admin <contraseña>`\n"
            "Ejemplo: `/admin MiClaveSecreta`",
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    password = parts[1].strip()

    if password != ADMIN_PASSWORD:
        await update.message.reply_text("❌ Contraseña de administrador incorrecta.")
        return

    # Agregar a ADMIN_IDS si no está ya
    if user_id not in ADMIN_IDS:
        ADMIN_IDS.append(user_id)
        logger.info(f"Usuario {user_id} promovido a administrador.")

    admin_text = (
        "👑 *Panel de Administración*\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "Comandos disponibles:\n\n"
        "📝 *Gestión de Usuarios:*\n"
        "`/adduser <id> [plan] [creditos]`\n"
        "   Crear o actualizar usuario\n\n"
        "`/setplan <id> <plan>`\n"
        "   Cambiar plan (FREE/GOLD/DIAMOND)\n\n"
        "`/addcredits <id> <cantidad>`\n"
        "   Agregar créditos a un usuario\n\n"
        "`/delcredits <id> <cantidad>`\n"
        "   Quitar créditos a un usuario\n\n"
        "`/userinfo <id>`\n"
        "   Ver información de un usuario\n\n"
        "📊 *Estadísticas:*\n"
        "`/stats`\n"
        "   Ver estadísticas del bot\n\n"
        "📢 *Mensajes:*\n"
        "`/broadcast <mensaje>`\n"
        "   Enviar mensaje a todos los usuarios\n\n"
        "🔄 *Sistema:*\n"
        "`/reset_limits <id>`\n"
        "   Resetear límites de un usuario\n\n"
        "`/give_monthly`\n"
        "   Dar créditos mensuales a todos"
    )

    await update.message.reply_text(admin_text, parse_mode=ParseMode.MARKDOWN)


async def add_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Comando /adduser - Crear o actualizar usuario.
    Uso: /adduser <id> [plan] [creditos]
    """
    user_id = update.effective_user.id
    if not _is_admin(user_id):
        await update.message.reply_text("❌ No tienes permisos de administrador.")
        return

    parts = update.message.text.split()
    if len(parts) < 2:
        await update.message.reply_text(
            "❌ Uso: `/adduser <id> [plan] [creditos]`\n"
            "Ejemplo: `/adduser 123456789 GOLD 100`",
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    try:
        target_id = int(parts[1])
    except ValueError:
        await update.message.reply_text("❌ El ID debe ser un número.")
        return

    plan = parts[2].upper() if len(parts) > 2 else "FREE"
    if plan not in PLAN_HIERARCHY:
        await update.message.reply_text(
            f"❌ Plan inválido. Usa: {', '.join(PLAN_HIERARCHY)}"
        )
        return

    creditos = int(parts[3]) if len(parts) > 3 else INITIAL_CREDITS.get(plan, 0)

    db = DatabaseService()
    existing = db.get_user(target_id)

    if existing:
        db.update_user(target_id, plan=plan, creditos=creditos, is_whitelisted=True)
        await update.message.reply_text(
            f"✅ Usuario *{target_id}* actualizado:\n"
            f"   Plan: *{plan}*\n"
            f"   Créditos: *{creditos}*",
            parse_mode=ParseMode.MARKDOWN,
        )
    else:
        db.create_user(
            user_id=target_id,
            plan=plan,
            creditos=creditos,
        )
        await update.message.reply_text(
            f"✅ Usuario *{target_id}* creado:\n"
            f"   Plan: *{plan}*\n"
            f"   Créditos: *{creditos}*",
            parse_mode=ParseMode.MARKDOWN,
        )


async def set_plan(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Comando /setplan - Cambiar plan de un usuario.
    Uso: /setplan <id> <plan>
    """
    user_id = update.effective_user.id
    if not _is_admin(user_id):
        await update.message.reply_text("❌ No tienes permisos de administrador.")
        return

    parts = update.message.text.split()
    if len(parts) < 3:
        await update.message.reply_text(
            "❌ Uso: `/setplan <id> <plan>`\n"
            "Ejemplo: `/setplan 123456789 DIAMOND`",
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    try:
        target_id = int(parts[1])
    except ValueError:
        await update.message.reply_text("❌ El ID debe ser un número.")
        return

    plan = parts[2].upper()
    if plan not in PLAN_HIERARCHY:
        await update.message.reply_text(
            f"❌ Plan inválido. Usa: {', '.join(PLAN_HIERARCHY)}"
        )
        return

    db = DatabaseService()
    result = db.update_user(target_id, plan=plan)

    if result:
        await update.message.reply_text(
            f"✅ Plan de *{target_id}* cambiado a *{plan}*.",
            parse_mode=ParseMode.MARKDOWN,
        )
    else:
        await update.message.reply_text(f"❌ Usuario {target_id} no encontrado.")


async def add_credits(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Comando /addcredits - Agregar créditos a un usuario.
    Uso: /addcredits <id> <cantidad>
    """
    user_id = update.effective_user.id
    if not _is_admin(user_id):
        await update.message.reply_text("❌ No tienes permisos de administrador.")
        return

    parts = update.message.text.split()
    if len(parts) < 3:
        await update.message.reply_text(
            "❌ Uso: `/addcredits <id> <cantidad>`\n"
            "Ejemplo: `/addcredits 123456789 50`",
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    try:
        target_id = int(parts[1])
        amount = int(parts[2])
    except ValueError:
        await update.message.reply_text("❌ El ID y la cantidad deben ser números.")
        return

    if amount <= 0:
        await update.message.reply_text("❌ La cantidad debe ser positiva.")
        return

    db = DatabaseService()
    result = db.add_credits(target_id, amount)

    if result:
        await update.message.reply_text(
            f"✅ Se agregaron *{amount}* créditos a *{target_id}*.\n"
            f"💰 Saldo actual: *{result.creditos}*",
            parse_mode=ParseMode.MARKDOWN,
        )
    else:
        await update.message.reply_text(f"❌ Usuario {target_id} no encontrado.")


async def del_credits(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Comando /delcredits - Quitar créditos a un usuario.
    Uso: /delcredits <id> <cantidad>
    """
    user_id = update.effective_user.id
    if not _is_admin(user_id):
        await update.message.reply_text("❌ No tienes permisos de administrador.")
        return

    parts = update.message.text.split()
    if len(parts) < 3:
        await update.message.reply_text(
            "❌ Uso: `/delcredits <id> <cantidad>`\n"
            "Ejemplo: `/delcredits 123456789 20`",
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    try:
        target_id = int(parts[1])
        amount = int(parts[2])
    except ValueError:
        await update.message.reply_text("❌ El ID y la cantidad deben ser números.")
        return

    if amount <= 0:
        await update.message.reply_text("❌ La cantidad debe ser positiva.")
        return

    db = DatabaseService()
    user = db.get_user(target_id)

    if not user:
        await update.message.reply_text(f"❌ Usuario {target_id} no encontrado.")
        return

    new_credits = max(0, user.creditos - amount)
    db.update_user(target_id, creditos=new_credits)

    await update.message.reply_text(
        f"✅ Se quitaron *{amount}* créditos a *{target_id}*.\n"
        f"💰 Saldo actual: *{new_credits}*",
        parse_mode=ParseMode.MARKDOWN,
    )


async def user_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Comando /userinfo - Ver información de un usuario.
    Uso: /userinfo <id>
    """
    user_id = update.effective_user.id
    if not _is_admin(user_id):
        await update.message.reply_text("❌ No tienes permisos de administrador.")
        return

    parts = update.message.text.split()
    if len(parts) < 2:
        await update.message.reply_text(
            "❌ Uso: `/userinfo <id>`\n"
            "Ejemplo: `/userinfo 123456789`",
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    try:
        target_id = int(parts[1])
    except ValueError:
        await update.message.reply_text("❌ El ID debe ser un número.")
        return

    db = DatabaseService()
    user = db.get_user(target_id)

    if not user:
        await update.message.reply_text(f"❌ Usuario {target_id} no encontrado.")
        return

    logs = db.get_user_logs(target_id, limit=5)
    minute_count = db.get_minute_count(target_id)
    daily_count = db.get_daily_count(target_id)

    info_text = (
        f"👤 *Información del Usuario*\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"🆔 ID: `{user.id}`\n"
        f"📛 Nombre: {user.first_name or 'N/A'}\n"
        f"📱 Usuario: @{user.username or 'N/A'}\n"
        f"💎 Plan: {user.plan_emoji} {user.plan}\n"
        f"💰 Créditos: {user.creditos}\n"
        f"✅ Whitelist: {'Sí' if user.is_whitelisted else 'No'}\n"
        f"📅 Registro: {user.registered_at or 'N/A'}\n"
        f"🕐 Último acceso: {user.last_active or 'N/A'}\n\n"
        f"📊 *Uso:*\n"
        f"   • Por minuto: {minute_count}\n"
        f"   • Hoy: {daily_count}\n\n"
    )

    if logs:
        info_text += "📋 *Últimas consultas:*\n"
        for log in logs:
            emoji = "✅" if log["success"] else "❌"
            info_text += f"   {emoji} `{log['command']}` ({log['timestamp']})\n"

    await update.message.reply_text(info_text, parse_mode=ParseMode.MARKDOWN)


async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Comando /broadcast - Enviar mensaje a todos los usuarios.
    Uso: /broadcast <mensaje>
    """
    user_id = update.effective_user.id
    if not _is_admin(user_id):
        await update.message.reply_text("❌ No tienes permisos de administrador.")
        return

    parts = update.message.text.split(maxsplit=1)
    if len(parts) < 2:
        await update.message.reply_text(
            "❌ Uso: `/broadcast <mensaje>`\n"
            "Ejemplo: `/broadcast Mantenimiento programado...`",
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    message = parts[1]

    db = DatabaseService()
    users = db.get_all_users()

    sent = 0
    failed = 0

    for user in users:
        try:
            await context.bot.send_message(
                chat_id=user.id,
                text=f"📢 *Comunicado:*\n\n{message}",
                parse_mode=ParseMode.MARKDOWN,
            )
            sent += 1
        except Exception as e:
            logger.warning(f"Error enviando broadcast a {user.id}: {e}")
            failed += 1

    await update.message.reply_text(
        f"📢 Broadcast enviado.\n"
        f"✅ Enviados: {sent}\n"
        f"❌ Fallidos: {failed}",
    )


async def give_monthly(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Comando /give_monthly - Otorga créditos mensuales a todos los usuarios
    según su plan (GOLD: 50, DIAMOND: 200).
    """
    user_id = update.effective_user.id
    if not _is_admin(user_id):
        await update.message.reply_text("❌ No tienes permisos de administrador.")
        return

    from config import PLAN_LIMITS

    db = DatabaseService()
    users = db.get_all_users()

    given = 0
    for user in users:
        monthly = PLAN_LIMITS.get(user.plan, {}).get("monthly_free_credits", 0)
        if monthly > 0:
            db.add_credits(user.id, monthly)
            given += 1

    await update.message.reply_text(
        f"✅ Créditos mensuales otorgados a *{given}* usuarios.",
        parse_mode=ParseMode.MARKDOWN,
    )
