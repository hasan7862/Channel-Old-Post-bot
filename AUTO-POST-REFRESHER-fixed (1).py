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

# 📢 দ্বিতীয় চ্যানেল — এখানে নতুন copy পোস্ট হবে
# এই চ্যানেলের কোনো message delete করা হবে না।
TARGET_CHANNEL_ID = -1003704917412
# Username দিলে Telegram peer আগে থেকেই resolve করতে পারে; ID fallback হিসেবে থাকবে।
TARGET_CHANNEL_USERNAME = "Islamic_Stor"

# 🏷️ Source এবং Target caption tags
# একাধিক tag কমা দিয়ে লিখুন — যেমন:
# "#Alqalam, #Islamic, #Quran"
# পোস্টে এগুলো একই লাইনে space দিয়ে দেখা যাবে।
# সাধারণ দিনের পুরনো পোস্ট খোঁজার tag
SOURCE_SEARCH_TAGS = "#ALQalamBD"
# সাধারণ দিনের নতুন refreshed source পোস্টে লেখা হবে এই tag
SOURCE_CAPTION_TAGS = "#ALQalam365" #source channel tag
FRIDAY_SOURCE_CAPTION_TAGS = "#Jumuah_Mubarak"
TARGET_CAPTION_TAGS = "#IslamicStore" #post tag
FRIDAY_TARGET_CAPTION_TAGS = "#Jumuah_Mubarak" #post tag

# ০ দিলে pending join request approval বন্ধ থাকবে।
JOIN_REQUESTS_PER_RUN = 40

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
      ("11:11", "PM"),
      ("01:11", "AM"),
      ("03:33", "AM"),
      ("03:25", "PM"),
    # ("11:00", "AM"),
    # ("04:30", "PM"),
    # ("11:00", "PM"),
]

# 🕌 শুক্রবারের Jumuah পোস্টের আলাদা সময়সূচি (বাংলাদেশ সময়)
#
#    এখানে সময় দিলে শুক্রবারে SCHEDULE_TIMES আর ব্যবহার হবে না;
#    শুধু এই তালিকার সময়গুলোতেই Jumuah পোস্ট Refresh হবে।
#
#    তালিকাটি খালি রাখলে আগের নিয়ম বজায় থাকবে — শুক্রবারেও
#    SCHEDULE_TIMES-এর সময়ে Jumuah পোস্ট Refresh হবে।
# ---------------------------------------------------------------
FRIDAY_SCHEDULE_TIMES = [
       ("12:01", "AM"),
       ("03:45", "AM"),
       ("08:40", "AM"),
       ("11:46", "AM"),
       ("01:15", "PM"),
]

# 📦 Refresh policy
# প্রতিটি scheduled time-এ source channel-এর সব পোস্টের মধ্যে
# সবচেয়ে পুরনো matching/tagged পোস্টটি একটিমাত্র refresh হবে।
# কোনো history limit বা মোট পোস্টের সংখ্যা এখানে সেট করার দরকার নেই।


# ====================================================================
#           🔧 নিচের কোড পরিবর্তন করার প্রয়োজন নেই
# ====================================================================

import asyncio
import logging
import os
import re
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
CHANNEL_TAG = "#alqalambd"
JUMUAH_TAGS = {"#jumuah", "#jumah"}


# ── AM/PM → 24-hour ────────────────────────────────────────────────
def parse_ampm(time_str: str, ampm: str):
    try:
        h, m = map(int, time_str.strip().split(":"))
        p = ampm.strip().upper()
    except (AttributeError, TypeError, ValueError):
        raise ValueError(f"Invalid time: {time_str!r}; use H:MM")
    if not 1 <= h <= 12 or not 0 <= m <= 59 or p not in {"AM", "PM"}:
        raise ValueError(f"Invalid time: {time_str!r} {ampm!r}; use H:MM AM/PM")
    if p == "AM":
        if h == 12: h = 0
    elif p == "PM":
        if h != 12: h += 12
    return h, m


