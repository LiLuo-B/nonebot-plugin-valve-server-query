from a2s import ainfo, aplayers, SourceInfo, Player
from .model import ServerInformationConfig,PlayerInformationConfig
from asyncio.exceptions import TimeoutError
from .database import sq_L4D2
import asyncio


async def queries_server_info(ip_port: str) -> ServerInformationConfig | bool:
    ip, port = ip_port.split(":")
    try:
        players_info: list[Player] = await aplayers(address=(ip, port), timeout=5.0)
        server_info: SourceInfo = await ainfo(address=(ip, port), timeout=5.0)
    except (ConnectionRefusedError, TimeoutError):
        return False
    players: list[PlayerInformationConfig] = []
    for player_info in players_info:
        players.append(
            PlayerInformationConfig(
                player_info.name,
                player_info.score,
                player_info.duration,
            )
        )
    return ServerInformationConfig(
        server_info.server_name,
        server_info.platform,
        server_info.version,
        server_info.map_name,
        server_info.player_count,
        server_info.max_players,
        server_info.ping,
        players,
    )


async def queries_info(
    id: int, ip: str, port: int
) -> tuple[int, ServerInformationConfig | None]:
    try:
        server_info: SourceInfo = await ainfo(address=(ip, port), timeout=2.0)
    except (ConnectionRefusedError, TimeoutError):
        return (id, None)
    return (
        id,
        ServerInformationConfig(
            server_info.server_name,
            server_info.platform,
            server_info.version,
            server_info.map_name,
            server_info.player_count,
            server_info.max_players,
            server_info.ping,
            [],
        ),
    )


async def queries_group_info(
    group_name: str,
) -> list[tuple[int, ServerInformationConfig | None]]:
    server_list = sq_L4D2.get_l4d2_servers(group_name)
    tasks = [queries_info(id, ip, port) for id, ip, port in server_list]
    result = await asyncio.gather(*tasks, return_exceptions=True)
    return result
