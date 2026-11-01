"""
╔══════════════════════════════════════════════════════════════════╗
║           AUTO POST REFRESHER — USER SESSION MODE (CHAIN CHANNELS)              ║
╚══════════════════════════════════════════════════════════════════╝

  ✅ নির্ধারিত সময়ে Account connect হয়, কাজ শেষে disconnect।
     সারাদিন Account active থাকে না

  📌 CHANNEL_USERNAME কীভাবে পাবেন?
     Telegram-এ চ্যানেলে যান → Info → Username (t.me/xxxxx)
     শুধু "xxxxx" অংশটুকু দিন (@ ছাড়া)।
     Username না থাকলে CHANNEL_ID দিয়ে রাখুন, বট নিজে খুঁজে নেবে।
"""

# ====================================================================
#                   ⚙️  CONFIGURATION  ⚙️
#         (শুধু এই অংশ পরিবর্তন করুন — বাকি কোডে হাত দেবেন না)
# ====================================================================

# 🔑 Telegram Credentials (https://my.telegram.org) #pygram session এটা
API_ID         = 37001641
API_HASH       = "75aaefa6b305facc4745d25eb1fcf9f4"
SESSION_STRING = "BQIIe4IACV5OFLbJbrFHblh0B_FxkoHnRqpRbA0DmRrA60bXiRSSfjDNdx_Omep9gx8XaPVDlYegTNkWQMyJDirX8tAYgJgUZ8NkmJXHIlATJ_GKuShfS_OWUhiPYrLELv0PiYfnKpXVSNv3iER1JFBpEJQY7QyFtjUyhxbuokk2BsDT5Z-B4cm-hJDa6HpBktJs4cUmGEvP0hi8PIACb-MADKuiBEpRg8VB79KSrvUEN2XWTksfizA-Ea2nMB_EcT19e47fyKCRLiof82aPLuVmBdwQyZE5C5UKXYJFIWYEvchGLJPKw7CilwZJ71FOX8VvrVnIxj5gWsLLX_gm64ucnp65HQAAAAISgrD2AA"

# 📢 Channel সনাক্তকরণ
#    Username থাকলে username দিন (@ ছাড়া), না থাকলে "" রাখুন
CHANNEL_USERNAME = "ALQalam365"          # অথবা "" ফাঁকা রাখুন
CHANNEL_ID       = -1003797236998       # Channel ID (backup হিসেবে)

# 📢 Chain channels — ক্রমানুসারে Source → Target 1 → Target 2 → Target 3
# Target 1-এর schedule না দিলে পুরনো SCHEDULE_TIMES / FRIDAY_SCHEDULE_TIMES
# ব্যবহার হবে। পরের target-গুলোর schedule আলাদা করে দিন।
# প্রতিটি target আগের channel-এর tagged পুরনো post থেকে নেবে।
# approval_enabled=True হলে ওই channel-এর pending join request approve হবে।
TARGET_CHANNELS = [
    {
        "name": "Target 1",
        "username": "Islamic_Stor",
        "auto_username_tags": True,
        "id": -1003704917412,
        "legacy_search_tags": "#IslamicStore",  # পুরনো post খোঁজার জন্য; নতুন caption-এ যাবে না
        "schedule_times": None,          # None = SCHEDULE_TIMES ব্যবহার
        "friday_schedule_times": None,  # None = FRIDAY_SCHEDULE_TIMES ব্যবহার
        "approval_enabled": True,
        "join_requests_per_run": 60,
    },
    # নতুন channel যোগ করতে নিচের block copy করে values দিন।
    # Target 2-এর source হবে Target 1; Target 3-এর source হবে Target 2।
    # {
    #     "name": "Target 2",
    #     "username": "YOUR_TARGET_2_USERNAME",
    #     "id": -1001234567890,
    #     "auto_username_tags": True,  # resolved chat-এর actual username থেকে tag
    #     "schedule_times": [("06:00", "PM")],
    #     "friday_schedule_times": [("07:00", "PM")],
    #     "approval_enabled": False,
    #     "join_requests_per_run": 60,
    # },
]

# 🏷️ Channel tag automation
# নতুন caption-এর hashtag/@username প্রতিবার Telegram থেকে resolved actual
# channel username দেখে তৈরি হবে; নিচে আলাদা tag name লেখার দরকার নেই।
# Legacy search tag শুধু পুরনো Source posts খুঁজতে ব্যবহৃত হয়; নতুন caption-এ যায় না।
SOURCE_SEARCH_TAGS = "#ALQalamBD"
SOURCE_CAPTION_TAGS = ""
# Friday marker chain-এর Friday post চিনতে সাহায্য করে; এটি channel handle নয়।
FRIDAY_SOURCE_CAPTION_TAGS = "#Jumuah_Mubarak"