def schedule_for(now=None):
    """
    নির্দিষ্ট দিনের জন্য কার্যকর সময়সূচি ফেরত দেয়।

    Friday list খালি থাকলে পুরনো SCHEDULE_TIMES fallback হিসেবে থাকে,
    যাতে নতুন কনফিগ না দিলেও আগের আচরণ নষ্ট না হয়।
    """
    current = now or datetime.now(DHAKA_TZ)
    if current.weekday() == 4 and FRIDAY_SCHEDULE_TIMES:
        return FRIDAY_SCHEDULE_TIMES
    return SCHEDULE_TIMES


def format_schedule(schedule_times) -> list:
    """সময়গুলোকে মানুষের পড়ার উপযোগী ১২ ঘণ্টার format-এ দেখায়।"""
    labels = []
    for ts, period in schedule_times:
        h, m = parse_ampm(ts, period)
        h12 = h % 12 or 12
        ap = "AM" if h < 12 else "PM"
        labels.append(f"{h12}:{m:02d} {ap}")
    return labels


def parse_tags(tag_text: str) -> list:
    """কমা বা space-separated tag config-কে unique tag list-এ পরিণত করে।"""
    tags = []
    seen = set()
    for raw in re.split(r"[,\s]+", tag_text or ""):
        tag = raw.strip()
        if not tag:
            continue
        if not tag.startswith("#"):
            tag = f"#{tag}"
        key = tag.casefold()
        if key not in seen:
            tags.append(tag)
            seen.add(key)
    return tags


def caption_without_tags(caption: str) -> str:
    """Caption-এর পুরনো hashtag সরিয়ে মূল লেখা রাখে।"""
    base = re.sub(r"(?<!\w)#[^\s#]+", "", caption or "")
    base = re.sub(r"[ \t]+\n", "\n", base)
    return re.sub(r"\n{3,}", "\n\n", base).strip()


def caption_with_tags(caption: str, tag_config: str) -> str:
    """মূল caption-এর শেষে configured tags একই লাইনে যোগ করে।"""
    base = caption_without_tags(caption)
    tags_line = " ".join(parse_tags(tag_config))
    if base and tags_line:
        return f"{base}\n\n{tags_line}"
    return base or tags_line


def is_jumuah(caption: str) -> bool:
    c = (caption or "").lower()
    return any(tag in c for tag in JUMUAH_TAGS) and has_source_tag(c)

def has_source_tag(caption: str) -> bool:
    c = (caption or "").lower()
    source_markers = {
        CHANNEL_TAG,
        *(tag.lower() for tag in parse_tags(SOURCE_SEARCH_TAGS)),
        *(tag.lower() for tag in parse_tags(SOURCE_CAPTION_TAGS)),
        *(tag.lower() for tag in parse_tags(FRIDAY_SOURCE_CAPTION_TAGS)),
    }
    return any(tag in c for tag in source_markers)

def has_source_search_tag(caption: str) -> bool:
    """সাধারণ দিনের legacy source tag আছে কি না দেখে।"""
    c = (caption or "").lower()
    return any(
        tag.lower() in c
        for tag in parse_tags(SOURCE_SEARCH_TAGS)
    )

def has_current_source_tag(caption: str) -> bool:
    """সাধারণ দিনের নতুন source tag আছে কি না দেখে।"""
    c = (caption or "").lower()
    return any(
        tag.lower() in c
        for tag in parse_tags(SOURCE_CAPTION_TAGS)
    )

def is_regular(caption: str) -> bool:
    c = (caption or "").lower()
    return (
        has_source_tag(c)
        and not any(tag in c for tag in JUMUAH_TAGS)
    )


