import asyncio
import os
import random
import sys
import time
import string
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated

from bot import Bot
from config import *
from helper_func import get_readable_time, increasepremtime, subscribed, subscribed2, decode, get_messages, get_shortlink, get_verify_status, update_verify_status, get_exp_time
from database.database import add_admin, add_user, del_admin, del_user, full_adminbase, full_userbase, present_admin, present_user, is_first, add_is_first, del_is_first

SECONDS = TIME 
TUT_VID = f"{TUT_VID}"

@Bot.on_message(filters.command('start') & filters.private & subscribed & subscribed2)
async def start_command(client: Client, message: Message):
    id = message.from_user.id
    mentio = message.from_user.mention
    uname = message.from_user.username
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    verify_status = await get_verify_status(id)
    logging.info(f"The user {first_name} ({id}) is using the bot now")
    LOG_MESSAGE = f"User : {first_name} {last_name} \nUsername : {uname} \nId : {id} \n{mentio}\n<blockquote>{verify_status}</blockquote>"
    if not await present_user(id):
        try:
            await add_user(id)
            await update_verify_status(id,verify_token="new_user",is_verified=True, verified_time=time.time())
            log_message1 = f"""#ɴᴇᴡ_ᴜꜱᴇʀ\n\n◉ ᴜꜱᴇʀ-ɪᴅ: <code>{id}</code>\n◉ ᴀᴄᴄ-ɴᴀᴍᴇ: {first_name} {last_name}\n◉ ᴜꜱᴇʀɴᴀᴍᴇ: @{uname}"""
            if LOG_ID:
                await client.send_message(chat_id=LOG_ID, text=log_message1)
           
        except:
            pass
    if USE_SHORTLINK:
        for i in range(1):
            if id in ADMINS:
                continue
            #if await is_first(id):
             #   pass

        verify_status = await get_verify_status(id)
        logging.info(f'{verify_status}')
        if verify_status['is_verified'] and VERIFY_EXPIRE < (time.time() - verify_status['verified_time']):
            await update_verify_status(id, is_verified=False)
        if "verify_" in message.text:
            _, token = message.text.split("_", 1)
            if verify_status['verify_token'] != token:
                return await message.reply(f"ʏᴏᴜʀ ᴛᴏᴋᴇɴ ɪs ɪɴᴠᴀʟɪᴅ ᴏʀ ᴇxᴘɪʀᴇᴅ \n\nᴛʀʏ ᴀɢᴀɪɴ ʙʏ ᴄʟɪᴄᴋɪɴɢ ' /start ' ᴄᴏᴍᴍᴀɴᴅ")
            await update_verify_status(id, verify_token=token, is_verified=True, verified_time=time.time())
            if verify_status["link"] == "":
                reply_markup = None
            await message.reply(f"ʏᴏᴜʀ ʜᴀᴠᴇ sᴜᴄᴄᴇssғᴜʟʟʏ ᴠᴇʀɪғɪᴇᴅ\n\nʏᴏᴜ ᴄᴀɴ ᴜsᴇ ᴍᴇ ғᴏʀ: {get_exp_time(VERIFY_EXPIRE)} ⏳", reply_markup=reply_markup, protect_content=False, quote=True)
            if VERIFY_LOG_ID:
                vf_status = await get_verify_status(id)
                LOG_MESSAGE = f"User Passed The Token\n\nUser : {first_name} {last_name} \nId : {id}\nUsername : {uname}\n{mentio}\n\n<blockquote>{vf_status}</blockquote>\n\nReport By @{client.username}"
                await client.send_message(chat_id=VERIFY_LOG_ID, text=LOG_MESSAGE, parse_mode=ParseMode.HTML)
                logging.info('log sent')
            else:
                pass

                        
    if len(message.text) > 7:
        for i in range(1):
            if USE_SHORTLINK : 
                if id not in ADMINS:
                    try:
                        if not verify_status['is_verified']:
                            continue
                    except:
                        continue
            try:
                base64_string = message.text.split(" ", 1)[1]
            except:
                return
            _string = await decode(base64_string)
            argument = _string.split("-")
            if len(argument) == 3:
                try:
                    start = int(int(argument[1]) / abs(client.db_channel.id))
                    end = int(int(argument[2]) / abs(client.db_channel.id))
                except:
                    return
                if start <= end:
                    ids = range(start, end+1)
                else:
                    ids = []
                    i = start
                    while True:
                        ids.append(i)
                        i -= 1
                        if i < end:
                            break
            elif len(argument) == 2:
                try:
                    ids = [int(int(argument[1]) / abs(client.db_channel.id))]
                except:
                    return
            temp_msg = await message.reply("Please wait....")
            try:
                messages = await get_messages(client, ids)
            except:
                await message.reply_text("Something went wrong...! 🥲")
                return
            await temp_msg.delete()
            isfst = await is_first(id)
            logging.info(f'108 {bool(isfst)}')
            if not isfst == True:
                logging.info(f' 109 {isfst}')
                await client.send_message(chat_id=id, text=f"<b>Congragulation, You have got Free Trial period {get_exp_time(VERIFY_EXPIRE)}</b>")
                #await add_is_first(id)
                #LOGGER(__name__).info(f"line 109 bot.py...{}")

            snt_msgs = []
            for msg in messages:
                if bool(CUSTOM_CAPTION) & bool(msg.document):
                    caption = CUSTOM_CAPTION.format(previouscaption="" if not msg.caption else msg.caption.html,    filename=msg.document.file_name)
                else:   
                    caption = "" if not msg.caption else msg.caption.html   
                if DISABLE_CHANNEL_BUTTON:  
                    reply_markup = msg.reply_markup 
                else:   
                    reply_markup = None 
                try:    
                    snt_msg = await msg.copy(chat_id=message.from_user.id, caption=caption, parse_mode=ParseMode.HTML,  reply_markup=reply_markup, protect_content=PROTECT_CONTENT)
                    await asyncio.sleep(0.5)    
                    snt_msgs.append(snt_msg)    
                except FloodWait as e:  
                    await asyncio.sleep(e.x)    
                    snt_msg = await msg.copy(chat_id=message.from_user.id, caption=caption, parse_mode= ParseMode.HTML,  reply_markup=reply_markup, protect_content=PROTECT_CONTENT)
                    snt_msgs.append(snt_msg)    
                except: 
                    pass    
                
            notification_msg = await message.reply(f"<b>File will be deleted in {get_exp_time(SECONDS)} to avoid Copyright issue please forward it to somewhere else</b>")
            if not isfst:
                try:
                    #await add_is_first(id)
                    logging.info(f'added to is_first')
                except Exception as e:
                    logging.info(f"line 138 bot.py {e}")

            await asyncio.sleep(SECONDS)    
            for snt_msg in snt_msgs:    
                try:    
                    await snt_msg.delete()
                    await notification_msg.delete()  
                except: 
                    pass    
            #await notification_msg.edit("<b>Your file has been successfully deleted! 😼</b>")  
            #return  
    for i in range(1):
        if USE_SHORTLINK : 
            if id not in ADMINS:
                try:
                    if not verify_status['is_verified']:
                        continue
                except:
                    continue
        reply_markup = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("Aʙᴏᴜᴛ", callback_data="about"),
                    InlineKeyboardButton("Cʟᴏsᴇ", callback_data="close")
                ]
            ]
        )
        await message.reply_text(
            text=START_MSG.format(
                first=message.from_user.first_name,
                last=message.from_user.last_name,
                username=None if not message.from_user.username else '@' + message.from_user.username,
                mention=message.from_user.mention,
                id=message.from_user.id
            ),
            reply_markup=reply_markup,
            disable_web_page_preview=True,
            quote=True
        )       
                                  

    if USE_SHORTLINK : 
        if id in ADMINS:
            return
        else:
            verify_status = await get_verify_status(id)
            if not verify_status['is_verified']:
                token = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
                link = await get_shortlink(SHORTLINK_API_URL, SHORTLINK_API_KEY,f'https://telegram.dog/{client.username}?start=verify_{token}')
                await update_verify_status(id, verify_token=token, link=link)
                if VERIFY_LOG_ID:
                    LOG_MESG = f"Token Is Generated For The User\n\nUser : {first_name} {last_name}\nId : {id}\nUsername : {uname}\n\nToken : <code>{token}</code>\n\nReport By @{client.username}"
                    await client.send_message(chat_id=VERIFY_LOG_ID, text=LOG_MESG, parse_mode=ParseMode.HTML)
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
    return


    
