import os
import random

import requests
from dotenv import load_dotenv

XKCD_URL_TEMLATE = "http://xkcd.com/{issue}/info.0.json"
VK_API_BASE_URL = "https://api.vk.com/method/{method}"


class VkWallPhotoPublisher:
    def __init__(self):
        self.group_id = os.getenv('XKCD_VK_GROUP_ID')
        self.default_parameters = {
            'v': 5.102,
            'access_token': os.getenv('USER_ACCESS_TOKEN_VK_DVMN')
        }

    @staticmethod
    def prep_api_url(method):
        return VK_API_BASE_URL.format(method=method)

    @staticmethod
    def parse_response(response):
        # check response and parse it
        response.raise_for_status()
        result = response.json()
        if 'error' in result:
            raise Exception(f"error code {result['error']['error_code']} {result['error']['error_msg']}")
        return result

    def photos_get_wall_upload_server(self, group_id=None):
        # https://vk.com/dev/photos.getWallUploadServer
        if not group_id:
            group_id = self.group_id

        get_wall_upload_server_uri = self.prep_api_url(method='photos.getWallUploadServer')
        parameters = {'group_id': group_id, **self.default_parameters}
        resp = requests.get(get_wall_upload_server_uri, params=parameters)
        result = self.parse_response(resp)
        return result['response']['upload_url']

    @staticmethod
    def upload_photo_to_server(upload_url, file_path):
        with open(file_path, 'rb') as fl:
            files = {
                'photo': fl
            }
            response = requests.post(upload_url, files=files)
            response.raise_for_status()

            return response.json()

    @staticmethod
    def parse_photo_names(response):
        # prepare filenames for https://vk.com/dev/wall.post
        names = []
        photos = response['response']
        for photo in photos:
            names = names + [f"photo{photo['owner_id']}_{photo['id']}"]

        return names

    def photos_save_wall_photo(self, parameters):
        # https://vk.com/dev/photos.saveWallPhoto
        photos_save_wall_photo_uri = self.prep_api_url(method='photos.saveWallPhoto')
        if 'group_id' not in parameters:
            parameters['group_id'] = self.group_id

        parameters = {**parameters,
                      **self.default_parameters}

        resp = requests.post(photos_save_wall_photo_uri, params=parameters)
        return self.parse_response(resp)

    def photo_wall_post(self, parameters):
        # https://vk.com/dev/wall.post
        photo_wall_post_uri = self.prep_api_url(method='wall.post')
        if 'owner_id' not in parameters:
            parameters['owner_id'] = f"-{self.group_id}"

        if 'from_group' not in parameters:
            parameters['from_group'] = os.getenv('XKCD_VK_WALL_POST_FROM_GROUP', 0)

        parameters = {**self.default_parameters, **parameters}
        resp = requests.post(photo_wall_post_uri, data=parameters)
        _ = self.parse_response(resp)
        print("Comics has been published")


def download_picture(url, picture_name=None, image_store_path=''):
    response = requests.get(url)
    response.raise_for_status()
    if image_store_path:
        os.makedirs(image_store_path, exist_ok=True)
    if not picture_name:
        _, picture_name = url.rsplit('/', 1)
    picture_path = os.path.join(image_store_path, picture_name)
    with open(picture_path, 'wb') as file:
        file.write(response.content)
    return picture_path


def publish_comics_to_group(comics_file_path, message):
    photo_publisher = VkWallPhotoPublisher()
    upload_url = photo_publisher.photos_get_wall_upload_server()
    uploaded_photo_parameters = photo_publisher.upload_photo_to_server(upload_url, comics_file_path)
    names = photo_publisher.parse_photo_names(photo_publisher.photos_save_wall_photo(uploaded_photo_parameters))
    comics_to_publish = {
        'attachments': ','.join(names),
        'message': message,
    }
    photo_publisher.photo_wall_post(comics_to_publish)


def get_comics_by_issue(issue=''):
    python_comics = XKCD_URL_TEMLATE.format(issue=issue)
    response = requests.get(python_comics)
    response.raise_for_status()
    comics = response.json()
    num = comics['num']
    if not issue:
        return num, None, None

    image_url = comics['img']
    picture_path = download_picture(image_url)
    title = comics['title']
    return num, picture_path, title


def main():
    latest_comics, *_ = get_comics_by_issue()
    random_issue = random.randint(1, latest_comics)
    _, file_path, title = get_comics_by_issue(random_issue)

    try:
        publish_comics_to_group(file_path, title)
    finally:
        os.remove(file_path)


if __name__ == '__main__':
    load_dotenv()
    main()