# JOIN_REQUESTS_PER_RUN হলো channel-specific limit না দিলে ব্যবহৃত legacy default;
# approval_enabled=True/False দিয়ে প্রতিটি target-এর approval চালু/বন্ধ করুন।
JOIN_REQUESTS_PER_RUN = 60

# ⏰ Auto Refresh সময়সূচি (বাংলাদেশ সময় — ১২ ঘণ্টা AM/PM)
#
#    ফরম্যাট: ("ঘণ্টা:মিনিট", "AM/PM")
#
#    উদাহরণ:
#      ("6:00",  "AM")  →  ভোর ৬:০০
#    এই root schedule Target 1-এর fallback; Target 2+ এর schedule
#    TARGET_CHANNELS-এর প্রতিটি channel object-এ আলাদা করে দিন।
#
#    ✅ যত খুশি লাইন যোগ করুন — কোনো সীমা নেই
# ---------------------------------------------------------------
SCHEDULE_TIMES = [
      ("12:00", "AM"),
      ("03:45", "AM"),
      ("09:45", "AM"),
    # ("11:11", "AM"),
    # ("03:45", "PM"),
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
        ("12:00", "AM"),
      # ("03:45", "AM"),
        ("08:30", "AM"),
      # ("11:45", "AM"),
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
import json
import os
import re
import pytz
from datetime import datetime
from threading import Thread, Lock

# Python 3.12+ fix: event loop must exist before Pyrogram loads
try:
    asyncio.get_event_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())

import time
from flask import Flask
from pyrogram import Client, enums
from pyrogram.types import MessageEntity
from pyrogram.errors import FloodWait, MessageDeleteForbidden, MessageIdInvalid

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

DHAKA_TZ    = pytz.timezone("Asia/Dhaka")
JUMUAH_TAGS = {"#jumuah", "#jumah"}
# এই file-টি deploy/restart-এর পরও রেখে দিন; এতে আগের channel usernames থাকে।
_USERNAME_HISTORY_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "channel_username_history.json"
)


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
    """Caption-এর পুরনো hashtag এবং paired @mention সরিয়ে মূল লেখা রাখে।"""
    # আগে তৈরি করা "#Tag , @Tag" জোড়া একসাথে সরাই, unrelated @mention নয়।
    base = re.sub(
        r"(?<!\w)#[^\s#]+\s*,\s*@[A-Za-z0-9_]+", "", caption or ""
    )
    base = re.sub(r"(?<!\w)#[^\s#]+", "", base)
    base = re.sub(r"[ \t]+\n", "\n", base)
    return re.sub(r"\n{3,}", "\n\n", base).strip()


def caption_with_tags(caption: str, tag_config: str) -> str:
    """Caption-এর শেষে প্রতিটি tag-কে #Tag , @Tag pair হিসেবে যোগ করে।"""
    base = caption_without_tags(caption)
    paired_tags = " ".join(
        f"{tag} , @{tag[1:]}" for tag in parse_tags(tag_config)
    )
    if base and paired_tags:
        return f"{base}\n\n{paired_tags}"
    return base or paired_tags


# ── Fired-slot tracker (restart-proof) ────────────────────────────
# "YYYY-MM-DD HH:MM" ফরম্যাটে চলে-যাওয়া slot ফাইলে রাখে।
# Restart হলেও ফাইল টিকে থাকে → একই মিনিটে দুবার চলবে না।
_SLOTS_FILE = "fired_slots.txt"
# A short grace window prevents a scheduled run being lost when the
# scheduler wakes a few seconds late after a restart/deploy.
SLOT_GRACE_SECONDS = 90
_REFRESH_LOCK = Lock()

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

def _edge_schedule(target_index: int, now=None):
    """Target schedule None হলে legacy root schedule/fallback বজায় রাখে."""
    current = now or datetime.now(DHAKA_TZ)
    config = TARGET_CHANNELS[target_index]
    if current.weekday() == 4:
        friday = config.get("friday_schedule_times")
        if friday is None:
            friday = FRIDAY_SCHEDULE_TIMES
        if friday:
            return friday
    regular = config.get("schedule_times")
    return SCHEDULE_TIMES if regular is None else regular