#=====================================================================================#

WAIT_MSG = """<b>Processing.......</b>"""

REPLY_ERROR = """<code>Use this command as a replay to any telegram message without any spaces.</code>"""

#=====================================================================================#

@Bot.on_message(filters.command('start') & filters.private)
async def not_joined(client: Client, message: Message):
    if FORCE_SUB_CHANNEL & FORCE_SUB_CHANNEL2:
        buttons = [
        [
            InlineKeyboardButton(
                "ᴄʜᴀɴɴᴇʟ 1",
                url=client.invitelink),
            InlineKeyboardButton(
                "ᴄʜᴀɴɴᴇʟ 2",
                url=client.invitelink2),
        ]
    ]
    elif FORCE_SUB_CHANNEL:
        buttons = [
            [
                InlineKeyboardButton(
                    " ᴄʜᴀɴɴᴇʟ 🔔",
                    url=client.invitelink)
            ]
        ]
    try:
        buttons.append(
            [
                InlineKeyboardButton(
                    text='Try Again',
                    url=f"https://t.me/{client.username}?start={message.command[1]}"
                )
            ]
        )
    except IndexError:
        pass

    await message.reply(
        text=FORCE_MSG.format(
            first=message.from_user.first_name,
            last=message.from_user.last_name,
            username=None if not message.from_user.username else '@' + message.from_user.username,
            mention=message.from_user.mention,
            id=message.from_user.id
        ),
        reply_markup=InlineKeyboardMarkup(buttons),
        quote=True,
        disable_web_page_preview=True
    )


