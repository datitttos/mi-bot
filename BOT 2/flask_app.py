import asyncio
import os
from flask import Flask, request
from telegram import Update
from main import setup_application, BOT_TOKEN
import logging

# Configurar logs básicos
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ====== CAMBIA ESTO POR TU USUARIO DE PYTHONANYWHERE ======
# Ejemplo: si tu usuario es "jonatan", entonces:
PA_USERNAME = "datitosbot"
# ==========================================================

WEBHOOK_URL = f"https://{PA_USERNAME}.pythonanywhere.com/bot_hook"

app = Flask(__name__)

# Configuramos la aplicación de Python Telegram Bot
ptb_app = setup_application()

@app.route('/')
def home():
    return "¡Bot funcionando activo con Webhooks en PythonAnywhere!"

@app.route('/bot_hook', methods=['POST', 'GET'])
async def telegram_webhook():
    """Ruta que recibe los mensajes de Telegram."""
    if request.method == "POST":
        update_data = request.get_json(force=True)
        update = Update.de_json(update_data, ptb_app.bot)
        
        # Iniciar PTB solo la primera vez si no ha sido inicializado
        if not ptb_app.bot_data.get("is_initialized"):
            logger.info("Inicializando PTB application...")
            await ptb_app.initialize()
            await ptb_app.start()
            ptb_app.bot_data["is_initialized"] = True
            
        await ptb_app.process_update(update)
        return "OK", 200
    
    return "Esta URL es solo para el webhook de Telegram."

@app.route('/set_webhook', methods=['GET'])
async def set_webhook():
    """Ruta de conveniencia para registrar el webhook en Telegram."""
    success = await ptb_app.bot.set_webhook(url=WEBHOOK_URL)
    if success:
        return f"Webhook configurado exitosamente a: {WEBHOOK_URL}"
    else:
        return "Error al configurar el webhook", 500

# Archivo de entrada WSGI para PythonAnywhere
# PA usará la variable `app` para correr Flask.
