import random
import socket
import struct
import time

def check_port(ip, start, end):
    if check_connection(ip):
        open_ports = []
        for port in range(start, end + 1):
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            is_online = sock.connect_ex(("127.0.0.1", port))
            if is_online == 0:
                try:
                    hostname = socket.gethostbyaddr(ip)[0]
                except Exception:
                    hostname = "Hostname Could Not Be Resolved"
                try:
                    service = socket.getservbyport(port)
                except Exception:
                    service = "Service Could Not Be Resolved"
                finally:
                    print("Open Port Detected:", ip, "   --port:", port, "   --service:", service, "   --hostname:",hostname)
                open_ports.append((port, service, hostname))
        if len(open_ports) > 0:
            print("No Other Ports Were Detected.")
        else:
            print("NO OPEN PORTS DETECTED")
    else:
        print("CONNECTION TO", ip, "COULD NOT BE ESTABLISHED")

def check_connection(ip):
    icmp_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.getprotobyname('icmp'))
    icmp_socket.settimeout(3)
    packet = create_icmp_packet(1)
    try:
        icmp_socket.sendto(packet, (ip, 1))
        icmp_socket.recv(1024)
        return True
    except socket.timeout:
        return False
    finally:
        icmp_socket.close()

def create_icmp_packet(seq):
    packet_id = random.randrange(1, 65536)
    header = struct.pack('bbHHh', 8, 0, 0, packet_id, seq)
    checksum_value = checksum(header)
    header = struct.pack('bbHHh', 8, 0, socket.htons(checksum_value), packet_id, seq)
    payload = b'hello'
    return header + payload

def checksum(packet_data):
    total = 0
    for i in range(0, len(packet_data), 2):
        word = packet_data[i] + (packet_data[i + 1] << 8) if i + 1 < len(packet_data) else packet_data[i]
        total += word
    total = (total >> 16) + (total & 0xFFFF)
    total += (total >> 16)

    return ~total & 0xFFFF

def check_delay(ip, port, req_num):
    delay_sum = 0
    pings = 0
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ip, port))
        for i in range(0, req_num):
            s_time = time.perf_counter()
            sock.send("0".encode())
            sock.recv(1024)
            e_time = time.perf_counter()
            delay = e_time - s_time
            delay_sum += delay
            if delay > 0:
                pings += 1
                print("test", i + 1, "took", delay, "seconds")
            else:
                print("test", i + 1, "failed")
    except Exception:
        print("Connection Error")
    finally:
        sock.close()
    if delay_sum > 0:
        print("Average Delay For", ip, "Is", delay_sum/pings, "Seconds")
    else:
        print("No Data Was Received")

def get(user_id, host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    sock.send(user_id.encode())
    response = sock.recv(1024)
    print(response)

def post(user_data, host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    sock.send(user_data.encode())
    response = sock.recv(1024)
    print(response)

def main():
    while True:
        input_line = input()
        cmd = input_line.split()
        match cmd[0]:
            case "-cp":
                check_port(cmd[1], int(cmd[2]), int(cmd[3]))
            case "-cc":
                if check_connection(cmd[1]):
                    print(cmd[1], "Is Online")
                else:
                    print(cmd[1], "Is Offline")
            case "-cd":
                check_delay(cmd[1], int(cmd[2]), int(cmd[3]))
            case "POST":
                post(input_line,"127.0.0.1", 8080)
            case "GET":
                get(input_line,"127.0.0.1", 8080)
            case "-help":
                print("-cp ip start_port end_port: Checks All The Ports In The Given Range For The Given IP")
                print("-cc ip: Checks If The Given IP Is Online")
                print("-cd ip port req_num: Calculates The Average Delay For The Given IP And Port Number")
                print("POST user_name user_age: Adds The Given Data To The Server")
                print("GET user_id: Returns The Given User's Data To The Client")
            case _:
                print(cmd[0], 'Could Not Be Resolved As A Command, Type -help For Assistance')

if __name__ == "__main__":
    main()