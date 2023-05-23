from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
from datetime import date
from config import comunity_token
from main import *
from database import add_worksheet, find_worksheets


class BotInterface:

    def __init__(self, token):
        self.bot = vk_api.VkApi(token=token)
        user_info = tools.get_profile_info()
        user_id = user_info[0]['id']

    def message_send(self, user_id, message=None, attachment=None):
        self.bot.method('messages.send',
                        {'user_id': user_id,
                         'message': message,
                         'random_id': get_random_id(),
                         'attachment': attachment
                         })

    def get_search_city(self, user_id):
        try:
            city_id = user_info[0]['city']['id']

        except KeyError:
            self.message_send(user_id, message='Укажите город для поиска:')

            longpoll = VkLongPoll(self.bot)
            for event in longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    city_title = event.text.capitalize()

                    try:
                        city = tools.ext_api.method('database.getCities',
                                                    {'q': city_title
                                                     })

                        city_id = city['items'][0]['id']
                        break

                    except KeyError:
                        self.message_send(user_id, message='Город не найден')
                        return

        return city_id

    def get_search_sex(self, user_id):
        try:
            user_sex = user_info[0]['sex']
            if user_sex == 1:
                sex = 2
            elif user_sex == 2:
                sex = 1

        except KeyError:
            self.message_send(user_id, message='Укажите пол партнера для поиска:')

            longpoll = VkLongPoll(self.bot)
            for event in longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    sex_title = event.text.lower()
                    if sex_title == 'женский' or 'жен' or 'ж':
                        sex = 1
                    elif sex_title == 'мужской' or 'муж' or 'м':
                        sex = 2
                    else:
                        self.message_send(event.user_id, 'пол не определен')

        return sex

    def get_search_age(self, user_id):
        try:
            bdate = user_info[0]['bdate'].split('.')
            born = date(int(bdate[2]), int(bdate[1]), int(bdate[0]))
            today = date.today()
            age = today.year - born.year - ((today.month, today.day) < (born.month, born.day))

        except KeyError:
            self.message_send(user_id, message='Укажите ваш возраст:')

            longpoll = VkLongPoll(self.bot)
            for event in longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    age = event.text

        if (age - 5) >= 18:
            age_from = age - 5
        else:
            age_from = 18

        age_to = age + 5

        search_age = {'age_from': age_from, 'age_to': age_to}

        return search_age

    def handler(self, offset=0):
        longpoll = VkLongPoll(self.bot)
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                if event.text.lower() == 'привет':
                    self.message_send(event.user_id, 'Добрый день')

                elif event.text.lower() == 'поиск':
                    city_id = self.get_search_city(user_id)
                    sex = self.get_search_sex(user_id)
                    age_from = self.get_search_age(user_id)['age_from']
                    age_to = self.get_search_age(user_id)['age_to']

                    result = tools.users_search(city_id, sex, age_from, age_to, offset)
                    self.message_send(event.user_id, 'Анкеты  подобраны, для просморта нажите "далее"')

                elif event.text.lower() == 'далее':
                    for worksheet in result:
                        if find_worksheets(worksheet['id']) == 0:
                            self.message_send(event.user_id, f"{worksheet['name']} \n"
                                                             f"vk.com/id{worksheet['id']}")
                            add_worksheet(worksheet['id'])
                            media_list = bot.get_media(worksheet['id'])

                            for media in media_list:
                                self.message_send(event.user_id, attachment=media)

                            result.remove(worksheet)
                            break

                        else:
                            result.remove(worksheet)
                            continue

                    if not result:
                        self.message_send(event.user_id, 'Для поиска новых анкет нажмите "поиск"')
                        offset += 10

                else:
                    self.message_send(event.user_id, 'неизвестная команда ')

    def get_media(self, owner_id):
        photos = tools.photos_get(owner_id)
        media_list = []
        for num, item in enumerate(photos):
            owner_id = item[1]['owner_id']
            photo_id = item[1]['photo_id']
            media = 'photo' + str(owner_id) + '_' + str(photo_id)
            media_list.append(media)
            if num == 2:
                break

        return media_list


if __name__ == '__main__':
    bot = BotInterface(comunity_token)
    bot.handler()
