import socket
import time
import json
import threading

# 广播地址和端口
BROADCAST_IP = "255.255.255.255"
BROADCAST_PORT = 5000
# TCP 连接端口
TCP_PORT = 6000

# 广播消息间隔时间 (秒)
BROADCAST_INTERVAL = 3

# 已发现的设备
discovered_devices = {}

# 连接状态
connected_socket = None
connected_address = None


def get_local_ip():
    """获取本机局域网 IP 地址"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # 不需要连接实际地址，只是利用创建 socket 的过程获取本机 IP
        s.connect(('10.255.255.255', 1))
        local_ip = s.getsockname()[0]
    except Exception:
        local_ip = '127.0.0.1'  # 获取不到IP时使用环回地址
    finally:
        s.close()
    return local_ip


def handle_connection(conn, addr):
    """处理连接，用于接收消息"""
    global connected_socket, connected_address
    print(f"接收到来自 {addr[0]}:{addr[1]} 的连接请求")
    connected_socket = conn
    connected_address = addr
    try:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            print(f"收到来自 {addr[0]}:{addr[1]} 的消息: {data.decode('utf-8')}")

    except Exception as e:
        print(f"处理连接时发生错误: {e}")
    finally:
        print(f"与 {addr[0]}:{addr[1]} 的连接已断开")
        conn.close()
        connected_socket = None
        connected_address = None


def start_tcp_server(local_ip):
    """启动 TCP 服务器，用于监听连接请求"""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((local_ip, TCP_PORT))
    server_socket.listen()
    print(f"TCP 服务器启动，监听端口 {TCP_PORT}...")

    try:
        while True:
            conn, addr = server_socket.accept()
            client_thread = threading.Thread(target=handle_connection, args=(conn, addr))
            client_thread.start()

    except Exception as e:
        print(f"TCP 服务器发生错误: {e}")
    finally:
        server_socket.close()


def main():
    global connected_socket, connected_address
    # 获取本机 IP 地址
    local_ip = get_local_ip()
    print(f"本机 IP 地址: {local_ip}")

    # 启动 TCP 服务器
    server_thread = threading.Thread(target=start_tcp_server, args=(local_ip,))
    server_thread.daemon = True  # 设置为守护线程，主线程退出时也退出
    server_thread.start()

    # 创建 UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

    # 设置允许广播
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    # 绑定 socket 到广播端口
    sock.bind(("", BROADCAST_PORT))

    print(f"开始监听广播端口 {BROADCAST_PORT}...")

    try:
        while True:
            # 发送广播消息
            message = {"ip": local_ip, "time": time.time()}
            message_json = json.dumps(message).encode('utf-8')
            sock.sendto(message_json, (BROADCAST_IP, BROADCAST_PORT))
            print(f"已广播: {message_json.decode('utf-8')}")

            # 接收广播消息
            while True:
              try:
                  sock.settimeout(1) # 设置接收超时时间 避免一直阻塞
                  data, addr = sock.recvfrom(1024)
                  if addr[0] != local_ip: # 忽略来自自己的广播
                    received_message = json.loads(data.decode('utf-8'))
                    if addr[0] not in discovered_devices:
                      discovered_devices[addr[0]] = received_message
                      print(f"发现设备 {addr[0]}")
                      print("输入设备IP地址连接，或者输入 s 发送消息")
              except socket.timeout:
                 break #超时跳出内循环
            # 连接逻辑
            if connected_socket:
                input_text = input("输入消息发送: ")
                if input_text:
                   connected_socket.sendall(input_text.encode('utf-8'))
            else:
                input_text = input("输入设备IP地址连接，或者输入 s 发送消息: ")
                if input_text in discovered_devices:
                    try:
                        print(f"正在连接 {input_text}:{TCP_PORT}...")
                        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        client_socket.connect((input_text, TCP_PORT))
                        print(f"连接 {input_text}:{TCP_PORT} 成功")
                        connected_socket = client_socket
                        connected_address = (input_text, TCP_PORT)
                        client_thread = threading.Thread(target=handle_connection, args=(client_socket, (input_text,TCP_PORT)))
                        client_thread.start()
                    except Exception as e:
                         print(f"连接失败: {e}")

            time.sleep(BROADCAST_INTERVAL)
    except KeyboardInterrupt:
        print("程序已停止")
    finally:
        sock.close()


if __name__ == "__main__":
    main()
