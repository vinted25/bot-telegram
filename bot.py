# -*- coding: utf-8 -*-
"""
ShopDuPeupleFrance — Bot Telegram.
Canal: t.me/ShopDuPeupleFrance · Vouch: t.me/shopVouchFR · Contact: @SqlSaint
python-telegram-bot v22+
"""

import asyncio
import logging
import os
import time
from typing import Optional

try:
    from dotenv import load_dotenv
    load_dotenv("config.env")
except:
    pass

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)
from telegram.constants import ParseMode, ChatAction
from telegram.error import BadRequest, NetworkError

logger = logging.getLogger(__name__)


def _user_log_context(update: Update) -> str:
    """Une ligne compacte : user_id, @username, nom, langue, chat_type."""
    parts = []
    user = getattr(update, "effective_user", None) or (update.callback_query.from_user if update.callback_query else None)
    if user:
        parts.append(f"id={user.id}")
        parts.append(f"@{user.username}" if user.username else "no@")
        name = ((user.first_name or "") + " " + (user.last_name or "")).strip() or "—"
        parts.append(f'"{name}"')
        parts.append(f"lang={user.language_code or '?'}")
    chat = getattr(update, "effective_chat", None) or (update.callback_query.message.chat if update.callback_query and update.callback_query.message else None)
    if chat:
        parts.append(f"chat={chat.id}")
        parts.append(f"type={chat.type or '?'}")
        if getattr(chat, "title", None):
            t = (chat.title or "")[:25]
            parts.append(f'title="{t}"' + ("…" if len(chat.title or "") > 25 else ""))
    return " ".join(parts) if parts else "unknown"


def _log_action(kind: str, update: Update, action: str = "", extra: str = "") -> None:
    """Log fluide : [KIND] user... | action | extra."""
    ctx = _user_log_context(update)
    msg = f"[{kind}] {ctx}"
    if action:
        msg += f" | {action}"
    if extra:
        msg += f" | {extra}"
    logger.info(msg)


# -----------------------------------------------------------------------------
# CONFIGURATION
# -----------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    print("❌ BOT_TOKEN manquant !")
    print("1. Crée config.env avec BOT_TOKEN=ton_nouveau_token")
    print("2. Ou : set BOT_TOKEN=ton_nouveau_token")
    raise SystemExit(1)
CANAL_SHOP_URL = os.environ.get("CANAL_SHOP_URL", "https://t.me/ShopDuPeupleFrance")
VOUCH_CHANNEL_URL = os.environ.get("VOUCH_CHANNEL_URL", "https://t.me/shopVouchFR")
SUPPORT_CONTACT = os.environ.get("SUPPORT_CONTACT", "https://t.me/SqlSaint")
SHOP_LOGO_PATH = os.path.join(BASE_DIR, "shop_logo.png")
ADMIN_IDS: list[int] = []
MAX_MESSAGE_LENGTH = 4096
CHUNK_SEND = 4090

# -----------------------------------------------------------------------------
# IMAGES
# -----------------------------------------------------------------------------

IMAGE_URLS = {
    "fortnite": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6e/Fortnite_letter_e_logo.svg/512px-Fortnite_letter_e_logo.png",
    "valorant": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b0/Valorant_logo.svg/512px-Valorant_logo.png",
    "minecraft": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/32/Minecraft_logo.svg/512px-Minecraft_logo.svg.png",
    "netflix": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/08/Netflix_2015_logo.svg/512px-Netflix_2015_logo.png",
    "disney": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6a/Disney%2B_logo.svg/512px-Disney%2B_logo.svg.png",
    "prime": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/ca/Amazon_Prime_Video_logo_%282024%29.svg/512px-Amazon_Prime_Video_logo_%282024%29.svg.png",
    "vpn": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2e/Anonymous_globe.svg/512px-Anonymous_globe.svg.png",
    "premium": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5c/Gold_icon.svg/512px-Gold_icon.svg.png",
    "pack": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/47/Gift_icon.svg/512px-Gift_icon.svg.png",
    "hbo": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/42/HBO_Max_Logo.svg/512px-HBO_Max_Logo.svg.png",
    "discord": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/73/Discord_Color_Text_Logo_%282015-2021%29.svg/512px-Discord_Color_Text_Logo_%282015-2021%29.svg.png",
    "twitch": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a7/Circle-icons-twitch.svg/512px-Circle-icons-twitch.svg.png",
    "cod": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/25/Call_of_Duty_Black_Ops_4_logo.svg/512px-Call_of_Duty_Black_Ops_4_logo.svg.png",
    "chatgpt": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/04/ChatGPT_logo.svg/512px-ChatGPT_logo.svg.png",
    "instagram": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a5/Instagram_icon.png/512px-Instagram_icon.png",
}
DEFAULT_IMAGE = IMAGE_URLS["premium"]

def _img(k: str):
    return IMAGE_URLS.get(k, DEFAULT_IMAGE)

# -----------------------------------------------------------------------------
# CATALOGUE — ShopDuPeupleFrance
# -----------------------------------------------------------------------------