@Bot.on_message(filters.command('ch2l') & filters.private)
async def gen_link_encoded(client: Bot, message: Message):
    try:
        hash = await client.ask(text="Enter the code here... \n /cancel to cancel the operation",chat_id = message.from_user.id, timeout=60)
    except Exception as e:
        print(e)
        await hash.reply(f"😔 some error occurred {e}")
        return
    if hash.text == "/cancel":
        await hash.reply("Cancelled 😉!")
        return
    link = f"https://t.me/{client.username}?start={hash.text}"
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🎉 Click Here ", url=link)]])
    await hash.reply_text(f"<b>🧑‍💻 Here is your generated link", quote=True, reply_markup=reply_markup)
    return
        

@Bot.on_message(filters.command('users') & filters.private & filters.user(ADMINS))
async def get_users(client: Bot, message: Message):
    msg = await client.send_message(chat_id=message.chat.id, text=WAIT_MSG)
    users = await full_userbase()
    await msg.edit(f"{len(users)} users are using this bot 👥")
    return

@Bot.on_message(filters.private & filters.command('broadcast') & filters.user(ADMINS))
async def send_text(client: Bot, message: Message):
    if message.reply_to_message:
        query = await full_userbase()
        broadcast_msg = message.reply_to_message
        total = 0
        successful = 0
        blocked = 0
        deleted = 0
        unsuccessful = 0

        pls_wait = await message.reply("<i>Broadcasting Message.. This will Take Some Time ⌚</i>")
        for chat_id in query:
            try:
                await broadcast_msg.copy(chat_id)
                successful += 1
            except FloodWait as e:
                await asyncio.sleep(e.x)
                await broadcast_msg.copy(chat_id)
                successful += 1
            except UserIsBlocked:
                await del_user(chat_id)
                await del_is_first(chat_id)
                blocked += 1
            except InputUserDeactivated:
                await del_user(chat_id)
                await del_is_first(chat_id)
                deleted += 1
            except:
                unsuccessful += 1
                pass
            total += 1

        status = f"""<b><u>Broadcast Completed 🟢</u>
                
                Total Users: <code>{total}</code>
                Successful: <code>{successful}</code>
                Blocked Users: <code>{blocked}</code>
                Deleted Accounts: <code>{deleted}</code>
                Unsuccessful: <code>{unsuccessful}</code></b>"""

        return await pls_wait.edit(status)

    else:
        msg = await message.reply(REPLY_ERROR)
        await asyncio.sleep(8)
        await msg.delete()
    return

