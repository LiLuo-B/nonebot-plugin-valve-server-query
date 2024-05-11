import re
import json
from .model import CQFile
from .database import sq_L4D2
from typing import Optional, List, Tuple


def get_file_info(CQ_code: str) -> Optional[CQFile]:
    match = re.search(r"CQ:([^,]+)", CQ_code)
    if match:
        CQ_type = match.group(1)
        if CQ_type == "file":
            file_name = re.search(r"file=([^,]+)", CQ_code).group(1)
            file_id = re.search(r"file_id=([^,]+)", CQ_code).group(1)
            file_size = re.search(r"file_size=(\d+)", CQ_code).group(1)
            return CQFile(file_name=file_name, file_id=file_id, file_size=file_size)
    return None


def is_json_file(filename: str) -> bool:
    return bool(re.match(r".*\.json$", filename, re.IGNORECASE))


def parse_json_file(
    file_path: str,
) -> Optional[List[Tuple[str, bool, int, int, int, int]]]:
    json_flie = open(file_path, "r")
    content = json_flie.read()
    groups_name = [group_name[0] for group_name in sq_L4D2.get_l4d2_groups_name()]
    groups_info = []
    try:
        json_data = json.loads(content)
        if not isinstance(json_data, dict):
            return None
        for key, value in json_data.items():
            if not isinstance(value, list):
                return None
            if key in groups_name:
                is_exists = True
            else:
                is_exists = False
            old_id_list = [id[0] for id in sq_L4D2.get_l4d2_server_ids(key)]
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
                sq_L4D2.del_l4d2_server(key, id)
            for id in ids_update:
                ip_port = ip_list[id_list.index(id)]
                ip, port = ip_port.split(":")
                sq_L4D2.update_l4d2_server(key, id, ip, port)
            for id in ids_add:
                ip_port = ip_list[id_list.index(id)]
                ip, port = ip_port.split(":")
                sq_L4D2.add_l4d2_server(key, id, ip, port)
            groups_info.append(
                (key, is_exists, ip_count, len(ids_add), len(ids_del), len(ids_update))
            )
        return groups_info

    except (json.JSONDecodeError, KeyError):
        return None
