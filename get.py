import metadata
import json
import os
import sys
import time

import requests
import tweepy

available_saveto = ['local', 's3']

# read basic config
with open('config.json', 'r') as f:
    config = json.load(f)

    save_to = config['save_to']
    count = config['count']
    screen_name = config["username"]
    CUSTOMER_KEY = config["CUSTOMER_KEY"]
    CUSTOMER_SECRET = config["CUSTOMER_SECRET"]
    ACCESS_TOKEN = config["ACCESS_TOKEN"]
    ACCESS_TOKEN_SECRET = config["ACCESS_TOKEN_SECRET"]

if save_to not in available_saveto:
    sys.exit("save_toが不正です")

if save_to == "local":
    with open('config.json', 'r') as f:
        config = json.load(f)
        SAVE_DIR = config['save_dir_local'] + '/'

    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)

elif save_to == "s3":
    from boto3.session import Session
    with open('config.json', 'r') as f:
        config = json.load(f)
        S3_access_key = config["S3_access_key"]
        S3_secret_key = config["S3_secret_key"]
        S3_region = config["S3_region"]
        S3_bucket = config["S3_bucket"]
        S3_path = config["S3_path"] + "/"

    session = Session(aws_access_key_id=S3_access_key,
                      aws_secret_access_key=S3_secret_key,
                      region_name=S3_region)
    s3 = session.resource('s3')
    bucket_name = S3_bucket
    SAVE_DIR = S3_path
    bucket = s3.Bucket(bucket_name)

auth = tweepy.OAuthHandler(CUSTOMER_KEY, CUSTOMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)

db_path = SAVE_DIR+'/'+'favorite_tweets.sqlite'
metadata.init_db(db_path)

res = api.get_favorites(screen_name=screen_name, count=count)


def main():
    filecount = 0
    for twi in res:
        time.sleep(1)

        if 'extended_entities' in twi._json:
            metadata.insert_twi(twi._json, db_path)
            tweet_id = str(twi.id)
            for media_data in twi._json['extended_entities']['media']:
                # 複数画像対応
                if media_data['type'] == 'photo':
                    filename = format(
                        twi.user._json['screen_name']) + '-' + tweet_id + '-' + media_data['media_url_https'].split("/")[-1]
                    filepath = SAVE_DIR+filename

                    req = requests.get(
                        media_data['media_url_https']+'?format=png&name=4096x4096')
                    if req.status_code == 200:
                        if save_to == "local":
                            f = open(filepath, 'wb')
                            f.write(req.content)
                            f.close()
                        elif save_to == "s3":
                            bucket.put_object(Key=filepath, Body=req.content)
                        filecount += 1

                # 動画対応
                elif media_data['type'] == 'video':
                    video_variants = media_data['video_info']['variants']
                    bitarate = 0
                    for variant in video_variants:
                        if variant['content_type'] == 'video/mp4':
                            if variant['bitrate'] > bitarate:  # 最大720pが降ってくるはず
                                video_url = variant['url']

                    filename = format(
                        twi.user._json['screen_name']) + '-' + tweet_id + '-' + video_url.split("/")[-1].split('?')[-2]
                    filepath = SAVE_DIR+filename

                    req = requests.get(video_url)
                    if req.status_code == 200:
                        if save_to == "local":
                            f = open(filepath, 'wb')
                            f.write(req.content)
                            f.close()
                        elif save_to == "s3":
                            bucket.put_object(Key=filepath, Body=req.content)
                        filecount += 1

    print("{} files downloaded. finish at {}".format(
        filecount, time.strftime("%Y/%m/%d %H:%M:%S")))


if '__main__' == __name__:
    main()
