"""
╔══════════════════════════════════════════════════════════════════╗
║           AUTO POST REFRESHER — USER SESSION MODE              ║
╚══════════════════════════════════════════════════════════════════╝

  ✅ নির্ধারিত সময়ে Account connect হয়, কাজ শেষে disconnect।
     সারাদিন Account active থাকে না।

  📌 CHANNEL_USERNAME কীভাবে পাবেন?
     Telegram-এ চ্যানেলে যান → Info → Username (t.me/xxxxx)
     শুধু "xxxxx" অংশটুকু দিন (@ ছাড়া)।
     Username না থাকলে CHANNEL_ID দিয়ে রাখুন, বট নিজে খুঁজে নেবে।
"""

# ====================================================================
#                   ⚙️  CONFIGURATION  ⚙️
#         (শুধু এই অংশ পরিবর্তন করুন — বাকি কোডে হাত দেবেন না)
# ====================================================================

# 🔑 Telegram Credentials (https://my.telegram.org)
API_ID         = 37001641
API_HASH       = "75aaefa6b305facc4745d25eb1fcf9f4"
SESSION_STRING = "BQI0makAaOaV435DZ54UwZ9yQyorV7BjDJhMbDkdUepGOwKRaczVDT_IueOC7sG3ZcET39NovSL_Xk4hHGFehcHBaayHwQGioxunMZsbGBxvN4JPP4M0P7Qp_0mpMKD4Lzj8BYbgUPpYL6QpypOTmDc8Q_MEO5QgRjCed90XigP-MSUTDy77CQHfTcC2A6XxweUCASwRprby4bxf7f8PNpLKFx3KFTmvp7wz9v6uScDIJZMeqXqxpw3v9CWqKExp9O9UtHTXVR4po4CTK3OzjUQzRvjan7bq60Kz055y9KPBKs0ksO6bVkypn3nyfY43IdCxWS3rP4ECRv9A3z7R1YRLEnF6wgAAAAHPS6uXAA"

# 📢 Channel সনাক্তকরণ
#    Username থাকলে username দিন (@ ছাড়া), না থাকলে "" রাখুন
CHANNEL_USERNAME = "ALQalamBD"          # অথবা "" ফাঁকা রাখুন
CHANNEL_ID       = -1003797236998       # Channel ID (backup হিসেবে)

# ⏰ Auto Refresh সময়সূচি (বাংলাদেশ সময় — ১২ ঘণ্টা AM/PM)
#
#    ফরম্যাট: ("ঘণ্টা:মিনিট", "AM/PM")
#
#    উদাহরণ:
#      ("6:00",  "AM")  →  ভোর ৬:০০
#
#    ✅ যত খুশি লাইন যোগ করুন — কোনো সীমা নেই
# ---------------------------------------------------------------
SCHEDULE_TIMES = [
      ("5:05",  "AM"),
    # ("11:11",  "PM"),
    # ("6:00",  "PM"),
    # ("9:00",  "PM"),
    # ("6:00",  "AM"),
    # ("11:30", "AM"),
    # ("4:30",  "PM"),
    # ("11:00", "PM"),
]

# 📦 প্রতিটি সময়ে কতটি পোস্ট Refresh হবে (1 = একটা, 5 = পাঁচটা)
POSTS_PER_RUN = 1


# ====================================================================
#           🔧 নিচের কোড পরিবর্তন করার প্রয়োজন নেই
# ====================================================================

import asyncio
import logging
import os
import pytz
from datetime import datetime
from threading import Thread

# Python 3.12+ fix: event loop must exist before Pyrogram loads
try:
    asyncio.get_event_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())

import time
from flask import Flask
from pyrogram import Client
from pyrogram.errors import FloodWait, MessageDeleteForbidden, MessageIdInvalid

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

DHAKA_TZ    = pytz.timezone("Asia/Dhaka")
JUMUAH_TAG  = "#jumuah"
CHANNEL_TAG = "#alqalambd"


# ── AM/PM → 24-hour ────────────────────────────────────────────────
def parse_ampm(time_str: str, ampm: str):
    h, m = map(int, time_str.strip().split(":"))
    p = ampm.strip().upper()
    if p == "AM":
        if h == 12: h = 0
    elif p == "PM":
        if h != 12: h += 12
    return h, m


def is_jumuah(caption: str) -> bool:
    c = (caption or "").lower()
    return JUMUAH_TAG in c and CHANNEL_TAG in c

def is_regular(caption: str) -> bool:
    return JUMUAH_TAG not in (caption or "").lower()