def _edge_slot_key(target_index: int, slot_time: str) -> str:
    return f"{target_index}|{slot_time}"


def _prefill_past_slots(fired: set) -> set:
    """প্রতিটি chain edge-এর আজকের grace window পেরোনো slot skip করে।"""
    now = datetime.now(DHAKA_TZ)
    today = now.strftime("%Y-%m-%d")
    for index in range(len(TARGET_CHANNELS)):
        for ts, period in _edge_schedule(index, now):
            h, m = parse_ampm(ts, period)
            scheduled_at = now.replace(hour=h, minute=m, second=0, microsecond=0)
            if (now - scheduled_at).total_seconds() > SLOT_GRACE_SECONDS:
                key = _edge_slot_key(index, f"{today} {h:02d}:{m:02d}")
                if key not in fired:
                    fired.add(key)
                    _persist_slot(key)
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
    """Channel ID-কে স্থায়ী identity ধরে username resolve/fallback করে।"""
    if CHANNEL_USERNAME:
        try:
            chat = await client.get_chat(CHANNEL_USERNAME)
            if CHANNEL_ID is None or int(chat.id) == int(CHANNEL_ID):
                logger.info(f"📢 Source: {chat.title} (id={chat.id})")
                return chat.id
            logger.warning(
                f"⚠️ Configured Source username এখন অন্য chat-এ resolve হয়েছে "
                f"(id={chat.id}); নিরাপত্তার জন্য ID={CHANNEL_ID} fallback হবে"
            )
        except Exception as e:
            logger.warning(f"⚠️ Source username resolve হয়নি: {e} — ID fallback চেষ্টা করছি...")

    async for dialog in client.get_dialogs():
        if CHANNEL_ID is not None and int(dialog.chat.id) == int(CHANNEL_ID):
            logger.info(f"📢 Source ID থেকে পাওয়া: {dialog.chat.title}")
            return dialog.chat.id
    raise RuntimeError(f"Source channel পাওয়া যায়নি (ID={CHANNEL_ID}, Username={CHANNEL_USERNAME})")


async def resolve_configured_channel(client: Client, channel_config: dict):
    """Configured ID verify করে; username বদলালে dialog ID দিয়ে channel খুঁজে।"""
    username = (channel_config.get("username") or "").strip().lstrip("@")
    channel_id = channel_config.get("id")
    if username:
        try:
            chat = await client.get_chat(username)
            if channel_id is None or int(chat.id) == int(channel_id):
                logger.info(f"📢 {channel_config.get('name', 'Channel')}: {chat.title} (id={chat.id})")
                return chat
            logger.warning(
                f"⚠️ {channel_config.get('name', 'Channel')} username অন্য chat-এ গেছে "
                f"(id={chat.id}); ID={channel_id} দিয়ে resolve হবে"
            )
        except Exception as e:
            logger.warning(f"⚠️ {channel_config.get('name', 'Channel')} username resolve হয়নি: {e}")
    async for dialog in client.get_dialogs():
        if channel_id is not None and int(dialog.chat.id) == int(channel_id):
            logger.info(f"📢 {channel_config.get('name', 'Channel')} ID থেকে পাওয়া: {dialog.chat.title}")
            return dialog.chat
    raise RuntimeError(
        f"Channel পাওয়া যায়নি ({channel_config.get('name')}, ID={channel_id}, Username={username})"
    )


def remember_channel_usernames(chat, configured_username: str = None) -> list:
    """Stable chat ID অনুযায়ী configured, previous ও current usernames সংরক্ষণ করে."""
    chat_key = str(int(chat.id))
    history = {}
    try:
        with open(_USERNAME_HISTORY_FILE, encoding="utf-8") as f:
            loaded = json.load(f)
            if isinstance(loaded, dict):
                history = loaded
    except FileNotFoundError:
        pass
    except Exception as e:
        logger.warning(f"⚠️ Username history পড়া যায়নি: {e}")

    names = list(history.get(chat_key, []))
    for value in (configured_username, getattr(chat, "username", None)):
        name = (value or "").strip().lstrip("@")
        if name and re.fullmatch(r"[A-Za-z0-9_]+", name) and name not in names:
            names.append(name)
    names = names[-20:]
    history[chat_key] = names
    try:
        temp_path = _USERNAME_HISTORY_FILE + ".tmp"
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
        os.replace(temp_path, _USERNAME_HISTORY_FILE)
    except Exception as e:
        logger.warning(f"⚠️ Username history সেভ হয়নি: {e}")
    return names


