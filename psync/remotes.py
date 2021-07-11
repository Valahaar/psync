import os
from typing import Optional

from jsonargparse import ArgumentParser

from psync.command import PsyncSubcommand, PsyncCommandWithSubcommands
from psync.config import PsyncRemoteConfig
from psync.host_data import HostData
from psync import config as pconf


class ListRemotes(PsyncSubcommand):
    name = "list"

    def run(self):
        alias_name = pconf.default
        for name, remote in pconf.remotes.items():
            default_str = "*** " if alias_name == name else ""
            print(f"{default_str}{name} -> {remote}")


class AddRemote(PsyncSubcommand):
    name = "add"

    def run(
        self,
        alias: str,
        path: str,
        host: Optional[str] = None,
        user: Optional[str] = None,
        port: Optional[int] = None,
        hostname: Optional[str] = None,
    ):

        if host is not None:
            host_data = HostData.from_host(host)
        else:
            user = user or os.environ.get("USER")
            host_data = HostData(host, user, hostname, port or 22)

        new_remote = PsyncRemoteConfig(alias=alias, path=path, host=host_data)

        alias = new_remote.alias
        if alias in pconf.remotes:
            print(f"Alias {alias} is already in use -> {pconf.remotes[alias]}")
            return

        print(f"Adding {new_remote} to remotes")
        pconf.remotes_real[alias] = new_remote
        pconf.persist()


class DelRemote(PsyncSubcommand):
    name = "del"

    def parser(self) -> Optional[ArgumentParser]:
        parser = ArgumentParser()
        parser.add_argument("alias")
        return parser

    def run(self, alias):
        if alias == "*":
            pconf.remotes_real.clear()
            pconf.persist()
            return

        if alias not in pconf.remotes_real:
            aliases = ", ".join(pconf.remotes_real.keys())
            print(f"{alias} not among valid remotes: {aliases}")
            return

        pconf.remotes_real.pop(alias)
        pconf.persist()


PsyncRemotesCommand = PsyncCommandWithSubcommands.create(
    "remotes", (ListRemotes, AddRemote, DelRemote)
)
