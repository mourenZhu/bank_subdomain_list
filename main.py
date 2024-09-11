import requests
import socket
import os
import time


ip_dest_dir_name = "bank_ips"
domain_dest_dir_name = "bank_domains"


def query_crt_sh(_domain):
    url = f"https://crt.sh/?q={_domain}&output=json"
    response = requests.get(url)
    try:
        return [result['name_value'] for result in response.json()]
    except:
        return []


def get_sub_domain_list(_root_domain: str):
    max_request_num = 10
    print("正在获取 {} 的子域名".format(_root_domain))
    _domain_set = set()
    _sub_domain_list = []
    # 如果获取子域名失败，重复获取10次
    i = 0
    for i in range(max_request_num):
        _sub_domain_list = query_crt_sh(_root_domain)
        if len(_sub_domain_list) > 0:
            break
        print("获取子域名失败，等待10s后重试")
        time.sleep(10)
    if i == max_request_num - 1 and len(_sub_domain_list) == 0:
        print("10次都未成功获取子域名")

    for _sub_domain in _sub_domain_list:
        """
        下面这一行代码是因为crt.sh获取子域名时，一个list[i]中有多行子域名
        """
        _real_domain_list = str(_sub_domain).splitlines()
        for _real_sub_domain in _real_domain_list:
            if "*" not in _real_sub_domain:
                _domain_set.add(_real_sub_domain)

    _domain_list = list(_domain_set)
    _domain_list.sort()
    print("{} 子域名数为: {}".format(_root_domain, len(_domain_list)))
    return _domain_list


def get_ip_list(_domain_list: [str]):
    _ip_set = set()
    for _domain in _domain_list:
        try:
            ip = socket.gethostbyname(_domain)
            _ip_set.add(ip)
        except Exception as e:
            print(e)
            pass

    print("ip数为: {}".format(len(_ip_set)))
    _ip_list = list(_ip_set)
    _ip_list.sort()
    return _ip_list


def get_bank_root_domains() -> [str]:
    domains_file_path = os.path.join(os.getcwd(), "bank_root_domains.txt")
    with open(domains_file_path, 'r') as f:
        root_domains = list(set(f.read().splitlines()))
        root_domains.sort()
        return root_domains


def make_dest_dir():
    dir_path = os.path.join(os.getcwd(), ip_dest_dir_name)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    dir_path = os.path.join(os.getcwd(), domain_dest_dir_name)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)


def write_list_to_file(_dir_name: str, _domain: str, _list: [str]):
    _file_path = os.path.join(os.getcwd(), _dir_name, '{}.txt'.format(_domain))
    with open(_file_path, 'w', newline='\n') as f:
        f.write('\n'.join(_list))
        f.flush()


if __name__ == "__main__":
    root_domain_list = get_bank_root_domains()
    make_dest_dir()
    for root_domain in root_domain_list:
        sub_domain_list = get_sub_domain_list(root_domain)
        if len(sub_domain_list) > 0:
            write_list_to_file(domain_dest_dir_name, root_domain, sub_domain_list)

        # ip_list = get_ip_list(sub_domain_list)
        # write_list_to_file(ip_dest_dir_name, root_domain, ip_list)


