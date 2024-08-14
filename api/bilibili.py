import os

import requests


class Bilibili:
    def __init__(self, bili_cookie=None):
        self.fav_list = []
        self.session = requests.session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/58.0.3029.110 Safari/537.3",
            "Referer": "https://www.bilibili.com/"
        })
        if bili_cookie:
            cookie_dict = dict(x.split('=') for x in bili_cookie.split('; '))
            for key, value in cookie_dict.items():
                self.session.cookies.set(key, value)
        else:
            print("Please set BILI_COOKIE environment variable.")

    def _get_fav_pn(self, media_id, pn):
        params = {"media_id": media_id, "ps": 20, "pn": pn, "platform": "web"}
        response = self.session.get("https://api.bilibili.com/x/v3/fav/resource/list", params=params)
        return response.json()

    def _get_fav(self, media_id):
        pn = 1
        invalid = 0
        while True:
            response = self._get_fav_pn(media_id, pn)
            if response["code"] != 0:
                print(response["message"])
                break
            data = response["data"]
            medias = data["medias"]
            if not medias:
                break
            for media in medias:
                if media["attr"] != 0:
                    invalid += 1
                    continue
                self.fav_list.append(media)
            if not data["has_more"]:
                break
            pn += 1
        print("Get fav list successfully.total:%d.invalid:%d" % (len(self.fav_list), invalid))

    def get_fav_info(self, media_id):
        self._get_fav(media_id)
        if len(self.fav_list) == 0:
            print("No fav list found.")
            return
        fav_info = []
        for fav in self.fav_list:
            m, s = divmod(fav["duration"], 60)
            h, m = divmod(m, 60)
            fav_info.append(
                {
                    "bvid": fav["bvid"],
                    "title": fav["title"],
                    "cover": fav["cover"],
                    "intro": fav["intro"],
                    "link": "https://www.bilibili.com/video/%s" % fav["bvid"],
                    "duration": "%02d:%02d:%02d" % (h, m, s),
                    "upper_name": fav["upper"]["name"],
                    "upper_mid": fav["upper"]["mid"],
                    "play": fav["cnt_info"]["play"],
                    "danmaku": fav["cnt_info"]["danmaku"],
                    "collect": fav["cnt_info"]["collect"],
                }
            )
        return fav_info


if __name__ == '__main__':
    bilibili = Bilibili(bili_cookie=os.environ.get("BILI_COOKIE"))
    fav_info = bilibili.get_fav_info(os.environ.get("BILI_FAV_ID"))
