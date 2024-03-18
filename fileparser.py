import xml.dom.minidom as xml
from typing import *

def parseFile(path: str) -> List[str]:
    ext = path.split(".")[-1]

    if (ext == "xml"):
        xmlDoc = xml.parse(path)
        xmlHosts = xmlDoc.getElementsByTagName("host")

        hosts = []

        for host in xmlHosts:
            addr = host.getElementsByTagName("address")[0].getAttribute("addr")
            port = host.getElementsByTagName("port")[0].getAttribute("portid")
            hosts.append(f"{addr}:{port}")

        return hosts
    else:
        with open(path, "r") as f:
            return [x for x in list(set(f.read().split("\n"))) if x]