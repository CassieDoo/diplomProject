from datetime import date
import vk_api
from vk_api.exceptions import ApiError
from config import acces_token
from database import find_worksheets


class VkTools:
    def __init__(self, token):
        self.ext_api = vk_api.VkApi(token=token)

    def get_profile_info(self):
        try:
            user_info = self.ext_api.method('users.get',
                                            {'fields': 'bdate,city,sex'
                                             })
        except ApiError:
            return

        return user_info

    @staticmethod
    def get_search_info(user_info):

        city_id = user_info[0]['city']['id']

        bdate = user_info[0]['bdate'].split('.')
        born = date(int(bdate[2]), int(bdate[1]), int(bdate[0]))
        today = date.today()
        age = today.year - born.year - ((today.month, today.day) < (born.month, born.day))

        if (age - 5) >= 18:
            age_from = age - 5
        else:
            age_from = 18

        age_to = age + 5

        user_sex = user_info[0]['sex']
        if user_sex == 1:
            sex = 2
        elif user_sex == 2:
            sex = 1
        else:
            print('пол не определен')
            sex = 0

        search_info = {'city_id': city_id, 'age_from': age_from, 'age_to': age_to, 'sex': sex}

        return search_info

    def users_search(self, offset=None):
        search_info = tools.get_search_info(user_info)
        try:
            profiles = self.ext_api.method('users.search',
                                           {'city_id': search_info['city_id'],
                                            'age_from': search_info['age_from'],
                                            'age_to': search_info['age_to'],
                                            'sex': search_info['sex'],
                                            'status': 6,
                                            'fields': 'relation',
                                            'count': 10,
                                            'offset': offset
                                            })

        except ApiError:
            return

        profiles = profiles['items']

        for profile in profiles:
            try:
                relation = profile['relation']

                if profile['is_closed'] == False and find_worksheets(profile['id']) == 0 and relation == 6:
                    result = {'name': profile['first_name'] + ' ' + profile['last_name'],
                              'id': profile['id']
                              }

                else:
                    continue

            except KeyError:
                continue

        return result

    def photos_get(self, owner_id):
        photos = self.ext_api.method('photos.get',
                                     {'album_id': 'profile',
                                      'owner_id': owner_id,
                                      'extended': 'likes'
                                      })
        try:
            photos = photos['items']
        except KeyError:
            return

        photo_info = []
        for photo in photos:
            photo_info.append([int(photo['likes']['count']),
                               {'owner_id': photo['owner_id'],
                                'photo_id': photo['id']
                                }])
        photo_info.sort(key=lambda item: item[0], reverse=True)

        return photo_info


tools = VkTools(acces_token)

user_info = tools.get_profile_info()
user_id = user_info[0]['id']
