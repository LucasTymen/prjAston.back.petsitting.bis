"""
Telegram Bot — Interface de controle du Job Search Agent System
Securite : whitelist user_id, rate limiting, audit log
Evite blocage : I/O bloquant exécuté en thread pour garder l'event loop réactif.
"""
import asyncio
import json
import logging
import os
import sqlite3
import sys
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")
import subprocess
from collections import defaultdict
from datetime import datetime, timedelta
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
)

# Config
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") or os.getenv("token")
ALLOWED_USER_IDS = set(
    int(x) for x in (os.getenv("TELEGRAM_ALLOWED_IDS") or os.getenv("TELEGRAM_USER_ID") or "").split(",") if x.strip()
)
DB_PATH = os.getenv("DB_PATH") or str(PROJECT_ROOT / "storage" / "applications.db")
LOG_PATH = os.getenv("LOG_PATH") or str(PROJECT_ROOT / "logs" / "cron.log")
FOLLOWUP_LOG = os.getenv("FOLLOWUP_LOG") or str(PROJECT_ROOT / "logs" / "followup.log")

RATE_LIMIT = 10
RATE_WINDOW = 60
_rate_counters = defaultdict(list)

LOGS_DIR = PROJECT_ROOT / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    handlers=[
        logging.FileHandler(LOGS_DIR / "telegram_bot.log"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger("telegram_bot")


def is_allowed(user_id: int) -> bool:
    return user_id in ALLOWED_USER_IDS


def is_authorized(update: Update) -> bool:
    user = update.effective_user
    if not user:
        return False
    if not is_allowed(user.id):
        log.warning("[BLOCKED] Unauthorized access attempt: user_id=%s", user.id)
        return False
    return True


def rate_limited(user_id: int) -> bool:
    now = datetime.now()
    window_start = now - timedelta(seconds=RATE_WINDOW)
    _rate_counters[user_id] = [t for t in _rate_counters[user_id] if t > window_start]
    if len(_rate_counters[user_id]) >= RATE_LIMIT:
        return True
    _rate_counters[user_id].append(now)
    return False


def guard(func):
    async def wrapper(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        if not is_authorized(update):
            return  # Blocage silencieux
        if rate_limited(update.effective_user.id):
            await update.message.reply_text("Rate limit atteint.")
            return
        log.info("CMD %s — user=%s", func.__name__, update.effective_user.id)
        await func(update, ctx)

    wrapper.__name__ = func.__name__
    return wrapper


def tail_log(path: str, n: int = 25) -> str:
    """Dernières N lignes d'un fichier (cross-platform, sans subprocess tail)."""
    path_obj = Path(path)
    if not path_obj.exists():
        return "(fichier absent)"
    try:
        with path_obj.open(encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
        return "".join(lines[-n:]) if lines else "(vide)"
    except Exception as e:
        log.warning("tail_log %s: %s", path[:50], e)
        return "(erreur lecture)"


async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Répond toujours : si non autorisé, envoie ton ID pour que tu l'ajoutes au .env (aucun bot tiers)."""
    user = update.effective_user
    if not user:
        return
    user_id = user.id
    if rate_limited(user_id):
        await update.message.reply_text("Rate limit atteint.")
        return
    if is_allowed(user_id):
        await update.message.reply_text("Bot actif.")
        log.info("CMD start — user=%s", user_id)
        return
    # Pas encore autorisé : on lui donne son ID pour qu'il l'ajoute au .env (pas de bot tiers)
    await update.message.reply_text(
        f"Ton ID Telegram : {user_id}\n\n"
        f"Ajoute dans ton fichier .env :\n"
        f"TELEGRAM_ALLOWED_IDS={user_id}\n\n"
        f"Puis redémarre le bot. Ensuite /start répondra « Bot actif. »"
    )
    log.info("ID envoyé à user=%s (pas encore autorisé)", user_id)


@guard
async def cmd_status(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    try:
        if not Path(DB_PATH).exists():
            await update.message.reply_text("Aucune candidature en base.")
            return

        def _fetch() -> list:
            conn = sqlite3.connect(DB_PATH, timeout=5.0)
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT job_url, score, status, result_json, created_at FROM applications "
                "ORDER BY created_at DESC LIMIT 10"
            ).fetchall()
            conn.close()
            return [dict(r) for r in rows]

        rows = await asyncio.to_thread(_fetch)

        if not rows:
            await update.message.reply_text("Aucune candidature en base.")
            return

        statut_emoji = {"J0": "📤", "relance_j4": "🔔", "relance_j10": "🔕", "envoyee": "📤"}
        msg = "Candidatures recentes\n\n"
        for r in rows:
            try:
                data = json.loads(r.get("result_json") or "{}")
                offre = data.get("offre", {})
                entreprise = offre.get("entreprise", "?")
                titre = offre.get("titre", "?")
            except (json.JSONDecodeError, TypeError):
                entreprise, titre = "?", "?"
            emoji = statut_emoji.get(r.get("status", ""), "•")
            score_str = f"{r.get('score')}/100" if r.get("score") is not None else "—"
            date_str = (r.get("created_at") or "")[:10]
            msg += f"{emoji} {entreprise}\n  {titre} | Score: {score_str} | {date_str}\n\n"

        await update.message.reply_text(msg)
    except Exception as e:
        log.exception("cmd_status")
        await update.message.reply_text(f"Erreur : {e}")


@guard
async def cmd_offres(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    try:
        scan_dir = PROJECT_ROOT / "storage" / "scans"
        if not scan_dir.exists():
            await update.message.reply_text("Aucun scan disponible.")
            return
        files = sorted(scan_dir.glob("*.csv"), key=lambda f: f.stat().st_mtime, reverse=True)
        if not files:
            files = list(scan_dir.glob("*.json"))
            files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
        if not files:
            await update.message.reply_text("Aucun scan disponible.")
            return

        latest = files[0]
        text = await asyncio.to_thread(lambda: latest.read_text(encoding="utf-8", errors="replace"))
        if latest.suffix == ".json":
            try:
                data = json.loads(text)
                offres = data.get("offres", [])[:10]
                msg = f"Dernieres offres ({latest.name})\n\n"
                for o in offres:
                    msg += f"• {o.get('entreprise','?')} — {o.get('titre','?')} | {o.get('score_pct','')}%\n"
            except json.JSONDecodeError:
                msg = "Fichier JSON invalide."
        else:
            lines = text.splitlines()
            msg = f"Dernieres offres ({latest.name})\n\n"
            header = lines[0].split(",") if lines else []
            for line in lines[1:11]:
                parts = line.split(",")
                if len(parts) >= 3:
                    msg += f"• {parts[1]} — {parts[2]} | {parts[7] if len(parts) > 7 else ''}\n"

        await update.message.reply_text(msg[:4000])
    except Exception as e:
        log.exception("cmd_offres")
        await update.message.reply_text(f"Erreur : {e}")


@guard
async def cmd_relances(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    try:
        if not Path(DB_PATH).exists():
            await update.message.reply_text("Aucune relance en attente.")
            return

        def _fetch():
            conn = sqlite3.connect(DB_PATH, timeout=5.0)
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT result_json, created_at, status FROM applications "
                "WHERE status IN ('J0', 'envoyee', 'relance_j4') AND result_json IS NOT NULL"
            ).fetchall()
            conn.close()
            return [dict(r) for r in rows]

        rows = await asyncio.to_thread(_fetch)
        today = datetime.now().date()
        msg = "Relances a venir\n\n"
        count = 0
        for r in rows:
            try:
                data = json.loads(r.get("result_json") or "{}")
                offre = data.get("offre", {})
                canal = data.get("canal_application", {})
                entreprise = offre.get("entreprise", "?")
                titre = offre.get("titre", "?")
                email = canal.get("contact_cible", "")
                if not email or email == "Inconnu":
                    continue
                date_str = (r.get("created_at") or "")[:10]
                date_cand = datetime.fromisoformat(date_str).date()
                delta = (today - date_cand).days
                j4 = date_cand + timedelta(days=4)
                j10 = date_cand + timedelta(days=10)

                if delta < 4:
                    msg += f"J+4 le {j4} — {entreprise}\n"
                elif delta == 4:
                    msg += f"J+4 AUJOURD'HUI — {entreprise}\n"
                elif r.get("status") == "relance_j4" and delta < 10:
                    msg += f"J+10 le {j10} — {entreprise}\n"
                elif r.get("status") == "relance_j4" and delta >= 10:
                    msg += f"J+10 AUJOURD'HUI — {entreprise}\n"
                count += 1
            except (ValueError, KeyError, TypeError):
                continue

        if count == 0:
            msg = "Aucune relance en attente."
        await update.message.reply_text(msg[:4000])
    except Exception as e:
        log.exception("cmd_relances")
        await update.message.reply_text(f"Erreur : {e}")


@guard
async def cmd_stats(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    try:
        if not Path(DB_PATH).exists():
            await update.message.reply_text("Aucune donnee.")
            return

        def _fetch():
            conn = sqlite3.connect(DB_PATH, timeout=5.0)
            total = conn.execute("SELECT COUNT(*) FROM applications").fetchone()[0]
            par_statut = conn.execute(
                "SELECT status, COUNT(*) FROM applications GROUP BY status"
            ).fetchall()
            score_row = conn.execute("SELECT AVG(score) FROM applications").fetchone()
            conn.close()
            return total, par_statut, score_row

        total, par_statut, score_row = await asyncio.to_thread(_fetch)

        score_moy = score_row[0] if score_row and score_row[0] is not None else None
        msg = f"Statistiques\n\nTotal : {total}\nScore moyen : {round(score_moy, 1) if score_moy else '—'}/100\n\nPar statut :\n"
        for statut, cnt in par_statut:
            msg += f"  • {statut} : {cnt}\n"
        await update.message.reply_text(msg)
    except Exception as e:
        log.exception("cmd_stats")
        await update.message.reply_text(f"Erreur : {e}")


def _escape_html(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")[:3500]


@guard
async def cmd_logs(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    content = await asyncio.to_thread(tail_log, LOG_PATH, 25)
    content = _escape_html(content)
    await update.message.reply_text(f"<pre>{content}</pre>", parse_mode="HTML")


@guard
async def cmd_followup_logs(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    content = await asyncio.to_thread(tail_log, FOLLOWUP_LOG, 20)
    content = _escape_html(content)
    await update.message.reply_text(f"<pre>{content}</pre>", parse_mode="HTML")


@guard
async def cmd_scan(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("Confirmer", callback_data="scan_confirm"),
            InlineKeyboardButton("Annuler", callback_data="scan_cancel"),
        ]
    ]
    await update.message.reply_text(
        "Lancer un scan (Indeed, France Travail, HelloWork, Dogfinance, Meteojob, Glassdoor, LinkedIn, WTTJ, APEC) ?",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def callback_scan(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    if not user or user.id not in ALLOWED_USER_IDS:
        await query.edit_message_text("Acces non autorise.")
        return

    if query.data == "scan_cancel":
        await query.edit_message_text("Scan annule.")
        return

    await query.edit_message_text("Scan en cours...")
    log.info("Scan manuel declenche par user=%s", user.id)

    try:
        log_file = LOGS_DIR / "manual_scan.log"
        with open(log_file, "a", encoding="utf-8") as f:
            subprocess.Popen(
                [
                    sys.executable, "-m", "scheduler.cron_runner",
                    "--mode", "both",
                    "--sources", "wttj,francetravail,indeed,hellowork,dogfinance,meteojob,glassdoor,linkedin,apec",
                    "--max", "10",
                ],
                cwd=str(PROJECT_ROOT),
                stdout=f,
                stderr=subprocess.STDOUT,
                start_new_session=True,
            )
        await ctx.bot.send_message(
            chat_id=query.message.chat_id,
            text="Scan lance. /logs dans 2-3 min pour les resultats.",
        )
    except Exception as e:
        log.exception("callback_scan")
        await ctx.bot.send_message(
            chat_id=query.message.chat_id,
            text=f"Erreur lancement scan : {e}",
        )


@guard
async def cmd_help(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    msg = (
        "Job Search Agent — Panneau de controle\n\n"
        "/status — Candidatures recentes\n"
        "/offres — Dernieres offres scannees\n"
        "/relances — Relances J+4/J+10 a venir\n"
        "/scan — Lancer un scan manuel\n"
        "/logs — Dernieres lignes cron.log\n"
        "/followup_logs — Logs relances\n"
        "/stats — Statistiques globales\n"
        "/help — Cette aide\n"
    )
    await update.message.reply_text(msg)


def main():
    if not TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN manquant dans .env")

    log.info("Bot demarre — users autorises : %s (envoie /start a ton bot pour obtenir ton ID)", ALLOWED_USER_IDS or "aucun")

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("status", cmd_status))
    app.add_handler(CommandHandler("offres", cmd_offres))
    app.add_handler(CommandHandler("relances", cmd_relances))
    app.add_handler(CommandHandler("stats", cmd_stats))
    app.add_handler(CommandHandler("logs", cmd_logs))
    app.add_handler(CommandHandler("followup_logs", cmd_followup_logs))
    app.add_handler(CommandHandler("scan", cmd_scan))
    app.add_handler(CallbackQueryHandler(callback_scan, pattern="^scan_"))

    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