async def approve_target_join_requests(client: Client, target_channel_id: int, limit: int) -> int:
    """Pending join request থেকে configured limit পর্যন্ত approve করে।"""
    approved = 0
    try:
        async for request in client.get_chat_join_requests(
            target_channel_id,
            limit=limit,
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
        f"👥 Target channel join approval: {approved}/{limit}"
    )
    return approved


def channel_tag_config(
    channel_config: dict, is_friday: bool, actual_username: str = None
) -> str:
    """Resolved Telegram username-কে এই channel-এর hashtag হিসেবে ফেরত দেয়."""
    username = (actual_username or "").strip().lstrip("@")
    if channel_config.get("auto_username_tags", True) and re.fullmatch(r"[A-Za-z0-9_]+", username):
        return f"#{username}"
    if channel_config.get("is_source"):
        return FRIDAY_SOURCE_CAPTION_TAGS if is_friday else SOURCE_CAPTION_TAGS
    return (
        channel_config.get("friday_caption_tags", "")
        if is_friday else channel_config.get("caption_tags", "")
    )


def _utf16_length(value: str) -> int:
    return len(value.encode("utf-16-le")) // 2


def channel_caption_payload(
    caption: str,
    channel_config: dict,
    is_friday: bool,
    actual_username: str = None,
):
    """Caption text এবং শুধু channel handle pair-এর bold entity তৈরি করে."""
    username = (actual_username or "").strip().lstrip("@")
    auto_handle = bool(
        channel_config.get("auto_username_tags", True)
        and re.fullmatch(r"[A-Za-z0-9_]+", username)
    )
    tag_config = channel_tag_config(channel_config, is_friday, username)
    pairs = [f"{tag} , @{tag[1:]}" for tag in parse_tags(tag_config)]
    pair_text = " ".join(pairs)
    marker_tags = []
    if is_friday and auto_handle:
        marker_config = channel_config.get(
            "friday_marker_tags", FRIDAY_SOURCE_CAPTION_TAGS
        )
        marker_tags = parse_tags(marker_config)

    base = caption_without_tags(caption)
    body_parts = marker_tags + ([pair_text] if pair_text else [])
    body = " ".join(body_parts)
    prefix = base + ("\n\n" if base and body else "")
    rendered = prefix + body

    entities = []
    if pair_text:
        bold_prefix = prefix
        if marker_tags:
            bold_prefix += " ".join(marker_tags) + " "
        entities.append(MessageEntity(
            type=enums.MessageEntityType.BOLD,
            offset=_utf16_length(bold_prefix),
            length=_utf16_length(pair_text),
        ))
    return rendered, entities


def channel_caption(caption: str, channel_config: dict, is_friday: bool) -> str:
    """Compatibility helper; scheduled posts use channel_caption_payload."""
    text, _ = channel_caption_payload(caption, channel_config, is_friday)
    return text


def bold_tag_entities(caption: str, tag_config: str) -> list:
    """Legacy helper; offset is correct whether or not the caption has body text."""
    base = caption_without_tags(caption)
    pairs = " ".join(f"{tag} , @{tag[1:]}" for tag in parse_tags(tag_config))
    if not pairs:
        return []
    prefix = base + ("\n\n" if base else "")
    return [MessageEntity(
        type=enums.MessageEntityType.BOLD,
        offset=_utf16_length(prefix),
        length=_utf16_length(pairs),
    )]


def configured_search_tags(
    channel_config: dict, is_friday: bool, actual_username: str = None,
    known_usernames=None,
) -> list:
    """Channel-এর বর্তমান username tag ও প্রয়োজনীয় legacy marker মিলিয়ে দেয়."""
    values = []
    username = (actual_username or "").strip().lstrip("@")
    if re.fullmatch(r"[A-Za-z0-9_]+", username):
        values.append(f"#{username}")
    for old_name in known_usernames or []:
        if re.fullmatch(r"[A-Za-z0-9_]+", old_name):
            values.append(f"#{old_name}")
    if channel_config.get("is_source"):
        values.extend([SOURCE_SEARCH_TAGS, FRIDAY_SOURCE_CAPTION_TAGS if is_friday else ""])
    else:
        values.extend([
            channel_config.get("search_tags", ""),
            channel_config.get("legacy_search_tags", ""),
        ])
        if is_friday:
            values.append(channel_config.get("friday_marker_tags", FRIDAY_SOURCE_CAPTION_TAGS))
    tags = []
    seen = set()
    for value in values:
        for tag in parse_tags(value):
            key = tag.casefold()
            if key not in seen:
                tags.append(tag)
                seen.add(key)
    return tags


