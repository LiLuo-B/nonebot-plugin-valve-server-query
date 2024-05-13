import re
import json
import aiohttp
from .model import URLFile, IDFile
from .database import valve_db
from .authority import authority_json
from typing import Optional, List, Tuple

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:107.0) Gecko/20100101 Firefox/107.0",  # noqa: E501
}


async def url_to_msg(url: str):
    """获取URL数据的字节流"""
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, timeout=600) as response:
            if response.status == 200:
                return await response.text()
            return None


# 获取文件url
def get_file_url(message_info: dict) -> Optional[URLFile]:
    if message_info["notice_type"] == "offline_file":
        file_info: dict = message_info["file"]
        return URLFile(
            file_name=file_info["name"],
            file_url=file_info["url"],
            file_size=file_info["size"],
        )
    return None


# 获取文件信息（根据id）
def get_file_info(CQ_code: str) -> Optional[IDFile]:
    match = re.search(r"CQ:([^,]+)", CQ_code)
    if match:
        CQ_type = match.group(1)
        if CQ_type == "file":
            file_name = re.search(r"file=([^,]+)", CQ_code).group(1)
            file_id = re.search(r"file_id=([^,]+)", CQ_code).group(1)
            file_size = re.search(r"file_size=(\d+)", CQ_code).group(1)
            return IDFile(file_name=file_name, file_id=file_id, file_size=file_size)
    return None


# 判断是否为json
def is_json_file(filename: str) -> bool:
    return bool(re.match(r".*\.json$", filename, re.IGNORECASE))


# 解析json
def parse_json_file(
    user_id: str,
    json_info: str | bytes,
) -> Optional[List[Tuple[str, bool, int, int, int, int]]]:
    groups_name = [group_name[0] for group_name in valve_db.get_valve_groups_name()]
    groups_info = []
    try:
        json_data = json.loads(json_info)
        if not isinstance(json_data, dict):
            return None
        for key, value in json_data.items():
            print(key)
            print(authority_json.get_group_administrators(key))
            if not isinstance(
                value, list
            ) or user_id not in authority_json.get_group_administrators(key):
                return None
            if key in groups_name:
                is_exists = True
            else:
                is_exists = False
            old_id_list = [id[0] for id in valve_db.get_valve_server_ids(key)]
            ip_count = 0
            id_list = []
            ip_list = []
            for item in value:
                if not isinstance(item, dict):
                    return None
                ip_count += 1
                id_list.append(item["id"])
                ip_list.append(item["ip"])
            old_id_set = set(old_id_list)
            id_set = set(id_list)
            ids_update = list(old_id_set & id_set)
            ids_add = list(id_set - old_id_set)
            ids_del = list(old_id_set - id_set)
            for id in ids_del:
                valve_db.del_valve_server(key, id)
            for id in ids_update:
                ip_port = ip_list[id_list.index(id)]
                ip, port = ip_port.split(":")
                valve_db.update_valve_server(key, id, ip, port)
            for id in ids_add:
                ip_port = ip_list[id_list.index(id)]
                ip, port = ip_port.split(":")
                valve_db.add_valve_server(key, id, ip, port)
            groups_info.append(
                (key, is_exists, ip_count, len(ids_add), len(ids_del), len(ids_update))
            )
        return groups_info

    except (json.JSONDecodeError, KeyError):
        return None
