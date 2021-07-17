from typing import Dict, Union, Type

from jsonargparse import ArgumentParser

from psync.command import PsyncBaseCommand
from psync.init import InitCommand
from psync.push_pull import PushCommand, PullCommand
from psync.replicas import PsyncReplicasCommand


class PsyncApplication:
    commands: Dict[str, PsyncBaseCommand] = {}

    def get_parser(self) -> ArgumentParser:
        parser = ArgumentParser()

        subcommands = parser.add_subcommands(dest="cmd")
        for command in self.commands.values():
            command.fill_parser(subcommands)

        return parser

    def run(self):
        args = self.get_parser().parse_args()
        command = args.cmd
        command_config = getattr(args, command)
        self.commands[command].run(command_config)

    @classmethod
    def create(
        cls, *commands: Union[Type[PsyncBaseCommand], PsyncBaseCommand]
    ) -> "PsyncApplication":
        instance = cls()

        for command in commands:
            if not isinstance(command, PsyncBaseCommand):
                command = command()

            instance.commands[command.name] = command

        return instance


def run():
    PsyncApplication.create(
        PsyncReplicasCommand,
        InitCommand,
        PushCommand,
        PullCommand,
    ).run()


if __name__ == "__main__":
    run()
