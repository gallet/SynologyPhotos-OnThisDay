import os
import datetime

from Config import Config
from SynoToken import SynoToken
from SynoPhotos import SynoPhotos
from SynoAlbum import SynoAlbums

config = Config(
    data={
        "URL": os.getenv("URL"),
        "USER": os.getenv("USER"),
        "PSWD": os.getenv("PSWD"),
        "ALBUM_NAME": os.getenv("ALBUM_NAME"),
        "ALBUM_NAME_UNRATED": os.getenv("ALBUM_NAME_UNRATED")
    }
)

today_album_not_empty = False
today_tag = datetime.date.today().strftime('%m:%d')
if today_tag == "02:29":
    today_tag = "02:28"
# today_tag = "08:01"
# today_tag_id = None


with SynoToken(config) as syno_token:
    with SynoPhotos(syno_token, config) as photos:
        today_tag_id = photos.get_tag_id(today_tag)

        # Gathering picture tag info and creating new tags if required
        for p in photos.photo_data:
            # print(f"{p['id']}: {p['filename']}")
            photo_id = p['id']
            photo_tags = [t['name'] for t in p['additional']["tag"]]
            tag_to_be_set = datetime.datetime.fromtimestamp(p['time'], datetime.timezone.utc).strftime('%m:%d')

            if tag_to_be_set == "02:29":
                tag_to_be_set = "02:28"

            if not today_album_not_empty:
                if tag_to_be_set == today_tag:
                    today_album_not_empty = True
                if today_tag in photo_tags:
                    today_album_not_empty = True
                if today_album_not_empty:
                    print(f"Found at least 1 photo with today's tag {today_tag}")

            if tag_to_be_set in photo_tags:
                # print('picture already properly tagged')
                continue

            photos.add_photo_to_tag(photo_id, tag_to_be_set)

        # Tagging photo that do not yet have a tag (in photos_to_tag)
        for tag_id in photos.photos_to_tag:
            photos.tag_photos(photos.photos_to_tag[tag_id]["photos"], photos.photos_to_tag[tag_id]["tag"])

    with SynoAlbums(syno_token, config) as albums:
        if today_album_not_empty:
            rsp = albums.update_conditions(
                albums.get_album(config.album_name),
                {'general_tag': [today_tag_id], 'general_tag_policy': 'or', 'rating': [2, 3, 4, 5], 'user_id': 0}
            )
            print(f"{config.album_name} update: {rsp}")

            rsp = albums.update_conditions(
                albums.get_album(config.album_name_unrated),
                {'general_tag': [today_tag_id], 'general_tag_policy': 'or', 'rating': [0], 'user_id': 0}
            )
            print(f"{config.album_name_unrated} album update: {rsp}")
        else:
            conditions = {'time': [{'start_time': 4123353600}], 'user_id': 0}

            rsp = albums.update_conditions(
                albums.get_album(config.album_name),
                conditions
            )
            print(f"{config.album_name} update (empty): {rsp}")

            rsp = albums.update_conditions(
                albums.get_album(config.album_name_unrated),
                conditions
            )
            print(f"{config.album_name_unrated} album update (empty): {rsp}")
