from knock import KNOCKPY

domain = 'boc.cn'

results = KNOCKPY(domain, dns=None, useragent=None, timeout=None, threads=None, recon=True, bruteforce=True, wordlist=None)

print (results)

domain_list = []
ip_list = []
for item in results:
    domain_list.append(item['domain'])
    ip_list += item['ip']

print(domain_list)
print(len(domain_list))

print(len(ip_list))
