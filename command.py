import os
import importlib
from typing import *

possible = {}
commands = []

def loadCommands():
    cmdFiles = os.listdir("commands")
    for cmdFile in cmdFiles:
        if (not os.path.isfile(os.path.join("commands", cmdFile))):
            continue

        moduleName = cmdFile.split(".")[0]
        path = f"commands.{moduleName}"

        module = importlib.import_module(path)
        cmd = getattr(module, "CMD")()

        commands.append(cmd)
        possible[cmd.cmd] = cmd
        for alias in cmd.aliases:
            possible[alias] = cmd

class Command(object):
    def __init__(self, name: str, cmd: str, aliases: List[str]):
        self.name: str = name
        self.cmd: str = cmd
        self.aliases: List[str] = aliases

    def run(self, addresses: List[str]): # Must override
        pass