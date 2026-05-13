"""
Validadores de entrada para comandos y parámetros.
"""
import re
from typing import Optional, Tuple


def sanitize_command(text: str) -> str:
    """
    Limpia el texto del comando: elimina espacios extra,
    normaliza el formato.
    """
    return " ".join(text.split())


def parse_command(text: str) -> Tuple[Optional[str], str]:
    """
    Parsea un mensaje de texto para extraer el comando base y los argumentos.
    Retorna (comando_base, argumentos).
    Ejemplo: "/dni 44445555" -> ("/dni", "44445555")
    """
    parts = text.strip().split()
    if not parts:
        return None, ""

    command = parts[0].lower()

    # Limpiar @botname si está presente (ej: /dni@MiBot)
    if "@" in command:
        command = command.split("@")[0]

    args = " ".join(parts[1:]) if len(parts) > 1 else ""
    return command, args


def validate_dni(dni: str) -> bool:
    """Valida que un DNI tenga 8 dígitos numéricos."""
    return bool(re.match(r"^\d{8}$", dni.strip()))


def validate_ruc(ruc: str) -> bool:
    """Valida que un RUC tenga 11 dígitos numéricos."""
    return bool(re.match(r"^\d{11}$", ruc.strip()))


def validate_plate(plate: str) -> bool:
    """Valida una placa vehicular (formato peruano: ABC-123 o ABC123)."""
    return bool(re.match(r"^[A-Za-z]{3}[-]?\d{3}$", plate.strip()))


def validate_phone(phone: str) -> bool:
    """Valida un número de teléfono (9 dígitos)."""
    return bool(re.match(r"^\d{9}$", phone.strip()))


def validate_email(email: str) -> bool:
    """Valida un email básico."""
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email.strip()))


def validate_ce(ce: str) -> bool:
    """Valida un Carné de Extranjería (hasta 12 dígitos)."""
    return bool(re.match(r"^\d{1,12}$", ce.strip()))


def validate_cedula(cedula: str) -> bool:
    """Valida una cédula venezolana."""
    return bool(re.match(r"^\d{6,10}$", cedula.strip()))


def validate_passport(passport: str) -> bool:
    """Valida un pasaporte."""
    return bool(re.match(r"^[A-Za-z0-9]{6,20}$", passport.strip()))


def get_param_hint(command: str) -> str:
    """
    Retorna un hint de qué parámetro espera el comando.
    """
    hints = {
        "/dni": "<DNI: 8 dígitos>",
        "/dnif": "<DNI: 8 dígitos>",
        "/dnidb": "<DNI: 8 dígitos>",
        "/dnidbf": "<DNI: 8 dígitos>",
        "/nm": "<NOMBRES,APELLIDOS>",
        "/dnim": "<DNI: 8 dígitos>",
        "/mh": "<DNI: 8 dígitos>",
        "/c4": "<DNI: 8 dígitos>",
        "/dnivaz": "<DNI: 8 dígitos>",
        "/dnivam": "<DNI: 8 dígitos>",
        "/dnivel": "<DNI: 8 dígitos>",
        "/dniveln": "<DNI: 8 dígitos>",
        "/fa": "<DNI: 8 dígitos>",
        "/fadb": "<DNI: 8 dígitos>",
        "/fb": "<DNI: 8 dígitos>",
        "/fbdb": "<DNI: 8 dígitos>",
        "/fis": "<DNI: 8 dígitos>",
        "/fisnm": "<NOMBRES APELLIDOS>",
        "/rqh": "<DNI: 8 dígitos>",
        "/reportev1": "<DNI: 8 dígitos>",
        "/antpenv": "<DNI: 8 dígitos>",
        "/dend": "<DNI: 8 dígitos>",
        "/sun": "<RUC: 11 dígitos o DNI: 8 dígitos>",
        "/sunat": "<RUC: 11 dígitos>",
        "/reptrib": "<RUC: 11 dígitos>",
        "/sunr": "<RAZÓN SOCIAL>",
        "/tel": "<TELÉFONO: 9 dígitos>",
        "/telp": "<TELÉFONO: 9 dígitos>",
        "/stel": "<DNI: 8 dígitos>",
        "/cel": "<TELÉFONO: 9 dígitos>",
        "/telpdb": "<TELÉFONO: 9 dígitos>",
        "/claro": "<TELÉFONO: 9 dígitos>",
        "/bitel": "<TELÉFONO: 9 dígitos>",
        "/movistar": "<TELÉFONO: 9 dígitos>",
        "/entel": "<TELÉFONO: 9 dígitos>",
        "/migra": "<DNI: 8 dígitos>",
        "/migrapdf": "<DNI: 8 dígitos>",
        "/migradb": "<DNI: 8 dígitos>",
        "/migrapdfdb": "<DNI: 8 dígitos>",
        "/pro": "<RUC: 11 dígitos>",
        "/propdf": "<RUC: 11 dígitos>",
        "/partida": "<RUC|PARTIDA>",
        "/sbs": "<DNI: 8 dígitos>",
        "/pla": "<DNI: 8 dígitos>",
        "/plat": "<PLACA: ABC123>",
        "/revtec": "<PLACA: ABC123>",
        "/revtecpdf": "<PLACA: ABC123>",
        "/boi": "<PLACA: ABC123>",
        "/tive": "<PLACA: ABC123>",
        "/tivep": "<PLACA: ABC123>",
        "/tivev": "<PLACA: ABC123>",
        "/tremp": "<RUC: 11 dígitos>",
        "/sue": "<DNI: 8 dígitos>",
        "/con": "<DNI: 8 dígitos>",
        "/exd": "<DNI: 8 dígitos>",
        "/meta": "<DNI: 8 dígitos>",
        "/dir": "<DNI: 8 dígitos>",
        "/cla": "<RUC: 11 dígitos>",
        "/sune": "<RUC: 11 dígitos>",
        "/cun": "<RUC: 11 dígitos>",
        "/colp": "<RUC: 11 dígitos>",
        "/mine": "<DNI: 8 dígitos>",
        "/cor": "<EMAIL>",
        "/seeker": "<DNI: 8 dígitos>",
        "/afp": "<DNI: 8 dígitos>",
        "/bdir": "<DIRECCIÓN>",
        "/ce": "<CE: número>",
        "/nmv": "<NOMBRES APELLIDOS>",
        "/cedula": "<CÉDULA VENEZOLANA>",
        "/rfn": "<enviar foto>",
        "/pasaporte": "<PASAPORTE>",
        "/agvp": "<DNI: 8 dígitos>",
        "/agv": "<DNI: 8 dígitos>",
        "/actnac": "<DNI: 8 dígitos>",
        "/actmat": "<DNI: 8 dígitos>",
        "/actdef": "<DNI: 8 dígitos>",
        "/spm": "<TELÉFONO: 9 dígitos>",
        "/spm2": "<TELÉFONO: 9 dígitos>",
        "/spm3": "<TELÉFONO: 9 dígitos>",
        "/intelx": "<EMAIL/URL/USERNAME>",
        "/yape": "<monto|nombre|telefono|formato>",
        "/plin": "<monto|nombre|telefono|formato>",
        "/ibk": "<cuenta|formato|monto>",
    }
    return hints.get(command, "<parámetros>")
