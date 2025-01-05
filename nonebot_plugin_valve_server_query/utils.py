import socket
import asyncio
from re import match


async def domain_to_ip(ip_port: str):
    pattern = r"([^:]+):(\d+)"
    domain = match(pattern, ip_port).group(1)
    port = match(pattern, ip_port).group(2)
    loop = asyncio.get_event_loop()
    try:
        ip = await loop.run_in_executor(None, socket.gethostbyname, domain)
        return f"{ip}:{port}"
    except socket.gaierror:
        return ip_port


async def mask_player_name(name: str):
    if len(name) == 2:
        return name[0] + "*"
    elif len(name) > 2:
        return name[0] + "*" * (len(name) - 2) + name[-1]
    else:
        return name
