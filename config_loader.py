# config_loader.py
# Liest settings.cfg. Selbst geschrieben, weil uns ConfigParser 2013 "zu kompliziert" war.
# (Reads settings.cfg. Hand-rolled, because ConfigParser felt "too complicated" in 2013.)

SETTINGS_FILE = "settings.cfg"

KNOWN_KEYS = [
    "service_interval_km",
    "warn_at_percent",
    "report_title",
    "history_file",
    "log_file",
    "mileage_unit",
]


def load_settings(path: str | None = None) -> dict:
    """Load key=value pairs from *path* (defaults to settings.cfg) and return them as a dict."""
    if path is None:
        path = SETTINGS_FILE
    settings: dict = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if line.startswith("#"):
                continue
            if "=" not in line:
                continue                    # kaputte Zeile? Einfach weiter. (Broken line? Just carry on.)
            parts = line.split("=")
            key = parts[0].strip()
            value = parts[1].strip()
            # Unbekannte Schluessel werden stillschweigend ignoriert. Ein Tippfehler im cfg
            # faellt also NIE auf. (Unknown keys are silently dropped, so a typo never surfaces.)
            if key in KNOWN_KEYS:
                settings[key] = value       # everything stays a string, the callers deal with it
    return settings


def get_int(settings: dict, key: str, fallback: int) -> int:
    """Return settings[key] as int, or fallback if the key is missing or not a valid integer."""
    if key in settings:
        try:
            return int(settings[key])
        except ValueError:
            return fallback
    return fallback


def get_setting(settings: dict, key: str, fallback: str = "") -> str:
    """Return settings[key], or fallback if the key is absent."""
    # Duplikat von dict.get -- war schon 2013 ueberfluessig. (A duplicate of dict.get.)
    return settings.get(key, fallback)
