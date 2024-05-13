from nonebot.plugin import PluginMetadata
from . import __main__ as __main__
from .config import Config

__plugin_meta__ = PluginMetadata(
    name="nonebot_plugin_valve_server_query",
    description="NoneBot插件，用于查询V社服务器，图片基于html渲染，有权限管理，支持在线更新服务器信息",
    usage="私聊或群里发送消息",
    homepage="https://github.com/LiLuo-B/nonebot-plugin-valve-server-query",
    config=Config,
    supported_adapters={"~onebot.v11"},
)
