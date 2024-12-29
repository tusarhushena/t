import asyncio
import platform
import psutil
from sys import version as pyver

from pyrogram import __version__ as pyrover
from pyrogram import filters
from pyrogram.errors import FloodWait, MessageIdInvalid
from pyrogram.types import CallbackQuery, InputMediaPhoto, Message
from pytgcalls.__version__ import __version__ as pytgver

from Bikash import config, YouTube, app
from Bikash.config import BANNED_USERS, MUSIC_BOT_NAME
from Bikash.core.userbot import assistants
from Bikash.misc import SUDOERS, mongodb
from plugins import ALL_MODULES
from Bikash.Bgt import get_command
from Bikash.utils.database import (
    get_global_tops,
    get_particulars,
    get_queries,
    get_served_chats,
    get_served_users,
    get_sudoers,
    get_top_chats,
    get_topp_users,
)
from Bikash.utils.decorators.language import language, languageCB
from Bikash.utils.inline.stats import (
    back_stats_buttons,
    back_stats_markup,
    get_stats_markup,
    overallback_stats_markup,
    stats_buttons,
    top_ten_stats_markup,
)

loop = asyncio.get_running_loop()

# Commands
GSTATS_COMMAND = get_command("GSTATS_COMMAND")
STATS_COMMAND = get_command("STATS_COMMAND")


@app.on_message(filters.command(STATS_COMMAND) & ~BANNED_USERS)
@language
async def stats_global(client, message: Message, _):
    upl = stats_buttons(_, message.from_user.id in SUDOERS)
    await message.reply_photo(
        photo=config.STATS_IMG_URL,
        caption=_["gstats_11"].format(config.MUSIC_BOT_NAME),
        reply_markup=upl,
    )


@app.on_message(filters.command(GSTATS_COMMAND) & ~BANNED_USERS)
@language
async def gstats_global(client, message: Message, _):
    mystic = await message.reply_text(_["gstats_1"])
    stats = await get_global_tops()
    if not stats:
        await asyncio.sleep(1)
        return await mystic.edit(_["gstats_2"])

    async def get_stats():
        results = {}
        for i in stats:
            top_list = stats[i]["spot"]
            results[str(i)] = top_list
        list_arranged = dict(
            sorted(results.items(), key=lambda item: item[1], reverse=True)
        )
        videoid = None
        co = None
        for vidid, count in list_arranged.items():
            if vidid == "telegram":
                continue
            videoid = vidid
            co = count
            break
        return videoid, co

    try:
        videoid, co = await loop.run_in_executor(None, get_stats)
    except Exception as e:
        print(e)
        return
    (
        title,
        duration_min,
        duration_sec,
        thumbnail,
        vidid,
    ) = await YouTube.details(videoid, True)
    title = title.title()
    final = f"**Top Played Track on {app.mention}**\n\n**Title:** {title}\n\nPlayed: **{co}** times"
    upl = get_stats_markup(_, message.from_user.id in SUDOERS)
    try:
        await app.send_photo(
            message.chat.id,
            photo=thumbnail,
            caption=final,
            reply_markup=upl,
        )
    except FloodWait as e:
        asyncio.sleep(e.value)
    await mystic.delete()


@app.on_callback_query(filters.regex("GetStatsNow") & ~BANNED_USERS)
@languageCB
async def top_users_ten(client, CallbackQuery: CallbackQuery, _):
    await CallbackQuery.answer()
    mystic = await CallbackQuery.edit_message_text(
        _["gstats_3"].format(
            f"of {CallbackQuery.message.chat.title}" if "Here" else "Global"
        )
    )
    # Implementation here for different cases
    # Follow the same structure used in the `gstats_global` function


