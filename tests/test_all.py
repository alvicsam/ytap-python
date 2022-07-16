#!/usr/bin/env python3

from app.main import *


def test_is_youtube_url():
    assert is_youtube_url("https://www.youtube.com/watch?v=1aaa1a11a1A") == True
    assert is_youtube_url("/start") == False
    assert is_youtube_url("some lalala") == False
