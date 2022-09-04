import os
import re
import requests
import shutil
import parser.constants as constants
from bs4 import BeautifulSoup


def parse_img(page, id_post, name_public):
    """Uploads images from a post to subfolders inside the img folder"""
    links = re.findall(r'url\((.+?)\);"', str(page))
    if links:
        # Создание папки под изображения из поста
        if not os.path.exists(f'{name_public}/img/img{id_post}'):
            os.makedirs(f'{name_public}/img/img{id_post}')

        # Проход по изображениям и их сохранение
        for i, img in enumerate(links):
            res = requests.get(img.replace('amp;', ''), stream = True)
            if res.status_code == 200:
                with open(f'{name_public}/img/img{id_post}/img{i}.jpg','wb') as f:
                    shutil.copyfileobj(res.raw, f)
            else:
                print('Адрес не верный!')


def parse_data(link):
    '''Return ID post'''
    res = requests.get(link)
    soup = BeautifulSoup(res.text, 'lxml')
    return soup.find('a', 'pi_author').attrs['data-post-id'].split('_')[0]


def parse(link, parser_img=False, parser_text=True, parser_links=False):
    """Creates a post data folder

    Params
        link(str): link to the group where the data comes from
        parser_img(bool): a value that determines whether images should be parsed
        parser_text(bool): a value that determines whether text should be parsed
        parser_link(bool): a value that determines whether links should be parsed
    """
    id_public = parse_data(link)
    name_public = link.split('/')[-1]
    # Созданение папки для отдельной группы
    if not os.path.exists(f'{name_public}'):
        os.makedirs(f'{name_public}')
        # Созданение папки под изображения
        if parser_img:
            if not os.path.exists(f'{name_public}/img'):
                os.makedirs(f'{name_public}/img')

    for index in range(0, constants.COUNT_POST, 10):
        try:
            # POST-запрос на получение постов
            page = requests.post('https://vk.com/al_wall.php?act=get_wall',headers=constants.HEADER, json=f'act=get_wall&al=1&offset={index}&onlyCache=false&owner_id={id_public}&type=own&wall_start_from={index}').json()
            soup = BeautifulSoup(page['payload'][1][0], 'lxml')
            contents = soup.find_all('div', 'post_info')
            with open(f'{name_public}/text_{name_public}.txt', 'a', encoding='utf-8') as file:

                # Проход по всем постам
                for page_post in contents:
                    soup = BeautifulSoup(str(page_post), 'lxml')
                    # id поста
                    tag_id = soup.find('div', 'wall_post_cont').get('id').replace('wpt', 'wall')
                    post_id = tag_id.split('_')[1]
                    # Парсинг изображений
                    if parser_img:
                        parse_img(page_post, post_id, name_public)

                    if parser_text or parser_links:
                        # Парсинг текста поста
                        text_content = soup.find('div', 'wall_post_text')
                        file.write(f'Пост {post_id}\n')

                        if parser_text and text_content is not None:
                            file.write(str(text_content.text) + '\n')

                        # Парсинг ссылок на посты
                        if parser_links:
                            file.write(f'https://vk.com/{name_public}?w={tag_id}\n')
        except AttributeError:
            print('Wrong data! Try again.')

