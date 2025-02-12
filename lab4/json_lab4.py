import json
with open("/Users/nuraimuhambet/Downloads/sample-data.json", "r") as file:
        data = json.load(file)
interfaces = data["imdata"]
header = f"{'DN':<42} {'Description':<22} {'Speed':<8} {'MTU':<8}"
separator = "-" * 42 + " " + "-" * 22 + " " + "-" * 8 + " " + "-" * 8  

print("Interface Status")
print("=" * len(header))  
print(header)
print(separator)

for interface in interfaces:
    attributes = interface["l1PhysIf"]["attributes"]
    dn = attributes["dn"]
    descr = attributes["descr"] if attributes["descr"] else " "
    speed = attributes["speed"]
    mtu = attributes["mtu"]

    print(f"{dn:<50} {descr:<20} {speed:<10} {mtu:<10}")