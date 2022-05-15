# ytap-python

Telegram bot which converts youtube video to telegram audio.

Uses python3, [youtube-dl](https://github.com/ytdl-org/youtube-dl), [ffmpeg](https://github.com/FFmpeg/FFmpeg), [python-telegram-bot](https://python-telegram-bot.org/), docker and docker-compose.

The original idea: https://github.com/Spmart/YTAP-Bot

# How to run

1. Create your own bot via [Bot Father in telegram](https://core.telegram.org/bots#3-how-do-i-create-a-bot)
2. Clone this repo `git clone https://github.com/alvicsam/ytap-python`
2. Place bot token in `docker-compose.yml`:

```yml
    environment:
      - BOT_TOKEN=<place_your_token_here>
```
3. Run docker compose: `docker-compose up -d --build`
