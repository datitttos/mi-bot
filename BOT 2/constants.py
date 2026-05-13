"""
Constantes del negocio: comandos, costos, planes requeridos, categorías y aliases.
Basado en la documentación oficial de PRIMEDOX API.
"""
from typing import Dict, Final

# ─── Categorías de Comandos ──────────────────────────────────────────────────
CATEGORIES: Final[Dict[str, str]] = {
    "reniec": "RENIEC",
    "justicia": "JUSTICIA",
    "sunat": "SUNAT",
    "telefonia": "TELEFONÍA",
    "migraciones": "MIGRACIONES",
    "sunarp": "SUNARP",
    "financiero": "FINANCIERO",
    "vehiculos": "VEHÍCULOS",
    "laboral": "LABORAL",
    "plus": "PLUS GENERAL",
    "familia": "FAMILIA",
    "actas": "ACTAS",
    "spam": "SPAM",
    "bauchers": "BAUCHERS",
}

# ─── Costo de cada comando (en créditos) ─────────────────────────────────────
COMMAND_COSTS: Final[Dict[str, int]] = {
    # RENIEC
    "/dni": 1, "/dnif": 3, "/dnidb": 1, "/dnidbf": 2, "/nm": 2, "/dnim": 2,
    "/mh": 5, "/c4": 10, "/dnivaz": 10, "/dnivam": 10, "/dnivel": 10,
    "/dniveln": 10, "/fa": 10, "/fadb": 8, "/fb": 10, "/fbdb": 8,
    # JUSTICIA
    "/fis": 10, "/fisnm": 10, "/rqh": 10, "/reportev1": 10, "/antpenv": 12,
    "/dend": 10,
    # SUNAT
    "/sun": 5, "/sunat": 10, "/reptrib": 10, "/sunr": 5,
    # TELEFONÍA
    "/tel": 2, "/telp": 10, "/stel": 5, "/cel": 5, "/telpdb": 5,
    "/claro": 5, "/bitel": 5, "/movistar": 5, "/entel": 5,
    # MIGRACIONES
    "/migra": 10, "/migrapdf": 12, "/migradb": 8, "/migrapdfdb": 10,
    # SUNARP
    "/pro": 5, "/propdf": 15, "/partida": 10,
    # FINANCIERO
    "/sbs": 5,
    # VEHÍCULOS
    "/pla": 5, "/plat": 3, "/revtec": 5, "/revtecpdf": 5, "/boi": 15,
    "/tive": 20, "/tivep": 10, "/tivev": 10,
    # LABORAL
    "/tremp": 10, "/sue": 10,
    # PLUS GENERAL
    "/con": 5, "/exd": 5, "/meta": 10, "/dir": 5, "/cla": 10, "/sune": 10,
    "/cun": 10, "/colp": 10, "/mine": 10, "/cor": 5, "/seeker": 15,
    "/afp": 5, "/bdir": 5, "/ce": 5, "/nmv": 5, "/cedula": 5, "/rfn": 0,
    "/pasaporte": 5,
    # FAMILIA
    "/agvp": 15, "/agv": 10,
    # ACTAS
    "/actnac": 30, "/actmat": 30, "/actdef": 30,
    # SPAM
    "/spm": 3, "/spm2": 5, "/spm3": 10, "/intelx": 20,
    # BAUCHERS
    "/yape": 1, "/plin": 3, "/ibk": 3,
}