def channel_post_is_eligible(
    caption: str, channel_config: dict, is_friday: bool,
    actual_username: str = None, known_usernames=None,
) -> bool:
    text_value = (caption or "").casefold()
    tags = configured_search_tags(
        channel_config, is_friday, actual_username, known_usernames
    )
    has_channel_tag = any(tag.casefold() in text_value for tag in tags)
    if is_friday:
        return has_channel_tag and any(tag in text_value for tag in JUMUAH_TAGS)
    return has_channel_tag and not any(tag in text_value for tag in JUMUAH_TAGS)


async def copy_to_target_with_caption(
    client: Client,
    target_channel_id: int,
    source_channel_id: int,
    message,
    caption: str,
    caption_entities=None,
):
    """Target-এ caption এবং নির্বাচিত Telegram formatting entity সহ copy করে।"""
    if getattr(message, "media", None):
        return await client.copy_message(
            chat_id=target_channel_id,
            from_chat_id=source_channel_id,
            message_id=message.id,
            caption=caption,
            caption_entities=caption_entities,
            parse_mode=None,
        )
    return await client.send_message(
        chat_id=target_channel_id,
        text=caption,
        entities=caption_entities,
        parse_mode=None,
    )


async def copy_to_source_with_caption(
    client: Client,
    source_channel_id: int,
    message,
    caption: str,
    caption_entities=None,
):
    """Upstream-এ caption এবং নির্বাচিত Telegram formatting entity সহ copy করে।"""
    if getattr(message, "media", None):
        return await client.copy_message(
            chat_id=source_channel_id,
            from_chat_id=source_channel_id,
            message_id=message.id,
            caption=caption,
            caption_entities=caption_entities,
            parse_mode=None,
        )
    return await client.send_message(
        chat_id=source_channel_id,
        text=caption,
        entities=caption_entities,
        parse_mode=None,
    )


async def delete_previous_friday_target_posts(
    client: Client,
    target_channel_id: int,
    current_friday,
    keep_message_ids=None,
    friday_tag_config: str = FRIDAY_SOURCE_CAPTION_TAGS,
) -> int:
    """
    Target channel থেকে শুধু আজকের আগের দিনের Friday-tagged post মুছে।
    Friday tags exact hashtag হিসেবে মিলবে; আজকের post ও অন্য tag-এর post থাকবে।
    """
    friday_tags = {
        tag.casefold() for tag in parse_tags(friday_tag_config)
    }
    if not friday_tags:
        logger.warning(
            "শুক্রবারের target tag সেট নেই — পুরনো Friday post delete করা হয়নি"
        )
        return 0

    keep_message_ids = set(keep_message_ids or ())
    hashtag_pattern = re.compile(r"(?<![\w])#[\w]+", flags=re.UNICODE)
    old_message_ids = []

    try:
        async for msg in client.get_chat_history(target_channel_id):
            if (
                msg.date is None
                or getattr(msg, "service", False)
                or getattr(msg, "empty", False)
                or msg.id in keep_message_ids
            ):
                continue

            msg_date = msg.date
            if msg_date.tzinfo is None:
                msg_date = pytz.UTC.localize(msg_date)
            if msg_date.astimezone(DHAKA_TZ).date() >= current_friday:
                continue

            text = msg.caption or msg.text or ""
            message_tags = {
                tag.casefold() for tag in hashtag_pattern.findall(text)
            }
            if message_tags & friday_tags:
                old_message_ids.append(msg.id)
    except Exception as scan_err:
        logger.error(
            f"Target-এর পুরনো Friday post খোঁজা যায়নি: "
            f"{type(scan_err).__name__}: {scan_err}"
        )
        return 0

    if not old_message_ids:
        logger.info("Target-এ আগের দিনের কোনো Friday-tagged post পাওয়া যায়নি")
        return 0

    deleted_count = 0
    # Telegram bulk delete-এ ছোট batch ব্যবহার করি; কোনো batch ব্যর্থ হলে
    # বাকি ID-গুলো এককভাবে চেষ্টা করা হবে।
    for start in range(0, len(old_message_ids), 100):
        batch = old_message_ids[start:start + 100]
        try:
            result = await client.delete_messages(target_channel_id, batch)
            deleted_count += int(result or 0)
            logger.info(
                f"Target-এর পুরনো Friday post delete: "
                f"{len(batch)}টি ID, Telegram result={result}"
            )
            continue
        except FloodWait as e:
            logger.warning(f"Friday post delete FloodWait {e.value}s")
            await asyncio.sleep(e.value + 1)
            try:
                result = await client.delete_messages(target_channel_id, batch)
                deleted_count += int(result or 0)
                logger.info(
                    f"FloodWait-এর পর target Friday post delete: "
                    f"{len(batch)}টি ID, Telegram result={result}"
                )
                continue
            except Exception as retry_err:
                logger.warning(
                    f"Batch retry ব্যর্থ; এককভাবে delete চেষ্টা হবে: {retry_err}"
                )
        except Exception as batch_err:
            logger.warning(
                f"Friday post batch delete ব্যর্থ; এককভাবে চেষ্টা হবে: {batch_err}"
            )

        for message_id in batch:
            try:
                result = await client.delete_messages(
                    target_channel_id, message_id
                )
                deleted_count += int(result or 0)
            except FloodWait as e:
                logger.warning(
                    f"একটি Friday post delete FloodWait {e.value}s; অপেক্ষা করে retry"
                )
                await asyncio.sleep(e.value + 1)
                try:
                    result = await client.delete_messages(
                        target_channel_id, message_id
                    )
                    deleted_count += int(result or 0)
                except Exception as retry_err:
                    logger.warning(
                        f"Target message {message_id} delete retry ব্যর্থ: {retry_err}"
                    )
            except (MessageDeleteForbidden, MessageIdInvalid) as delete_err:
                logger.warning(
                    f"Target message {message_id} delete করা যায়নি: {delete_err}"
                )
            except Exception as delete_err:
                logger.warning(
                    f"Target message {message_id} delete ব্যর্থ: {delete_err}"
                )

    logger.info(
        f"Target-এর আগের Friday-tagged post delete সম্পন্ন: "
        f"{deleted_count}/{len(old_message_ids)}"
    )
    return deleted_count


