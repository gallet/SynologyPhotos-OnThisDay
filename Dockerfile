FROM python:3.11

# WORKDIR /usr/app/src

# VOLUME /config/


ADD main.py ./
ADD Config.py ./
ADD SynoAlbum.py ./
ADD SynologyApi.py ./
ADD SynoPhotos.py ./
ADD SynoToken.py ./

RUN pip install requests datetime

CMD ["python", "./main.py"]

# run this with  docker run -e "CONFIG_FILE=./"