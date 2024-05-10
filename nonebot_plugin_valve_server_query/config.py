from pydantic import BaseModel
from nonebot import get_plugin_config
from pathlib import Path
import datetime


class PlayerInformationConfig:
    def __init__(self, name: str, score: int, duration_str: float):
        self.name = name
        self.score = score
        self.duration = f"{int(duration_str)//3600}时{int(duration_str)%3600//60}分{int(duration_str)%3600%60}秒"


class ServerInformationConfig:
    def __init__(
        self,
        server_name: str,
        platform: str,
        version: str,
        map_name: str,
        player_count: int,
        max_players: int,
        ping: float,
        players: list[PlayerInformationConfig | None],
    ):
        self.server_name = server_name
        self.platform = (
            "Linux"
            if platform == "l"
            else (
                "Windows"
                if platform == "w"
                else ("macOS" if platform == "m" else "Unknown")
            )
        )
        self.version = version
        self.map_name = map_name
        self.player_count = player_count
        self.max_players = max_players
        self.ping = round(ping * 1000, 2)
        self.players = players


class CQFile:
    def __init__(self, file_name: str, file_id: str, file_size: int) -> None:
        self.file_name = file_name
        self.file_id = file_id
        self.file_size = file_size


class Config(BaseModel):
    pass


config = get_plugin_config(Config)

data_path = Path.cwd() / "data"
l4d2_path = data_path / "l4d2"
img_path = l4d2_path / "resources/img"
resources_path = Path.cwd() / "src/plugins/nonebot_plugin_l4d2_server/resources"
templates_path = resources_path / "templates"
