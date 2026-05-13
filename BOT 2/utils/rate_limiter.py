"""
Rate Limiter - Control de límites por usuario y plan.
Implementa el patrón Strategy para diferentes estrategias de rate limiting.
"""
import logging
from typing import Optional
from services.database import DatabaseService
from config import PLAN_LIMITS

logger = logging.getLogger(__name__)


class RateLimitResult:
    """Resultado de una verificación de rate limit."""

    def __init__(
        self,
        allowed: bool,
        reason: Optional[str] = None,
        retry_after: Optional[int] = None,
    ):
        self.allowed = allowed
        self.reason = reason
        self.retry_after = retry_after

    @classmethod
    def ok(cls) -> 'RateLimitResult':
        return cls(allowed=True)

    @classmethod
    def denied(cls, reason: str, retry_after: Optional[int] = None) -> 'RateLimitResult':
        return cls(allowed=False, reason=reason, retry_after=retry_after)


class RateLimiter:
    """
    Controla los límites de velocidad por usuario según su plan.
    Evalúa límite por minuto y límite diario.
    """

    def __init__(self):
        self.db = DatabaseService()

    def check_rate_limit(self, user_id: int, plan: str) -> RateLimitResult:
        """
        Verifica si el usuario puede realizar una consulta.
        Retorna un RateLimitResult indicando si está permitido o no.
        """
        limits = PLAN_LIMITS.get(plan, PLAN_LIMITS["FREE"])

        # Verificar límite por minuto
        minute_count = self.db.get_minute_count(user_id)
        if minute_count >= limits["rate_per_minute"]:
            logger.warning(
                f"Rate limit por minuto excedido para usuario {user_id}: "
                f"{minute_count}/{limits['rate_per_minute']}"
            )
            return RateLimitResult.denied(
                reason=f"⏳ Has excedido el límite de {limits['rate_per_minute']} consultas por minuto para tu plan {plan}.",
                retry_after=60,
            )

        # Verificar límite diario
        daily_count = self.db.get_daily_count(user_id)
        if daily_count >= limits["rate_per_day"]:
            logger.warning(
                f"Rate limit diario excedido para usuario {user_id}: "
                f"{daily_count}/{limits['rate_per_day']}"
            )
            return RateLimitResult.denied(
                reason=f"📅 Has alcanzado el límite diario de {limits['rate_per_day']} consultas para tu plan {plan}.",
                retry_after=86400,
            )

        return RateLimitResult.ok()

    def record_request(self, user_id: int) -> None:
        """Registra una consulta para el rate limiting."""
        self.db.increment_daily_count(user_id)