@app.on_callback_query(filters.regex("TopOverall") & ~BANNED_USERS)
@languageCB
async def overall_stats(client, CallbackQuery, _):
    await CallbackQuery.answer()
    served_chats = len(await get_served_chats())
    served_users = len(await get_served_users())
    total_queries = await get_queries()
    blocked = len(BANNED_USERS)
    sudoers = len(SUDOERS)
    mod = len(ALL_MODULES)
    assistant = len(assistants)
    playlist_limit = config.SERVER_PLAYLIST_LIMIT
    fetch_playlist = config.PLAYLIST_FETCH_LIMIT
    song = config.SONG_DOWNLOAD_DURATION
    play_duration = config.DURATION_LIMIT_MIN
    auto_leave = "Yes" if config.AUTO_LEAVING_ASSISTANT else "No"

    # Safely await any asyncio.Future object here if needed.
    # Example:
    # datasize_call = some_async_function()
    # data_size = await datasize_call

    text = f"""**Bot Stats:**

**Modules:** {mod}
**Chats Served:** {served_chats}
**Users Served:** {served_users}
**Blocked Users:** {blocked}
**Sudo Users:** {sudoers}

**Total Queries:** {total_queries}
**Assistants:** {assistant}
**Auto Leaving Assistants:** {auto_leave}

**Play Duration Limit:** {play_duration} mins
**Song Download Limit:** {song} mins
**Server Playlist Limit:** {playlist_limit}
**Playlist Fetch Limit:** {fetch_playlist}
"""
    med = InputMediaPhoto(media=config.STATS_IMG_URL, caption=text)
    try:
        await CallbackQuery.edit_message_media(media=med, reply_markup=overallback_stats_markup(_))
    except MessageIdInvalid:
        await CallbackQuery.message.reply_photo(
            photo=config.STATS_IMG_URL, caption=text, reply_markup=overallback_stats_markup(_)
        )


# Add other functions following the same pattern as necessary.


@app.on_callback_query(filters.regex("bot_stats_sudo"))
@languageCB
async def overall_stats(client, CallbackQuery, _):
    if CallbackQuery.from_user.id not in SUDOERS:
        return await CallbackQuery.answer("ᴏɴʟʏ ғᴏʀ sᴜᴅᴏ ᴜsᴇʀ's", show_alert=True)
    callback_data = CallbackQuery.data.strip()
    what = callback_data.split(None, 1)[1]
    if what != "s":
        upl = overallback_stats_markup(_)
    else:
        upl = back_stats_buttons(_)
    try:
        await CallbackQuery.answer()
    except:
        pass
    await CallbackQuery.edit_message_text(_["gstats_8"])
    sc = platform.system()
    p_core = psutil.cpu_count(logical=False)
    t_core = psutil.cpu_count(logical=True)
    ram = str(round(psutil.virtual_memory().total / (1024.0**3))) + " GB"
    try:
        cpu_freq = psutil.cpu_freq().current
        if cpu_freq >= 1000:
            cpu_freq = f"{round(cpu_freq / 1000, 2)}GHz"
        else:
            cpu_freq = f"{round(cpu_freq, 2)}MHz"
    except:
        cpu_freq = "Unable to Fetch"
    hdd = psutil.disk_usage("/")
    total = hdd.total / (1024.0**3)
    total = str(total)
    used = hdd.used / (1024.0**3)
    used = str(used)
    free = hdd.free / (1024.0**3)
    free = str(free)
    mod = len(ALL_MODULES)
    db = mongodb
    call = db.command("dbstats")
    datasize = call["dataSize"] / 1024
    datasize = str(datasize)
    storage = call["storageSize"] / 1024
    objects = call["objects"]
    collections = call["collections"]

    served_chats = len(await get_served_chats())
    served_users = len(await get_served_users())
    total_queries = await get_queries()
    blocked = len(BANNED_USERS)
    sudoers = len(await get_sudoers())
    text = f""" **ʙᴏᴛ sᴛᴀᴛ's ᴀɴᴅ ɪɴғᴏʀᴍᴀᴛɪᴏɴ:**

**ɪᴍᴘᴏʀᴛᴇᴅ ᴍᴏᴅᴜʟᴇs:** {mod}
**ᴘʟᴀᴛғᴏʀᴍ:** {sc}
**ʀᴀᴍ:** {ram}
**ᴘʜʏsɪᴄᴀʟ ᴄᴏʀᴇs:** {p_core}
**ᴛᴏᴛᴀʟ ᴄᴏʀᴇs:** {t_core}
**ᴄᴘᴜ ғʀᴇǫᴜᴇɴᴄʏ:** {cpu_freq}

**ᴘʏᴛʜᴏɴ ᴠᴇʀsɪᴏɴ :** {pyver.split()[0]}
**ᴘʏʀᴏɢʀᴀᴍ ᴠᴇʀsɪᴏɴ :** {pyrover}
**Pʏ-TɢCᴀʟʟs ᴠᴇʀsɪᴏɴ :** {pytgver}
**N-Tɢᴄᴀʟʟs ᴠᴇʀsɪᴏɴ :** {ngtgver}
**ᴀᴠᴀɪʟᴀʙʟᴇ sᴛᴏʀᴀɢᴇ :** {total[:4]} ɢiʙ
**sᴛᴏʀᴀɢᴇ ᴜsᴇᴅ:** {used[:4]} ɢiʙ
**sᴛᴏʀᴀɢᴇ ʟᴇғᴛ:** {free[:4]} ɢiʙ

**sᴇʀᴠᴇᴅ ᴄʜᴀᴛs:** {served_chats} 
**sᴇʀᴠᴇᴅ ᴜsᴇʀs:** {served_users} 
**ʙʟᴏᴄᴋᴇᴅ ᴜsᴇʀs:** {blocked} 
**sᴜᴅᴏ ᴜsᴇʀs:** {sudoers} 

**ᴛᴏᴛᴀʟ ᴅʙ sᴛᴏʀᴀɢᴇ:** {storage} ᴍʙ
**ᴛᴏᴛᴀʟ ᴅʙ ᴄᴏʟʟᴇᴄᴛɪᴏɴs:** {collections}
**ᴛᴏᴛᴀʟ ᴅʙ ᴋᴇʏs:** {objects}
**ᴛᴏᴛᴀʟ ʙᴏᴛ ǫᴜᴇʀɪᴇs:** `{total_queries} `
    """
    med = InputMediaPhoto(media=config.STATS_IMG_URL, caption=text)
    try:
        await CallbackQuery.edit_message_media(media=med, reply_markup=upl)
    except MessageIdInvalid:
        await CallbackQuery.message.reply_photo(
            photo=config.STATS_IMG_URL, caption=text, reply_markup=upl
        )


