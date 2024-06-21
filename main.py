import requests
import socket
import os


dest_dir_name = "bank_ips"


def query_crt_sh(domain):
    url = f"https://crt.sh/?q={domain}&output=json"
    response = requests.get(url)
    try:
        return [result['name_value'] for result in response.json()]
    except:
        return []


def get_domain_ips(root_domain: str):
    domain_list = set()
    sub_domain_list = query_crt_sh(root_domain)
    for sub_domain in sub_domain_list:
        domain_list_ = str(sub_domain).splitlines()
        for domain_ in domain_list_:
            if "*" not in domain_:
                domain_list.add(domain_)

    print("{} 子域名数为: {}".format(root_domain, len(domain_list)))
    ip_set = set()
    for domain_ in domain_list:
        # print("ipset add icbc {}".format(icbc_domain))
        try:
            ip = socket.gethostbyname(domain_)
            ip_set.add(ip)
        except Exception as e:
            pass

    print("ip数为: {}".format(len(ip_set)))
    return ip_set


def get_bank_root_domains() -> [str]:
    domains_file_path = os.path.join(os.getcwd(), "bank_root_domains.txt")
    with open(domains_file_path, 'r') as f:
        return set(f.read().splitlines())


def make_dest_dir():
    dir_path = os.path.join(os.getcwd(), dest_dir_name)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)


if __name__ == "__main__":
    root_domain_list = get_bank_root_domains()
    make_dest_dir()
    for root_domain in root_domain_list:
        ip_list = get_domain_ips(root_domain)
        bank_ips_file_path = os.path.join(os.getcwd(), dest_dir_name, '{}.txt'.format(root_domain))
        with open(bank_ips_file_path, 'w') as f:
            f.write('\n'.join(ip_list))
            f.flush()

