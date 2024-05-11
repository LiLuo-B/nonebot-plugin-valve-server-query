from pydantic import BaseModel
from typing import Optional, List


class PlayerInformationConfig(BaseModel):
    name: str
    score: int
    duration: float

    @property
    def duration(self) -> str:
        hours = int(self.duration) // 3600
        minutes = (int(self.duration) % 3600) // 60
        seconds = int(self.duration) % 60
        return f"{hours}h{minutes}m{seconds}s"


class ServerInformationConfig(BaseModel):
    game_name: str
    server_name: str
    platform: str
    version: str
    map_name: str
    player_count: int
    max_players: int
    ping: float
    players: Optional[List[PlayerInformationConfig]]=[]

    @property
    def platform(self) -> str:
        return (
            "Linux"
            if self.platform == "l"
            else (
                "Windows"
                if self.platform == "w"
                else ("macOS" if self.platform == "m" else "Unknown")
            )
        )

    @property
    def ping(self) -> int:
        return self.ping * 1000


class CQFile(BaseModel):
    file_name: str
    file_id: str
    file_size: int