# ── Fired-slot tracker (restart-proof) ────────────────────────────
# "YYYY-MM-DD HH:MM" ফরম্যাটে চলে-যাওয়া slot ফাইলে রাখে।
# Restart হলেও ফাইল টিকে থাকে → একই মিনিটে দুবার চলবে না।
_SLOTS_FILE = "fired_slots.txt"

def _load_slots() -> set:
    try:
        with open(_SLOTS_FILE) as f:
            return {ln.strip() for ln in f if ln.strip()}
    except FileNotFoundError:
        return set()

def _persist_slot(slot: str):
    """slot key ফাইলে লিখে রাখে (append)।"""
    try:
        with open(_SLOTS_FILE, "a") as f:
            f.write(slot + "\n")
    except Exception as e:
        logger.warning(f"⚠️  slot সেভ হয়নি: {e}")

def _prune_slots(slots: set) -> set:
    """আজকের আগের পুরনো slot ছেঁটে ফেলে — ফাইল ছোট রাখে।"""
    today = datetime.now(DHAKA_TZ).strftime("%Y-%m-%d")
    kept  = {s for s in slots if s.startswith(today)}
    try:
        with open(_SLOTS_FILE, "w") as f:
            f.write("\n".join(kept) + ("\n" if kept else ""))
    except Exception:
        pass
    return kept

def _prefill_past_slots(fired: set) -> set:
    """
    Startup-এ আজকের যেসব scheduled time ইতিমধ্যে পেরিয়ে গেছে (>১ মিনিট আগে),
    সেগুলো fired সেটে ভরে দেয়।

    কেন দরকার:
      Render-এ প্রতি deploy-এ fresh container আসে → fired_slots.txt থাকে না।
      তাই ৮টায় deploy হলে ৫টার slot আবার fire করত।
      এই ফাংশন সেটা ঠেকায়।
    """
    now   = datetime.now(DHAKA_TZ)
    today = now.strftime("%Y-%m-%d")
    now_total_mins = now.hour * 60 + now.minute

    for ts, period in SCHEDULE_TIMES:
        h, m = parse_ampm(ts, period)
        sched_total_mins = h * 60 + m
        # ১ মিনিটের বেশি আগে হলে — পুরনো, skip করো
        if now_total_mins - sched_total_mins > 1:
            slot_key = f"{today} {h:02d}:{m:02d}"
            if slot_key not in fired:
                fired.add(slot_key)
                _persist_slot(slot_key)
                h12 = h % 12 or 12
                ap  = "AM" if h < 12 else "PM"
                logger.info(
                    f"⏭️  Startup guard: আজকের {h12}:{m:02d} {ap} slot পেরিয়ে গেছে → skip হবে"
                )
    return fired


# ── Channel peer resolve (username → ID cache) ─────────────────────
async def resolve_channel(client: Client) -> int:
    """Channel-এর resolved ID ফেরত দেয়। Username থাকলে সেটা ব্যবহার করে,
    না থাকলে dialogs খুঁজে CHANNEL_ID match করে।"""
    if CHANNEL_USERNAME:
        try:
            chat = await client.get_chat(CHANNEL_USERNAME)
            logger.info(f"📢 Channel: {chat.title} (id={chat.id})")
            return chat.id
        except Exception as e:
            logger.warning(f"⚠️  Username দিয়ে resolve হয়নি: {e} — dialog search চেষ্টা করছি...")

    # Fallback: dialogs থেকে খোঁজা
    async for dialog in client.get_dialogs():
        if dialog.chat.id == CHANNEL_ID:
            logger.info(f"📢 Channel dialog থেকে পাওয়া: {dialog.chat.title}")
            return dialog.chat.id
    raise RuntimeError(f"Channel পাওয়া যায়নি (ID={CHANNEL_ID}, Username={CHANNEL_USERNAME})")