# ── একটি Refresh চক্র: connect → কাজ → disconnect ─────────────────
async def run_refresh(target_index: int = 0):
    """একটি chain edge চালায়: upstream → target; পুরনো order বজায় থাকে।"""
    if not TARGET_CHANNELS:
        logger.error("❌ TARGET_CHANNELS খালি — কোনো destination configured নেই")
        return
    if target_index < 0 or target_index >= len(TARGET_CHANNELS):
        logger.error(f"❌ ভুল target index: {target_index}")
        return

    now = datetime.now(DHAKA_TZ)
    is_friday = now.weekday() == 4
    target_config = TARGET_CHANNELS[target_index]
    upstream_config = (
        {"name": "Source", "username": CHANNEL_USERNAME, "id": CHANNEL_ID,
         "is_source": True, "auto_username_tags": True,
         "caption_tags": SOURCE_CAPTION_TAGS,
         "friday_caption_tags": FRIDAY_SOURCE_CAPTION_TAGS}
        if target_index == 0 else TARGET_CHANNELS[target_index - 1]
    )
    target_name = target_config.get("name", f"Target {target_index + 1}")
    logger.info(
        f"\n{'='*56}\n  🔄 Chain refresh: {upstream_config.get('name')} → {target_name}\n"
        f"  ⏰ {now.strftime('%I:%M %p')} (BD) | {'শুক্রবার' if is_friday else now.strftime('%A')}\n"
        f"{'='*56}"
    )

    client = Client(
        name="refresher", api_id=API_ID, api_hash=API_HASH,
        session_string=SESSION_STRING,
    )
    refreshed = 0
    try:
        await client.start()
        me = await client.get_me()
        logger.info(f"🔗 Account: {me.first_name} (@{me.username})")

        if target_index == 0:
            upstream_id = await resolve_channel(client)
            upstream_chat = await client.get_chat(upstream_id)
        else:
            upstream_chat = await resolve_configured_channel(client, upstream_config)
            upstream_id = upstream_chat.id
        target_chat = await resolve_configured_channel(client, target_config)
        target_id = target_chat.id
        upstream_usernames = remember_channel_usernames(
            upstream_chat,
            CHANNEL_USERNAME if target_index == 0 else upstream_config.get("username"),
        )
        target_usernames = remember_channel_usernames(
            target_chat, target_config.get("username")
        )
        if not getattr(upstream_chat, "username", None):
            logger.warning(
                f"⚠️ {upstream_config.get('name')} channel-এ public username নেই; "
                "automatic #tag/@username তৈরি করা যাবে না"
            )
        if not getattr(target_chat, "username", None):
            logger.warning(
                f"⚠️ {target_name} channel-এ public username নেই; "
                "automatic #tag/@username তৈরি করা যাবে না"
            )

        oldest_candidate = None
        matched_kind = "configured chain tag"
        async for msg in client.get_chat_history(upstream_id):
            if msg.date is None or getattr(msg, "service", False) or getattr(msg, "empty", False):
                continue
            caption = msg.caption or msg.text or ""
            if channel_post_is_eligible(
                caption, upstream_config, is_friday,
                getattr(upstream_chat, "username", None),
                upstream_usernames,
            ):
                oldest_candidate = (msg, caption)

        if oldest_candidate is None:
            logger.info(f"ℹ️ {upstream_config.get('name')} channel-এ উপযুক্ত tagged post নেই")
        else:
            msg, caption = oldest_candidate
            old_id = msg.id
            logger.info(f"🎯 {upstream_config.get('name')} থেকে oldest post id={old_id} নির্বাচিত")
            upstream_new = None
            try:
                upstream_caption, upstream_entities = channel_caption_payload(
                    caption, upstream_config, is_friday,
                    getattr(upstream_chat, "username", None),
                )
                upstream_new = await copy_to_source_with_caption(
                    client, upstream_id, msg, upstream_caption,
                    caption_entities=upstream_entities,
                )
                logger.info(f"✅ {upstream_config.get('name')} refreshed copy → {upstream_new.id}")
                target_caption_text, target_entities = channel_caption_payload(
                    caption, target_config, is_friday,
                    getattr(target_chat, "username", None),
                )
                target_new = await copy_to_target_with_caption(
                    client, target_id, upstream_id, msg, target_caption_text,
                    caption_entities=target_entities,
                )
                logger.info(f"✅ {target_name} copy → {target_new.id}")

                if is_friday:
                    friday_tags = target_config.get(
                        "friday_marker_tags", FRIDAY_SOURCE_CAPTION_TAGS
                    )
                    deleted = await delete_previous_friday_target_posts(
                        client, target_id, now.date(),
                        keep_message_ids={target_new.id},
                        friday_tag_config=target_config.get(
                            "friday_marker_tags", FRIDAY_SOURCE_CAPTION_TAGS
                        ),
                    )
                    logger.info(f"🕌 {target_name}: আগের Friday post delete {deleted}টি")
            except Exception as copy_err:
                logger.error(
                    f"❌ {target_name} chain copy ব্যর্থ: {type(copy_err).__name__}: {copy_err!r}; "
                    "upstream পুরনো post delete হবে না"
                )
                if upstream_new is not None:
                    try:
                        await client.delete_messages(upstream_id, upstream_new.id)
                        logger.info(f"↩️ অসম্পূর্ণ upstream copy rollback → {upstream_new.id}")
                    except Exception as rollback_err:
                        logger.error(f"❌ upstream rollback ব্যর্থ: {rollback_err}")
            else:
                await asyncio.sleep(1.5)
                try:
                    await client.delete_messages(upstream_id, old_id)
                    logger.info(f"🗑️ {upstream_config.get('name')} পুরনো post delete → {old_id}")
                except FloodWait as e:
                    await asyncio.sleep(e.value + 1)
                    await client.delete_messages(upstream_id, old_id)
                except Exception as del_err:
                    logger.error(f"❌ upstream পুরনো post delete ব্যর্থ: {del_err}")
                refreshed += 1

        approval_enabled = bool(target_config.get("approval_enabled", False))
        approval_limit = int(target_config.get("join_requests_per_run", JOIN_REQUESTS_PER_RUN))
        if approval_enabled and approval_limit > 0:
            await approve_target_join_requests(client, target_id, approval_limit)
        else:
            logger.info(f"👥 {target_name} join-request approval বন্ধ")
    except FloodWait as e:
        logger.warning(f"⏳ FloodWait {e.value}s — পরবর্তী scheduled run-এ চেষ্টা হবে")
        await asyncio.sleep(e.value)
    except Exception as e:
        logger.error(f"❌ Chain refresh ব্যর্থ ({target_name}): {type(e).__name__}: {e}")
    finally:
        try:
            await client.stop()
        except Exception:
            pass
        logger.info(f"🔌 Account disconnect | {target_name}: {refreshed}টি post chain হয়েছে")


