from .model import ServerInformationConfig
from .queries import queries_server_info, queries_group_info
from .check import is_valid_address, is_valid_port, is_valid_address_port
from .database import valve_db
from .image import server_info_img, group_info_img
from .file import get_file_info, is_json_file, parse_json_file, get_file_url, url_to_msg
from .authority import authority_json
from nonebot import on_command, on_message, on_notice
from nonebot.params import CommandArg, CommandStart, RawCommand
from nonebot.adapters.onebot.v11 import (
    MessageSegment,
    Event,
    NoticeEvent,
    PrivateMessageEvent,
    Bot,
)
from nonebot.adapters.onebot.v11.message import Message


async def Permission_Check(event: Event):
    administrators = authority_json.get_all_administrators()
    if event.get_user_id() in administrators:
        return True
    return False


valve_server_add = on_command(
    "a2s添加",
    aliases={"A2s添加", "A2S添加"},
    permission=Permission_Check,
)
valve_server_list = on_command(
    "a2s列表",
    aliases={"A2s列表", "A2S列表"},
    permission=Permission_Check,
)
valve_server_del = on_command(
    "a2s删除",
    aliases={"A2s删除", "A2S删除"},
    permission=Permission_Check,
)
valve_server_update = on_command(
    "a2s更新",
    aliases={"A2s更新", "A2S更新"},
    permission=Permission_Check,
)
valve_server_queries = on_command(
    "connect",
    aliases={group_name for group_name in authority_json.get_group_name()},
)


@valve_server_add.handle()
async def _(event: Event, args: Message = CommandArg()):
    user_id = event.get_user_id()
    user_judge = authority_json.judge_administrators_server_num(user_id)
    if data := args.extract_plain_text():
        data_list: list = data.split()
        if len(data_list) == 4 and user_judge:
            group_name_list = authority_json.get_administrator_group(user_id)
            group_name: str = data_list[0]
            if group_name not in group_name_list:
                await valve_server_add.finish()
            server_id_str: str = data_list[1]
            if server_id_str.isdigit():
                server_id = int(server_id_str)
                if is_valid_address(server_ip := data_list[2]):
                    server_port = data_list[3]
                    if is_valid_port(server_port):
                        if valve_db.judge_valve_server(group_name, server_id):
                            await valve_server_add.finish("该ID已存在")
                        else:
                            valve_db.add_valve_server(
                                group_name, server_id, server_ip, server_port
                            )
                            await valve_server_add.finish(
                                f"添加成功，组名：{group_name}"
                            )
                    else:
                        await valve_server_add.finish("端口号错误")
                else:
                    await valve_server_add.finish("IP错误")
            else:
                await valve_server_add.finish("ID应为整数")
        elif len(data_list) != 4 and user_judge:
            await valve_server_add.finish("参数数量错误（呆呆 1 127.0.0.1 25535）")
        elif len(data_list) == 3 and not user_judge:
            group_name = authority_json.get_administrator_group(user_id)[0]
            server_id_str: str = data_list[0]
            if server_id_str.isdigit():
                server_id = int(server_id_str)
                if is_valid_address(server_ip := data_list[1]):
                    server_port = data_list[2]
                    if is_valid_port(server_port):
                        if valve_db.judge_valve_server(group_name, server_id):
                            await valve_server_add.finish("该ID已存在")
                        else:
                            valve_db.add_valve_server(
                                group_name, server_id, server_ip, server_port
                            )
                            await valve_server_add.finish(
                                f"添加成功，组名：{group_name}"
                            )
                    else:
                        await valve_server_add.finish("端口号错误")
                else:
                    await valve_server_add.finish("IP错误")
            else:
                await valve_server_add.finish("ID应为整数")
        elif len(data_list) != 3 and not user_judge:
            await valve_server_add.finish("参数数量错误（1 127.0.0.1 25535）")
    else:
        await valve_server_add.finish()


@valve_server_list.handle()
async def _(args: Message = CommandArg()):
    if data := args.extract_plain_text():
        group_name: str = data
        servers_info: list = valve_db.get_valve_servers(group_name)
        if servers_info:
            message_text = ""
            for server_info in servers_info:
                message_text += (
                    f"id:{server_info[0]} 地址:{server_info[1]}:{server_info[2]}\n"
                )
            await valve_server_list.finish(message_text)
        else:
            await valve_server_list.finish("该组不存在")


@valve_server_del.handle()
async def _(args: Message = CommandArg()):
    if data := args.extract_plain_text():
        data_list: list = data.split()
        if len(data_list) == 2:
            group_name: str = data_list[0]
            server_id_str: str = data_list[1]
            if server_id_str.isdigit():
                server_id = int(server_id_str)
                servers_info: list = valve_db.get_valve_servers(group_name)
                if servers_info:
                    for server_info in servers_info:
                        if server_info[0] == server_id:
                            valve_db.del_valve_server(group_name, server_id)
                            await valve_server_del.finish("删除成功")
                    await valve_server_del.finish("该ID不存在")
                else:
                    await valve_server_del.finish("该组不存在")
            else:
                await valve_server_del.finish("ID应为整数")
        else:
            await valve_server_del.finish("参数数量错误（呆呆 1）")
    else:
        await valve_server_del.finish("请输入组名、ID（呆呆 1或呆呆 1 2 3 4）")


