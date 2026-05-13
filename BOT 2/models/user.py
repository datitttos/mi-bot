"""
Modelo de Usuario con patrón Data Class.
Representa la entidad de usuario en el sistema.
"""
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class User:
    """Representa un usuario del bot con su plan y créditos."""
    id: int
    plan: str = "FREE"
    creditos: int = 0
    is_whitelisted: bool = False
    username: Optional[str] = None
    first_name: Optional[str] = None
    registered_at: Optional[str] = None
    last_active: Optional[str] = None
    monthly_credits_given: int = 0
    referral_code: Optional[str] = None
    referred_by: Optional[int] = None

    def can_access_command(self, required_plan: str, plan_levels: dict) -> bool:
        """Verifica si el usuario tiene el plan suficiente para un comando."""
        from config import PLAN_LEVELS
        user_level = PLAN_LEVELS.get(self.plan, 1)
        required_level = PLAN_LEVELS.get(required_plan, 1)
        return user_level >= required_level

    def has_sufficient_credits(self, cost: int) -> bool:
        """Verifica si el usuario tiene créditos suficientes."""
        return self.creditos >= cost

    def deduct_credits(self, cost: int) -> bool:
        """Descuenta créditos si es posible. Retorna True si se pudo."""
        if not self.has_sufficient_credits(cost):
            return False
        self.creditos -= cost
        return True

    def add_credits(self, amount: int) -> None:
        """Agrega créditos al usuario."""
        self.creditos += amount

    @property
    def plan_emoji(self) -> str:
        """Retorna el emoji según el plan."""
        emojis = {
            "FREE": "🟢",
            "GOLD": "🟡",
            "DIAMOND": "🔴",
        }
        return emojis.get(self.plan, "⚪")

    @property
    def is_free(self) -> bool:
        return self.plan == "FREE"

    @property
    def is_gold(self) -> bool:
        return self.plan == "GOLD"

    @property
    def is_diamond(self) -> bool:
        return self.plan == "DIAMOND"