# ── Flask keep-alive (Render free tier) ────────────────────────────
flask_app = Flask(__name__)

@flask_app.route("/")
def home():
    now = datetime.now(DHAKA_TZ).strftime("%Y-%m-%d %I:%M %p")
    chain_rows = [f"<li>Source → {TARGET_CHANNELS[0].get('name', 'Target 1')}</li>"] if TARGET_CHANNELS else []
    for i in range(1, len(TARGET_CHANNELS)):
        chain_rows.append(f"<li>{TARGET_CHANNELS[i-1].get('name', f'Target {i}')} → {TARGET_CHANNELS[i].get('name', f'Target {i+1}')}</li>")
    return (
        "<h2>✅ Auto Post Refresher চলছে</h2>"
        f"<p>বাংলাদেশ সময়: <b>{now}</b></p>"
        "<p>Chain: Source → Target 1 → Target 2 → …</p>"
        f"<ol>{''.join(chain_rows)}</ol>"
        f"<p>Root schedule: {', '.join(format_schedule(SCHEDULE_TIMES)) or '(নেই)'}</p>"
        f"<p>Friday root schedule: {', '.join(format_schedule(FRIDAY_SCHEDULE_TIMES)) or 'সাধারণ schedule fallback'}</p>"
        "<p>প্রতিটি caption tag pair আকারে যাবে: #Tag , @Tag</p>"
        "<p>Target-এর schedule None হলে প্রথম Target-এর জন্য root schedule ব্যবহৃত হবে।</p>"
    )


