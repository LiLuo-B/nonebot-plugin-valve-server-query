from pydantic import BaseModel
from pathlib import Path
from nonebot import get_plugin_config


class Config(BaseModel):
    a2s_path: str = Path.cwd() / "data/valve"
    a2s_ip: bool = False
    a2s_mask_name: bool = False


plugin_config = get_plugin_config(Config)
