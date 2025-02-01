import re
import json
import aiohttp
import aiofiles
from .model import FileInfo
from .database import valve_db
from .authority import authority_json
from typing import Optional, List, Tuple, Union
from urllib.parse import urlparse

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:107.0) Gecko/20100101 Firefox/107.0",  # noqa: E501
}


async def url_to_msg(url: str):
    """获取URL数据的字节流"""
    parsed_url = urlparse(url)
    # 如果是本地文件路径（file://）
    if parsed_url.scheme == "file":
        # 获取本地文件路径
        file_path = parsed_url.path
        try:
            # 使用 aiofiles 异步读取文件内容
            async with aiofiles.open(file_path, mode="rb") as f:
                return await f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"Local file not found: {file_path}")
        except Exception as e:
            raise Exception(f"Error reading local file: {file_path}. Error: {e}")
    # 如果是网络 URL（http:// 或 https://）
    elif parsed_url.scheme in ["http", "https"]:
        try:
            # 使用 aiohttp 异步获取网络文件内容
            url = url.replace("&amp;", "&")
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout=600) as response:
                    if response.status == 200:
                        return await response.read()  # 返回字节流
                    else:
                        raise Exception(
                            f"HTTP request failed with status {response.status}"
                        )
        except aiohttp.ClientError as e:
            raise Exception(f"Failed to fetch file from URL: {url}. Error: {e}")
    # 如果 URL 类型不支持
    else:
        raise ValueError(f"Unsupported URL scheme: {parsed_url.scheme}")


cq_pattern = r"CQ:([^,]+)"
file_pattern = r"file=([^,]+)"  # 匹配 file 的值
file_name_pattern = r"file_name=([^,]+)"  # 匹配 file_name 的值
url_pattern = r"url=([^,]+)"  # 匹配 url 的值
id_pattern = r"file_id=([^,]+)"


# 获取文件信息（根据id）
def get_file_info(CQ_code: str) -> Optional[FileInfo]:
    # 匹配 CQ 类型
    match = re.search(cq_pattern, CQ_code)
    if match:
        CQ_type = match.group(1)
        if CQ_type == "file":
            # 提取 file 或 file_name 的值
            file_match = re.search(file_pattern, CQ_code)
            file_name_match = re.search(file_name_pattern, CQ_code)
            file_name = (
                file_match.group(1)
                if file_match
                else (file_name_match.group(1) if file_name_match else None)
            )
            url_match = re.search(url_pattern, CQ_code)
            file_url = url_match.group(1) if url_match else None
            file_id_match = re.search(id_pattern, CQ_code)
            file_id = file_id_match.group(1) if file_id_match else None
            if is_json_file(file_name):
                return FileInfo(file_name=file_name, file_url=file_url, file_id=file_id)
    return None


# 判断是否为json
def is_json_file(filename: str) -> bool:
    return bool(re.match(r".*\.json$", filename, re.IGNORECASE))


# 解析json
def parse_json_file(
    user_id: str,
    json_info: Union[str, bytes],
) -> Optional[List[Tuple[str, bool, int, int, int, int]]]:
    json_info = json_info.decode("utf-8")
    groups_name = [group_name[0] for group_name in valve_db.get_valve_groups_name()]
    groups_info = []
    try:
        json_data = json.loads(json_info)
        if not isinstance(json_data, dict):
            return None
        for key, value in json_data.items():
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
