from a2s import ainfo, aplayers, SourceInfo, Player
from .model import ServerInformationConfig, PlayerInformationConfig
from asyncio.exceptions import TimeoutError
from .database import valve_db
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
                name=player_info.name,
                score=(
                    f"+{player_info.score}"
                    if player_info.score >= 0
                    else f"{player_info.score}"
                ),
                duration=f"{int(player_info.duration//3600)}h{int(player_info.duration% 3600 // 60)}m{int(player_info.duration) % 60}s",
            )
        )
    return ServerInformationConfig(
        game_name=server_info.game,
        server_name=server_info.server_name,
        platform=(
            "Linux"
            if server_info.platform == "l"
            else (
                "Windows"
                if server_info.platform == "w"
                else ("macOS" if server_info.platform == "m" else "Unknown")
            )
        ),
        version=server_info.version,
        map_name=server_info.map_name,
        player_count=server_info.player_count,
        max_players=server_info.max_players,
        ping=round(server_info.ping * 1000),
        players=players,
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
            game_name=server_info.game,
            server_name=server_info.server_name,
            platform=(
                "Linux"
                if server_info.platform == "l"
                else (
                    "Windows"
                    if server_info.platform == "w"
                    else ("macOS" if server_info.platform == "m" else "Unknown")
                )
            ),
            version=server_info.version,
            map_name=server_info.map_name,
            player_count=server_info.player_count,
            max_players=server_info.max_players,
            ping=round(server_info.ping * 1000),
        ),
    )


async def queries_group_info(
    group_name: str,
) -> list[tuple[int, ServerInformationConfig | None]]:
    server_list = valve_db.get_valve_servers(group_name)
    tasks = [queries_info(id, ip, port) for id, ip, port in server_list]
    result = await asyncio.gather(*tasks, return_exceptions=True)
    return result