# ─── Plan mínimo requerido por comando ───────────────────────────────────────
COMMAND_PLANS: Final[Dict[str, str]] = {
    # RENIEC
    "/dni": "GOLD", "/dnif": "GOLD", "/dnidb": "GOLD", "/dnidbf": "GOLD",
    "/nm": "GOLD", "/dnim": "GOLD", "/mh": "GOLD", "/c4": "GOLD",
    "/dnivaz": "GOLD", "/dnivam": "GOLD", "/dnivel": "GOLD", "/dniveln": "GOLD",
    "/fa": "GOLD", "/fadb": "GOLD", "/fb": "GOLD", "/fbdb": "GOLD",
    # JUSTICIA
    "/fis": "GOLD", "/fisnm": "GOLD", "/rqh": "GOLD", "/reportev1": "DIAMOND",
    "/antpenv": "GOLD", "/dend": "GOLD",
    # SUNAT
    "/sun": "GOLD", "/sunat": "DIAMOND", "/reptrib": "DIAMOND", "/sunr": "GOLD",
    # TELEFONÍA
    "/tel": "GOLD", "/telp": "GOLD", "/stel": "GOLD", "/cel": "GOLD",
    "/telpdb": "GOLD", "/claro": "GOLD", "/bitel": "GOLD", "/movistar": "GOLD",
    "/entel": "GOLD",
    # MIGRACIONES
    "/migra": "GOLD", "/migrapdf": "GOLD", "/migradb": "GOLD",
    "/migrapdfdb": "GOLD",
    # SUNARP
    "/pro": "GOLD", "/propdf": "DIAMOND", "/partida": "DIAMOND",
    # FINANCIERO
    "/sbs": "GOLD",
    # VEHÍCULOS
    "/pla": "GOLD", "/plat": "GOLD", "/revtec": "GOLD", "/revtecpdf": "GOLD",
    "/boi": "DIAMOND", "/tive": "DIAMOND", "/tivep": "GOLD", "/tivev": "GOLD",
    # LABORAL
    "/tremp": "GOLD", "/sue": "GOLD",
    # PLUS GENERAL
    "/con": "GOLD", "/exd": "GOLD", "/meta": "GOLD", "/dir": "GOLD",
    "/cla": "GOLD", "/sune": "GOLD", "/cun": "GOLD", "/colp": "GOLD",
    "/mine": "GOLD", "/cor": "GOLD", "/seeker": "GOLD", "/afp": "GOLD",
    "/bdir": "GOLD", "/ce": "GOLD", "/nmv": "GOLD", "/cedula": "GOLD",
    "/rfn": "DIAMOND", "/pasaporte": "GOLD",
    # FAMILIA
    "/agvp": "DIAMOND", "/agv": "GOLD",
    # ACTAS
    "/actnac": "DIAMOND", "/actmat": "DIAMOND", "/actdef": "DIAMOND",
    # SPAM
    "/spm": "FREE", "/spm2": "GOLD", "/spm3": "DIAMOND", "/intelx": "DIAMOND",
    # BAUCHERS
    "/yape": "FREE", "/plin": "FREE", "/ibk": "FREE",
}

# ─── Aliases de comandos ─────────────────────────────────────────────────────
COMMAND_ALIASES: Final[Dict[str, str]] = {
    "/reniec": "/dni",
    "/placa": "/plat",
}

# ─── Comandos por Categoría ──────────────────────────────────────────────────
COMMANDS_BY_CATEGORY: Final[Dict[str, list[str]]] = {
    "reniec": [
        "/dni", "/dnif", "/dnidb", "/dnidbf", "/nm", "/dnim", "/mh", "/c4",
        "/dnivaz", "/dnivam", "/dnivel", "/dniveln", "/fa", "/fadb", "/fb", "/fbdb",
    ],
    "justicia": [
        "/fis", "/fisnm", "/rqh", "/reportev1", "/antpenv", "/dend",
    ],
    "sunat": [
        "/sun", "/sunat", "/reptrib", "/sunr",
    ],
    "telefonia": [
        "/tel", "/telp", "/stel", "/cel", "/telpdb", "/claro", "/bitel",
        "/movistar", "/entel",
    ],
    "migraciones": [
        "/migra", "/migrapdf", "/migradb", "/migrapdfdb",
    ],
    "sunarp": [
        "/pro", "/propdf", "/partida",
    ],
    "financiero": [
        "/sbs",
    ],
    "vehiculos": [
        "/pla", "/plat", "/revtec", "/revtecpdf", "/boi", "/tive", "/tivep",
        "/tivev",
    ],
    "laboral": [
        "/tremp", "/sue",
    ],
    "plus": [
        "/con", "/exd", "/meta", "/dir", "/cla", "/sune", "/cun", "/colp",
        "/mine", "/cor", "/seeker", "/afp", "/bdir", "/ce", "/nmv", "/cedula",
        "/rfn", "/pasaporte",
    ],
    "familia": [
        "/agvp", "/agv",
    ],
    "actas": [
        "/actnac", "/actmat", "/actdef",
    ],
    "spam": [
        "/spm", "/spm2", "/spm3", "/intelx",
    ],
    "bauchers": [
        "/yape", "/plin", "/ibk",
    ],
}