# ── একটি Refresh চক্র: connect → কাজ → disconnect ─────────────────
async def run_refresh():
    now       = datetime.now(DHAKA_TZ)
    is_friday = now.weekday() == 4   # 0=Mon, 4=Fri

    logger.info(
        f"\n{'='*56}\n"
        f"  🔄 Auto Refresh শুরু\n"
        f"  ⏰ সময় : {now.strftime('%I:%M %p')} (BD)\n"
        f"  📅 দিন  : {'শুক্রবার ✅' if is_friday else now.strftime('%A')}\n"
        f"{'='*56}"
    )

    client    = Client(
        name           = "refresher",
        api_id         = API_ID,
        api_hash       = API_HASH,
        session_string = SESSION_STRING,
    )
    refreshed = 0

    try:
        await client.start()
        me = await client.get_me()
        logger.info(f"🔗 Account: {me.first_name} (@{me.username})")

        channel_id = await resolve_channel(client)

        # পুরনো থেকে নতুন ক্রমে পোস্ট সাজানো
        messages = []
        async for msg in client.get_chat_history(channel_id, limit=200):
            messages.append(msg)
        messages = [m for m in messages if m.date is not None]
        messages.sort(key=lambda m: m.date)

        logger.info(f"📋 চ্যানেলে {len(messages)}টি পোস্ট পাওয়া গেছে")

        for msg in messages:
            if refreshed >= POSTS_PER_RUN:
                break
            if msg.service or msg.empty:
                continue

            caption = msg.caption or msg.text or ""

            # শুক্রবার: শুধু Jumuah পোস্ট Refresh হবে
            if is_friday:
                if not is_jumuah(caption):
                    continue
            else:
                # অন্য দিন: Jumuah পোস্ট বাদ
                if not is_regular(caption):
                    continue

            old_id  = msg.id
            preview = caption[:70].replace("\n", " ") if caption else "[media]"
            logger.info(f"\n  🎯 Refresh: id={old_id} | {preview}")

            try:
                # হুবহু কপি করে নতুন পোস্ট (caption সহ)
                new = await client.copy_message(
                    chat_id      = channel_id,
                    from_chat_id = channel_id,
                    message_id   = old_id,
                )
                logger.info(f"  ✅ নতুন পোস্ট → new_id={new.id}")

            except Exception as copy_err:
                # copy না হলে forward করা (sticker/poll ইত্যাদির জন্য)
                logger.warning(f"  ⚠️  copy_message ব্যর্থ ({copy_err}) — forward চেষ্টা করছি...")
                try:
                    fwd = await client.forward_messages(
                        chat_id     = channel_id,
                        from_chat_id= channel_id,
                        message_ids = old_id,
                    )
                    logger.info(f"  ✅ Forward সফল → new_id={fwd.id}")
                except Exception as fwd_err:
                    logger.error(f"  ❌ forward_messages ব্যর্থ: {fwd_err} — skip")
                    continue

            await asyncio.sleep(1.5)

            # পুরনো পোস্ট ডিলেট
            try:
                await client.delete_messages(channel_id, old_id)
                logger.info(f"  🗑️  পুরনো পোস্ট ডিলেট → old_id={old_id}\n")
            except FloodWait as e:
                logger.warning(f"  ⏳ FloodWait {e.value}s...")
                await asyncio.sleep(e.value + 1)
                await client.delete_messages(channel_id, old_id)
            except Exception as del_err:
                logger.error(f"  ❌ delete ব্যর্থ: {del_err}")

            refreshed += 1

        if refreshed == 0:
            if is_friday:
                logger.info("  ℹ️  শুক্রবার: #ALQalamBD + #Jumuah পোস্ট পাওয়া যায়নি")
            else:
                logger.info("  ℹ️  Refresh-যোগ্য পোস্ট পাওয়া যায়নি")

    except FloodWait as e:
        logger.warning(f"⏳ FloodWait {e.value}s — পরবর্তী সময়ে চেষ্টা হবে")
        await asyncio.sleep(e.value)
    except Exception as e:
        logger.error(f"❌ Refresh ব্যর্থ: {e}")
    finally:
        try:
            await client.stop()
        except Exception:
            pass
        logger.info(f"🔌 Account disconnect | ✅ {refreshed}টি পোস্ট Refresh হয়েছে\n")


# ── Flask keep-alive (Render free tier) ────────────────────────────
flask_app = Flask(__name__)

@flask_app.route("/")
def home():
    now = datetime.now(DHAKA_TZ).strftime("%Y-%m-%d %I:%M %p")
    sl  = []
    for ts, p in SCHEDULE_TIMES:
        h, m = parse_ampm(ts, p)
        h12  = h % 12 or 12
        ap   = "AM" if h < 12 else "PM"
        sl.append(f"{h12}:{m:02d} {ap}")
    return (
        "<h2>✅ Auto Post Refresher চলছে</h2>"
        f"<p>বাংলাদেশ সময়: <b>{now}</b></p>"
        "<p>💡 Account শুধু Refresh-এর সময় connect হয়</p>"
        f"<p>Channel: <b>@{CHANNEL_USERNAME or CHANNEL_ID}</b></p>"
        f"<p>Schedule ({len(sl)}টি):<br>"
        + "<br>".join(f"&nbsp;&nbsp;• {s} (BD)" for s in sl)
        + f"</p><p>প্রতিবার: <b>{POSTS_PER_RUN}</b>টি পোস্ট</p>"
    )

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    try:
        flask_app.run(host="0.0.0.0", port=port, use_reloader=False)
    except OSError:
        flask_app.run(host="0.0.0.0", port=8090, use_reloader=False)


