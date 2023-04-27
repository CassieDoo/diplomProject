from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
from config import comunity_token
from main import *
from database import add_worksheet


class BotInterface:

    def __init__(self, token):
        self.bot = vk_api.VkApi(token=token)

    def message_send(self, user_id, message=None, attachment=None):
        self.bot.method('messages.send',
                        {'user_id': user_id,
                         'message': message,
                         'random_id': get_random_id(),
                         'attachment': attachment
                         })

    def handler(self):
        longpoll = VkLongPoll(self.bot)
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                if event.text.lower() == 'привет':
                    self.message_send(event.user_id, 'Добрый день')

                elif event.text.lower() == 'поиск':
                    result = tools.users_search()
                    self.message_send(event.user_id, f"{result['name']} \n"
                                                     f"vk.com/id{result['id']}")
                    add_worksheet(result['id'])
                    media_list = bot.get_media(result['id'])
                    for media in media_list:
                        self.message_send(event.user_id, attachment=media)

                else:
                    self.message_send(event.user_id, 'неизвестная команда ')

    def get_media(self, owner_id):
        photos = tools.photos_get(owner_id)
        media_list = []
        for num, x in enumerate(photos):
            owner_id = x[1]['owner_id']
            photo_id = x[1]['photo_id']
            media = 'photo' + str(owner_id) + '_' + str(photo_id)
            media_list.append(media)
            if num == 2:
                break

        return media_list


if __name__ == '__main__':
    bot = BotInterface(comunity_token)
    bot.handler()
