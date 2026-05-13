import logging
import os
import signal
import sys
import subprocess

# Configuración de logs para el despliegue
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("DeployHelper")

def check_env():
    """Verifica que el entorno sea correcto antes de iniciar."""
    if not os.path.exists("main.py"):
        logger.error("No se encontró main.py. Asegúrate de estar en la carpeta del bot.")
        return False
    return True

def install_dependencies():
    """Instala las dependencias necesarias en el VPS."""
    logger.info("Instalando dependencias...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        logger.info("Dependencias instaladas correctamente.")
        return True
    except Exception as e:
        logger.error(f"Error instalando dependencias: {e}")
        return False

def run_background():
    """Lanza el bot en segundo plano usando nohup."""
    logger.info("Lanzando bot en segundo plano...")
    try:
        # Comando para ejecutar en segundo plano y redirigir logs
        command = "nohup python3 main.py > bot_output.log 2>&1 &"
        os.system(command)
        logger.info("¡Bot lanzado con éxito!")
        logger.info("Puedes ver los logs en tiempo real con: tail -f bot_output.log")
        return True
    except Exception as e:
        logger.error(f"Error lanzando el bot: {e}")
        return False

if __name__ == "__main__":
    print("-" * 30)
    print(" GCloud Deploy Helper ")
    print("-" * 30)
    
    if check_env():
        if install_dependencies():
            run_background()
