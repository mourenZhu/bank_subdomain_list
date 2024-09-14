import requests
import socket
import os
import time
import sys, getopt
# from knock import KNOCKPY


ip_dest_dir_name = "bank_ips"
domain_dest_dir_name = "bank_domains"
all_bank_sub_domains_filename = "all_bank_sub_domains.txt"
all_bank_ips_filename = "all_bank_ips.txt"


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
            addrs = socket.getaddrinfo(_domain, None)
            for item in addrs:
                if item[0] == socket.AddressFamily.AF_INET:
                    _ip_set.add(item[4][0])
        except Exception as e:
            print("获取域名 {} IP时错误, {}".format(_domain, e))
            pass

    print("ip数为: {}".format(len(_ip_set)))
    _ip_list = list(_ip_set)
    _ip_list.sort()
    return _ip_list


# def get_subdomain_and_ip_list(_domain: str):
#     reconn_num = 3
#     _sub_domain_list = []
#     _ip_list = []
#     while reconn_num > 0:
#         try:
#             results = KNOCKPY(_domain, dns=None, useragent=None, timeout=None, threads=None, recon=True, bruteforce=True,
#                               wordlist=None)
#             for item in results:
#                 _sub_domain_list.append(item['domain'])
#                 _ip_list += item['ip']
#             return _sub_domain_list, _ip_list
#         except Exception as e:
#             reconn_num -= 1
#             print("获取域名{}时, 出现意外{}, 再重试{}次".format(_domain, e, reconn_num))
#     return _sub_domain_list, _ip_list


def get_bank_root_domains() -> [str]:
    domains_file_path = os.path.join(os.getcwd(), "bank_root_domains.txt")
    with open(domains_file_path, 'r', encoding='utf-8') as f:
        root_domains = list(set(f.read().splitlines()))
        for i in range(len(root_domains)):
            domain = root_domains[i]
            if "/" in domain:
                domain = domain[:domain.find('/')]
            root_domains[i] = domain.strip()
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


def write_dir_all_file_to_fir(_dir_path, _file_path):
    with open(_file_path, 'a+', newline='\n') as all_content_file:
        all_content_file.truncate(0)
        for sub_file_name in os.listdir(_dir_path):
            ban_sub_domains_file_path = os.path.join(_dir_path, sub_file_name)
            with open(ban_sub_domains_file_path, 'r') as sub_file:
                all_content_file.write(sub_file.read())


if __name__ == "__main__":
    argv = sys.argv[1:]
    try:
        opts, args = getopt.getopt(argv, "u")
    except getopt.GetoptError:
        sys.exit(2)

    # 如果执行脚本时带-u 那么只会更新banl_root_domains.txt中有，但bank_domains目录下没有的域名
    is_only_update_bank_root_domains = False
    for opt, arg in opts:
        if opt == '-u':
            is_only_update_bank_root_domains = True

    root_domain_list = get_bank_root_domains()
    make_dest_dir()

    if is_only_update_bank_root_domains:
        for bank_sub_domain_filename in os.listdir(os.path.join(os.getcwd(), domain_dest_dir_name)):
            _domain = bank_sub_domain_filename[:bank_sub_domain_filename.find('.txt')]
            if _domain in root_domain_list:
                root_domain_list.remove(_domain)
        print("开启了只更新没有记录的子域名,更新的子域名为: {}".format(root_domain_list))
    for root_domain in root_domain_list:
        sub_domain_list = get_sub_domain_list(root_domain)
        if len(sub_domain_list) > 0:
            write_list_to_file(domain_dest_dir_name, root_domain, sub_domain_list)
    #
    # for bank_sub_domain_filename in os.listdir(os.path.join(os.getcwd(), domain_dest_dir_name)):
    #     with open(os.path.join(os.getcwd(), domain_dest_dir_name, bank_sub_domain_filename), 'r', encoding='utf-8') as f:
    #         domains = f.readlines()
    #         domain_list = [x.strip() for x in domains]
    #         print("准备获取{}的IP".format(bank_sub_domain_filename))
    #         ip_list = get_ip_list(domain_list)
    #         write_list_to_file(ip_dest_dir_name, bank_sub_domain_filename[:bank_sub_domain_filename.find(".txt")], ip_list)

    # now_get_root_domain_nums = 0
    # for root_domain in root_domain_list:
    #     now_get_root_domain_nums += 1
    #     print("开始获取 {} 所有子域名和IP，现在是第 {} 个根域名".format(root_domain, now_get_root_domain_nums))
    #     sub_domain_list, ip_list = get_subdomain_and_ip_list(root_domain)
    #     if len(sub_domain_list) > 0 and len(ip_list) > 0:
    #         write_list_to_file(domain_dest_dir_name, root_domain, sub_domain_list)
    #         write_list_to_file(ip_dest_dir_name, root_domain, ip_list)

    # 把所有银行的域名都写入一个文件
    write_dir_all_file_to_fir(os.path.join(os.getcwd(), domain_dest_dir_name),
                              os.path.join(os.getcwd(), all_bank_sub_domains_filename))

    # 把所有银行的IP都写入一个文件
    # write_dir_all_file_to_fir(os.path.join(os.getcwd(), ip_dest_dir_name),
    #                           os.path.join(os.getcwd(), all_bank_ips_filename))
