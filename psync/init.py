from typing import Optional

from jsonargparse import ArgumentParser

from psync.command import PsyncBaseCommand


class InitCommand(PsyncBaseCommand):
    name = "init"

    def run(self, config):
        print("psync init config:", config)

    def parser(self) -> Optional[ArgumentParser]:
        parser = ArgumentParser()

        parser.add_argument("--path", required=True)
        parser.add_argument("--host", required=True)

        return parser
