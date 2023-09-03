FROM python:3.11

ENV URL "nas.me"
ENV USER "me"
ENV PSWD "password"
ENV ALBUM_NAME "On this day"
ENV ALBUM_NAME_UNRATED "On this day (unrated)"
ENV SSL_VERIFY "True"

COPY requirements.txt /app/
COPY cron /tmp/cron
COPY run_cron.sh run_cron.sh
RUN chmod +x run_cron.sh

# install cron & requirements
RUN apt-get update &&  \
    apt-get install cron -y -qq && \
    pip install --requirement /app/requirements.txt

COPY main.py        /app/
COPY Config.py      /app/
COPY SynoAlbum.py   /app/
COPY SynologyApi.py /app/
COPY SynoPhotos.py  /app/
COPY SynoToken.py   /app/

CMD ["/run_cron.sh"]