CATALOG = {
    "streaming_premium": {
        "title": "🎬 STREAMING PREMIUM",
        "image": _img("netflix"),
        "products": [
            {"id": "netflix_premium", "name": "Netflix Premium Access", "price": "3,50€", "benefits": ["Accès premium", "Livraison instantanée"], "badges": [], "image": _img("netflix")},
            {"id": "netflix_uhd", "name": "Netflix UHD Private Slot", "price": "2.50€", "benefits": ["UHD", "Slot privé", "Livraison instantanée"], "badges": [], "image": _img("netflix")},
            {"id": "netflix_lifetime", "name": "Netflix Lifetime", "price": "5€", "benefits": ["Accès à vie", "Livraison instantanée", "Support inclus"], "badges": ["🔥 Le plus vendu"], "image": _img("netflix")},
            {"id": "disney_premium", "name": "Disney+ Premium Access", "price": "3,99€", "benefits": ["Accès premium", "Livraison instantanée"], "badges": [], "image": _img("disney")},
            {"id": "prime_premium", "name": "Prime Video Premium", "price": "3,49€", "benefits": ["Prime Video", "Livraison instantanée"], "badges": [], "image": _img("prime")},
            {"id": "hbo_premium", "name": "HBO Max Premium", "price": "2,99€", "benefits": ["HBO Max", "Livraison instantanée"], "badges": [], "image": _img("hbo")},
            {"id": "crunchyroll_mega", "name": "Crunchyroll MEGA FAN", "price": "2,49€", "benefits": ["MEGA FAN", "Livraison instantanée"], "badges": [], "image": _img("pack")},
            {"id": "pack_streaming", "name": "Pack Streaming (Netflix + Disney+)", "price": "7,99€", "benefits": ["Netflix + Disney+", "Prix imbattable"], "badges": ["🔥 Le plus vendu"], "image": _img("pack")},
        ],
    },
    "abonnements_premium": {
        "title": "🎧 ABONNEMENTS PREMIUM",
        "image": _img("pack"),
        "products": [
            {"id": "spotify_premium", "name": "Spotify Premium", "price": "5,99€", "benefits": ["Spotify Premium", "Livraison instantanée"], "badges": [], "image": _img("pack")},
            {"id": "youtube_premium", "name": "YouTube Premium", "price": "3,99€", "benefits": ["YouTube Premium", "Livraison instantanée"], "badges": [], "image": _img("pack")},
            {"id": "duolingo_plus", "name": "Duolingo Plus", "price": "1,99€", "benefits": ["Duolingo Plus", "Livraison instantanée"], "badges": [], "image": _img("pack")},
            {"id": "capcut_pro", "name": "CapCut Pro", "price": "3,99€", "benefits": ["CapCut Pro", "Livraison instantanée"], "badges": [], "image": _img("pack")},
            {"id": "nba_access", "name": "NBA Access", "price": "1,99€", "benefits": ["NBA Access", "Livraison instantanée"], "badges": [], "image": _img("pack")},
            {"id": "ufc_access", "name": "UFC Access", "price": "49,99€", "benefits": ["UFC Access", "Support inclus"], "badges": [], "image": _img("pack")},
        ],
    },
    "vpn_securite": {
        "title": "🔐 VPN & SÉCURITÉ",
        "image": _img("vpn"),
        "products": [
            {"id": "vpn_premium_1an", "name": "VPN Premium 1 An", "price": "4,99€", "benefits": ["1 an", "Protection complète"], "badges": ["⭐ Recommandé"], "image": _img("vpn")},
            {"id": "vpn_premium_plus", "name": "VPN Premium+", "price": "6,99€", "benefits": ["Performances max", "Support prioritaire"], "badges": [], "image": _img("vpn")},
            {"id": "nord_vpn", "name": "Nord VPN Access", "price": "5,99€", "benefits": ["Nord VPN", "Livraison instantanée"], "badges": [], "image": _img("vpn")},
            {"id": "mullvad_vpn", "name": "Mullvad VPN", "price": "5,99€", "benefits": ["Mullvad", "Support inclus"], "badges": [], "image": _img("vpn")},
            {"id": "vpn_gen_lifetime", "name": "VPN Generator Lifetime", "price": "24,99€", "benefits": ["À vie", "Mises à jour"], "badges": ["🔥 Le plus vendu"], "image": _img("vpn")},
        ],
    },
    "discord_boosts": {
        "title": "💬 DISCORD & BOOSTS",
        "image": _img("discord"),
        "products": [
            {"id": "discord_gen_lifetime", "name": "Discord Generator Lifetime", "price": "33,00€", "benefits": ["Générateur à vie", "Livraison rapide"], "badges": ["🔥 Le plus vendu"], "image": _img("discord")},
            {"id": "discord_boosts_14", "name": "14x Boosts Serveur (1 mois)", "price": "3,50€", "benefits": ["14 Boosts 1 mois", "Livraison rapide"], "badges": [], "image": _img("discord")},
            {"id": "discord_fa_email", "name": "Discord FA – E-Mail Verified", "price": "0,10€", "benefits": ["E-mail vérifié", "Livraison instantanée"], "badges": [], "image": _img("discord")},
            {"id": "discord_fa_email_phone", "name": "Discord FA – E-Mail + Phone Verified", "price": "0,20€", "benefits": ["E-mail + Tél vérifiés"], "badges": ["⭐ Recommandé"], "image": _img("discord")},
            {"id": "discord_fa_aged", "name": "Discord FA – Aged 3+ Months", "price": "0,50€", "benefits": ["Compte vieilli", "Plus fiable"], "badges": [], "image": _img("discord")},
            {"id": "discord_2023", "name": "Discord Accounts 2023", "price": "0,92€", "benefits": ["Compte 2023", "Livraison instantanée"], "badges": [], "image": _img("discord")},
            {"id": "discord_2020", "name": "Discord Accounts 2020", "price": "1,85€", "benefits": ["Compte 2020", "Support inclus"], "badges": [], "image": _img("discord")},
            {"id": "discord_2019", "name": "Discord Accounts 2019", "price": "2,75€", "benefits": ["Compte 2019", "Livraison rapide"], "badges": [], "image": _img("discord")},
            {"id": "discord_2017", "name": "Discord Accounts 2017", "price": "7,35€", "benefits": ["Compte 2017", "Rareté"], "badges": [], "image": _img("discord")},
            {"id": "discord_2016", "name": "Discord Accounts 2016", "price": "13,80€", "benefits": ["Compte 2016", "Très rare"], "badges": ["⏰ Stock limité"], "image": _img("discord")},
        ],
    },
    "gaming_accounts": {
        "title": "🎮 GAMING ACCOUNTS",
        "image": _img("minecraft"),
        "products": [
            {"id": "minecraft_full", "name": "Minecraft Full Access", "price": "5,00€", "benefits": ["Compte Java complet", "Livraison instantanée"], "badges": ["🚀 Livraison rapide"], "image": _img("minecraft")},
            {"id": "gta5", "name": "GTA 5 Account", "price": "10,00€", "benefits": ["Compte GTA 5", "Livraison rapide"], "badges": [], "image": _img("premium")},
            {"id": "rdr2", "name": "RDR2 Social Club", "price": "3,85€", "benefits": ["RDR2 Social Club", "Livraison rapide"], "badges": [], "image": _img("premium")},
            {"id": "rust_nfa", "name": "Rust NFA", "price": "3,00€", "benefits": ["Rust NFA", "Livraison instantanée"], "badges": [], "image": _img("premium")},
            {"id": "rust_full", "name": "Rust Full", "price": "11,00€", "benefits": ["Compte Rust", "Support inclus"], "badges": [], "image": _img("premium")},
            {"id": "dayz", "name": "DayZ Account", "price": "1,95€", "benefits": ["Compte DayZ", "Livraison rapide"], "badges": [], "image": _img("premium")},
            {"id": "tarkov", "name": "Escape From Tarkov", "price": "12,65€", "benefits": ["Compte Tarkov", "Livraison rapide"], "badges": [], "image": _img("premium")},
            {"id": "ea_fc_26", "name": "EA FC 26", "price": "19,25€", "benefits": ["EA FC 26", "Support inclus"], "badges": [], "image": _img("premium")},
            {"id": "black_ops_6_7", "name": "Black Ops 6 [ 100-200 Level + RARE ]", "price": "20,50€", "benefits": ["100-200 Level", "Contenu rare", "Livraison rapide"], "badges": ["🔥 Le plus vendu"], "image": _img("cod")},
        ],
    },
    "fortnite_accounts": {
        "title": "🟣 FORTNITE ACCOUNTS",
        "image": _img("fortnite"),
        "products": [
            {"id": "fn_10_20", "name": "10–20 Skins (Ranked Ready)", "price": "1,50€", "benefits": ["Ranked ready", "Livraison rapide"], "badges": [], "image": _img("fortnite")},
            {"id": "fn_20_50", "name": "20–50 Skins", "price": "3,90€", "benefits": ["Skins variés", "Livraison instantanée"], "badges": ["⭐ Recommandé"], "image": _img("fortnite")},
            {"id": "fn_50_100", "name": "50–100 Skins (OG)", "price": "7,50€", "benefits": ["OG Outfit", "Support client"], "badges": [], "image": _img("fortnite")},
            {"id": "fn_100_150", "name": "100–150 Skins (OG)", "price": "10,00€", "benefits": ["Large choix", "Livraison rapide"], "badges": [], "image": _img("fortnite")},
            {"id": "fn_150_250", "name": "150–250 Skins (OG)", "price": "15,25€", "benefits": ["Collection complète", "Compte premium"], "badges": [], "image": _img("fortnite")},
            {"id": "fn_leviathan", "name": "Leviathan Axe + 100–200 Skins", "price": "17,50€", "benefits": ["Leviathan Axe", "100–200 Skins"], "badges": ["🔥 Le plus vendu"], "image": _img("fortnite")},
            {"id": "fn_travis", "name": "Travis Scott + OG Skins", "price": "44,00€", "benefits": ["Travis Scott", "OG Outfits"], "badges": [], "image": _img("fortnite")},
            {"id": "fn_black_knight", "name": "Black Knight OG", "price": "85,55€", "benefits": ["Black Knight", "MOST OG"], "badges": ["🔥 Le plus vendu", "⏰ Stock limité"], "image": _img("fortnite")},
        ],
    },
    "valorant_eu": {
        "title": "🔫 VALORANT (EU)",
        "image": _img("valorant"),
        "products": [
            {"id": "val_1_20_ranked", "name": "Level 1–20 Ranked Ready", "price": "4,80€", "benefits": ["EU", "Ranked ready"], "badges": [], "image": _img("valorant")},
            {"id": "val_20_40_knife", "name": "Level 20–40 Knife + Skins", "price": "17,25€", "benefits": ["Knife + Skins", "Livraison rapide"], "badges": ["⭐ Recommandé"], "image": _img("valorant")},
            {"id": "val_40_100_knife", "name": "Level 40–100 Knife + Skins", "price": "23,00€", "benefits": ["Niveau élevé", "Skins inclus"], "badges": [], "image": _img("valorant")},
            {"id": "val_100_300_knife", "name": "Level 100–300 Knife + Skins", "price": "46,00€", "benefits": ["Niveau max", "Collection complète"], "badges": ["🔥 Le plus vendu"], "image": _img("valorant")},
        ],
    },
    "reseaux_sociaux": {
        "title": "📱 RÉSEAUX SOCIAUX",
        "image": _img("pack"),
        "products": [
            {"id": "tiktok_1k", "name": "TikTok 1k Followers", "price": "3,20€", "benefits": ["1k followers", "Livraison rapide"], "badges": [], "image": _img("pack")},
            {"id": "tiktok_10k", "name": "TikTok 10k Followers", "price": "19,25€", "benefits": ["10k followers", "Livraison rapide"], "badges": [], "image": _img("pack")},
            {"id": "tiktok_20k", "name": "TikTok 20k Followers", "price": "33,55€", "benefits": ["20k followers", "Livraison rapide"], "badges": [], "image": _img("pack")},
            {"id": "instagram_1k", "name": "Instagram 1k Followers", "price": "9,10€", "benefits": ["1k followers", "Livraison sécurisée"], "badges": [], "image": _img("instagram")},
            {"id": "instagram_5k", "name": "Instagram 5k Followers", "price": "25,00€", "benefits": ["5k followers", "Livraison rapide"], "badges": [], "image": _img("instagram")},
            {"id": "twitch_fresh", "name": "Twitch Fresh", "price": "0,03€", "benefits": ["Compte Twitch", "Livraison instantanée"], "badges": [], "image": _img("twitch")},
            {"id": "twitch_10k", "name": "Twitch 10k Followers", "price": "10,45€", "benefits": ["10k followers", "Livraison rapide"], "badges": ["⭐ Recommandé"], "image": _img("twitch")},
        ],
    },
    "ia_tools": {
        "title": "🤖 IA & TOOLS",
        "image": _img("chatgpt"),
        "products": [
            {"id": "chatgpt_access", "name": "ChatGPT+ Access", "price": "4,60€", "benefits": ["ChatGPT+", "Livraison rapide"], "badges": ["🔥 Le plus vendu"], "image": _img("chatgpt")},
            {"id": "chatgpt_generator", "name": "ChatGPT+ Generator", "price": "46,20€", "benefits": ["Générateur ChatGPT+", "Livraison rapide"], "badges": [], "image": _img("chatgpt")},
            {"id": "steam_gen_lifetime", "name": "Steam Generator Lifetime", "price": "13,20€", "benefits": ["Générateur à vie", "Mises à jour"], "badges": [], "image": _img("premium")},
            {"id": "fortnite_gen", "name": "Fortnite Accounts Generator", "price": "33,00€", "benefits": ["Générateur comptes Fortnite", "Livraison rapide"], "badges": [], "image": _img("fortnite")},
            {"id": "tools_lifetime", "name": "Tools Lifetime", "price": "59,99€", "benefits": ["Accès à vie", "Mises à jour incluses"], "badges": ["🚀 Livraison rapide"], "image": _img("premium")},
        ],
    },
    "packs": {
        "title": "🎁 PACKS EXCLUSIFS",
        "image": _img("pack"),
        "products": [
            {"id": "pack_streaming_only", "name": "Pack Streaming", "price": "7,99€", "benefits": ["Netflix + Disney+", "Prix imbattable"], "badges": ["🔥 Le plus vendu"], "image": _img("pack")},
            {"id": "pack_gamer", "name": "Pack Gamer (Minecraft + VPN)", "price": "11,99€", "benefits": ["Minecraft Full + VPN 1 an", "Économie garantie"], "badges": ["⭐ Recommandé"], "image": _img("pack")},
        ],
    },
}

