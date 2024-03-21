import json
import requests
from tqdm import tqdm
from datetime import datetime, timezone


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
        set_likes = set()
        for photo in data.get('response').get('items'):
            sizes = photo.get('sizes')
            if sizes:
                biggest_size = max(sizes, key=lambda size: size['width'] * size['height'])
                max_size = biggest_size['url']
                file_name = photo.get('likes').get('count')
                photo_date = datetime.fromtimestamp(photo.get('date'), timezone.utc).strftime('%Y-%m-%d')
                if file_name in set_likes:
                    name = f'{file_name}_{photo_date}.jpg'
                else:
                    name = f'{file_name}.jpg'
                    set_likes.add(file_name)

                photos_list.append({'file_name': name,
                                    'size': biggest_size['type'],
                                    'url': max_size})
        return photos_list


class YandexDisk:
    def __init__(self, ya_token):
        self.token = ya_token

    def create_folder(self):
        url_create_folder = f'{url_base}/v1/disk/resources'
        params = {
            'path': f'{folder_name}'
        }
        headers = {
            'Authorization': f'OAuth {ya_token}'
        }
        response = requests.put(url_create_folder, headers=headers, params=params)
        return response.json()

    def upload(self, url, path_to_disk):
        url_upload = f'{url_base}/v1/disk/resources/upload'
        params = {
            'path': path_to_disk,
            'url': url,
            'overwrite': True
        }
        headers = {
            'Authorization': f'OAuth {ya_token}'
        }
        response = requests.post(url_upload, params=params, headers=headers)
        return response.json()


url_get_photos = 'https://api.vk.com/method/photos.get'
access_token_vk = ' '
user_id = input('Введите id пользователя VK: ')
vk = VK(access_token_vk, user_id)

url_base = 'https://cloud-api.yandex.net'
ya_token = input('Введите OAuth token Яндекс Диска: ')
disk = YandexDisk(ya_token)
folder_name = input('Введите название папки(туда будут загружаться фото) на Яндекс Диске: ')
disk.create_folder()

photos = vk.sizes_photos()
photos_json = []
count = 0
for photo in tqdm(photos):
    count += 1
    disk.upload(photo['url'], f'/{folder_name}/{photo["file_name"]}')
    print(f' Файл №{count}: {photo["file_name"]} загружен на Яндекс Диск')

    photos_json.append({'file_name': photo['file_name'],
                        'size': photo['size']})
    with open('Result_photo1.json', 'w') as f:
        json.dump(photos_json, f, indent=4)