# ── Sync wrapper — clock thread থেকে async চালায় ──────────────────
def _run_refresh_sync():
    """Clock scheduler-এর daemon thread হিসেবে চলে — fresh event loop তৈরি করে।"""
    logger.info("⏰ Scheduled time match → Refresh শুরু হচ্ছে...")
    try:
        asyncio.run(run_refresh())
    except Exception as e:
        logger.error(f"❌ _run_refresh_sync error: {e}")


# ── Clock-based scheduler loop ──────────────────────────────────────
def _clock_scheduler():
    """
    প্রতি ৩০ সেকেন্ডে BD ঘড়ি চেক করে।
    SCHEDULE_TIMES-এ সেট করা মিনিট হলেই — এবং সেই slot আগে না চললে —
    refresh job চালায়।

    Restart-proof: চলে-যাওয়া slot _SLOTS_FILE-এ persist থাকে।
    Render ৫০০ বার restart দিলেও সঠিক মিনিট ছাড়া চলবে না।
    """
    # startup: আজকের পুরনো slot লোড করো, তারপর আজকের পেরিয়ে-যাওয়া slots মার্ক করো
    fired = _prune_slots(_load_slots())
    fired = _prefill_past_slots(fired)

    # schedule label তৈরি করো (log-এর জন্য)
    labels = []
    for ts, p in SCHEDULE_TIMES:
        h, m  = parse_ampm(ts, p)
        h12   = h % 12 or 12
        ap    = "AM" if h < 12 else "PM"
        labels.append(f"{h12}:{m:02d} {ap}")

    now = datetime.now(DHAKA_TZ)
    logger.info(
        f"\n{'='*60}\n"
        f"  🤖 Auto Post Refresher সক্রিয়!\n"
        f"  📅 বাংলাদেশ সময়  : {now.strftime('%Y-%m-%d %I:%M %p')}\n"
        f"  📢 Channel        : @{CHANNEL_USERNAME or CHANNEL_ID}\n"
        f"  ⏰ Schedule       : {', '.join(labels) or '(কোনো সময় সেট নেই)'}\n"
        f"  📦 প্রতিবার       : {POSTS_PER_RUN}টি পোস্ট\n"
        f"  💡 Account শুধু Refresh-এর সময় active হয়\n"
        f"  🔁 চেক           : প্রতি ৩০ সেকেন্ডে BD সময় দেখা হয়\n"
        f"{'='*60}"
    )

    while True:
        try:
            now      = datetime.now(DHAKA_TZ)
            today    = now.strftime("%Y-%m-%d")
            slot_key = now.strftime("%Y-%m-%d %H:%M")

            # নতুন দিন শুরু হলে in-memory set রিফ্রেশ করো
            # (ফাইলে ইতিমধ্যে আগের দিনের slot নেই — _prune_slots মুছে দিয়েছে)
            if not any(s.startswith(today) for s in fired) and fired:
                fired = _prune_slots(fired)

            # এই মিনিটে কোনো scheduled time আছে কিনা চেক
            for ts, period in SCHEDULE_TIMES:
                h, m = parse_ampm(ts, period)
                if now.hour == h and now.minute == m and slot_key not in fired:
                    # ── সাথে সাথে slot mark করো → rapid restart-এও দ্বিতীয়বার চলবে না
                    fired.add(slot_key)
                    _persist_slot(slot_key)
                    logger.info(
                        f"⏰ {now.strftime('%I:%M %p')} BD — scheduled! → job চালু হচ্ছে"
                    )
                    Thread(target=_run_refresh_sync, daemon=True).start()
                    break   # একাধিক slot একই মিনিটে থাকলেও একবারই চলবে

        except Exception as e:
            logger.error(f"❌ clock scheduler error: {e}")

        time.sleep(30)


# ── Main ────────────────────────────────────────────────────────────
def main():
    Thread(target=run_flask, daemon=True).start()
    logger.info("🌐 Keep-alive সার্ভার চালু")

    # Clock scheduler background thread-এ চলবে
    Thread(target=_clock_scheduler, daemon=True).start()

    # Main thread জীবিত রাখা
    try:
        while True:
            time.sleep(60)
            logger.debug(f"💓 alive | {datetime.now(DHAKA_TZ).strftime('%I:%M %p')}")
    except (KeyboardInterrupt, SystemExit):
        logger.info("🛑 Refresher বন্ধ হয়েছে")


if __name__ == "__main__":
    main()
