#!/usr/bin/env python3

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
            "https://www.youtube.com/watch?v=1gKdzgjRirk&list=PLFtS8Ah0wZvWS37oveJ0-D5K6V7GWUpqY&index=23"
        )
        == "https://www.youtube.com/watch?v=1gKdzgjRirk"
    )
    assert (
        trim_link("https://www.youtube.com/watch?v=1gKdzgjRirk")
        == "https://www.youtube.com/watch?v=1gKdzgjRirk"
    )
