#!/usr/bin/env python3
import os

from app.main import *


def test_is_youtube_url():
    assert is_youtube_url("https://www.youtube.com/watch?v=1aaa1a11a1A") == True
    assert is_youtube_url("https://m.youtube.com/watch?v=1aaa1a11a1A") == True
    assert is_youtube_url("https://youtu.be/1aaa1a11a1A") == True
    assert is_youtube_url("/start") == False
    assert is_youtube_url("some lalala") == False


def test_trim_link():
    assert (
        trim_link(
            "https://www.youtube.com/watch?v=1aaa1a11a1A&list=PLFtS8Ah0wZvWS37oveJ0-D5K6V7GWUpqY&index=23"
        )
        == "https://www.youtube.com/watch?v=1aaa1a11a1A"
    )
    assert (
        trim_link("https://www.youtube.com/watch?v=1aaa1a11a1A")
        == "https://www.youtube.com/watch?v=1aaa1a11a1A"
    )


def test_download_audio_and_ffmpeg():
    # should work
    url = "https://www.youtube.com/watch?v=BaW_jenozKc"
    id = 123
    full_file_path = f"/tmp/video-{id}.mp4"
    full_audio_path = f"/tmp/audio-{id}.mp3"
    # test download
    assert download_video(id, url) == "youtube-dl test video \"'/\ä↭𝕐"
    assert os.path.isfile(full_file_path) == True
    # test ffmpeg transformation
    assert get_audio_from_video(id) == (0, full_audio_path)
    assert os.path.isfile(full_audio_path) == True
    # remove files
    os.remove(full_file_path)
    os.remove(full_audio_path)

    # shouldn't work (members only)
    url = "https://www.youtube.com/watch?v=ingEMVU93dA"
    id = 123
    assert download_video(id, url) == "fail"
