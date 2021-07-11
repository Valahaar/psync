from typing import Dict, Optional, Iterable, Type

from jsonargparse import ArgumentParser, namespace_to_dict


class PsyncBaseCommand:
    name: str

    def run(self, config):
        raise NotImplemented

    def parser(self) -> Optional[ArgumentParser]:
        raise NotImplemented

    def fill_parser(self, subcommands):
        subcommands.add_subcommand(self.name, self.parser())

    def __repr__(self):
        return self.name


class PsyncSubcommand(PsyncBaseCommand):
    name: str

    def run(self, *args, **kwargs):
        raise NotImplemented

    def parser(self) -> Optional[ArgumentParser]:
        parser = ArgumentParser()
        parser.add_function_arguments(self.run)
        return parser


class PsyncCommandWithSubcommands(PsyncBaseCommand):
    def __init__(
        self, name: str, subcommands: Optional[Dict[str, PsyncSubcommand]] = None
    ):
        self.name = name
        self.subcommands: Dict[str, PsyncSubcommand] = subcommands or {}

    def add_subcommand(self, subcmd: PsyncSubcommand):
        self.subcommands[subcmd.name] = subcmd

    def fill_parser(self, parent_subcommands):
        parser = ArgumentParser()
        parent_subcommands.add_subcommand(self.name, parser)

        subcommands = parser.add_subcommands(dest="action")
        for name, subcmd in self.subcommands.items():
            subcommands.add_subcommand(name, subcmd.parser() or ArgumentParser())

    def run(self, config):
        action = config.action
        action_config = getattr(config, action, None)
        action_config = (
            namespace_to_dict(action_config) if action_config is not None else {}
        )
        self.subcommands[action].run(**action_config)

    @classmethod
    def create(cls, name: str, subcommands: Iterable[Type[PsyncSubcommand]]):
        subcmds = {}

        for subcommand in subcommands:
            instance = subcommand()
            subcmds[instance.name] = instance

        return cls(name, subcmds)
