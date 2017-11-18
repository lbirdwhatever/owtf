import yaml
import sys


with open(sys.argv[1], 'r') as f:
    data = f.read().splitlines()

result = list()

for line in data:
    if not line.startswith("#"):
        tmp = line.replace(" ", "").split("|")
        # print tmp
        result.append({"code": tmp[0], "name": tmp[2], "hint": tmp[3].replace("?", ""), "url": tmp[4]})

with open('groups.yaml', 'w') as a:
    yaml.dump(result, a, default_flow_style=False)
