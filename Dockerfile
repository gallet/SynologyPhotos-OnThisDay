FROM python:3.11

ADD main.py ./
ADD Config.py ./
ADD SynoAlbum.py ./
ADD SynologyApi.py ./
ADD SynoPhotos.py ./
ADD SynoToken.py ./

ENV URL "nas.me"
ENV USER "me"
ENV PSWD "password"
ENV ALBUM_NAME "On this day"
ENV ALBUM_NAME_UNRATED "On this day (unrated)"
ENV SSL_VERIFY "True"

RUN pip install requests datetime

CMD ["python", "./main.py"]
