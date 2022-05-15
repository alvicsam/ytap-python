FROM docker.io/library/python:slim-buster

WORKDIR /app

RUN apt-get update && apt-get install -y curl; \
    curl -L https://yt-dl.org/downloads/latest/youtube-dl -o /usr/local/bin/youtube-dl; \
    chmod +x /usr/local/bin/youtube-dl; \
    apt install ffmpeg -y; \
    apt-get autoremove -y ; \
    apt-get clean ; \
    rm -rf /var/lib/apt/lists/*; \
    pip install python-telegram-bot; \
    groupadd -g 10000 nonroot && \
    useradd -u 10000 -g 10000 -s /bin/bash -m nonroot

COPY ./main.py /app/main.py

USER nonroot:nonroot
CMD ["python3", "/app/main.py"]
