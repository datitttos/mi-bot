"""
Handler principal para procesar consultas de los usuarios.
Maneja la lógica completa: validación, rate limiting, descuento de créditos,
llamada a la API y envío de respuestas.
"""
import base64
import logging
from typing import Optional

from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from services.database import DatabaseService
from services.api_client import PrimedoxAPIClient
from utils.rate_limiter import RateLimiter
from utils.validators import parse_command, sanitize_command, get_param_hint
from constants import (
    COMMAND_COSTS,
    COMMAND_PLANS,
    COMMAND_ALIASES,
    COMMANDS_REQUIRING_PHOTO,
)
from config import DEFAULT_COST, PLAN_LEVELS

logger = logging.getLogger(__name__)


async def handle_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Procesa cualquier comando enviado por el usuario.
    Flujo completo: validación → rate limit → créditos → API → respuesta.
    """
    user_id = update.effective_user.id
    message_text = update.message.text or update.message.caption

    if not message_text:
        return

    # ─── 1. Sanitizar y parsear comando ──────────────────────────────────────
    message_text = sanitize_command(message_text)
    base_command, args = parse_command(message_text)

    if not base_command:
        return

    # ─── 2. Verificar si es un comando de administración ─────────────────────
    if base_command in ("/admin", "/adduser", "/setplan", "/addcredits",
                        "/delcredits", "/userinfo", "/broadcast", "/give_monthly",
                        "/reset_limits", "/stats"):
        return

    # ─── 3. Resolver alias ───────────────────────────────────────────────────
    if base_command in COMMAND_ALIASES:
        base_command = COMMAND_ALIASES[base_command]
        message_text = f"{base_command} {args}".strip()

    # ─── 4. Obtener usuario de BD ────────────────────────────────────────────
    db = DatabaseService()
    db_user = db.get_user(user_id)

    if not db_user:
        await update.message.reply_text(
            "❌ No estás registrado. Usa /start para registrarte."
        )
        return

    db.update_last_active(user_id)

    # ─── 5. Verificar whitelist ──────────────────────────────────────────────
    if not db_user.is_whitelisted:
        logger.warning(f"Usuario {user_id} no whitelisted intentó usar {base_command}")
        return

    # ─── 6. Verificar que el comando existe ──────────────────────────────────
    if base_command not in COMMAND_COSTS:
        await update.message.reply_text(
            f"❌ Comando `{base_command}` no reconocido.\n"
            f"Usa /start para ver los comandos disponibles.",
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    # ─── 7. Verificar plan suficiente ────────────────────────────────────────
    required_plan = COMMAND_PLANS.get(base_command, "FREE")
    user_level = PLAN_LEVELS.get(db_user.plan, 1)
    required_level = PLAN_LEVELS.get(required_plan, 1)

    if user_level < required_level:
        db.log_request(
            user_id, message_text,
            success=False,
            error_msg=f"INSUFFICIENT_PLAN: requiere {required_plan}",
        )
        await update.message.reply_text(
            f"🔒 Tu plan *{db_user.plan}* no permite usar este comando.\n"
            f"Requiere plan *{required_plan}* o superior.\n\n"
            f"💡 Contacta al administrador para mejorar tu plan.",
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    # ─── 8. Verificar que tenga argumentos si el comando los requiere ────────
    if not args and base_command not in COMMANDS_REQUIRING_PHOTO:
        hint = get_param_hint(base_command)
        await update.message.reply_text(
            f"❌ El comando `{base_command}` requiere parámetros.\n"
            f"📝 Uso: `{base_command} {hint}`\n\n"
            f"💡 Ejecuta /start y selecciona la categoría para ver los comandos.",
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    # ─── 9. Verificar foto si el comando la requiere ─────────────────────────
    if base_command in COMMANDS_REQUIRING_PHOTO and not update.message.photo:
        await update.message.reply_text(
            f"📸 El comando `{base_command}` requiere una foto adjunta.\n"
            f"Envía el comando junto con una foto.",
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    # ─── 10. Rate Limiting ───────────────────────────────────────────────────
    rate_limiter = RateLimiter()
    rate_result = rate_limiter.check_rate_limit(user_id, db_user.plan)

    if not rate_result.allowed:
        db.log_request(
            user_id, message_text,
            success=False,
            error_msg=rate_result.reason,
        )
        await update.message.reply_text(rate_result.reason)
        return

    # ─── 11. Verificar créditos suficientes ──────────────────────────────────
    cost = COMMAND_COSTS.get(base_command, DEFAULT_COST)

    if db_user.creditos < cost:
        db.log_request(
            user_id, message_text,
            success=False,
            error_msg="INSUFFICIENT_CREDITS",
        )
        await update.message.reply_text(
            f"❌ Créditos insuficientes.\n"
            f"💰 Costo: *{cost}* créditos\n"
            f"💳 Tienes: *{db_user.creditos}* créditos\n\n"
            f"📞 Contacta al administrador para recargar.",
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    # ─── 12. Descontar créditos ──────────────────────────────────────────────
    db.deduct_credits(user_id, cost)
    rate_limiter.record_request(user_id)

    # Mensaje de "procesando"
    processing_msg = await update.message.reply_text(
        "⏳ Procesando consulta, por favor espera..."
    )

    # ─── 13. Preparar foto si existe ─────────────────────────────────────────
    photo_base64: Optional[str] = None
    if update.message.photo:
        try:
            photo_file = await context.bot.get_file(update.message.photo[-1].file_id)
            photo_bytes = await photo_file.download_as_bytearray()
            photo_base64 = base64.b64encode(photo_bytes).decode("utf-8")
        except Exception as e:
            logger.error(f"Error procesando foto: {e}")
            await processing_msg.edit_text("❌ Error al procesar la imagen adjunta.")
            # Reembolsar créditos
            db.add_credits(user_id, cost)
            return

    # ─── 14. Llamar a la API de PRIMEDOX ─────────────────────────────────────
    api_client = PrimedoxAPIClient()
    status_code, api_responses = await api_client.execute_command(
        command=message_text,
        user_id=str(user_id),
        photo_base64=photo_base64,
    )

    # Eliminar mensaje de "procesando"
    await processing_msg.delete()

    # ─── 15. Manejar errores de la API ───────────────────────────────────────
    if status_code != 200 or not api_responses:
        error_msg = "Error desconocido"
        if api_responses and api_responses[0].error:
            error_msg = api_responses[0].error

        db.log_request(
            user_id, message_text,
            cost=cost,
            success=False,
            error_msg=f"API_ERROR: {error_msg}",
        )

        # Reembolsar créditos si fue error del servidor
        if status_code in (408, 503, 500):
            db.add_credits(user_id, cost)
            error_msg += "\n\n♻️ Créditos reembolsados."

        await update.message.reply_text(f"❌ {error_msg}")
        return

    # ─── 16. Registrar éxito ─────────────────────────────────────────────────
    db.log_request(
        user_id, message_text,
        cost=cost,
        success=True,
    )

    # ─── 17. Enviar respuestas al usuario ────────────────────────────────────
    user_plan = db_user.plan
    footer = (
        f"\n\n✅ Consulta exitosa | 💎 {user_plan} | 💰 -{cost}"
    )

    for api_resp in api_responses:
        try:
            # Enviar texto si existe
            if api_resp.text:
                text_content = api_resp.text + (footer if not api_resp.has_media else "")
                try:
                    await update.message.reply_text(
                        text_content,
                        parse_mode=ParseMode.HTML,
                    )
                except Exception:
                    await update.message.reply_text(text_content)

            # Enviar multimedia si existe
            if api_resp.has_media:
                media_io = api_resp.get_media_bytes_io()
                caption = footer

                try:
                    if api_resp.is_image:
                        await update.message.reply_photo(
                            photo=media_io,
                            caption=caption,
                        )
                    else:
                        await update.message.reply_document(
                            document=media_io,
                            caption=caption,
                        )
                except Exception as media_err:
                    logger.warning(f"Error enviando multimedia: {media_err}")
                    media_io.seek(0)
                    await update.message.reply_document(
                        document=media_io,
                        caption=caption,
                    )

        except Exception as e:
            logger.error(f"Error enviando respuesta: {e}")
            await update.message.reply_text(
                "❌ Error interno al enviar un fragmento de la respuesta."
            )
