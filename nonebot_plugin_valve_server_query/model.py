from pydantic import BaseModel
from typing import Optional, List


class PlayerInformationConfig(BaseModel):
    name: str
    score: int
    duration: str


class ServerInformationConfig(BaseModel):
    game_name: str
    server_name: str
    platform: str
    version: str
    map_name: str
    player_count: int
    max_players: int
    ping: int
    players: Optional[List[PlayerInformationConfig]] = []


class IDFile(BaseModel):
    file_name: str
    file_id: str
    file_size: int


class URLFile(BaseModel):
    file_name: str
    file_url: str
    file_size: int
