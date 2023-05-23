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

    def users_search(self, city_id, sex, age_from, age_to, offset=None):

        try:
            profiles = self.ext_api.method('users.search',
                                           {'city_id': city_id,
                                            'age_from': age_from,
                                            'age_to': age_to,
                                            'sex': sex,
                                            'status': 6,
                                            'fields': 'relation',
                                            'count': 10,
                                            'offset': offset
                                            })

        except ApiError:
            return

        profiles = profiles['items']

        result = []
        for profile in profiles:
            try:
                relation = profile['relation']

                if profile['is_closed'] == False and relation == 6 and find_worksheets(profile['id']) == 0:
                    result.append({'name': profile['first_name'] + ' ' + profile['last_name'],
                                   'id': profile['id']
                                   })

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
