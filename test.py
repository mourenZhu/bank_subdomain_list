import socket


def try_ports(start_port, end_port, host='192.168.225.1'):
    """
    尝试打开一个在start_port和end_port之间的TCP端口。
    如果成功，返回端口号，否则返回None。
    """
    for port in range(start_port, end_port + 1):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.bind((host, port))
            sock.close()
            return port
        except socket.error as e:
            continue
            return None

# 使用示例
start_port = 1024
end_port = 65535

open_port = try_ports(start_port, end_port)
if open_port:
    print(f"找到开放的端口: {open_port}")
else:
    print("没有找到开放的端口")