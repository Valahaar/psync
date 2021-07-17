import os
from pathlib import Path

from typing import Dict, Optional
from omegaconf import OmegaConf, SI
from dataclasses import dataclass

from psync.host_data import HostData


@dataclass
class PsyncReplicaConfig:
    alias: str
    path: str
    host: HostData

    @property
    def hostdata(self) -> HostData:
        return (
            HostData.from_host(self.host) if isinstance(self.host, str) else self.host
        )

    def __str__(self):
        host = self.hostdata.filled
        return f"{host.user}@{host.hostname}:{host.port} -> {self.path}"


@dataclass
class PsyncGeneralConfig:
    local: str = SI("${oc.env:PSYNC_LOCAL}")
    remote: Optional[str] = SI("${oc.env:PSYNC_LOCAL,null}")
    ask_confirm: bool = SI("${oc.decode:${oc.env:PSYNC_ASK_CONFIRM,false}}")
    compress: bool = SI("${oc.decode:${oc.env:PSYNC_COMPRESS,false}}")
    debug: bool = SI("${oc.decode:${oc.env:PSYNC_DEBUG,false}}")


@dataclass
class PsyncConfigOC:
    replicas: Dict[str, PsyncReplicaConfig]
    general: PsyncGeneralConfig = PsyncGeneralConfig()


class PsyncConfig:
    def __init__(self, oc: PsyncConfigOC, path: Path):
        self.__config = oc
        self.__config_path = path

    @property
    def general(self) -> PsyncGeneralConfig:
        return OmegaConf.to_object(self.__config.general)

    @property
    def replicas_real(self):
        return self.__config.replicas

    @property
    def replicas(self) -> Dict[str, PsyncReplicaConfig]:
        result = {}
        for alias, replica in self.__config.replicas.items():
            replica.alias = alias
            result[alias] = OmegaConf.to_object(replica)
        return result

    @property
    def local(self) -> PsyncReplicaConfig:
        return self.replicas[self.__config.general.local]

    @property
    def project(self) -> str:
        return self.local.path

    @property
    def default(self) -> str:
        return self.__config.general.remote

    @property
    def default_replica(self) -> PsyncReplicaConfig:
        if self.default is not None:
            return self.replicas[self.default]

        replicas = list(self.replicas.values())
        n = len(replicas)
        if n == 1:
            print(
                f"There is only one replica ({replicas[0]}), which should be the local replica."
            )
            exit()

        if n == 2:
            return next(
                filter(
                    lambda replica: replica.alias != self.general.local,
                    self.replicas.values(),
                )
            )

        raise ValueError(
            f"Cannot choose a default replica. Default is not set and {n} replicas have been provided."
        )

    @property
    def aliases(self):
        return list(self.replicas.keys())

    def as_yaml(self):
        return OmegaConf.to_yaml(self.__config, resolve=True)

    @property
    def path(self) -> Path:
        return self.__config_path

    def persist(self, backup: bool = True):
        if backup:
            backup_path = self.path.rename(self.path.parent / (self.path.name + ".bak"))
            print(f"Config backed up at {backup_path}")

        for replica in self.replicas_real.values():
            replica.alias = None

        OmegaConf.save(self.__config, self.path, resolve=True)


def try_find_config_file(search_home: bool = True) -> Optional[Path]:
    psync_conf_filename = ".psync.yml"

    proj_path = os.environ.get("PSYNC_LOCAL_PROJECT", None)
    if proj_path is not None:
        config_path = Path(proj_path) / psync_conf_filename
        if config_path.exists():
            return config_path
        return None

    curdir = Path.cwd()
    while (
        curdir.parent != curdir
    ):  # exits upon reaching / (root folder; because the parent of / is /)
        conf_file = curdir / psync_conf_filename
        if conf_file.exists():
            return conf_file
        curdir = curdir.parent

    if search_home:
        home_config = Path("~/.config") / psync_conf_filename

        if home_config.exists():
            return home_config

    return None


class ConfigNotFoundException(BaseException):
    pass


class NullPsyncConfig(PsyncConfig):
    def __init__(self):
        super().__init__(None, None)

    def __getattr__(self, item):
        raise ConfigNotFoundException()


def get_config() -> PsyncConfig:
    config_path = try_find_config_file()

    if config_path is None:
        return NullPsyncConfig()

    _conf = OmegaConf.load(config_path)
    schema = OmegaConf.structured(PsyncConfigOC)
    oc = OmegaConf.merge(schema, _conf)
    OmegaConf.resolve(oc)
    return PsyncConfig(oc, config_path)
