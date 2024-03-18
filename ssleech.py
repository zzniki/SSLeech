#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
from netaddr import IPNetwork
import os

import command
import settings
import fileparser
from logger import *
import json

def main():

    parser = argparse.ArgumentParser(
        prog="SSLeech",
        description="Leeches",
        epilog="python3 ssleech.py inferedomain -a 127.0.0.1 -o output.json\r\npython3 ssleech.py infdom -f hosts.txt -o output.json"
    )

    parser.add_argument("command")
    parser.add_argument("-a", "--address", type=str)
    parser.add_argument("-f", "--file", type=str)
    parser.add_argument("-p", "--port", type=int)
    parser.add_argument("-t", "--timeout", type=int)
    parser.add_argument("-th", "--threads", type=int)
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("-o", "--output", type=str)

    args = parser.parse_args()

    command.loadCommands()
    if (not args.command in command.possible):
        logErr("Command not found")
        # TODO: List possible commands
        os._exit(1)
    else:
        cmd = command.possible[args.command]

    port = args.port if args.port != None else 443
    
    if (args.file != None):
        log("Reading file...")
        addresses = fileparser.parseFile(args.file)
    elif (args.address != None):
        addresses = parseAddr(args.address, port)
    else:
        logErr("You must specify one or more addresses with -a (addr) or -f (file)")
        os._exit(1)

    log(f"Loaded {len(addresses)} addresses")

    if (args.timeout != None): settings.TIMEOUT = args.timeout
    if (args.threads != None): settings.THREADS = args.threads
    if (args.verbose == True): settings.VERBOSE = True

    log(f"Running {cmd.name}...")

    res = cmd.run(addresses)

    if (args.output != None):
        with open(args.output, "w+") as f:
            f.write(json.dumps(res))

    os._exit(1)

def parseAddr(addr: str, port: int):
    if ("/" in addr):
        return [str(x) + ":" + str(port) for x in list(IPNetwork(addr))]
    else: return [str(addr) + ":" + str(port)]

if (__name__ == "__main__"):
    main()