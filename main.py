#!/usr/bin/env python3

import logging
import random
import string
import subprocess
import telegram
import os

from time import sleep

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

SAMPLE = "https://www.youtube.com/watch?v=ONj9cvHCado"
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


def download_video(id, url=SAMPLE):
    """
    Download video in the worst possible format
    :param url: youtube video url
    :param id: generated id for a file
    :return: exit code of youtube-dl, filename
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
    video_filename = f"/tmp/video-{id}.mp4"
    audio_filename = f"/tmp/audio-{id}.mp3"
    if os.path.isfile(video_filename) and os.path.isfile(audio_filename):
        os.remove(video_filename)
        os.remove(audio_filename)
    else:
        logging.error(f"Error: couldn't find audio/video file")
    pass


def is_youtube_url(text):
    if "https://www.youtube.com" or "https://m.youtube.com" in text:
        return True
    return False


def calculate_file_size(filepath: str) -> int:
    """
    Returns filesize in MB
    """
    return os.stat(filepath).st_size / (1024 * 1024)


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
            if is_youtube_url(message):
                logging.info(f"Got a youtube link {message}")
                bot.send_message(user_id, "Preparing video")
                id = id_generator()
                video_name = download_video(id, message)
                get_audio_from_video(id)
                # Telegram doesn't support media files > 50 MB for bots to send
                filesize = calculate_file_size(f"/tmp/audio-{id}.mp3")
                if filesize < 50:
                    bot.send_audio(
                        user_id,
                        audio=open(f"/tmp/audio-{id}.mp3", "rb"),
                        title=video_name,
                    )
                else:
                    bot.send_message(
                        user_id,
                        f"Sorry, the audio file is too big ({filesize} MB). I don't know how to split audio files yet.",
                    )
                cleanup(id)
            else:
                logging.info(f"Got a message: {message}")
        if message_id:
            updates = bot.get_updates(offset=message_id + 1)
        sleep(60)


if __name__ == "__main__":
    main()
