from typing import Dict, Union, Type

from jsonargparse import ArgumentParser

from psync.command import PsyncBaseCommand
from psync.init import InitCommand
from psync.push_pull import PushCommand, PullCommand
from psync.remotes import PsyncRemotesCommand


class PsyncApplication:
    commands: Dict[str, Union[Type[PsyncBaseCommand], PsyncBaseCommand]] = dict(
        remotes=PsyncRemotesCommand,
        init=InitCommand,
        push=PushCommand,
        pull=PullCommand,
    )

    def get_parser(self) -> ArgumentParser:
        parser = ArgumentParser()

        subcommands = parser.add_subcommands(dest="cmd")
        for name, command in self.commands.items():
            if not isinstance(command, PsyncBaseCommand):
                command = command()
                self.commands[name] = command

            command.fill_parser(subcommands)

        return parser

    def run(self, args):
        command = args.cmd
        command_config = getattr(args, command)
        self.commands[command].run(command_config)


def run():
    app = PsyncApplication()
    args = app.get_parser().parse_args()
    app.run(args)
