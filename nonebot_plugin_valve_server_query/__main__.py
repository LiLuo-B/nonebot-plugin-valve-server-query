from nonebot.params import CommandArg, CommandStart, RawCommand
from .model import ServerInformationConfig
from .queries import queries_server_info, queries_group_info
from .check import is_valid_address, is_valid_port, is_valid_address_port
from .database import sq_L4D2
from .image import server_info_img, group_info_img
from .file import get_file_info, is_json_file, parse_json_file

from nonebot import on_command, on_message
from nonebot.adapters.onebot.v11 import (
    MessageSegment,
    Event,
    PrivateMessageEvent,
    Bot,
)
from nonebot.adapters.onebot.v11.message import Message

l4d2_server_add = on_command("求生服添加")
l4d2_server_list = on_command("求生服列表")
l4d2_server_del = on_command("求生服删除")
l4d2_server_update = on_command("求生服更新")
l4d2_server_queries = on_command(
    "connect",
    aliases={server_group[0] for server_group in sq_L4D2.get_l4d2_groups_name()},
)


@l4d2_server_add.handle()
async def _(args: Message = CommandArg()):
    if data := args.extract_plain_text():
        data_list: list = data.split()
        if len(data_list) == 4:
            group_name: str = data_list[0]
            server_id_str: str = data_list[1]
            if server_id_str.isdigit():
                server_id = int(server_id_str)
                if is_valid_address(server_ip := data_list[2]):
                    server_port = data_list[3]
                    if is_valid_port(server_port):
                        if sq_L4D2.judge_l4d2_server(group_name, server_id):
                            await l4d2_server_add.finish("该ID已存在")
                        else:
                            sq_L4D2.add_l4d2_server(
                                group_name, server_id, server_ip, server_port
                            )
                            await l4d2_server_add.finish("添加成功")
                    else:
                        await l4d2_server_add.finish("端口号错误")
                else:
                    await l4d2_server_add.finish("IP错误")
            else:
                await l4d2_server_add.finish("ID应为整数")
        else:
            await l4d2_server_add.finish("参数数量错误（呆呆 1 127.0.0.1 25535）")
    else:
        await l4d2_server_add.finish(
            "请输入组名、ID、IP、端口号（呆呆 1 127.0.0.1 25535）"
        )


@l4d2_server_list.handle()
async def _(args: Message = CommandArg()):
    if data := args.extract_plain_text():
        group_name: str = data
        servers_info: list = sq_L4D2.get_l4d2_servers(group_name)
        if servers_info:
            message_text = ""
            for server_info in servers_info:
                message_text += (
                    f"id:{server_info[0]} 地址:{server_info[1]}:{server_info[2]}\n"
                )
            await l4d2_server_list.finish(message_text)
        else:
            await l4d2_server_list.finish("该组不存在")


@l4d2_server_del.handle()
async def _(args: Message = CommandArg()):
    if data := args.extract_plain_text():
        data_list: list = data.split()
        if len(data_list) == 2:
            group_name: str = data_list[0]
            server_id_str: str = data_list[1]
            if server_id_str.isdigit():
                server_id = int(server_id_str)
                servers_info: list = sq_L4D2.get_l4d2_servers(group_name)
                if servers_info:
                    for server_info in servers_info:
                        if server_info[0] == server_id:
                            sq_L4D2.del_l4d2_server(group_name, server_id)
                            await l4d2_server_del.finish("删除成功")
                    await l4d2_server_del.finish("该ID不存在")
                else:
                    await l4d2_server_del.finish("该组不存在")
            else:
                await l4d2_server_del.finish("ID应为整数")
        else:
            await l4d2_server_del.finish("参数数量错误（呆呆 1）")
    else:
        await l4d2_server_del.finish("请输入组名、ID（呆呆 1或呆呆 1 2 3 4）")