# Ordre des catégories pour « Tout le shop »
CATEGORY_ORDER = [
    "streaming_premium",
    "abonnements_premium",
    "vpn_securite",
    "discord_boosts",
    "gaming_accounts",
    "fortnite_accounts",
    "valorant_eu",
    "reseaux_sociaux",
    "ia_tools",
    "packs",
]

# -----------------------------------------------------------------------------
# PRIX / MARGE
# -----------------------------------------------------------------------------

def _parse_price(s: str) -> float:
    """Convertit une chaîne prix (ex. '4,99€') en float."""
    if not s:
        return 0.0
    t = s.replace(" ", "").replace("€", "").strip().replace(",", ".")
    try:
        return float(t)
    except ValueError:
        return 0.0

def _format_price(x: float) -> str:
    return f"{x:.2f}".replace(".", ",") + "€"

def _marge_produit(p: dict) -> tuple[float, float, float] | None:
    prix = _parse_price(p.get("price", "0€"))
    cost = _parse_price(p.get("cost", "0€"))
    return (prix, cost, round(max(0.0, prix - cost), 2))

def _get_product(category_key: str, product_id: str) -> Optional[dict]:
    cat = CATALOG.get(category_key)
    if not cat:
        return None
    for p in cat.get("products", []):
        if p["id"] == product_id:
            return p
    return None

