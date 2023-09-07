import os
import json
import datetime

from Synology import Synology

print("Welcome to Synology")

f = "config/config.json"
if os.path.isfile(f):
    with open(f) as file:
        data = json.load(file)
    data["SSL_VERIFY"] = data["SSL_VERIFY"] == "True"
else:
    data = {
        "URL": os.getenv("URL"),
        "USER": os.getenv("USER"),
        "PSWD": os.getenv("PSWD"),
        "SSL_VERIFY": os.getenv("SSL_VERIFY") == "True",
        "ALBUM_NAME": os.getenv("ALBUM_NAME"),
        "ALBUM_NAME_UNRATED": os.getenv("ALBUM_NAME_UNRATED")
    }

# TAGGING PHOTOS
with Synology(
    base_url=data["URL"],
    password=data["PSWD"],
    user=data['USER'],
    ssl_verify=data["SSL_VERIFY"]
) as synology:
    photos = synology.get_photos()
    photo_tags = synology.get_photo_tags()

    # Gathering picture tag info and creating new tags if required
    tags_to_be_added = {}
    for p in photos[0:10]:
        # print(f"{p['id']}: {p['filename']}")
        photo_id = p['id']
        tags = [t['name'] for t in p['additional']["tag"]]
        tag_to_be_set = datetime.datetime.fromtimestamp(p['time'], datetime.timezone.utc).strftime('%m:%d')

        if tag_to_be_set == "02:29":
            tag_to_be_set = "02:28"

        if tag_to_be_set in tags:
            # print('picture already properly tagged')
            continue

        if tag_to_be_set not in tags_to_be_added:
            tags_to_be_added[tag_to_be_set] = []
        tags_to_be_added[tag_to_be_set].append(photo_id)

    # Tagging photo that do not yet have a tag (in photos_to_tag)
    for tag in tags_to_be_added:
        if tag not in photo_tags:
            photo_tags.update(synology.new_photo_tag(tag))
        tag_id = photo_tags[tag]
        synology.tag_photos(tags_to_be_added[tag], tag_id)


# UPDATING ALBUMS
today_tag_id = None
today_tag = datetime.date.today().strftime('%m:%d')
if today_tag == "02:29":
    today_tag = "02:28"
# today_tag = "08:01"

with Synology(
    base_url=data["URL"],
    password=data["PSWD"],
    user=data['USER'],
    ssl_verify=data["SSL_VERIFY"]
) as synology:
    albums = synology.get_photo_albums()
    photo_tags = synology.get_photo_tags()

    if today_tag in photo_tags:
        today_tag_id = photo_tags[today_tag]

    for album in albums:
        conditions = {'time': [{'start_time': 4123353600}], 'user_id': 0}
        if album["name"] == data["ALBUM_NAME"]:
            album_id = album["id"]
            if today_tag_id is not None:
                conditions = {'general_tag': [today_tag_id], 'general_tag_policy': 'or', 'rating': [2, 3, 4, 5], 'user_id': 0}
        elif album["name"] == data["ALBUM_NAME_UNRATED"]:
            album_id = album["id"]
            if today_tag_id is not None:
                conditions = {'general_tag': [today_tag_id], 'general_tag_policy': 'or', 'rating': [0], 'user_id': 0}
        else:
            album_id = None

        if album_id is not None:
            synology.update_photo_album_condition(album_id, conditions)
