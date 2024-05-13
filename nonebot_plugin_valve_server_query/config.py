from pydantic import BaseModel
from nonebot import get_plugin_config


class Config(BaseModel):
    pass


plugin_config = get_plugin_config(Config)