@l4d2_server_update.handle()
async def _(args: Message = CommandArg()):
    if data := args.extract_plain_text():
        data_list: list = data.split()
        if len(data_list) == 4:
            group_name: str = data_list[0]
            server_id_str: str = data_list[1]
            if server_id_str.isdigit():
                server_id = int(server_id_str)
                if is_valid_address(server_ip := data_list[2]):
                    server_port = data_list[3]
                    if is_valid_port(server_port):
                        if sq_L4D2.judge_l4d2_server(group_name, server_id):
                            sq_L4D2.update_l4d2_server(
                                group_name, server_id, server_ip, server_port
                            )
                            await l4d2_server_update.finish("更新成功")
                        else:
                            await l4d2_server_update.finish("该ID不存在")
                    else:
                        await l4d2_server_update.finish("端口号错误")
                else:
                    await l4d2_server_update.finish("IP错误")
            else:
                await l4d2_server_update.finish("ID应为整数")
        else:
            await l4d2_server_update.finish("参数数量错误（呆呆 1 127.0.0.1 25535）")
    else:
        await l4d2_server_update.finish(
            "请输入组名、ID、IP、端口号（呆呆 1 127.0.0.1 25535）"
        )


@l4d2_server_queries.handle()
async def _(
    command_start: str = CommandStart(),
    raw_command: str = RawCommand(),
    args: Message = CommandArg(),
):
    if command_start:
        raw_command = raw_command.replace(command_start, "")
    msg: str = args.extract_plain_text()
    if msg:
        # 判断前缀为connect
        if raw_command == "connect":
            if is_valid_address_port(msg):
                judge = await queries_server_info(msg)
                if judge:
                    server_info: ServerInformationConfig = judge
                    img = await server_info_img(server_info)
                    await l4d2_server_queries.finish(MessageSegment.image(img))
                else:
                    await l4d2_server_queries.finish("服务器无响应")
            else:
                await l4d2_server_queries.finish()
        # 判断前缀为已录入的服组+id
        else:
            if msg.isdigit():
                if ip_port := sq_L4D2.get_l4d2_server_ip(raw_command, int(msg)):
                    server_info = await queries_server_info(ip_port)
                    if server_info == False:
                        await l4d2_server_queries.finish("服务器无响应")
                    img = await server_info_img(server_info)
                    await l4d2_server_queries.send(MessageSegment.image(img))
                    await l4d2_server_queries.finish(f"connect {ip_port}")
                else:
                    await l4d2_server_queries.finish("该ID不存在")
            else:
                await l4d2_server_queries.finish()
    # 判断前缀为已录入的服组
    else:
        group_info = await queries_group_info(raw_command)
        server_count = 0
        server_online_count = 0
        player_count = 0
        player_online_count = 0
        id_list = []
        for id, server_info in group_info:
            id_list.append(id)
            server_count += 1
            if server_info is not None:
                server_online_count += 1
                player_count += server_info.max_players
                player_online_count += server_info.player_count
        img = await group_info_img(
            raw_command,
            server_count,
            server_online_count,
            player_count,
            player_online_count,
            group_info,
        )
        await l4d2_server_queries.finish(MessageSegment.image(img))


def _rule(event: Event):
    return isinstance(event, PrivateMessageEvent)


get_json_file = on_message(rule=_rule)


@get_json_file.handle()
async def file_message_judge(event: PrivateMessageEvent, bot: Bot):
    file_info = get_file_info(str(event.get_message()))
    if file_info is not None and is_json_file(file_info.file_name):
        result = await bot.call_api("get_file", file_id=file_info.file_id)
        file_path = result["file"]
        if groups_info := parse_json_file(file_path):
            for (
                group_name,
                group_exist,
                server_count,
                server_add,
                server_del,
                server_update,
            ) in groups_info:
                if group_exist:
                    await get_json_file.send(
                        f"{group_name} 组已存在，本次更新将覆盖以往数据，新增{server_add}个，删除{server_del}个，更新{server_update}个，共计{server_count}个"
                    )
                else:
                    await get_json_file.send(
                        f"{group_name} 组为第一次加入，需重启后才能使用{group_name}指令查服，新增{server_count}个，共计{server_add}个"
                    )
        else:
            await get_json_file.finish("格式错误")
    await get_json_file.finish()