# ── Fired-slot tracker (restart-proof) ────────────────────────────
# "YYYY-MM-DD HH:MM" ফরম্যাটে চলে-যাওয়া slot ফাইলে রাখে।
# Restart হলেও ফাইল টিকে থাকে → একই মিনিটে দুবার চলবে না।
_SLOTS_FILE = "fired_slots.txt"
# A short grace window prevents a scheduled run being lost when the
# scheduler wakes a few seconds late after a restart/deploy.
SLOT_GRACE_SECONDS = 90

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
    Startup-এ আজকের যেসব scheduled time grace window-এর বেশি আগে পেরিয়ে গেছে,
    সেগুলো fired সেটে ভরে দেয়।

    কেন দরকার:
      Render-এ প্রতি deploy-এ fresh container আসে → fired_slots.txt থাকে না।
      তাই ৮টায় deploy হলে ৫টার slot আবার fire করত।
      এই ফাংশন সেটা ঠেকায়।
    """
    now   = datetime.now(DHAKA_TZ)
    today = now.strftime("%Y-%m-%d")
    today_schedule = schedule_for(now)

    for ts, period in today_schedule:
        h, m = parse_ampm(ts, period)
        scheduled_at = now.replace(
            hour=h, minute=m, second=0, microsecond=0
        )
        # Grace window পেরিয়ে গেলে পুরনো slot — skip করো।
        if (now - scheduled_at).total_seconds() > SLOT_GRACE_SECONDS:
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


def _scheduled_slot_for(now, schedule_times):
    """এই মুহূর্তে চালানোর মতো scheduled slot থাকলে তার key ফেরত দেয়।"""
    for ts, period in schedule_times:
        h, m = parse_ampm(ts, period)
        scheduled_at = now.replace(
            hour=h, minute=m, second=0, microsecond=0
        )
        age_seconds = (now - scheduled_at).total_seconds()
        if 0 <= age_seconds <= SLOT_GRACE_SECONDS:
            return scheduled_at.strftime("%Y-%m-%d %H:%M")
    return None


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


async def resolve_target_channel(client: Client):
    """Target channel-এর chat object ফেরত দেয় (username → dialogs fallback)।"""
    if TARGET_CHANNEL_USERNAME:
        try:
            chat = await client.get_chat(TARGET_CHANNEL_USERNAME)
            logger.info(f"📢 Target channel: {chat.title} (id={chat.id})")
            return chat
        except Exception as e:
            logger.warning(
                f"⚠️ Target username দিয়ে resolve হয়নি: {e} — dialog search চেষ্টা করছি..."
            )

    async for dialog in client.get_dialogs():
        if dialog.chat.id == TARGET_CHANNEL_ID:
            logger.info(
                f"📢 Target channel dialog থেকে পাওয়া: {dialog.chat.title}"
            )
            return dialog.chat
    raise RuntimeError(
        f"Target channel পাওয়া যায়নি "
        f"(ID={TARGET_CHANNEL_ID}, Username={TARGET_CHANNEL_USERNAME})"
    )


async def approve_target_join_requests(client: Client, target_channel_id: int) -> int:
    """Pending join request থেকে সর্বোচ্চ ৪০টি request approve করে।"""
    approved = 0
    try:
        async for request in client.get_chat_join_requests(
            target_channel_id,
            limit=JOIN_REQUESTS_PER_RUN,
        ):
            user = getattr(request, "from_user", None) or getattr(request, "user", None)
            user_id = getattr(user, "id", None)
            if user_id is None:
                logger.warning("⚠️ Join request-এ user ID পাওয়া যায়নি — skip")
                continue

            try:
                await client.approve_chat_join_request(target_channel_id, user_id)
                approved += 1
                logger.info(
                    f"✅ Target join request approved: "
                    f"{getattr(user, 'first_name', '')} (id={user_id})"
                )
            except FloodWait as e:
                logger.warning(
                    f"⏳ Approval FloodWait {e.value}s — এই run-এ {approved}টি approve হয়েছে"
                )
                await asyncio.sleep(e.value + 1)
                break
            except Exception as request_err:
                logger.warning(
                    f"⚠️ Join request approve ব্যর্থ (id={user_id}): {request_err}"
                )
    except FloodWait as e:
        logger.warning(f"⏳ Join request list-এ FloodWait {e.value}s")
        await asyncio.sleep(e.value)
    except Exception as e:
        logger.warning(f"⚠️ Target join request পড়া যায়নি: {e}")

    logger.info(
        f"👥 Target channel join approval: {approved}/{JOIN_REQUESTS_PER_RUN}"
    )
    return approved


def target_caption(caption: str, is_friday: bool) -> str:
    """Target caption-এ শুক্রবার/সাধারণ দিনের configured tags রাখে।"""
    tag_config = (
        FRIDAY_TARGET_CAPTION_TAGS
        if is_friday
        else TARGET_CAPTION_TAGS
    )
    return caption_with_tags(caption, tag_config)


def source_caption(caption: str, is_friday: bool) -> str:
    """Source refreshed copy-তে configured tags রাখে।"""
    tag_config = (
        FRIDAY_SOURCE_CAPTION_TAGS
        if is_friday
        else SOURCE_CAPTION_TAGS
    )
    return caption_with_tags(caption, tag_config)


async def copy_to_target_with_caption(
    client: Client,
    target_channel_id: int,
    source_channel_id: int,
    message,
    caption: str,
):
    """
    Target channel-এ নতুন post তৈরি করে এবং target-specific caption রাখে।
    Media হলে copy_message, text হলে send_message ব্যবহার করা হয়।
    """
    if getattr(message, "media", None):
        return await client.copy_message(
            chat_id=target_channel_id,
            from_chat_id=source_channel_id,
            message_id=message.id,
            caption=caption,
        )
    return await client.send_message(
        chat_id=target_channel_id,
        text=caption,
    )


async def copy_to_source_with_caption(
    client: Client,
    source_channel_id: int,
    message,
    caption: str,
):
    """Source channel-এ configured caption সহ নতুন refreshed copy রাখে।"""
    if getattr(message, "media", None):
        return await client.copy_message(
            chat_id=source_channel_id,
            from_chat_id=source_channel_id,
            message_id=message.id,
            caption=caption,
        )
    return await client.send_message(
        chat_id=source_channel_id,
        text=caption,
    )


# ── একটি Refresh চক্র: connect → কাজ → disconnect ─────────────────
async def run_refresh():
    now       = datetime.now(DHAKA_TZ)
    is_friday = now.weekday() == 4   # 0=Mon, 4=Fri
    friday_custom_schedule = is_friday and bool(FRIDAY_SCHEDULE_TIMES)

    logger.info(
        f"\n{'='*56}\n"
        f"  🔄 Auto Refresh শুরু\n"
        f"  ⏰ সময় : {now.strftime('%I:%M %p')} (BD)\n"
        f"  📅 দিন  : {'শুক্রবার ✅' if is_friday else now.strftime('%A')}\n"
        f"  🗓️ সময়সূচি : "
        f"{'শুক্রবারের আলাদা সময়' if friday_custom_schedule else 'সাধারণ সময়সূচি'}\n"
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
        target_chat = await resolve_target_channel(client)
        target_channel_id = target_chat.id

        # Pyrogram history newest → oldest আসে। কোনো limit না দিয়ে পুরো
        # history scan করি, কিন্তু সব message list-এ জমাই না। ফলে channel-এ
        # ২০০, ২০০০ বা তারও বেশি post থাকলেও memory অযথা বাড়ে না।
        #
        # scan চলাকালে date compare করে সবচেয়ে পুরনো eligible candidate রাখি।
        # ফলে API history order বদলালেও সঠিক oldest post-ই refresh হবে।
        oldest_candidate = None
        oldest_legacy_candidate = None
        oldest_current_candidate = None
        scanned_messages = 0
        async for msg in client.get_chat_history(channel_id):
            scanned_messages += 1
            if msg.date is None or msg.service or msg.empty:
                continue

            caption = msg.caption or msg.text or ""

            # শুক্রবার: source tag-সহ শুধু Jumuah পোস্ট
            if is_friday:
                eligible = is_jumuah(caption)
                if (
                    eligible
                    and (
                        oldest_candidate is None
                        or msg.date < oldest_candidate[0].date
                    )
                ):
                    oldest_candidate = (msg, caption)
            else:
                # অন্য দিন:
                # ১) আগে পুরনো #ALQalamBD পোস্ট শেষ করবে।
                # ২) পুরনো tag-এর পোস্ট শেষ হলে #ALQalam365 fallback হবে।
                eligible = is_regular(caption)
                if eligible and has_source_search_tag(caption):
                    if (
                        oldest_legacy_candidate is None
                        or msg.date < oldest_legacy_candidate[0].date
                    ):
                        oldest_legacy_candidate = (msg, caption)
                elif eligible and has_current_source_tag(caption):
                    if (
                        oldest_current_candidate is None
                        or msg.date < oldest_current_candidate[0].date
                    ):
                        oldest_current_candidate = (msg, caption)

        if not is_friday:
            # Legacy #ALQalamBD থাকলে সেটিই priority পাবে;
            # না থাকলেই নতুন #ALQalam365 পোস্টে যাবে।
            oldest_candidate = (
                oldest_legacy_candidate
                or oldest_current_candidate
            )

        logger.info(
            f"📋 পুরো channel history scan হয়েছে: {scanned_messages}টি message"
        )

        # প্রতি scheduled run-এ মাত্র oldest eligible post refresh হবে।
        # কোনো post-count setting বা history limit নেই।
        if oldest_candidate is not None:
            msg, caption = oldest_candidate
            old_id  = msg.id
            preview = caption[:70].replace("\n", " ") if caption else "[media]"
            logger.info(f"\n  🎯 Oldest tagged post Refresh: id={old_id} | {preview}")

            source_new = None
            try:
                # আগে source copy সফল করি, তারপর target-এ আলাদা caption সহ
                # নতুন post করি। এতে source protected হলে target-এ orphan post
                # তৈরি হবে না।
                source_new = await copy_to_source_with_caption(
                    client=client,
                    source_channel_id=channel_id,
                    message=msg,
                    caption=source_caption(caption, is_friday),
                )
                logger.info(
                    f"  ✅ Source channel-এ refreshed copy → new_id={source_new.id}"
                )

                # শুক্রবারে শুধু #Jumah, অন্য দিনে শুধু #Islam যোগ হবে।
                target_new = await copy_to_target_with_caption(
                    client=client,
                    target_channel_id=target_channel_id,
                    source_channel_id=channel_id,
                    message=msg,
                    caption=target_caption(caption, is_friday),
                )
                logger.info(
                    f"  ✅ Target channel-এ নতুন পোস্ট → new_id={target_new.id}"
                )

            except Exception as copy_err:
                logger.error(
                    f"  ❌ দুই channel-এ copy সম্পূর্ণ হয়নি: {copy_err} — "
                    "source old post delete হবে না"
                )
                # Target copy ব্যর্থ হলে শুধু এই run-এর নতুন source copy rollback।
                if source_new is not None:
                    try:
                        await client.delete_messages(channel_id, source_new.id)
                        logger.info(
                            f"  ↩️ অসম্পূর্ণ source copy rollback → new_id={source_new.id}"
                        )
                    except Exception as rollback_err:
                        logger.error(
                            f"  ❌ source rollback ব্যর্থ: {rollback_err}"
                        )
            else:
                await asyncio.sleep(1.5)

                # copy দুটো সফল হলেই পুরনো post delete
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

        # Scheduled run-এর সঙ্গে target channel-এর pending request approve হবে।
        # ০ দিলে approval বন্ধ থাকবে। Target channel-এর কোনো message এখানে
        # delete করা হয় না।
        if JOIN_REQUESTS_PER_RUN > 0:
            await approve_target_join_requests(client, target_channel_id)
        else:
            logger.info("👥 Target channel join approval বন্ধ (JOIN_REQUESTS_PER_RUN=0)")

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
    regular_sl = format_schedule(SCHEDULE_TIMES)
    friday_sl = format_schedule(FRIDAY_SCHEDULE_TIMES)
    friday_text = (
        ", ".join(friday_sl) + " (শুধু Jumuah)"
        if friday_sl
        else "সাধারণ সময়সূচি অনুসরণ করবে"
    )
    return (
        "<h2>✅ Auto Post Refresher চলছে</h2>"
        f"<p>বাংলাদেশ সময়: <b>{now}</b></p>"
        "<p>💡 Account শুধু Refresh-এর সময় connect হয়</p>"
        f"<p>Channel: <b>@{CHANNEL_USERNAME or CHANNEL_ID}</b></p>"
        f"<p>সাধারণ Schedule ({len(regular_sl)}টি):<br>"
        + "<br>".join(f"&nbsp;&nbsp;• {s} (BD)" for s in regular_sl)
        + f"</p><p>শুক্রবারের Jumuah Schedule:<br>"
        + f"&nbsp;&nbsp;• {friday_text}"
        + f"</p><p>Source tags: <b>{' '.join(parse_tags(SOURCE_CAPTION_TAGS)) or '(কোনো tag নেই)'}</b>"
        + f"<br>শুক্রবার Source tags: <b>{' '.join(parse_tags(FRIDAY_SOURCE_CAPTION_TAGS)) or '(কোনো tag নেই)'}</b>"
        + f"<br>Target tags: <b>{' '.join(parse_tags(TARGET_CAPTION_TAGS)) or '(কোনো tag নেই)'}</b>"
        + f"<br>শুক্রবার Target tags: <b>{' '.join(parse_tags(FRIDAY_TARGET_CAPTION_TAGS)) or '(কোনো tag নেই)'}</b>"
        + "</p><p>প্রতিবার: সব পোস্টের মধ্যে সবচেয়ে পুরনো matching/tagged পোস্টটি ১টি Refresh হবে</p>"
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
    প্রতি ৫ সেকেন্ডে BD ঘড়ি চেক করে।
    scheduled time থেকে SLOT_GRACE_SECONDS-এর মধ্যে — এবং সেই slot
    আগে না চললে — refresh job চালায়।

    Restart-proof: চলে-যাওয়া slot _SLOTS_FILE-এ persist থাকে।
    Render ৫০০ বার restart দিলেও সঠিক মিনিট ছাড়া চলবে না।
    """
    # startup: আজকের পুরনো slot লোড করো, তারপর grace window পেরিয়ে যাওয়া
    # slots মার্ক করো
    fired = _prune_slots(_load_slots())
    fired = _prefill_past_slots(fired)

    now = datetime.now(DHAKA_TZ)
    regular_labels = format_schedule(SCHEDULE_TIMES)
    friday_labels = format_schedule(FRIDAY_SCHEDULE_TIMES)
    friday_schedule_label = (
        ", ".join(friday_labels)
        if friday_labels
        else "সাধারণ সময়সূচির fallback"
    )
    logger.info(
        f"\n{'='*60}\n"
        f"  🤖 Auto Post Refresher সক্রিয়!\n"
        f"  📅 বাংলাদেশ সময়  : {now.strftime('%Y-%m-%d %I:%M %p')}\n"
        f"  📢 Source Channel : @{CHANNEL_USERNAME or CHANNEL_ID}\n"
        f"  📢 Target Channel : {TARGET_CHANNEL_ID}\n"
        f"  ⏰ সাধারণ Schedule : {', '.join(regular_labels) or '(কোনো সময় সেট নেই)'}\n"
        f"  🕌 Friday Schedule : {friday_schedule_label}\n"
        f"  📦 প্রতি slot      : oldest matching/tagged post ১টি Refresh + "
        f"{JOIN_REQUESTS_PER_RUN}টি পর্যন্ত join approval\n"
        f"  💡 Account শুধু Refresh-এর সময় active হয়\n"
        f"  🔁 চেক           : প্রতি ৫ সেকেন্ডে BD সময় দেখা হয় "
        f"(grace {SLOT_GRACE_SECONDS}s)\n"
        f"{'='*60}"
    )

    while True:
        try:
            now      = datetime.now(DHAKA_TZ)
            today    = now.strftime("%Y-%m-%d")
            today_schedule = schedule_for(now)

            # নতুন দিন শুরু হলে in-memory set রিফ্রেশ করো
            # (ফাইলে ইতিমধ্যে আগের দিনের slot নেই — _prune_slots মুছে দিয়েছে)
            if not any(s.startswith(today) for s in fired) and fired:
                fired = _prune_slots(fired)

            # Exact minute-এর বদলে grace window-এ চেক করি, যাতে ৩০–৬০
            # সেকেন্ড দেরিতে scheduler জাগলেও post মিস না হয়।
            slot_key = _scheduled_slot_for(now, today_schedule)
            if slot_key and slot_key not in fired:
                # ── সাথে সাথে slot mark করো → rapid restart-এও দ্বিতীয়বার চলবে না
                fired.add(slot_key)
                _persist_slot(slot_key)
                logger.info(
                    f"⏰ {now.strftime('%I:%M:%S %p')} BD — scheduled! "
                    "→ job চালু হচ্ছে"
                )
                Thread(target=_run_refresh_sync, daemon=True).start()

        except Exception as e:
            logger.error(f"❌ clock scheduler error: {e}")

        time.sleep(5)


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
