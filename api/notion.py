import os.path
import time

import requests


def _get_history(name):
    if not os.path.exists("history/%s.txt" % name):
        with open("history/%s.txt" % name, "w") as f:
            f.write("")
    with open("history/%s.txt" % name, "r") as f:
        history = f.read().splitlines()
    return history


def _set_history(name, history):
    path = "history/%s.txt" % name
    with open(path, "a+") as f:
        f.write("\n"+history)


class Notion:
    def __init__(self, token, database_id):
        self.database_id = database_id
        self.session = requests.session()
        self.session.headers.update({
            "Authorization": "Bearer " + token,
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json",
        })

        if not os.path.exists("history"):
            os.mkdir("history")
        if not os.path.exists("cover"):
            os.mkdir("cover")

    def _download_cover(self, url, bvid):
        path = './cover/%s.png' % bvid
        response = self.session.get(url)
        with open(path, 'wb') as f:
            f.write(response.content)
        return path

    def _invert_bili(self, fav):
        self._download_cover(fav['cover'], fav['bvid'])
        data = {
            "parent": {
                "database_id": self.database_id
            },
            'properties': {
                "标题": {"title": [{"type": "text", "text": {"content": fav['title']}}]},
                "地址": {"url": fav['link']},
                "封面": {"files": [
                    {
                        "external": {
                            "url": fav['cover']
                        },
                        "name": str(fav["bvid"]),
                        "type": "external"
                    }
                ]},

                "简介": {"type": "rich_text", "rich_text": [{"type": "text", "text": {"content": fav["intro"], }, }]},
                "时长": {"type": "rich_text", "rich_text": [{"type": "text", "text": {"content": fav["duration"], }, }]},
                "UP主": {"url": "https://space.bilibili.com" + str(fav['upper_mid'])},
                "收藏时间": {"type": "date", "date": {"start": time.strftime("%Y-%m-%d %H:%M:%S",
                                                                             time.localtime(fav["fav_time"]))}},
                "播放量": {"type": "number", "number": fav["play"]},
                "收藏数": {"type": "number", "number": fav["collect"]},
                "弹幕数": {"type": "number", "number": fav["danmaku"]},
            }
        }
        return self.session.request("POST", "https://api.notion.com/v1/pages", json=data)

    def add_bili(self, fav_list):
        for fav in fav_list:
            if fav["bvid"] in _get_history("bili"):
                continue
            response = self._invert_bili(fav)
            if response.status_code == 200:
                _set_history("bili", fav["bvid"])
                print("Add %s successfully." % fav["bvid"])
