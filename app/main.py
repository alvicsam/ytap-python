#!/usr/bin/env python3

import logging
import random
import string
import subprocess
import telegram
import os
import json
import datetime

from time import sleep

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

TOKEN = os.getenv("BOT_TOKEN")


def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    """
    Generates random sequence
    """
    return "".join(random.choice(chars) for _ in range(size))


def preflight():
    """
    Check the requirements
    """
    youtubedl_exists = os.path.exists("/usr/local/bin/youtube-dl")
    if not youtubedl_exists:
        print("Please install youtube-dl, exiting")
        exit(1)


def download_video(id, url):
    """
    Download video in the worst possible format and get video name
    :param url: youtube video url
    :param id: generated id for a file
    :return: name of the video
    """
    video_filename = f"/tmp/video-{id}.mp4"
    cmd_download = f"youtube-dl --newline -f worst {url} -o {video_filename}"
    cmd_name = f"youtube-dl --skip-download --get-title --no-warnings {url}"
    try:
        code = subprocess.run(cmd_download.split())
        video_name = subprocess.run(
            cmd_name, capture_output=True, text=True, shell=True
        )
    except Exception as e:
        logging.error(f"Something went wrong with downloading video: {e}")
        exit(1)
    return video_name.stdout.strip()


def get_audio_from_video(id):
    """
    Extract audio with ffmpeg
    """
    audio_filename = f"/tmp/audio-{id}.mp3"
    cmd = f"ffmpeg -i /tmp/video-{id}.mp4 -q:a 0 -map a {audio_filename}"
    try:
        code = subprocess.run(cmd.split())
    except Exception as e:
        logging.error(f"Something went wrong with getting audio from video: {e}")
        exit(1)
    return code, audio_filename


def cleanup(id):
    """
    Remove temp audio and video files
    """
    video_filename = f"/tmp/video-{id}.mp4"
    audio_filename = f"/tmp/audio-{id}.mp3"
    if os.path.isfile(video_filename) and os.path.isfile(audio_filename):
        os.remove(video_filename)
        os.remove(audio_filename)
    else:
        logging.error(f"Error: couldn't find audio/video file")
    pass


def is_youtube_url(text):
    if "https://www.youtube.com" in text or "https://m.youtube.com" in text:
        return True
    return False


def calculate_file_size(filepath: str) -> int:
    """
    Returns filesize in MB
    """
    return os.stat(filepath).st_size / (1024 * 1024)


def get_audio_duration(audiofile):
    cmd = f"ffprobe -v quiet -print_format json -show_format -show_streams -print_format json {audiofile} | tr -d '\n'"
    try:
        full_audio_info_raw = subprocess.run(
            cmd, capture_output=True, text=True, shell=True
        )
        full_audio_info = json.loads(full_audio_info_raw.stdout)
        duration = full_audio_info["format"]["duration"]
    except Exception as e:
        logging.error(f"Something went wrong with getting audio from video: {e}")
        exit(1)
    return int(float(duration))


def divide_file_into_parts(number_of_parts, duration, id):
    duration_of_one_part = duration // number_of_parts
    for i in range(0, number_of_parts):
        t1 = str(datetime.timedelta(seconds=i * int(duration_of_one_part)))
        t2 = str(datetime.timedelta(seconds=(i + 1) * int(duration_of_one_part)))
        cmd = f"ffmpeg -i /tmp/audio-{id}.mp3 -ss {t1} -to {t2} -c copy /tmp/audio-{id}_part{i}.mp3"
        try:
            code = subprocess.run(cmd.split())
        except Exception as e:
            logging.error(f"Something went wrong with splitting audio: {e}")
            exit(1)


def main():
    preflight()
    bot = telegram.Bot(TOKEN)
    message_id = 0
    while True:
        updates = bot.get_updates(offset=1)
        for i in range(0, len(updates)):
            user_id = updates[i]["message"]["chat"]["id"]
            message_id = updates[i]["update_id"]
            message = updates[i]["message"]["text"]
            print(f"User id: {user_id}, message: {message}, message id: {message_id}")
            if message in "/start":
                bot.send_message(
                    user_id,
                    "Hi! Just send me a youtube link and I'll send you an audio from it",
                )
            if is_youtube_url(message):
                logging.info(f"Got a youtube link {message}")
                bot.send_message(user_id, "Preparing video")
                id = id_generator()
                video_name = download_video(id, message)
                audiofile = f"/tmp/audio-{id}.mp3"
                get_audio_from_video(id)
                # Telegram doesn't support media files > 50 MB for bots to send
                filesize = calculate_file_size(audiofile)
                if filesize < 50:
                    bot.send_audio(
                        user_id,
                        audio=open(f"/tmp/audio-{id}.mp3", "rb"),
                        title=video_name,
                    )
                else:
                    number_of_parts = int(filesize // 45 + 1)
                    audio_duration = get_audio_duration(audiofile)
                    divide_file_into_parts(number_of_parts, audio_duration, id)
                    for i in range(0, number_of_parts):
                        bot.send_audio(
                            user_id,
                            audio=open(f"/tmp/audio-{id}_part{i}.mp3", "rb"),
                            title=video_name,
                        )
                cleanup(id)
            else:
                logging.info(f"Got a message: {message}")
        if message_id:
            updates = bot.get_updates(offset=message_id + 1)
        sleep(60)


if __name__ == "__main__":
    main()