# -----------------------------------------------------------------------------
# CLAVIERS (précalculés pour réduire latence)
# -----------------------------------------------------------------------------

def _build_main_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🛍️  Ouvrir le shop", callback_data="shop")],
        [
            InlineKeyboardButton("🎬 Streaming", callback_data="cat:streaming_premium"),
            InlineKeyboardButton("🎮 Gaming", callback_data="cat:gaming_accounts"),
        ],
        [
            InlineKeyboardButton("💬 Discord", callback_data="cat:discord_boosts"),
            InlineKeyboardButton("🟣 Fortnite", callback_data="cat:fortnite_accounts"),
        ],
        [InlineKeyboardButton("🔍  Lookup — Retrouver quelqu'un", callback_data="lookup")],
        [
            InlineKeyboardButton("💳 Paiement", callback_data="paiement"),
            InlineKeyboardButton("📸 Preuves", callback_data="vouch"),
        ],
        [
            InlineKeyboardButton("📢 Canal", callback_data="canal"),
            InlineKeyboardButton("📞 Contact", callback_data="support"),
        ],
    ])

def _build_shop_kb() -> InlineKeyboardMarkup:
    rows = []
    for key in CATEGORY_ORDER:
        cat = CATALOG.get(key)
        if not cat:
            continue
        rows.append([InlineKeyboardButton(cat["title"], callback_data=f"cat:{key}")])
    rows.append([InlineKeyboardButton("◀  Retour", callback_data="main")])
    return InlineKeyboardMarkup(rows)