@valve_server_update.handle()
async def _(event: Event, args: Message = CommandArg()):
    user_id = event.get_user_id()
    user_judge = authority_json.judge_administrators_server_num(user_id)
    if data := args.extract_plain_text():
        data_list: list = data.split()
        if len(data_list) == 4 and user_judge:
            group_name_list = authority_json.get_administrator_group(user_id)
            group_name: str = data_list[0]
            if group_name not in group_name_list:
                await valve_server_update.finish()
            server_id_str: str = data_list[1]
            if server_id_str.isdigit():
                server_id = int(server_id_str)
                if is_valid_address(server_ip := data_list[2]):
                    server_port = data_list[3]
                    if is_valid_port(server_port):
                        if not valve_db.judge_valve_server(group_name, server_id):
                            await valve_server_update.finish("该ID不存在")
                        else:
                            valve_db.update_valve_server(
                                group_name, server_id, server_ip, server_port
                            )
                            await valve_server_update.finish(
                                f"更新成功，组名：{group_name}"
                            )
                    else:
                        await valve_server_update.finish("端口号错误")
                else:
                    await valve_server_update.finish("IP错误")
            else:
                await valve_server_update.finish("ID应为整数")
        elif len(data_list) != 4 and user_judge:
            await valve_server_update.finish("参数数量错误（呆呆 1 127.0.0.1 25535）")
        elif len(data_list) == 3 and not user_judge:
            group_name = authority_json.get_administrator_group(user_id)[0]
            server_id_str: str = data_list[0]
            if server_id_str.isdigit():
                server_id = int(server_id_str)
                if is_valid_address(server_ip := data_list[1]):
                    server_port = data_list[2]
                    if is_valid_port(server_port):
                        if not valve_db.judge_valve_server(group_name, server_id):
                            await valve_server_update.finish("该ID不存在")
                        else:
                            valve_db.update_valve_server(
                                group_name, server_id, server_ip, server_port
                            )
                            await valve_server_update.finish(
                                f"更新成功，组名：{group_name}"
                            )
                    else:
                        await valve_server_update.finish("端口号错误")
                else:
                    await valve_server_update.finish("IP错误")
            else:
                await valve_server_update.finish("ID应为整数")
        elif len(data_list) != 3 and not user_judge:
            await valve_server_update.finish("参数数量错误（1 127.0.0.1 25535）")
    else:
        await valve_server_update.finish()


@valve_server_queries.handle()
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
                    await valve_server_queries.finish(MessageSegment.image(img))
                else:
                    await valve_server_queries.finish("服务器无响应")
            else:
                await valve_server_queries.finish()
        # 判断前缀为已录入的服组+id
        else:
            if msg.isdigit():
                if ip_port := valve_db.get_valve_server_ip(raw_command, int(msg)):
                    server_info = await queries_server_info(ip_port)
                    if server_info == False:
                        await valve_server_queries.finish("服务器无响应")
                    img = await server_info_img(server_info)
                    await valve_server_queries.finish(
                        Message(
                            [
                                MessageSegment.text(f"connect {ip_port}"),
                                MessageSegment.image(img),
                            ]
                        )
                    )
                else:
                    await valve_server_queries.finish("该ID不存在")
            else:
                await valve_server_queries.finish()
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
        await valve_server_queries.finish(MessageSegment.image(img))


def _rule(event: Event):
    return isinstance(event, PrivateMessageEvent)


# 适配LLOneBot|NapCat
get_llonebot_json_file = on_message(rule=_rule)


@get_llonebot_json_file.handle()
async def file_message_judge(event: PrivateMessageEvent, bot: Bot):
    file_info = get_file_info(str(event.get_message()))
    if file_info is not None and is_json_file(file_info.file_name):
        result = await bot.call_api("get_file", file_id=file_info.file_id)
        file_path = result["file"]
        json_file = open(file_path, "r").read()
        if groups_info := parse_json_file(json_file):
            for (
                group_name,
                group_exist,
                server_count,
                server_add,
                server_del,
                server_update,
            ) in groups_info:
                if group_exist:
                    await get_llonebot_json_file.send(
                        f"{group_name} 组已存在，本次更新将覆盖以往数据，新增{server_add}个，删除{server_del}个，更新{server_update}个，共计{server_count}个"
                    )
                else:
                    await get_llonebot_json_file.send(
                        f"{group_name} 组为第一次加入，新增{server_count}个，共计{server_add}个"
                    )
        else:
            await get_llonebot_json_file.finish("格式错误")
    await get_llonebot_json_file.finish()


# 适配Lagrange.Core Shamrock
get_lagrange_json_file = on_notice()


@get_lagrange_json_file.handle()
async def file_notice_judge(event: NoticeEvent, bot: Bot):
    file_info = get_file_url(event.model_dump())
    if file_info is not None and is_json_file(file_info.file_name):
        json_bytes = await url_to_msg(file_info.file_url)
        if json_bytes:
            if groups_info := parse_json_file(json_bytes):
                for (
                    group_name,
                    group_exist,
                    server_count,
                    server_add,
                    server_del,
                    server_update,
                ) in groups_info:
                    if group_exist:
                        await get_llonebot_json_file.send(
                            f"{group_name} 组已存在，本次更新将覆盖以往数据，新增{server_add}个，删除{server_del}个，更新{server_update}个，共计{server_count}个"
                        )
                    else:
                        await get_llonebot_json_file.send(
                            f"{group_name} 组为第一次加入，新增{server_count}个，共计{server_add}个"
                        )
            else:
                await get_llonebot_json_file.finish("格式错误")

    await get_lagrange_json_file.finish()
