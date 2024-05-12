import json
from pathlib import Path
from typing import List
from nonebot.log import logger

valve_path = Path.cwd() / "data/valve"
json_path = valve_path / "authority.json"


class ValveAuthorityJson:
    def __init__(self):
        json_exist: bool = Path(json_path).exists()
        if json_exist == True:
            logger.info("配置文件存在,正在加载权限配置")
            with open(json_path, "r") as json_file:
                authority_data = json.load(json_file)
        else:
            logger.info("配置文件不存在，请配置")
            authority_data = {}
            with open(json_path, "w") as json_file:
                json.dump(authority_data, json_file, ensure_ascii=False)
        self.authority_data = authority_data

    def get_group_name(self) -> List[str]:
        group_name_list = []
        for group_name in self.authority_data.keys():
            group_name_list.append(group_name)
        return group_name_list

    def get_group_administrators(self, group_name) -> List[str]:
        return [administrator for administrator in self.authority_data[group_name]]

    def get_all_administrators(self) -> List[str]:
        group_name_list = self.get_group_name()
        administrators = []
        for group_name in group_name_list:
            group_administrators = authority_json.get_group_administrators(group_name)
            administrators.extend(group_administrators)
        return administrators


authority_json = ValveAuthorityJson()
