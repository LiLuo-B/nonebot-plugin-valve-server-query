import json
import sqlite3
from typing import List
from pathlib import Path
from nonebot.log import logger

valve_path = Path.cwd() / "data/valve"
valve_db_path = valve_path / "server.db"
json_path = valve_path / "authority.json"


class ValveServerSqlite:
    def __init__(self):
        valve_path.mkdir(parents=True, exist_ok=True)
        server_db_exist: bool = valve_db_path.exists()
        self.conn = sqlite3.connect(valve_db_path)
        self.c = self.conn.cursor()
        if server_db_exist == True:
            logger.info("服务器数据库已被初始化过")
        else:
            logger.info("服务器数据库为空，正在初始化")
            self.c.execute(
                """CREATE TABLE VALVE_SERVER(
                ID INTEGER  PRIMARY KEY NOT NULL,
                GROUP_NAME  TEXT NOT NULL,
                SERVER_ID   INTEGER NOT NULL,
                SERVER_IP   TEXT NOT NULL,
                SERVER_PORT INTEGER NOT NULL
                );"""
            )
            self.c.execute(
                """CREATE TABLE VALVE_AUTHORITY(
                ID INTEGER     PRIMARY KEY NOT NULL,
                GROUP_NAME     TEXT NOT NULL,
                ADMINISTRATOR  TEXT NOT NULL
                );"""
            )
            logger.info("数据库初始化完成")
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
        self.conn = sqlite3.connect(valve_db_path)
        self.c = self.conn.cursor()
        self.del_valve_authority()
        for group_name, administrator_list in authority_data.items():
            self.add_valve_authority(group_name, administrator_list)

    # 添加组名与权限
    def add_valve_authority(self, group_name: str, administrator_list: List[str]):
        self.c.execute(
            "INSERT INTO VALVE_AUTHORITY (GROUP_NAME,ADMINISTRATOR) VALUES (?,?);",
            (group_name, " ".join(administrator_list)),
        )
        self.conn.commit()

    # 删除权限表所有组
    def del_valve_authority(self):
        self.c.execute("DELETE FROM VALVE_AUTHORITY")
        self.conn.commit()

    # 添加服务器
    def add_l4d2_server(
        self, group_name: str, server_id: int, server_ip: str, server_port: int
    ):
        self.c.execute(
            "INSERT INTO VALVE_SERVER (GROUP_NAME,SERVER_ID,SERVER_IP,SERVER_PORT) VALUES (?,?,?,?);",
            (group_name, server_id, server_ip, server_port),
        )
        self.conn.commit()

    def update_l4d2_server(
        self, group_name: str, server_id: int, server_ip: str, server_port: int
    ):
        self.c.execute(
            "UPDATE VALVE_SERVER SET SERVER_IP=?,SERVER_PORT=? WHERE GROUP_NAME=? AND SERVER_ID=?;",
            (server_ip, server_port, group_name, server_id),
        )
        self.conn.commit()

    def del_l4d2_server(self, group_name: str, server_id: int):
        self.c.execute(
            "DELETE FROM VALVE_SERVERP WHERE GROUP_NAME=? AND SERVER_ID=?;",
            (group_name, server_id),
        )
        self.conn.commit()

    def del_l4d2_servers(self, group_name: str, server_ids: list[int]):
        for server_id in server_ids:
            self.del_l4d2_server(group_name, server_id)

    # 删除服务器组的所有服务器
    def del_l4d2_group(self, group_name: str):
        self.c.execute(
            "DELETE FROM VALVE_SERVER WHERE GROUP_NAME=?;",
            (group_name,),
        )
        self.conn.commit()

    # 判断服务器是否存在
    def judge_l4d2_server(self, group_name: str, server_id: int) -> bool:
        cursor = self.c.execute(
            "SELECT GROUP_NAME,SERVER_ID FROM VALVE_SERVER WHERE GROUP_NAME=? AND SERVER_ID=?;",
            (group_name, server_id),
        )
        return bool(cursor.fetchall())

    # 获取服务器指定ID对应的ip
    def get_l4d2_server_ip(self, group_name: str, server_id: int) -> str | None:
        cursor = self.c.execute(
            "SELECT SERVER_IP,SERVER_PORT FROM VALVE_SERVER WHERE GROUP_NAME=? AND SERVER_ID=?;",
            (group_name, server_id),
        )
        if result := cursor.fetchone():
            ip, port = result
            return f"{ip}:{port}"
        else:
            return None

    # 获取指定服务器组的所有服务器地址
    def get_l4d2_servers(self, group_name: str) -> list:
        cursor = self.c.execute(
            "SELECT SERVER_ID,SERVER_IP,SERVER_PORT FROM VALVE_SERVER WHERE GROUP_NAME=? ORDER BY SERVER_ID;",
            (group_name,),
        )
        return cursor.fetchall()

    # 获取指定服务器组的所有服务器ID
    def get_l4d2_server_ids(self, group_name: str) -> list:
        cursor = self.c.execute(
            "SELECT SERVER_ID FROM VALVE_SERVER WHERE GROUP_NAME=?;",
            (group_name,),
        )
        return cursor.fetchall()

    # 获取所有服务器组名
    def get_l4d2_groups_name(self) -> list:
        cursor = self.c.execute("SELECT DISTINCT GROUP_NAME FROM VALVE_SERVER;")
        return cursor.fetchall()


valve_db = ValveServerSqlite()