def _build_canal_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📢  Rejoindre le canal", url=CANAL_SHOP_URL)],
        [InlineKeyboardButton("◀  Retour", callback_data="main")],
    ])

def _build_support_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📞  Contacter pour commander", url=SUPPORT_CONTACT)],
        [InlineKeyboardButton("◀  Retour", callback_data="main")],
    ])

def _build_vouch_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📸  Rejoindre Preuves & Avis", url=VOUCH_CHANNEL_URL)],
        [InlineKeyboardButton("◀  Retour", callback_data="main")],
    ])


def _build_paiement_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📞  Commander / Payer", url=SUPPORT_CONTACT)],
        [InlineKeyboardButton("◀  Retour", callback_data="main")],
    ])

def _build_lookup_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📞  Lookup avancé (tél, etc.)", url=SUPPORT_CONTACT)],
        [InlineKeyboardButton("◀  Retour", callback_data="main")],
    ])

KEYBOARD_MAIN = _build_main_kb()
KEYBOARD_SHOP = _build_shop_kb()
KEYBOARD_CANAL = _build_canal_kb()
KEYBOARD_SUPPORT = _build_support_kb()
KEYBOARD_VOUCH = _build_vouch_kb()
KEYBOARD_PAIEMENT = _build_paiement_kb()
KEYBOARD_LOOKUP = _build_lookup_kb()

def _keyboard_category(category_key: str) -> InlineKeyboardMarkup:
    """Clavier liste produits d'une catégorie + Retour / Shop."""
    cat = CATALOG.get(category_key)
    if not cat:
        return KEYBOARD_MAIN
    buttons = [[InlineKeyboardButton(f"▸ {p['name']}  ·  {p['price']}", callback_data=f"prod:{category_key}:{p['id']}")] for p in cat["products"]]
    buttons.append([InlineKeyboardButton("◀  Retour", callback_data="main")])
    buttons.append([InlineKeyboardButton("🛍️  Tout le shop", callback_data="shop")])
    return InlineKeyboardMarkup(buttons)

# Claviers catégories précalculés (évite recalcul à chaque vue)
KEYBOARD_CATEGORIES: dict[str, InlineKeyboardMarkup] = {k: _keyboard_category(k) for k in CATEGORY_ORDER}

def _keyboard_product(category_key: str, product_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🛒  Commander", url=SUPPORT_CONTACT)],
        [
            InlineKeyboardButton("◀  Catégorie", callback_data=f"cat:{category_key}"),
            InlineKeyboardButton("🏠  Menu", callback_data="main"),
        ],
    ])

# -----------------------------------------------------------------------------
# ENVOI PHOTOS (fallback)
# -----------------------------------------------------------------------------

async def _send_photo(chat_id: int, context: ContextTypes.DEFAULT_TYPE, url: str) -> bool:
    try:
        await context.bot.send_photo(chat_id=chat_id, photo=url)
        return True
    except BadRequest:
        return False

async def _send_photo_file(chat_id: int, context: ContextTypes.DEFAULT_TYPE, path: str) -> bool:
    if not os.path.isfile(path):
        return False
    try:
        with open(path, "rb") as f:
            await context.bot.send_photo(chat_id=chat_id, photo=f)
        return True
    except (BadRequest, OSError):
        return False

async def _delete_safe(context: ContextTypes.DEFAULT_TYPE, chat_id: int, message_id: int) -> None:
    try:
        await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
    except BadRequest:
        pass