@Bot.on_message(filters.command('auth') & filters.private)
async def auth_command(client: Bot, message: Message):
    await client.send_message(
        chat_id=OWNER_ID,
        text=f"Message for @{OWNER_TAG}\n<code>{message.from_user.id}</code>\n/add_admin <code>{message.from_user.id}</code> 🤫",
    )

    await message.reply("Please wait for verification from the owner. 🫣")
    return


@Bot.on_message(filters.command('add_admin') & filters.private & filters.user(OWNER_ID))
async def command_add_admin(client: Bot, message: Message):
    while True:
        try:
            admin_id = await client.ask(text="Enter admin id 🔢\n /cancel to cancel : ",chat_id = message.from_user.id, timeout=60)
        except Exception as e:
            print(e)
            return
        if admin_id.text == "/cancel":
            await admin_id.reply("Cancelled 😉!")
            return
        try:
            await Bot.get_users(user_ids=admin_id.text, self=client)
            break
        except:
            await admin_id.reply("❌ Error 😖\n\nThe admin id is incorrect.", quote = True)
            continue
    if not await present_admin(admin_id.text):
        try:
            await add_admin(admin_id.text)
            await message.reply(f"Added admin <code>{admin_id.text}</code> 😼")
            try:
                reply_markup = InlineKeyboardMarkup(
                    [
                        [InlineKeyboardButton("ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ", url=CHANNEL_LINK)]
                    ]
                )
                await client.send_message(
                    chat_id=admin_id.text,
                    text=f"You are verified, join the channel for forwarding links for batch commands. 😁",
                    reply_markup=reply_markup
                )
            except:
                await message.reply("Failed to send invite. Please ensure that they have started the bot. 🥲")
        except:
            await message.reply("Failed to add admin. 😔\nSome error occurred.")
    else:
        await message.reply("admin already exist. 💀")
    return


@Bot.on_message(filters.command('del_admin') & filters.private  & filters.user(OWNER_ID))
async def delete_admin_command(client: Bot, message: Message):
    while True:
        try:
            admin_id = await client.ask(text="Enter admin id 🔢\n /cancel to cancel : ",chat_id = message.from_user.id, timeout=60)
        except:
            return
        if admin_id.text == "/cancel":
            await admin_id.reply("Cancelled 😉!")
            return
        try:
            await Bot.get_users(user_ids=admin_id.text, self=client)
            break
        except:
            await admin_id.reply("❌ Error\n\nThe admin id is incorrect.", quote = True)
            continue
    if await present_admin(admin_id.text):
        try:
            await del_admin(admin_id.text)
            await message.reply(f"Admin <code>{admin_id.text}</code> removed successfully 😀")
        except Exception as e:
            print(e)
            await message.reply("Failed to remove admin. 😔\nSome error occurred.")
    else:
        await message.reply("admin doesn't exist. 💀")
    return

@Bot.on_message(filters.command('admins')  & filters.private & subscribed & subscribed2)
async def admin_list_command(client: Bot, message: Message):
    admin_list = await full_adminbase()
    await message.reply(f"Full admin list 📃\n<code>{admin_list}</code>")
    return

@Bot.on_message(filters.command('ping')  & filters.private)
async def check_ping_command(client: Bot, message: Message):
    start_t = time.time()
    rm = await message.reply_text("Pinging....", quote=True)
    end_t = time.time()
    time_taken_s = (end_t - start_t) * 1000
    await rm.edit(f"Ping 🔥!\n{time_taken_s:.3f} ms")
    return