@app.on_callback_query(
    filters.regex(pattern=r"^(TOPMARKUPGET|GETSTATS|GlobalStats)$") & ~BANNED_USERS
)
@languageCB
async def back_buttons(client, CallbackQuery, _):
    try:
        await CallbackQuery.answer()
    except:
        pass
    command = CallbackQuery.matches[0].group(1)
    if command == "TOPMARKUPGET":
        upl = top_ten_stats_markup(_)
        med = InputMediaPhoto(
            media=config.GLOBAL_IMG_URL,
            caption=_["gstats_9"],
        )
        try:
            await CallbackQuery.edit_message_media(media=med, reply_markup=upl)
        except MessageIdInvalid:
            await CallbackQuery.message.reply_photo(
                photo=config.GLOBAL_IMG_URL,
                caption=_["gstats_9"],
                reply_markup=upl,
            )
    if command == "GlobalStats":
        upl = get_stats_markup(
            _,
            True if CallbackQuery.from_user.id in SUDOERS else False,
        )
        med = InputMediaPhoto(
            media=config.GLOBAL_IMG_URL,
            caption=_["gstats_10"].format(app.mention),
        )
        try:
            await CallbackQuery.edit_message_media(media=med, reply_markup=upl)
        except MessageIdInvalid:
            await CallbackQuery.message.reply_photo(
                photo=config.GLOBAL_IMG_URL,
                caption=_["gstats_10"].format(app.mention),
                reply_markup=upl,
            )
    if command == "GETSTATS":
        upl = stats_buttons(
            _,
            True if CallbackQuery.from_user.id in SUDOERS else False,
        )
        med = InputMediaPhoto(
            media=config.STATS_IMG_URL,
            caption=_["gstats_11"].format(app.mention),
        )
        try:
            await CallbackQuery.edit_message_media(media=med, reply_markup=upl)
        except MessageIdInvalid:
            await CallbackQuery.message.reply_photo(
                photo=config.STATS_IMG_URL,
                caption=_["gstats_11"].format(app.mention),
                reply_markup=upl,
        )
