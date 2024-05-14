from pydantic import BaseModel
from pathlib import Path
from nonebot import get_plugin_config


class Config(BaseModel):
    a2s_path: str = Path.cwd() / "data/valve"
    

plugin_config = get_plugin_config(Config)
