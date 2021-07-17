import os
from pathlib import Path
from typing import Optional

from jsonargparse import ArgumentParser
from omegaconf import OmegaConf

from psync.config import PsyncReplicaConfig, try_find_config_file
from psync.command import PsyncBaseCommand
from psync.host_data import HostData


class PsyncInitializedException(BaseException):
    pass


class PsyncInvalidHost(BaseException):
    def __init__(self, host: HostData):
        super().__init__(
            f"You need to provide a valid host (either host or user and hostname): {host}"
        )


class InitCommand(PsyncBaseCommand):
    name = "init"

    def parser(self) -> Optional[ArgumentParser]:
        parser = ArgumentParser()

        parser.add_argument("alias")
        parser.add_argument(
            "connection", nargs="?", help="Connection string [user@]address[:port]"
        )
        parser.add_argument("-H", "--host", type=str)
        parser.add_argument("-u", "--user", type=str)
        parser.add_argument("-p", "--port", type=int)
        parser.add_argument("-i", "--hostname", "--ip", dest="hostname", type=str)

        return parser

    def run(self, config):

        config_path = try_find_config_file(search_home=False)
        if config_path is not None:
            raise PsyncInitializedException(
                f"Found existing psync config file at {config_path}"
            )

        alias = config.alias
        host_data = self.host_from_namespace(config)

        if not host_data.is_valid():
            raise PsyncInvalidHost(host_data)

        local_replica = PsyncReplicaConfig(
            alias=alias, path=str(Path.cwd()), host=host_data
        )

        OmegaConf.save(
            dict(general=dict(local=alias), replicas={alias: local_replica}),
            ".psync.yml",
        )

    @classmethod
    def host_from_namespace(cls, config):
        if config.connection is not None:
            host = cls.parse_host(config.connection)

        else:
            if config.host is not None:
                host = HostData.from_host(config.host).filled
            else:
                host = HostData()

            if config.user is not None:
                host.user = config.user

            if config.hostname is not None:
                host.hostname = config.hostname

            if config.port is not None:
                host.port = config.port

            if host.port is None:
                host.port = 22

        return host

    @classmethod
    def parse_host(cls, host) -> HostData:
        if "@" in host:
            user, host = host.split("@")
        else:
            user = os.environ.get("USER")

        if ":" in host:
            host, port = host.split(":")
            port = int(port)
        else:
            port = 22

        return HostData(user=user, hostname=host, port=port)
