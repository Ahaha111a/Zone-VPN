import os
from dataclasses import dataclass
from dotenv import load_dotenv
load_dotenv()

@dataclass(frozen=True)
class Plan:
    code: str
    title: str
    months: int
    price_rub: int
    stars_env: str

PLANS = {
    "m1": Plan("m1", "1 месяц", 1, 499, "STARS_MONTHLY"),
    "m2": Plan("m2", "2 месяца", 2, 1999, "STARS_2_MONTHS"),
    "m3": Plan("m3", "3 месяца", 3, 2999, "STARS_3_MONTHS"),
}

@dataclass(frozen=True)
class Settings:
    token: str = os.getenv("BOT_TOKEN", "")
    db_path: str = os.getenv("DATABASE_PATH", "./data/zona.sqlite3")
    admins: tuple = tuple(int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip().isdigit())
    support: str = os.getenv("SUPPORT_USERNAME", "")
    terms_url: str = os.getenv("TERMS_URL", "")
    vpn_mode: str = os.getenv("VPN_MODE", "disabled")
    sales_enabled: bool = os.getenv("SALES_ENABLED", "false").strip().lower() == "true"
    payment_delivery_ready: bool = os.getenv("PAYMENT_DELIVERY_READY", "false").strip().lower() == "true"
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

settings = Settings()
