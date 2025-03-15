import socket

def get_ip_address():
    hostname = socket.gethostname()


    ip_addresses = socket.getaddrinfo(hostname, None)

    ip_list = []
    for info in ip_addresses:
        ip_list.append(info[4][0])

    print(ip_list)
    return ip_list