async def _typing(chat_id: int, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Affiche « écriture… » (animation) puis micro-pause pour la rendre visible."""
    try:
        await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
        await asyncio.sleep(0.25)
    except BadRequest:
        pass


async def _edit_or_resend(
    q: CallbackQuery,
    context: ContextTypes.DEFAULT_TYPE,
    text: str,
    reply_markup: InlineKeyboardMarkup,
) -> None:
    """Édite le message (instantané). Si impossible (ex. message avec photo), supprime puis renvoie."""
    chat_id = q.message.chat_id
    msg_id = q.message.message_id
    try:
        await q.edit_message_text(text, parse_mode=ParseMode.HTML, reply_markup=reply_markup)
    except BadRequest:
        logger.debug("edit_message_text failed, fallback delete+send | chat_id=%s msg_id=%s", chat_id, msg_id)
        await _delete_safe(context, chat_id, msg_id)
        await context.bot.send_message(chat_id=chat_id, text=text, parse_mode=ParseMode.HTML, reply_markup=reply_markup)

# -----------------------------------------------------------------------------
# DONNÉES PRÉCALCULÉES (marges, listes)
# -----------------------------------------------------------------------------

def _collect_unique_products() -> list[dict]:
    """Liste tous les produits uniques (par id) dans l'ordre des catégories."""
    seen: set[str] = set()
    out: list[dict] = []
    for key in CATEGORY_ORDER:
        cat = CATALOG.get(key)
        if not cat:
            continue
        for p in cat.get("products", []):
            if p["id"] not in seen:
                seen.add(p["id"])
                out.append(p)
    return out


UNIQUE_PRODUCTS = _collect_unique_products()

# -----------------------------------------------------------------------------
# TEXTES INTERFACE
# -----------------------------------------------------------------------------

SEP = "────────────────────"
SEP2 = "════════════════════"
BANNER = (
    f"{SEP2}\n"
    "   <b>🛒 ShopDuPeupleFrance</b>\n"
    "   Prix bas · Livraison rapide\n"
    f"{SEP2}"
)

WELCOME_MAIN_TEXT = (
    f"{BANNER}\n\n"
    "Streaming, Gaming, Discord, Fortnite, VPN…\n"
    "Livraison <b>instantanée</b> · Support réactif.\n\n"
    "💰 <b>Les commandes sont à partir de 2€</b>\n\n"
    "▸ Paiement : Crypto · PayPal · RIB\n"
    "▸ Retrouver quelqu'un ? → <b>Lookup</b> ci-dessous.\n\n"
    "Choisis une option 👇"
)
CANAL_TEXT = (
    "📢 <b>ShopDuPeupleFrance — Canal officiel</b>\n"
    f"{SEP}\n\n"
    "▸ Promos et offres\n"
    "▸ Nouveautés en avant-première\n\n"
    "Rejoins le canal 👇"
)
SUPPORT_TEXT = (
    "📞 <b>Commander / Support</b>\n"
    f"{SEP}\n\n"
    "▸ Paiement sécurisé · Livraison rapide\n"
    "▸ Commandes à partir de <b>2€</b>\n\n"
    "Contacte-nous pour commander 👇"
)
VOUCH_TEXT = (
    "📸 <b>Preuves & Avis</b>\n"
    f"{SEP}\n\n"
    "Canal <b>ShopDuPeupleFrance</b> — Preuves (Vouch 1k+) :\n\n"
    "▸ Screens de livraisons\n"
    "▸ Avis clients\n\n"
    "Rejoins le canal 👇"
)
PAIEMENT_TEXT = (
    "💳 <b>Moyens de paiement</b>\n"
    f"{SEP}\n\n"
    "Nous acceptons :\n\n"
    "▸ <b>Crypto</b> (BTC, etc.)\n"
    "▸ <b>PayPal</b>\n"
    "▸ <b>RIB</b> (virement)\n\n"
    "Commandes à partir de <b>2€</b>. Contacte-nous pour commander 👇"
)
SHOP_TEXT = (
    "🛍️ <b>ShopDuPeupleFrance — Catalogue</b>\n"
    f"{SEP}\n\n"
    "Choisis une catégorie :\n\n"
    "▸ Streaming · Gaming · Discord · Fortnite · VPN…\n"
    "▸ Commandes à partir de 2€ · Livraison rapide"
)
LOOKUP_TEXT = (
    "🔍 <b>Lookup — Retrouver quelqu'un</b>\n"
    f"{SEP}\n\n"
    "• <b>Par ID Telegram</b> : envoie\n"
    "  <code>/lookup 123456789</code>\n\n"
    "• <b>Par @username</b> : envoie\n"
    "  <code>/lookup @pseudo</code>\n\n"
    "Le bot affiche les infos du compte (ID, nom, username) si disponibles.\n\n"
    "Pour un <b>lookup avancé</b> (numéro, email, etc.), contacte le support 👇"
)
COMMANDES_HELP_TEXT = (
    "📋 <b>Commandes — ShopDuPeupleFrance</b>\n"
    f"{SEP}\n\n"
    "▸ <code>/start</code> — Menu principal\n"
    "▸ <code>/lookup &lt;id ou @username&gt;</code> — Infos sur un compte Telegram\n"
    "▸ <code>/commandes</code> — Cette aide\n"
    "▸ <code>/marges</code> — (Admins) Marges bénéfice\n\n"
    "💰 <b>Les commandes (achats) sont à partir de 2€.</b>"
)

# -----------------------------------------------------------------------------
# HANDLERS
# -----------------------------------------------------------------------------

def _format_category_message(category_key: str) -> tuple[str, InlineKeyboardMarkup]:
    """Retourne (texte, clavier) pour une catégorie. Clavier depuis cache si possible."""
    cat = CATALOG.get(category_key)
    if not cat:
        return "Catégorie introuvable.", KEYBOARD_MAIN
    lines = [f"<b>{cat['title']}</b>", SEP, ""]
    for p in cat["products"]:
        lines.append(f"▸ {p['name']}  ·  <b>{p['price']}</b>")
    lines.append("")
    lines.append("Choisis un produit 👇")
    text = "\n".join(lines)
    kb = KEYBOARD_CATEGORIES.get(category_key, _keyboard_category(category_key))
    return text, kb


def _format_product_message(product: dict, is_admin: bool, category_key: str, product_id: str) -> tuple[str, InlineKeyboardMarkup]:
    """Retourne (texte, clavier) pour une fiche produit."""
    badges = " ".join(product.get("badges", []))
    benefits = "\n".join(f"▸ {b}" for b in product.get("benefits", []))
    marge_line = ""
    if is_admin:
        t = _marge_produit(product)
        if t:
            _, cost, marge = t
            marge_line = f"\n📊 Coût {_format_price(cost)} · Marge <b>{_format_price(marge)}</b>\n"
    name = product["name"]
    price = product["price"]
    head = f"{badges}\n\n" if badges else ""
    text = (
        f"{head}<b>{name}</b>\n{SEP}\n\n"
        f"💰 <b>{price}</b>{marge_line}\n"
        f"{benefits}\n\n"
        f"🚀 Livraison rapide · Support inclus"
    )
    return text, _keyboard_product(category_key, product_id)


async def cmd_marges(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Commande /marges : liste des marges (admins uniquement)."""
    _log_action("MARGES", update, "commande")
    try:
        user_id = update.effective_user.id if update.effective_user else None
        if user_id not in ADMIN_IDS:
            _log_action("MARGES", update, "refusé", "non admin")
            await update.effective_message.reply_text("⛔ Réservé aux admins. Ajoute ton ID dans ADMIN_IDS.")
            return
        _log_action("MARGES", update, "OK", "admin")
        products = UNIQUE_PRODUCTS
        lines = ["📊 <b>Marges bénéfice</b>\n\n<b>Produit</b> · Prix · Coût · Marge\n"]
        for p in products:
            t = _marge_produit(p)
            if not t:
                continue
            _, cost, marge = t
            name = (p["name"][:40] + "…") if len(p["name"]) > 40 else p["name"]
            lines.append(f"• {name}\n  💰 {p['price']} · Coût {_format_price(cost)} · Marge <b>{_format_price(marge)}</b>")
        total = sum((_marge_produit(p) or (0, 0, 0))[2] for p in products)
        lines.append(f"\n📈 <b>Marge totale (1 vente/produit) : {_format_price(total)}</b>")
        text = "\n".join(lines)
        if len(text) > MAX_MESSAGE_LENGTH:
            for i in range(0, len(text), CHUNK_SEND):
                await update.effective_message.reply_text(text[i : i + CHUNK_SEND], parse_mode=ParseMode.HTML)
        else:
            await update.effective_message.reply_text(text, parse_mode=ParseMode.HTML)
    except Exception as e:
        logger.exception("cmd_marges: %s", e)
        await update.effective_message.reply_text("❌ Une erreur s'est produite. Réessaie plus tard.")


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Commande /start : message de bienvenue + menu principal."""
    _log_action("START", update, "/start")
    try:
        chat_id = update.effective_chat.id
        await _typing(chat_id, context)
        await update.effective_message.reply_text(
            WELCOME_MAIN_TEXT,
            parse_mode=ParseMode.HTML,
            reply_markup=KEYBOARD_MAIN,
        )
    except Exception as e:
        _log_action("ERREUR", update, "cmd_start", str(e))
        logger.exception("cmd_start")
        await update.effective_message.reply_text("❌ Erreur. Réessaie avec /start.")


async def cmd_commandes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Commande /commandes : liste des commandes + rappel 2€."""
    _log_action("CMD", update, "/commandes")
    try:
        await update.effective_message.reply_text(
            COMMANDES_HELP_TEXT,
            parse_mode=ParseMode.HTML,
        )
    except Exception as e:
        logger.exception("cmd_commandes")
        await update.effective_message.reply_text("❌ Erreur.")


async def cmd_lookup(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Commande /lookup <id ou @username> : infos sur un compte Telegram."""
    _log_action("LOOKUP", update, " ".join((context.args or [])))
    if not context.args or len(context.args) != 1:
        await update.effective_message.reply_text(
            "Usage : <code>/lookup 123456789</code> ou <code>/lookup @username</code>\n"
            "Permet de retrouver les infos d'un compte Telegram (ID, nom, username).",
            parse_mode=ParseMode.HTML,
        )
        return
    arg = context.args[0].strip()
    chat_id = update.effective_chat.id
    await _typing(chat_id, context)
    if arg.startswith("@"):
        await update.effective_message.reply_text(
            "Lookup par @username : envoie l’ID du compte si tu l’as, ou contacte le support pour un lookup avancé.",
            parse_mode=ParseMode.HTML,
        )
        return
    try:
        user_id = int(arg)
    except ValueError:
        await update.effective_message.reply_text("❌ L’ID doit être un nombre (ex. 123456789).")
        return
    try:
        chat = await context.bot.get_chat(user_id)
        name = (chat.first_name or "") + (" " + (chat.last_name or "")).strip()
        username = f"@{chat.username}" if getattr(chat, "username", None) else "—"
        text = (
            f"🔍 <b>Lookup — Résultat</b>\n{SEP}\n\n"
            f"🆔 <b>ID</b> : <code>{chat.id}</code>\n"
            f"👤 <b>Nom</b> : {name or '—'}\n"
            f"📌 <b>Username</b> : {username}\n"
        )
        await update.effective_message.reply_text(text, parse_mode=ParseMode.HTML)
    except BadRequest as e:
        if "chat not found" in str(e).lower() or "user not found" in str(e).lower():
            await update.effective_message.reply_text(
                "❌ Compte introuvable ou pas de conversation en commun.\n"
                "Pour un lookup avancé (numéro, etc.), contacte le support.",
                parse_mode=ParseMode.HTML,
            )
        else:
            await update.effective_message.reply_text("❌ Impossible de récupérer les infos. Contacte le support.")
    except Exception as e:
        logger.exception("cmd_lookup: %s", e)
        await update.effective_message.reply_text("❌ Erreur. Réessaie ou contacte le support.")

async def _callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Dispatch des callbacks : main, canal, support, shop, paiement, vouch, cat:, prod:."""
    q = update.callback_query
    data = q.data or ""
    _log_action("BTN", update, data)
    await q.answer()
    chat_id = q.message.chat_id

    try:
        await _typing(chat_id, context)
        if data == "main":
            await _edit_or_resend(q, context, WELCOME_MAIN_TEXT, KEYBOARD_MAIN)
            return
        if data == "canal":
            await _edit_or_resend(q, context, CANAL_TEXT, KEYBOARD_CANAL)
            return
        if data == "support":
            await _edit_or_resend(q, context, SUPPORT_TEXT, KEYBOARD_SUPPORT)
            return
        if data == "vouch":
            await _edit_or_resend(q, context, VOUCH_TEXT, KEYBOARD_VOUCH)
            return
        if data == "paiement":
            await _edit_or_resend(q, context, PAIEMENT_TEXT, KEYBOARD_PAIEMENT)
            return
        if data == "shop":
            await _edit_or_resend(q, context, SHOP_TEXT, KEYBOARD_SHOP)
            return
        if data == "lookup":
            await _edit_or_resend(q, context, LOOKUP_TEXT, KEYBOARD_LOOKUP)
            return

        if data.startswith("cat:"):
            ckey = data.split(":", 1)[1]
            _log_action("BTN", update, data, f"cat={ckey}")
            text, kb = _format_category_message(ckey)
            await _edit_or_resend(q, context, text, kb)
            return

        if data.startswith("prod:"):
            parts = data.split(":", 2)
            if len(parts) != 3:
                return
            _, ckey, pid = parts
            _log_action("BTN", update, data, f"prod={pid} cat={ckey}")
            product = _get_product(ckey, pid)
            if not product:
                await _edit_or_resend(q, context, "Produit introuvable.", KEYBOARD_MAIN)
                return
            is_admin = q.from_user is not None and q.from_user.id in ADMIN_IDS
            text, kb = _format_product_message(product, is_admin, ckey, pid)
            await _edit_or_resend(q, context, text, kb)
            return

    except Exception as e:
        _log_action("ERREUR", update, f"data={data}", str(e))
        logger.exception("callback_handler")
        await _edit_or_resend(q, context, "❌ Une erreur s'est produite. Réessaie ou /start.", KEYBOARD_MAIN)

# -----------------------------------------------------------------------------
# GESTION GLOBALE DES ERREURS
# -----------------------------------------------------------------------------

async def _error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log propre des erreurs (handlers)."""
    err = context.error
    kind = type(err).__name__
    msg = (str(err) or "(pas de message)")[:80]
    if isinstance(update, Update):
        ctx = _user_log_context(update)
        logger.error("ERREUR %s | %s | %s", kind, ctx, msg)
    else:
        logger.error("ERREUR %s | %s", kind, msg)


# -----------------------------------------------------------------------------
# MAIN
# -----------------------------------------------------------------------------

async def _post_init(_app) -> None:
    logger.info("ShopDuPeupleFrance — Bot prêt | START / commandes / lookup / marges")

def _setup_logging() -> None:
    """Logging fluide, moins de bruit HTTP."""
    logging.basicConfig(
        format="%(asctime)s | %(message)s",
        datefmt="%H:%M:%S",
        level=logging.INFO,
    )
    for name in ("httpx", "httpcore", "telegram.request", "telegram.ext._application"):
        logging.getLogger(name).setLevel(logging.WARNING)
    logging.getLogger(__name__).setLevel(logging.INFO)

def main() -> None:
    """Point d'entrée : logging, handlers, polling avec reconnexion auto."""
    _setup_logging()
    app = (
        Application.builder()
        .token(BOT_TOKEN)
        .post_init(_post_init)
        .build()
    )
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("commandes", cmd_commandes))
    app.add_handler(CommandHandler("lookup", cmd_lookup))
    app.add_handler(CommandHandler("marges", cmd_marges))
    app.add_handler(CallbackQueryHandler(_callback_handler))
    app.add_error_handler(_error_handler)

    logger.info("ShopDuPeupleFrance — Démarrage (Ctrl+C pour arrêter)")
    while True:
        try:
            app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)
            break
        except KeyboardInterrupt:
            break
        except (NetworkError, OSError, Exception) as e:
            logger.error("RÉSEAU %s — reconnexion dans 15 s…", type(e).__name__)
            logger.debug("Détail: %s", e, exc_info=True)
            try:
                time.sleep(15)
            except KeyboardInterrupt:
                break
    logger.info("ShopDuPeupleFrance — Arrêt")

if __name__ == "__main__":
    main()
