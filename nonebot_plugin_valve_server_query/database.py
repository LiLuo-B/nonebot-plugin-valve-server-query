import json
import sqlite3
from pathlib import Path
from nonebot.log import logger

valve_path = Path.cwd() / "data/valve"
valve_db_path = valve_path / "server.db"


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
            logger.info("数据库初始化完成")
        self.conn = sqlite3.connect(valve_db_path)
        self.c = self.conn.cursor()

    def get_valve_group_list(self):
        cursor = self.c.execute("SELECT DISTINCT GROUP_NAME FROM VALVE_AUTHORITY;")
        return cursor.fetchall()

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
