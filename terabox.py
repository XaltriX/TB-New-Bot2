import os
import re
import random
import string
import logging
import asyncio
from bot import Bot
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
from pyrogram import Client, filters
from config import ADMINS, BOT_STATS_TEXT,HELP_TXT, USER_REPLY_TEXT, CHANNEL_ID, VERIFY_LOG_ID, SHORTLINK_API_KEY,  SHORTLINK_API_URL, USE_SHORTLINK, LOG_ID, TUT_VID, VERIFY_EXPIRE, USE_PAYMENT
from datetime import datetime
from helper_func import get_readable_time
from database.database import del_is_first, is_first
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated
from helper_func import subscribed, change_domain, format_duration, get_video_duration, update_url_if_keyword_exists, format_progress_bar, get_verify_status, get_shortlink, update_verify_status, get_exp_time
from video import download_video, upload_video
import pyrogram.utils



@Bot.on_message(filters.text & filters.private & subscribed & ~filters.command(['help','tutorial','logs']))
async def handle_message(client: Client, message: Message):
    user_id = message.from_user.id
    uname = message.from_user.username
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    user_mention = message.from_user.mention
    getted_link = message.text.strip()
    id = user_id
    if USE_SHORTLINK : 
        if id in ADMINS:
            pass
        else:
            verify_status = await get_verify_status(id)
            if not verify_status['is_verified']:
                token = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
                link = await get_shortlink(SHORTLINK_API_URL, SHORTLINK_API_KEY,f'https://telegram.dog/{client.username}?start=verify_{token}')
                await update_verify_status(id, verify_token=token, is_verified=False, link=link)
                if VERIFY_LOG_ID:
                    LOG_MESG = f"Token Is Generated For The User\n\nUser : {first_name} {last_name}\nId : {id}\nUsername : {uname}\n\nToken : <code>{token}</code>\n\nReport By @{client.username}"
                    await client.send_message(chat_id=VERIFY_LOG_ID, text=LOG_MESG)
                if USE_PAYMENT:
                    btn = [
                    [InlineKeyboardButton("ᴄʟɪᴄᴋ ʜᴇʀᴇ", url=link),
                    InlineKeyboardButton('ʜᴏᴡ ᴛᴏ ᴜsᴇ ᴛʜᴇ ʙᴏᴛ', url=TUT_VID)],
                    [InlineKeyboardButton("ʙᴜʏ ᴘʀᴇᴍɪᴜᴍ ᴘʟᴀɴ", callback_data="buy_prem")]
                    ]
                else:
                    btn = [
                    [InlineKeyboardButton("ᴄʟɪᴄᴋ ʜᴇʀᴇ", url=link)],
                    [InlineKeyboardButton('ʜᴏᴡ ᴛᴏ ᴜsᴇ ᴛʜᴇ ʙᴏᴛ', url=TUT_VID)]
                    ]
                await message.reply(f"<b>ʏᴏᴜʀ ᴀᴅs ᴛᴏᴋᴇɴ ɪs ᴇxᴘɪʀᴇᴅ, ʀᴇғʀᴇsʜ ʏᴏᴜʀ ᴛᴏᴋᴇɴ ᴀɴᴅ ᴛʀʏ ᴀɢᴀɪɴ.</b>\n\n<b>ᴛᴏᴋᴇɴ ᴛɪᴍᴇᴏᴜᴛ: {get_exp_time(VERIFY_EXPIRE)}</b>\n\n<b>ᴡʜᴀᴛ ɪs ᴛʜᴇ ᴛᴏᴋᴇɴ? ᴛʜɪs ɪs ᴀɴ ᴀᴅs ᴛᴏᴋᴇɴ. ɪғ ʏᴏᴜ ᴘᴀss 1 ᴀᴅ, ʏᴏᴜ ᴄᴀɴ ᴜsᴇ ᴛʜᴇ ʙᴏᴛ ғᴏʀ {get_exp_time(VERIFY_EXPIRE)} ᴀғᴛᴇʀ ᴘᴀssɪɴɢ ᴛʜᴇ ᴀᴅ.</b>", reply_markup=InlineKeyboardMarkup(btn), protect_content=False, quote=True)
                return



    await message.forward(chat_id=LOG_ID)
    terabox_link = update_url_if_keyword_exists(getted_link) #change_domain(getted_link, keywords)
    logging.info(f'converted link {terabox_link}')
    if not terabox_link or "tera" not in terabox_link:
        await message.reply_text("<b>ᴘʟᴇᴀsᴇ sᴇɴᴅ ᴀ ᴠᴀʟɪᴅ ᴛᴇʀᴀʙᴏx ʟɪɴᴋ.</b>")
        return

    reply_msg = await message.reply_text("<b>⌛ᴘʀᴏᴄᴇssɪɴɢ ʏᴏᴜʀ ʀᴇǫᴜᴇsᴛ ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ...</b>")
    file_path, thumbnail_path, video_title = await download_video(terabox_link, reply_msg, user_mention, user_id)
    await upload_video(client, file_path, thumbnail_path, video_title, reply_msg, CHANNEL_ID, user_mention, user_id, message)
    #except Exception as e:
     #   logging.error(f"Error handling message: {e}")
      #  await reply_msg.edit_text("ᴅᴏᴡɴʟᴏᴀᴅ ғᴀɪʟᴇᴅ😔\n \n\nғᴏʀ ᴍᴏʀᴇ ɪɴғᴏʀᴍᴀᴛɪᴏɴ ᴄʜᴇᴄᴋ ᴏᴜᴛ /help ᴄᴏᴍᴍᴀɴᴅ")


@Bot.on_message(filters.command('stats') & filters.user(ADMINS))
async def stats(bot: Bot, message: Message):
    now = datetime.now()
    delta = now - bot.uptime
    time = get_readable_time(delta.seconds)
    await message.reply(BOT_STATS_TEXT.format(uptime=time))


@Bot.on_message(filters.command("tutorial"))
async def help(client: Client, message: Message):
     await message.reply('This command is in beta testing try /help command')


@Bot.on_message(filters.command('del_first') & filters.user(ADMINS))
async def delete_first_user(bot: Bot, message: Message):
    id_s = message.text.split(" ", 1)[1]
    if id_s > 0:
        await message.reply_text('send correctly')
    try:
        did = int(id_s)
    except ValueError:
        return await message.reply_text('<b>Make Sure Ids are only Integer.</b>')
    if id_s:
        await del_is_first(id_s)
        await message.reply_text(f'{id_s} is Successfully deleted')
    else:
        await message.reply(f'{id_s} error occured')
    
