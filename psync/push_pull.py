import os
from pathlib import Path
from typing import Optional

from jsonargparse import ArgumentParser

from psync import config as pconf
from psync.command import PsyncBaseCommand
from psync.utils import run_command

CONSTS = {
    "host": "PSYNC_REMOTE_HOST",
    "remote": "PSYNC_REMOTE_PROJECT",
    "local": "PSYNC_LOCAL_PROJECT",
    "confirm": "PSYNC_ASK_CONFIRM",
    "local_host": "PSYNC_LOCAL_HOST",
    "debug": "PSYNC_DEBUG",
    "compress": "PSYNC_COMPRESS",
}


class PushPullCommand(PsyncBaseCommand):
    def parser(self) -> Optional[ArgumentParser]:
        parser = ArgumentParser(
            description="A glorified rsync which works with default remotes."
        )

        parser.add_argument("destination", default=None, nargs="?")

        parser.add_argument(
            "files", nargs="*", default=[], help="Files that need to be synced"
        )

        parser.add_argument(
            "-H",
            "--host",
            default=None,
            help=f'Remote hostname (in the form of user@host, defaults to ${CONSTS["host"]})',
        )
        parser.add_argument(
            "-r",
            "--remote",
            default=None,
            help=f'Remote destination (defaults to ${CONSTS["remote"]})',
        )
        parser.add_argument(
            "-l",
            "--local",
            default=None,
            help=f'Local source (defaults to ${CONSTS["local"]})',
        )

        parser.add_argument(
            "-x",
            "--exclude",
            nargs="+",
            type=str,
            help="Exclusion patterns provided to rsync",
        )

        parser.add_argument(
            "-p",
            "--port",
            type=int,
            default=None,
            help="SSH port to use (not needed in case of a host configured via ssh config)",
        )

        parser.add_argument(
            "-c",
            "--compress",
            action="store_true",
            help=f'Activates rsync compression (defaults to ${CONSTS["compress"]})',
        )

        parser.add_argument(
            "-n",
            "--confirm",
            action="store_true",
            help=f'Print the constructed rsync command before execution (enabled if ${CONSTS["confirm"]}) is set)',
        )

        parser.add_argument(
            "--debug",
            action="store_true",
            help=f"Prints the parsed arguments, some useful information and asks for confirmation before running the "
            f'command (enabled if ${CONSTS["debug"]}) is set)',
        )

        return parser

    def run(self, config):
        mode = self.name
        cwd = Path.cwd()

        compress_flag = "z" if config.compress else ""
        exclusions = ""

        default_exclusions = [".vscode", ".idea", ".git"]
        exclusions_list = default_exclusions + (config.exclude or [])

        for exclusion in exclusions_list:
            exclusions += f'--exclude "{exclusion}" '

        destination = config.destination

        # destination might actually be a file...
        # if that's the case, set it to None and prepend the file to the list of files
        if (cwd / destination).exists():
            config.destination = None
            config.files.insert(0, destination)

        if config.debug:
            print(config)

        dest = (
            pconf.remotes[config.destination]
            if config.destination is not None
            else pconf.default_remote
        )
        hostdata = dest.hostdata.filled
        port = config.port or hostdata.port
        custom_ssh = "" if (port is None or port == 22) else f'-e "ssh -p {port}" '

        remote = config.remote or dest.path
        local = config.local or pconf.project

        if remote is None:
            print(f"You must specify --remote or set ${CONSTS['remote']}")
            exit(1)

        if local is None:
            print(f"You must specify --local or set ${CONSTS['local']}")
            exit(1)

        local = Path(local).expanduser().absolute()
        remote = Path(remote).expanduser().absolute()

        if config.debug or os.environ.get(CONSTS["debug"]):
            print("cwd:", cwd)
            print("local:", local)
            print("remote:", remote)

        relative = cwd.relative_to(local)
        remote = str(remote / relative) + "/"
        local = str(local / relative) + "/"

        if config.debug:
            print(relative, local, remote)

        local_path = local
        remote_path = f"{hostdata.user}@{hostdata.hostname}:{remote}"

        if mode == "push":
            src, tgt = local_path, remote_path
        else:
            src, tgt = remote_path, local_path

        if len(config.files) > 0:
            src = " ".join(map(lambda f: f"{src}{f}", config.files))

        cmd = f"rsync {custom_ssh}-avh{compress_flag}P --info=progress2 {exclusions}{src} {tgt}"

        if config.confirm or pconf.general.ask_confirm or config.debug:

            print(cmd)

            choice = input("Execute? [y/n]\n>>> ")
            if choice != "y":
                print("Exiting.")
                exit(0)

        if config.debug:
            print("Executing the command")

        run_command(cmd, get_result=False)


class PushCommand(PushPullCommand):
    name = "push"


class PullCommand(PushPullCommand):
    name = "pull"
