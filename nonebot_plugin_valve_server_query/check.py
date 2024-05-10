import re


def is_valid_address(ip_str) -> bool:
    # 定义 IP或域名的正则表达式模式
    pattern = r"^(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|[a-zA-Z0-9\-\.]+)$"
    # 使用 re.match() 函数进行匹配
    if re.match(pattern, ip_str):
        return True
    else:
        return False


def is_valid_port(port_str):
    # 定义匹配端口号的正则表达式模式
    port_pattern = (
        r"^(?:[1-9]\d{0,4}|[1-5]\d{4}|6[0-4]\d{3}|65[0-4]\d{2}|655[0-2]\d|6553[0-5])$"
    )
    # 使用 re.match() 函数进行匹配
    if re.match(port_pattern, port_str):
        return True
    else:
        return False


def is_valid_address_port(address_port_str) -> bool:
    # 定义 IP:端口 或 域名:端口 的正则表达式模式
    pattern = r"^(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|[a-zA-Z0-9\-\.]+):(?:[1-9]\d{0,4}|[1-5]\d{4}|6[0-4]\d{3}|65[0-4]\d{2}|655[0-2]\d|6553[0-5])$"
    # 使用 re.match() 函数进行匹配
    if re.match(pattern, address_port_str):
        return True
    else:
        return False
