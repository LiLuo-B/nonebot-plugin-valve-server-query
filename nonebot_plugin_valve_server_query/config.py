from pydantic import BaseModel
from nonebot import get_plugin_config
from pathlib import Path



class Config(BaseModel):
    pass


config = get_plugin_config(Config)

l4d2_path = Path.cwd() / "data/l4d2"
resources_path = Path(__file__).resolve().parent / "resources"
templates_path = resources_path / "templates"