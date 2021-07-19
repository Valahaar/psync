import os
from typing import Optional

from jsonargparse import ArgumentParser

from psync.command import PsyncSubcommand, PsyncCommandWithSubcommands
from psync.config import PsyncReplicaConfig
from psync.host_data import HostData

from psync import config as pconf
from psync.utils import run_command


class ListReplica(PsyncSubcommand):
    name = "list"

    def run(self):
        default_remote = pconf.default
        local = pconf.local.alias

        for name, replica in pconf.replicas.items():
            end = ""
            if name == local:
                end = "    LOCAL"
            elif name == default_remote:
                end = "    DEFAULT"
            print(f"{name} -> {replica}{end}")


class AddReplica(PsyncSubcommand):
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

        new_remote = PsyncReplicaConfig(alias=alias, path=path, host=host_data)

        alias = new_remote.alias
        if alias in pconf.replicas:
            print(f"Replica '{alias}' exists already -> {pconf.replicas[alias]}")
            return

        print(f"Adding {new_remote} to replicas")
        pconf.replicas_real[alias] = new_remote
        pconf.persist()


class DelReplica(PsyncSubcommand):
    name = "del"

    def parser(self) -> Optional[ArgumentParser]:
        parser = ArgumentParser()
        parser.add_argument("alias")
        return parser

    def run(self, alias):
        if alias == "*":
            pconf.replicas_real.clear()
            pconf.persist()
            return

        if alias not in pconf.replicas_real:
            aliases = ", ".join(pconf.replicas_real.keys())
            print(f"{alias} not among valid remotes: {aliases}")
            return

        pconf.replicas_real.pop(alias)
        pconf.persist()


class SetupReplica(PsyncSubcommand):
    name = "setup"

    def parser(self) -> Optional[ArgumentParser]:
        parser = ArgumentParser(
            # TODO: figure help out :-)
            # help="Sets up the specified alias (or all aliases if * is provided as argument) by creating a ssh-key on "
            # "the host in case there isn't one, then copying it in case it wasn't (WARNING: requires password)"
        )
        parser.add_argument("alias")
        return parser

    def run(self, alias):
        if alias == "*":
            aliases = list(pconf.aliases)
            aliases.remove(pconf.general.local)
        else:
            if alias not in pconf.aliases:
                aliases = ", ".join(pconf.replicas_real.keys())
                print(f"{alias} not among valid remotes: {aliases}")
                return

            aliases = [alias]

        for alias_name in aliases:
            self.setup(alias_name)

    @classmethod
    def setup(cls, alias):
        replica_host = pconf.replicas[alias].hostdata
        # setup should:
        #  1) create a ssh key in the local host, if there isn't one
        #  2) ssh-copy-id the key on the remote host

        # dry-run ssh-copy-id
        #   - it returns 'ERROR: No identities found' in case no ssh key exists
        #   - it says 'All keys were skipped because they already exist on the remote system'
        #     if the key is already on the host, in which case we silently return
        first_attempt = run_command(
            f"ssh-copy-id -n {replica_host.ssh_connection}",
            get_result=True,
            from_stderr=True,
        )

        if "No identities found" in first_attempt:
            # this command creates a no-passphrase ssh key under ~/.ssh/id_rsa
            run_command('cat /dev/zero | ssh-keygen -q -N ""', get_result=False)
        elif "All keys were skipped" in first_attempt:
            print(
                f"Alias {alias} -> {replica_host} skipped because the key is already added."
            )
            return

        run_command(f"ssh-copy-id {replica_host.ssh_connection}", get_result=False)


# TODO: this requires pconf.general to actually be accessible (instead of returning a copy of the object)
# I should find a better way to handle configuration
# class DefaultReplica(PsyncSubcommand):
#     name = "default"
#
#     def parser(self) -> Optional[ArgumentParser]:
#         parser = ArgumentParser()
#         parser.add_argument("alias")
#         return parser
#
#     def run(self, alias):
#         if alias not in pconf.replicas_real:
#             aliases = ", ".join(pconf.replicas_real.keys())
#             print(f"{alias} not among valid remotes: {aliases}")
#             return
#
#         old_default = pconf.default
#         pconf.general.local = alias
#         new_default = pconf.default
#         pconf.persist()
#         print(
#             f"Replica '{new_default}' set as new default (old: '{old_default.alias}')"
#         )

PsyncReplicasCommand = PsyncCommandWithSubcommands.create(
    "replicas", (ListReplica, AddReplica, DelReplica, SetupReplica)
)
