"""
PRIMEDOX BOT - Telegram Bot para PRIMEDOX API
==============================================
Bot asíncrono con sistema de planes (FREE/GOLD/DIAMOND),
14 categorías de consultas, control de créditos y rate limiting.

Arquitectura modular con patrón de diseño:
- Service Layer: database.py, api_client.py
- Model Layer: user.py
- Handler Layer: handlers/*
- Utility Layer: utils/*
- Config Layer: config.py, constants.py
"""
import asyncio
import logging
import sys

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
)

from config import BOT_TOKEN
from services.database import DatabaseService
from services.api_client import PrimedoxAPIClient

# ─── Handlers ────────────────────────────────────────────────────────────────
from handlers.start import start
from handlers.categories import show_category, back_to_menu
from handlers.profile import show_profile, show_stats
from handlers.admin import (
    admin_panel,
    add_user,
    set_plan,
    add_credits,
    del_credits,
    user_info,
    broadcast,
    give_monthly,
)
from handlers.query import handle_command

# ─── Configuración de Logging ────────────────────────────────────────────────
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("bot.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)


async def post_init(application: Application) -> None:
    """
    Callback ejecutado después de inicializar la aplicación.
    Verifica la conexión con la API de PRIMEDOX.
    """
    logger.info("=" * 50)
    logger.info("PRIMEDOX BOT - Inicializando...")
    logger.info("=" * 50)

    # Verificar salud de la API
    api_client = PrimedoxAPIClient()
    health_ok = await api_client.check_health()

    if health_ok:
        logger.info("✅ API de PRIMEDOX: CONECTADA")
    else:
        logger.warning("⚠️ API de PRIMEDOX: NO DISPONIBLE (el bot seguirá funcionando)")

    # Obtener comandos disponibles
    commands_data = await api_client.get_commands()
    if commands_data:
        total = commands_data.get("total", 0)
        logger.info(f"📋 Comandos disponibles en API: {total}")
    else:
        logger.warning("⚠️ No se pudieron obtener los comandos de la API")

    # Cerrar sesión del cliente API
    await api_client.close()

    # Inicializar base de datos
    db = DatabaseService()
    user_count = db.get_user_count()
    logger.info(f"👥 Usuarios registrados: {user_count}")
    logger.info("✅ Bot listo para recibir peticiones")


async def post_shutdown(application: Application) -> None:
    """Callback ejecutado al detener la aplicación."""
    logger.info("🛑 Bot deteniéndose...")
    api_client = PrimedoxAPIClient()
    await api_client.close()
    logger.info("✅ Conexiones cerradas")


def setup_application() -> Application:
    """Configura y retorna la instancia de la aplicación."""
    if not BOT_TOKEN or BOT_TOKEN == "TU_TOKEN_AQUI":
        logger.error("❌ BOT_TOKEN no configurado.")
        sys.exit(1)

    application = Application.builder() \
        .token(BOT_TOKEN) \
        .post_init(post_init) \
        .post_shutdown(post_shutdown) \
        .build()

    # ─── Registrar Handlers ──────────────────────────────────────────────────
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("admin", admin_panel))
    application.add_handler(CommandHandler("adduser", add_user))
    application.add_handler(CommandHandler("setplan", set_plan))
    application.add_handler(CommandHandler("addcredits", add_credits))
    application.add_handler(CommandHandler("delcredits", del_credits))
    application.add_handler(CommandHandler("userinfo", user_info))
    application.add_handler(CommandHandler("broadcast", broadcast))
    application.add_handler(CommandHandler("give_monthly", give_monthly))
    application.add_handler(CallbackQueryHandler(show_category, pattern="^cat_"))
    application.add_handler(CallbackQueryHandler(show_profile, pattern="^profile$"))
    application.add_handler(CallbackQueryHandler(show_stats, pattern="^stats$"))
    application.add_handler(CallbackQueryHandler(back_to_menu, pattern="^back_to_menu$"))
    application.add_handler(MessageHandler(filters.COMMAND | filters.CaptionRegex(r"^/"), handle_command))

    return application

def main() -> None:
    """Punto de entrada principal para POLLING local."""
    application = setup_application()

    # ─── Iniciar el bot (Polling) ────────────────────────────────────────────
    logger.info("🚀 Iniciando PRIMEDOX BOT...")
    print("🚀 PRIMEDOX BOT iniciado. Presiona Ctrl+C para detener.")

    try:
        application.run_polling(allowed_updates=Update.ALL_TYPES)
    except KeyboardInterrupt:
        logger.info("🛑 Bot detenido por el usuario")
    except Exception as e:
        logger.error(f"❌ Error fatal: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
