FROM docker.io/library/python:slim-buster

WORKDIR /app

COPY requirements.txt /app/requirements.txt

RUN apt-get update && apt-get install -y curl &&  \
    curl -L https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp -o /usr/local/bin/yt-dlp &&  \
    chmod a+rx /usr/local/bin/yt-dlp &&  \
    apt install ffmpeg -y &&  \
    apt-get autoremove -y  &&  \
    apt-get clean  &&  \
    rm -rf /var/lib/apt/lists/* &&  \
    pip install -r requirements.txt &&  \
    groupadd -g 10000 nonroot && \
    useradd -u 10000 -g 10000 -s /bin/bash -m nonroot

COPY ./app/main.py /app/main.py

USER nonroot:nonroot
CMD ["python3", "/app/main.py"]