def run_flask():
    port = int(os.environ.get("PORT", 8080))
    try:
        flask_app.run(host="0.0.0.0", port=port, use_reloader=False)
    except OSError:
        flask_app.run(host="0.0.0.0", port=8090, use_reloader=False)


# ── Sync wrapper — clock thread থেকে async চালায় ──────────────────
def _run_refresh_sync(target_index: int):
    """একটি chain edge serialized async job হিসেবে চালায়।"""
    logger.info(f"⏰ Chain edge {target_index + 1} scheduled → Refresh শুরু")
    try:
        with _REFRESH_LOCK:
            asyncio.run(run_refresh(target_index))
    except Exception as e:
        logger.error(f"❌ _run_refresh_sync error: {e}")


def _clock_scheduler():
    """প্রতি ৫ সেকেন্ডে প্রতিটি target-এর নিজস্ব schedule পরীক্ষা করে।"""
    fired = _prune_slots(_load_slots())
    fired = _prefill_past_slots(fired)
    now = datetime.now(DHAKA_TZ)
    logger.info(
        f"\n{'='*60}\n  🤖 Auto Post Refresher সক্রিয়\n"
        f"  📅 বাংলাদেশ সময়: {now.strftime('%Y-%m-%d %I:%M %p')}\n"
        f"  🔗 Chain edges: {len(TARGET_CHANNELS)}\n"
        f"  🔁 প্রতি ৫ সেকেন্ডে schedule check (grace {SLOT_GRACE_SECONDS}s)\n"
        f"{'='*60}"
    )
    while True:
        try:
            now = datetime.now(DHAKA_TZ)
            today = now.strftime("%Y-%m-%d")
            if not any(s.split("|", 1)[-1].startswith(today) for s in fired) and fired:
                fired = _prune_slots(fired)
            for index in range(len(TARGET_CHANNELS)):
                slot_time = _scheduled_slot_for(now, _edge_schedule(index, now))
                if not slot_time:
                    continue
                slot_key = _edge_slot_key(index, slot_time)
                # পুরনো version-এ Target 1 slot edge prefix ছাড়া সেভ হতো;
                # deploy/restart-এর একই minute-এ সেটিকেও fired হিসেবে মানি।
                if slot_key in fired or (index == 0 and slot_time in fired):
                    continue
                fired.add(slot_key)
                _persist_slot(slot_key)
                logger.info(
                    f"⏰ {now.strftime('%I:%M:%S %p')} BD — "
                    f"{TARGET_CHANNELS[index].get('name', f'Target {index+1}')} schedule fired"
                )
                Thread(target=_run_refresh_sync, args=(index,), daemon=True).start()
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
