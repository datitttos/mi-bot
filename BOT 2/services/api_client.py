"""
Cliente asíncrono para la API de PRIMEDOX.
Implementa el patrón Service para encapsular toda la comunicación con la API externa.
"""
import asyncio
import base64
import io
import logging
from typing import Optional, Dict, Any, List, Tuple

import aiohttp

from config import (
    API_EXECUTE_URL,
    API_COMMANDS_URL,
    API_HEALTH_URL,
    API_TOKEN,
    API_TIMEOUT,
    BOT_NAME,
)

logger = logging.getLogger(__name__)


class APIResponse:
    """Respuesta procesada de la API de PRIMEDOX."""

    def __init__(
        self,
        success: bool,
        text: Optional[str] = None,
        media: Optional[bytes] = None,
        media_type: Optional[str] = None,
        mime_type: Optional[str] = None,
        filename: Optional[str] = None,
        error: Optional[str] = None,
    ):
        self.success = success
        self.text = text
        self.media = media
        self.media_type = media_type
        self.mime_type = mime_type
        self.filename = filename
        self.error = error

    @classmethod
    def from_api_json(cls, data: Dict[str, Any]) -> List['APIResponse']:
        """
        Parsea la respuesta JSON de la API y retorna una lista de APIResponse.
        Maneja múltiples respuestas (texto, fotos, documentos).
        """
        responses = []
        raw_responses = data.get("responses", [])

        if not raw_responses:
            responses.append(cls(
                success=data.get("success", False),
                error=data.get("error", "No se devolvió información."),
            ))
            return responses

        for resp in raw_responses:
            media_b64 = resp.get("media")
            media_bytes = None
            if media_b64:
                try:
                    media_bytes = base64.b64decode(media_b64)
                except Exception as e:
                    logger.warning(f"Error decodificando base64: {e}")

            responses.append(cls(
                success=True,
                text=resp.get("text"),
                media=media_bytes,
                media_type=resp.get("media_type"),
                mime_type=resp.get("mime_type"),
                filename=resp.get("filename"),
            ))

        return responses

    @property
    def has_media(self) -> bool:
        return self.media is not None

    @property
    def is_image(self) -> bool:
        return (
            self.media_type == "photo"
            or (self.mime_type and "image/" in self.mime_type)
        )

    @property
    def is_pdf(self) -> bool:
        return self.mime_type == "application/pdf"

    def get_filename(self) -> str:
        """Obtiene un nombre de archivo, generando uno por defecto si es necesario."""
        if self.filename:
            return self.filename
        if self.is_pdf:
            return "reporte.pdf"
        if self.is_image:
            ext = self.mime_type.split("/")[-1] if self.mime_type else "jpg"
            return f"imagen.{ext}"
        return "archivo.bin"

    def get_media_bytes_io(self) -> io.BytesIO:
        """Retorna los bytes de media como un BytesIO listo para enviar."""
        bio = io.BytesIO(self.media)
        bio.name = self.get_filename()
        return bio


class PrimedoxAPIClient:
    """
    Cliente asíncrono para consumir la API de PRIMEDOX.
    Maneja autenticación, timeouts, y parseo de respuestas.
    """

    def __init__(self):
        self._session: Optional[aiohttp.ClientSession] = None
        self._headers = {
            "Authorization": f"Bearer {API_TOKEN}",
            "Content-Type": "application/json",
        }

    async def _get_session(self) -> aiohttp.ClientSession:
        """Obtiene o crea una sesión HTTP."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def close(self) -> None:
        """Cierra la sesión HTTP."""
        if self._session and not self._session.closed:
            await self._session.close()

    async def check_health(self) -> bool:
        """
        Verifica si el servicio API está disponible.
        Endpoint público: GET /health
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(API_HEALTH_URL, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.info(f"API Health: {data}")
                        return data.get("status") == "ok"
                    return False
        except Exception as e:
            logger.error(f"Error verificando salud de la API: {e}")
            return False

    async def get_commands(self) -> Optional[Dict[str, Any]]:
        """
        Obtiene el catálogo de comandos disponibles.
        Endpoint: GET /api/commands
        """
        session = await self._get_session()
        try:
            async with session.get(
                API_COMMANDS_URL,
                headers=self._headers,
                timeout=30,
            ) as response:
                if response.status == 200:
                    return await response.json()
                logger.error(f"Error obteniendo comandos: HTTP {response.status}")
                return None
        except Exception as e:
            logger.error(f"Error obteniendo comandos: {e}")
            return None

    async def execute_command(
        self,
        command: str,
        user_id: str,
        photo_base64: Optional[str] = None,
    ) -> Tuple[int, Optional[List[APIResponse]]]:
        """
        Ejecuta un comando en la API de PRIMEDOX.

        Args:
            command: El comando completo (ej: "/dni 44445555")
            user_id: ID del usuario para auditoría
            photo_base64: Foto en base64 (opcional, para comandos como /rfn)

        Returns:
            Tuple de (status_code, lista de APIResponse o None)
        """
        payload: Dict[str, Any] = {
            "command": command,
            "user_id": user_id,
            "bot_name": BOT_NAME,
        }

        if photo_base64:
            payload["photo"] = photo_base64

        session = await self._get_session()

        try:
            async with session.post(
                API_EXECUTE_URL,
                json=payload,
                headers=self._headers,
                timeout=API_TIMEOUT,
            ) as response:
                status = response.status

                # Errores de autenticación
                if status in (401, 403):
                    error_body = await response.text()
                    logger.error(f"Error de autenticación API: HTTP {status} - {error_body}")
                    return status, [APIResponse(
                        success=False,
                        error="Error de autenticación con la API. Contacta al administrador.",
                    )]

                # Rate limit de la API
                if status == 429:
                    return status, [APIResponse(
                        success=False,
                        error="⏳ La API externa ha excedido su límite de consultas. Espera un momento.",
                    )]

                # Error del servidor
                if status != 200:
                    error_body = await response.text()
                    logger.error(f"Error API HTTP {status}: {error_body}")
                    return status, [APIResponse(
                        success=False,
                        error=f"Error del servidor API (HTTP {status}).",
                    )]

                # Éxito
                data = await response.json()
                api_responses = APIResponse.from_api_json(data)
                return status, api_responses

        except asyncio.TimeoutError:
            logger.error("Timeout en la llamada a la API de PRIMEDOX")
            return 408, [APIResponse(
                success=False,
                error="⏰ La consulta está tomando demasiado tiempo. Intenta de nuevo.",
            )]
        except aiohttp.ClientError as e:
            logger.error(f"Error de conexión con la API: {e}")
            return 503, [APIResponse(
                success=False,
                error="🔌 Error de conexión con el servidor. Intenta más tarde.",
            )]
        except Exception as e:
            logger.error(f"Error inesperado llamando a la API: {e}")
            return 500, [APIResponse(
                success=False,
                error="❌ Error interno inesperado.",
            )]