@Client.on_message(filters.command("bought") & filters.private)
async def bought(client, message):
    msg = await message.reply('Wait im checking...')
    replyed = message.reply_to_message
    if not replyed:
        await msg.edit("<b>Please reply with the screenshot of your payment for the premium purchase to proceed.\n\nFor example, first upload your screenshot, then reply to it using the '/bought' command</b>")
    if replyed and replyed.photo:
        await client.send_photo(
            photo=replyed.photo.file_id,
            chat_id=PAYMENT_LOGS,
            caption=f'<b>User - {message.from_user.mention}\nUser id - <code>{message.from_user.id}</code>\nusername - <code>{message.from_user.username}</code>\nUser Name - <code>{message.from_user.first_name}</code></b>',
            reply_markup=InlineKeyboardMarkup(
                [
                    
                    [
                        InlineKeyboardButton(
                            "• ᴄʟᴏsᴇ •", callback_data="close_data"
                        )
                    ]
                    
                ]
            )
        )
        await msg.edit_text('<b>Your screenshot has been sent to Admins</b>')


@Client.on_message(filters.private & filters.command('restart') & filters.user(ADMINS))
async def restart(client, message):
    msg = await message.reply_text(
        text="<i>Trying To Restarting.....</i>",
        quote=True
    )
    await asyncio.sleep(5)
    await msg.edit("<i>Server Restarted Successfully ✅</i>")
    try:
        os.execl(sys.executable, sys.executable, *sys.argv)
    except Exception as e:
        print(e)


if USE_PAYMENT:
    @Bot.on_message(filters.command('add_prem') & filters.private & filters.user(ADMINS))
    async def add_user_premium_command(client: Bot, message: Message):
        while True:
            try:
                user_id = await client.ask(text="Enter id of user 🔢\n /cancel to cancel : ",chat_id = message.from_user.id, timeout=60)
            except Exception as e:
                print(e)
                return  
            if user_id.text == "/cancel":
                await user_id.edit("Cancelled 😉!")
                return
            try:
                await Bot.get_users(user_ids=user_id.text, self=client)
                break
            except:
                await user_id.edit("❌ Error 😖\n\nThe admin id is incorrect.", quote = True)
                continue
        user_id = int(user_id.text)
        while True:
            try:
                timeforprem = await client.ask(text="Enter the amount of time you want to provide the premium \nChoose correctly. Its not reversible.\n\n⁕ <code>1</code> for 7 days.\n⁕ <code>2</code> for 1 Month\n⁕ <code>3</code> for 3 Month\n⁕ <code>4</code> for 6 Month\n⁕ <code>5</code> for 1 year.🤑", chat_id=message.from_user.id, timeout=60)
            except Exception as e:
                print(e)
                return
            if not int(timeforprem.text) in [1, 2, 3, 4, 5]:
                await message.reply("You have given wrong input. 😖")
                continue
            else:
                break
        timeforprem = int(timeforprem.text)
        if timeforprem==1:
            timestring = "7 days"
        elif timeforprem==2:
            timestring = "1 month"
        elif timeforprem==3:
            timestring = "3 month"
        elif timeforprem==4:
            timestring = "6 month"
        elif timeforprem==5:
            timestring = "1 year"
        try:
            await increasepremtime(user_id, timeforprem)
            await message.reply("Premium added! 🤫")
            await client.send_message(
            chat_id=user_id,
            text=f"Update for you\n\nPremium plan of {timestring} added to your account. 🤫",
        )
        except Exception as e:
            print(e)
            await message.reply("Some error occurred.\nCheck logs.. 😖\nIf you got premium added message then its ok.")
        return



@Bot.on_message(filters.command('logs') & filters.user(ADMINS))
async def log_file(bot: Bot, message: Message):
    """Send log file"""
    try:
        await message.reply_document('logs.txt')
    except Exception as e:
        await message.reply(str(e))

@Bot.on_message(filters.command("help"))
async def help(client: Client, message: Message):
     await message.reply(text=HELP_TXT)