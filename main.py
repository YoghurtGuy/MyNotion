import os

from api.bilibili import Bilibili
from api.notion import Notion

bilibili = Bilibili(bili_cookie=os.environ.get("BILI_COOKIE"))
fav_info = bilibili.get_fav_info(os.environ.get("BILI_FAV_ID"))
print(fav_info)
notion = Notion(token=os.environ.get("NOTION_TOKEN"), database_id=os.environ.get("NOTION_BILI"))
notion.add_bili(fav_info)
