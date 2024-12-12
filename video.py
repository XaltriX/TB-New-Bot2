import requests
import aria2p
from datetime import datetime
from helper_func import get_video_duration, format_progress_bar
from moviepy import VideoFileClip
import asyncio
import os, time
import logging
from bot import Bot

DOWNLOAD_LIST = []

aria2 = aria2p.API(
    
    aria2p.Client(
        host="http://localhost",
        port=6800,
        secret=""
    )
)

def checkFileType(name:str) -> str:
    name = name.lower()
    if any(ext in name for ext in ['.mp4', '.mov', '.m4v', '.mkv', '.asf', '.avi', '.wmv', '.m2ts', '.3g2', '.ts', 'flv']):
        typefile = 'video'
    elif any(ext in name for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg']):
        typefile = 'image'
    elif any(ext in name for ext in ['.pdf', '.docx', '.zip', '.rar', '.7z']):
        typefile = 'file'
    else:
        typefile = 'other'
    return(typefile)




def gen_tera_dil(url):
    api_url = "https://teradl-1vbm.onrender.com//generate_file"
    params1 = {
        "mode": "2",  # Replace with the desired mode
        "url": url    # Replace with the resource URL
    }
    response = requests.post(api_url, json=params1)
    if response.status_code == 200:
        data = response.json()
        if data['status'] == 'success':
          js = data['js_token']
          cook = data['cookie']
          shareid = data['shareid']
          uk = data['uk']
          timestamp = data['timestamp']
          sign = data['sign']
          fsl = data['list']
          fs = fsl[0]
          thumb = fs['image']
          name = fs['name']
          fs_id = fs['fs_id']
          type = fs['type']

    else:
        print(f"Failed with status code {response.status_code}: {response.text}")
        return
    parms2 = {
        "mode": 2,
        "js_token": js,
        "cookie": cook,
        "sign": sign,
        "timestamp": timestamp,
        "shareid": shareid,
        "uk": uk,
        "fs_id": fs_id
    }
    url = "https://teradl-1vbm.onrender.com/generate_link"
    headers = {
        "Content-Type": "application/json"
    }
    try:
        response = requests.post(url, json=parms2, headers=headers)
        response.raise_for_status()
        urll = response.json()
        deta = {'url': urll['download_link']['url_1'], 'name': name, 'thumb': thumb}
        logging.info('response successfull for gen link')
        return deta
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

async def download_video(url, reply_msg, user_mention, user_id):
    data = gen_tera_dil(url)
    if 'url' in data:
        video_title = data['name']
        thumbnail_url = data['thumb']
        ful = data['url']
        fast_download_link = ful.replace('terabox', '1024terabox')
    else:
        return

    options = {
            "dir": "utmp/downloads"
        }
    ud = f"{video_title}_{user_id}"
    download = aria2.add_uris([fast_download_link])   #, options=options)
    if ud in DOWNLOAD_LIST:
        await reply_msg.edit(f"<i>{video_title}</i>\n\n<b>ᴀʟʀᴇᴀᴅʏ ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ\nsᴏ ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ</b>")
        return
    start_time = datetime.now()
    logging.info(f"fast download link generated {fast_download_link} {download.gid}") #
    last_update = 0
    if download.is_active:
        logging.info(f"Download started {video_title}")
        
        DOWNLOAD_LIST.append(ud)
    while not download.is_complete:
        download.update()
        percentage = download.progress
        done = download.completed_length
        total_size = download.total_length
        speed = download.download_speed
        eta = download.eta
        elapsed_time_seconds = (datetime.now() - start_time).total_seconds()
        progress_text = format_progress_bar(
            filename=video_title,
            percentage=percentage,
            done=done,
            total_size=total_size,
            status="📥Downloading",
            eta=eta,
            speed=speed,
            elapsed=elapsed_time_seconds,
            user_mention=user_mention,
            user_id=user_id,
            aria2p_gid=download.gid
        )
        try:
            await reply_msg.edit_text(progress_text)
            await asyncio.sleep(2)
        except:
            continue
    if download.is_complete:
        file_path = download.files[0].path
        thumbnail_path = f"{video_title}.jpg"
        thumbnail_response = requests.get(thumbnail_url)
        with open(thumbnail_path, "wb") as thumb_file:
            thumb_file.write(thumbnail_response.content)

        await reply_msg.edit_text("📤ᴜᴘʟᴏᴀᴅɪɴɢ...")

        return file_path, thumbnail_path, video_title
    else:
        await reply_msg.edit_text(f"Error : {Exception}")


    


async def upload_video(client, file_path: str, thumbnail_path: str, video_title: str, reply_msg, collection_channel_id, user_mention, user_id, message):
    file_size = os.path.getsize(file_path)
    uploaded = 0
    start_time = datetime.now()
    last_update_time = time.time()

    try:
        video_path = str(file_path)
        clip = VideoFileClip(video_path)
        duration = int(clip.duration)
        clip.close()
    except Exception as e:
        logging.warning(f"Error updating progress message: {e}")
        duration = 0

    hours, remainder = divmod(duration, 3600)
    minutes, seconds = divmod(remainder, 60)
    formatted_duration = f"{hours:02}:{minutes:02}:{seconds:02}"

    async def progress(current, total):
        nonlocal uploaded, last_update_time
        uploaded = current
        percentage = (current / total) * 100
        elapsed_time_seconds = (datetime.now() - start_time).total_seconds()
        
        if time.time() - last_update_time > 2:
            progress_text = format_progress_bar(
                filename=video_title,
                percentage=percentage,
                done=current,
                total_size=total,
                status="📤Uploading",
                eta=(total - current) / (current / elapsed_time_seconds) if current > 0 else 0,
                speed=current / elapsed_time_seconds if current > 0 else 0,
                elapsed=elapsed_time_seconds,
                user_mention=user_mention,
                user_id=user_id,
                aria2p_gid=""
            )
            try:
                await reply_msg.edit_text(progress_text)
                last_update_time = time.time()
            except Exception as e:
                logging.warning(f"Error updating progress message: {e}")
    
    with open(file_path, 'rb') as file:
        type = checkFileType(video_title)
        if type == 'video':
            collection_message = await client.send_video(
                chat_id=collection_channel_id,
                video=file,
                duration=duration,
                caption=f"ғɪʟᴇ ɴᴀᴍᴇ : {video_title}\nᴅᴜʀᴀᴛɪᴏɴ : {formatted_duration}\nᴛᴀsᴋ ʙʏ : {user_mention}\nᴜsᴇʀ's ʟɪɴᴋ: tg://user?id={user_id}",
                thumb=thumbnail_path,
                progress=progress
                )
        elif type == 'image':
            collection_message =  await client.send_photo(
                chat_id = collection_channel_id,
                photo = file,
                caption = f"ғɪʟᴇ ɴᴀᴍᴇ : {video_title}\nᴅᴜʀᴀᴛɪᴏɴ : {formatted_duration}\nᴛᴀsᴋ ʙʏ : {user_mention}\nᴜsᴇʀ's ʟɪɴᴋ: tg://user?id={user_id}",
                progress=progress
                )          
        elif type == 'file' or type == 'other':
            collection_message = await client.send_document(
                chat_id = collection_channel_id,
                document = file,
                thumb = thumbnail_path,
                caption = f"ғɪʟᴇ ɴᴀᴍᴇ : {video_title}\nᴅᴜʀᴀᴛɪᴏɴ : {formatted_duration}\nᴛᴀsᴋ ʙʏ : {user_mention}\nᴜsᴇʀ's ʟɪɴᴋ: tg://user?id={user_id}",
                file_name= video_title
                )
        else:
            collection_message = await client.send_video(
                chat_id=collection_channel_id,
                video=file,
                duration=duration,
                caption=f"ғɪʟᴇ ɴᴀᴍᴇ : {video_title}\nᴅᴜʀᴀᴛɪᴏɴ : {formatted_duration}\nᴛᴀsᴋ ʙʏ : {user_mention}\nᴜsᴇʀ's ʟɪɴᴋ: tg://user?id={user_id}",
                thumb=thumbnail_path,
                progress=progress
                )

        await client.copy_message(
            chat_id=message.chat.id,
            from_chat_id=collection_channel_id,
            message_id=collection_message.id
        )
        await asyncio.sleep(1)
        await message.delete()

    await reply_msg.delete()
    logging.info(f"Download completed {video_title}")
    ud = f"{video_title}_{user_id}"
    try:
        DOWNLOAD_LIST.remove(ud)
    except Exception as e:
        logging.info(f"Error while removing download {e}")
    os.remove(file_path)
    os.remove(thumbnail_path)
    return collection_message.id




