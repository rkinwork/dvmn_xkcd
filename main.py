import os
import random
import logging

import requests
from dotenv import load_dotenv

XKCD_URL_TEMLATE = "http://xkcd.com/{issue}/info.0.json"
VK_API_BASE_URL = "https://api.vk.com/method/{method}"


class VkException(Exception):
    pass


def get_default_vk_parameters():
    access_token = os.getenv('USER_ACCESS_TOKEN_VK_DVMN')
    if access_token:
        return {
            'v': 5.102,
            'access_token': access_token
        }
    raise VkException("USER_ACCESS_TOKEN_VK_DVMN variable has not been set")


def get_vk_group_id():
    group_id = os.getenv('XKCD_VK_GROUP_ID')
    if group_id:
        return group_id
    raise VkException("XKCD_VK_GROUP_ID env variable has not been set")


def prep_api_url(method):
    return VK_API_BASE_URL.format(method=method)


def parse_response(response):
    # check response and parse it
    response.raise_for_status()
    result = response.json()
    if 'error' in result:
        raise VkException(f"error code {result['error']['error_code']} {result['error']['error_msg']}")
    return result


def get_wall_upload_server():
    # https://vk.com/dev/photos.getWallUploadServer
    get_wall_upload_server_uri = prep_api_url(method='photos.getWallUploadServer')
    parameters = {'group_id': get_vk_group_id(), **get_default_vk_parameters()}
    resp = requests.get(get_wall_upload_server_uri, params=parameters)
    result = parse_response(resp)
    return result['response']['upload_url']


def upload_photo_to_server(upload_url, file_path):
    with open(file_path, 'rb') as fl:
        files = {
            'photo': fl
        }
        response = requests.post(upload_url, files=files)
        response.raise_for_status()

        return response.json()


def parse_photo_names(response):
    # prepare filenames for https://vk.com/dev/wall.post
    names = []
    photos = response['response']
    for photo in photos:
        names = names + [f"photo{photo['owner_id']}_{photo['id']}"]

    return names


def save_wall_photo(parameters):
    # https://vk.com/dev/photos.saveWallPhoto
    photos_save_wall_photo_uri = prep_api_url(method='photos.saveWallPhoto')
    if 'group_id' not in parameters:
        parameters['group_id'] = get_vk_group_id()

    parameters = {**parameters,
                  **get_default_vk_parameters()}

    resp = requests.post(photos_save_wall_photo_uri, params=parameters)
    return parse_response(resp)


def post_to_wall(parameters):
    # https://vk.com/dev/wall.post
    photo_wall_post_uri = prep_api_url(method='wall.post')
    if 'owner_id' not in parameters:
        parameters['owner_id'] = f"-{get_vk_group_id()}"

    if 'from_group' not in parameters:
        parameters['from_group'] = os.getenv('XKCD_VK_WALL_POST_FROM_GROUP', 0)

    parameters = {**get_default_vk_parameters(), **parameters}
    resp = requests.post(photo_wall_post_uri, data=parameters)
    _ = parse_response(resp)


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


def publish_comic_to_group(comics_file_path, message):
    upload_url = get_wall_upload_server()
    uploaded_photo_parameters = upload_photo_to_server(upload_url, comics_file_path)
    names = parse_photo_names(save_wall_photo(uploaded_photo_parameters))
    comic_to_publish = {
        'attachments': ','.join(names),
        'message': message,
    }
    post_to_wall(comic_to_publish)


def get_comic_data_by_issue(issue=''):
    python_comics = XKCD_URL_TEMLATE.format(issue=issue)
    response = requests.get(python_comics)
    response.raise_for_status()
    comic = response.json()
    num = comic['num']
    if not issue:
        return num, None, None

    image_url = comic['img']
    picture_path = download_picture(image_url)
    title = comic['title']
    return num, picture_path, title


def main():
    latest_comic_issue_number, *_ = get_comic_data_by_issue()
    random_comic_number = random.randint(1, latest_comic_issue_number)
    _, file_path, title = get_comic_data_by_issue(random_comic_number)

    try:
        publish_comic_to_group(file_path, title)
    except (VkException, requests.HTTPError) as error:
        logging.error(f'Problems with {error}')
    finally:
        os.remove(file_path)


if __name__ == '__main__':
    load_dotenv()
    main()
