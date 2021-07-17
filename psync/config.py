import os
from pathlib import Path

from typing import Dict, Optional
from omegaconf import OmegaConf, SI
from dataclasses import dataclass

from psync.host_data import HostData


@dataclass
class PsyncRemoteConfig:
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
    ask_confirm: bool = SI("${oc.decode:${oc.env:PSYNC_ASK_CONFIRM,false}}")
    local_host: Optional[str] = SI("${oc.env:PSYNC_LOCAL_HOST,${oc.env:HOSTNAME,null}}")
    compress: bool = SI("${oc.decode:${oc.env:PSYNC_COMPRESS,false}}")
    debug: bool = SI("${oc.decode:${oc.env:PSYNC_DEBUG,false}}")


@dataclass
class PsyncConfigOC:
    remotes: Dict[str, PsyncRemoteConfig]
    general: PsyncGeneralConfig = PsyncGeneralConfig()

    project: str = SI("${oc.env:PSYNC_LOCAL_PROJECT,null}")
    default: Optional[str] = SI("${oc.env:PSYNC_DEFAULT_REMOTE,null}")


class PsyncConfig:
    def __init__(self, oc: PsyncConfigOC, path: Path):
        self.__config = oc
        self.__config_path = path

    @property
    def general(self) -> PsyncGeneralConfig:
        return OmegaConf.to_object(self.__config.general)

    @property
    def remotes_real(self):
        return self.__config.remotes

    @property
    def remotes(self) -> Dict[str, PsyncRemoteConfig]:
        result = {}
        for alias, remote in self.__config.remotes.items():
            remote.alias = alias
            result[alias] = OmegaConf.to_object(remote)
        return result

    @property
    def project(self) -> str:
        return self.__config.project

    @property
    def default(self) -> str:
        return self.__config.default

    @property
    def default_remote(self) -> PsyncRemoteConfig:
        if self.default is not None:
            return self.remotes[self.default]

        n = len(self.remotes)
        if n == 1:
            return next(iter(self.remotes.values()))

        raise ValueError(
            f"Cannot choose a default remote. Default is not set and {n} aliases have been provided."
        )

    @property
    def aliases(self):
        return list(self.remotes.keys())

    def as_yaml(self):
        return OmegaConf.to_yaml(self.__config, resolve=True)

    @property
    def path(self) -> Path:
        return self.__config_path

    def persist(self, backup: bool = True):
        if backup:
            backup_path = self.path.rename(self.path.parent / (self.path.name + ".bak"))
            print(f"Config backed up at {backup_path}")

        with self.path.open("w") as f:
            print(self.as_yaml(), file=f)


def try_find_config_file() -> Optional[Path]:
    psync_conf_filename = ".psync.yml"

    proj_path = os.environ.get("PSYNC_LOCAL_PROJECT", None)
    if proj_path is not None:
        config_path = Path(proj_path) / psync_conf_filename
        if config_path.exists():
            return config_path
        raise NotImplemented

    curdir = Path.cwd()
    while curdir.parent != curdir:  # exits upon reaching /
        conf_file = curdir / psync_conf_filename
        if conf_file.exists():
            return conf_file
        curdir = curdir.parent

    home_config = Path("~/.config") / psync_conf_filename

    if home_config.exists():
        return home_config

    raise NotImplemented


def _get_config() -> PsyncConfig:
    config_path = try_find_config_file()

    _conf = OmegaConf.load(config_path)
    schema = OmegaConf.structured(PsyncConfigOC)
    oc = OmegaConf.merge(schema, _conf)
    OmegaConf.resolve(oc)
    return PsyncConfig(oc, config_path)


config = _get_config()