# ─── Descripciones de comandos para mostrar en menús ─────────────────────────
COMMAND_DESCRIPTIONS: Final[Dict[str, str]] = {
    # RENIEC
    "/dni": "DNI ONLINE [1 FOTO]",
    "/dnif": "DNI ONLINE [4 FOTOS]",
    "/dnidb": "DNI DATABASE [1 FOTO]",
    "/dnidbf": "DNI DATABASE [4 FOTOS]",
    "/nm": "NOMBRES ONLINE",
    "/dnim": "DNI METADATA",
    "/mh": "MEJORES HUELLAS",
    "/c4": "CERTIFICADO C4",
    "/dnivaz": "DNI VIRTUAL AZUL",
    "/dnivam": "DNI VIRTUAL AMARILLO",
    "/dnivel": "DNI VIRTUAL ELECTRÓNICO",
    "/dniveln": "DNI VIRTUAL NUEVO",
    "/fa": "FICHA AZUL ONLINE",
    "/fadb": "FICHA AZUL DATABASE",
    "/fb": "FICHA BLANCA ONLINE",
    "/fbdb": "FICHA BLANCA DATABASE",
    # JUSTICIA
    "/fis": "FISCALÍA",
    "/fisnm": "FISCALÍA NOMBRES",
    "/rqh": "REQUISITORIAS HISTÓRICAS",
    "/reportev1": "REPORTE V1 [DNI]",
    "/antpenv": "ANTECEDENTES VERIFICADOR",
    "/dend": "DENUNCIAS POLICIALES",
    # SUNAT
    "/sun": "SUNAT RUC",
    "/sunat": "SUNAT ONLINE PDF",
    "/reptrib": "REPORTE TRIBUTARIO PDF",
    "/sunr": "SUNAT RAZÓN SOCIAL",
    # TELEFONÍA
    "/tel": "TELÉFONO FREE",
    "/telp": "TELÉFONO PREMIUM",
    "/stel": "OSIPTEL DATABASE N2",
    "/cel": "OSIPTEL DATABASE N2",
    "/telpdb": "OSIPTEL DATABASE N3",
    "/claro": "CLARO ONLINE N1",
    "/bitel": "BITEL ONLINE N2",
    "/movistar": "MOVISTAR ONLINE N3",
    "/entel": "ENTEL ONLINE N4",
    # MIGRACIONES
    "/migra": "MOVIMIENTOS ONLINE",
    "/migrapdf": "MOVIMIENTOS PDF",
    "/migradb": "MOVIMIENTOS DATABASE",
    "/migrapdfdb": "MOVIMIENTOS DB PDF",
    # SUNARP
    "/pro": "PROPIEDADES TEXTO",
    "/propdf": "PROPIEDADES PDF",
    "/partida": "PARTIDAS PDF",
    # FINANCIERO
    "/sbs": "SBS DEUDAS",
    # VEHÍCULOS
    "/pla": "VEHÍCULOS",
    "/plat": "VEHÍCULOS ONLINE",
    "/revtec": "REVISIÓN TÉCNICA",
    "/revtecpdf": "REVISIÓN TÉCNICA PDF",
    "/boi": "BOLETA INFORMATIVA PDF",
    "/tive": "TIVE ORIGINAL PDF",
    "/tivep": "TIVE PLANTILLA PDF",
    "/tivev": "TIVE ELECTRÓNICO FOTO",
    # LABORAL
    "/tremp": "TRABAJADORES EMPRESA",
    "/sue": "SUELDOS",
    # PLUS GENERAL
    "/con": "CÓNYUGES",
    "/exd": "EMPRESAS",
    "/meta": "METADATA COMPLETA",
    "/dir": "DIRECCIONES",
    "/cla": "CONSTANCIA DE LOGROS",
    "/sune": "TÍTULOS UNIVERSITARIOS",
    "/cun": "CARNET UNIVERSITARIO",
    "/colp": "COLEGIADOS",
    "/mine": "TÍTULOS INSTITUTOS",
    "/cor": "CORREOS",
    "/seeker": "SEEKER",
    "/afp": "AFP",
    "/bdir": "DIRECCIÓN INVERSA",
    "/ce": "CARNET EXTRANJERÍA",
    "/nmv": "VENEZOLANOS NOMBRES",
    "/cedula": "VENEZOLANOS CÉDULA",
    "/rfn": "RFN FACIAL [FOTO]",
    "/pasaporte": "PASAPORTE",
    # FAMILIA
    "/agvp": "ÁRBOL GENEALÓGICO PDF",
    "/agv": "ÁRBOL VISUAL [DNI]",
    # ACTAS
    "/actnac": "ACTA DE NACIMIENTO PDF",
    "/actmat": "ACTA DE MATRIMONIO PDF",
    "/actdef": "ACTA DE DEFUNCIÓN PDF",
    # SPAM
    "/spm": "SPM OPERADORES",
    "/spm2": "SPM BANCOS",
    "/spm3": "SPM ULTRA",
    "/intelx": "INTEL X [EMAIL/URL/USERNAME]",
    # BAUCHERS
    "/yape": "YAPE FAKE FOTO",
    "/plin": "PLIN FAKE FOTO",
    "/ibk": "INTERBANK FAKE FOTO",
}

# ─── Comandos que requieren foto adjunta ─────────────────────────────────────
COMMANDS_REQUIRING_PHOTO: Final[list[str]] = [
    "/rfn",
    "/yape",
    "/plin",
    "/ibk",
]
