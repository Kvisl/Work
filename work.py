import json
import requests
import yadisk
from tqdm import tqdm
import os
from datetime import datetime, timezone
import time


class VK:
    def __init__(self, access_token_vk, user_id,  version='5.131'):
        self.token = access_token_vk
        self.id = user_id
        self.version = version

    def get_photos(self):
        params = {
            'access_token': self.token,
            'owner_id': self.id,
            'album_id': 'profile',
            'rev': 0,
            'extended': 1,
            'count': 5,
            'photo_sizes': 1,
            'v': self.version
        }

        response = requests.get(url_get_photos, params=params)
        return response.json()

    def sizes_photos(self):
        data = self.get_photos()
        photos_list = []
        count = 0
        if not os.path.exists('VKphotos'):
            os.mkdir('VKphotos')
        for photo in tqdm(data.get('response').get('items')):
            sizes = photo.get('sizes')
            if sizes:
                biggest_size = max(sizes, key=lambda size: size['width'] * size['height'])
                max_size = biggest_size['url']
                file_name = photo.get('likes').get('count')
                photo_date = datetime.fromtimestamp(photo.get('date'), timezone.utc).strftime('%Y-%m-%d')
                photo_id = photo.get('id')
                name = f"{file_name}_{photo_date}_{photo_id}.jpg"
                with open(f'VKphotos/{name}', 'wb') as file:
                    response = requests.get(max_size)
                    file.write(response.content)
                    time.sleep(0.5)
                    count += 1
                    tqdm.write(f'Загружено {count} фото в папку VKphotos')

                photos_list.append({'file_name': name,
                                    'size': biggest_size['type']})
                with open('Result_photo.json', 'w') as f:
                    json.dump(photos_list, f, indent=4)


class YandexDisk:
    def __init__(self, OAuth_token):
        self.token = OAuth_token

    def create_folder(self):
        url_create_folder = f'{url_base}/v1/disk/resources'
        params = {
            'path': f'{folder_name}'
        }
        headers = {
            'Authorization': ya_token
        }
        response1 = requests.put(url_create_folder,
                                 headers=headers,
                                 params=params)

        return response1.json()

    def upload(self, path_to_vkphoto):
        for address, dirs, files in tqdm(os.walk(path_to_vkphoto)):
            count = 0
            for file in tqdm(files):
                count += 1
                y.upload(f'{address}/{file}', f'/{folder_name}/{file}')
                print(f' Файл №{count}: {file} загружен на Яндекс Диск')


url_get_photos = 'https://api.vk.com/method/photos.get'
access_token_vk = ' '
user_id = input('Введите id пользователя VK: ')
vk = VK(access_token_vk, user_id)
vk.sizes_photos()

url_base = 'https://cloud-api.yandex.net'

ya_token = input('Введите OAuth token Яндекс Диска: ')
disk = YandexDisk(ya_token)

folder_name = input('Введите название папки(туда будут загружаться фото) на Яндекс Диске: ')
disk.create_folder()
path = os.getcwd()
folder = 'VKphotos'
path_to_vkphoto = os.path.join(path, folder)
y = yadisk.YaDisk(token=f'{ya_token}')
disk.upload(path_to_vkphoto)
