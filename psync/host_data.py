from dataclasses import dataclass
from typing import Optional

from psync.utils import run_command


@dataclass
class HostData:
    host: Optional[str] = None
    user: Optional[str] = None
    hostname: Optional[str] = None
    port: Optional[int] = None

    def __str__(self):
        hn = self.host or "<no-host>"
        port = self.port or 22

        port_str = ""
        if port is not None and port != 22:
            port_str = f":{port}"

        return f"{hn} --- {self.user}@{self.hostname}{port_str}"

    def remote_run_command(self, command):
        return run_command(f"ssh {self.ssh_connection} {command}")

    @classmethod
    def extract(cls, host, info):
        res = run_command(f'ssh -G {host} | grep "^{info} "')
        return res.rstrip()[len(info) + 1 :]

    @property
    def ssh_connection(self):
        filled = self.filled
        return f"-p {filled.port} {filled.user}@{filled.hostname}"

    @classmethod
    def from_host(cls, host):
        return cls(
            host,
            cls.extract(host, "user"),
            cls.extract(host, "hostname"),
            int(cls.extract(host, "port")),
        )

    def info(self, info):
        item = getattr(self, info)
        if self.host is None:
            return item
        return item or self.extract(self.host, info)

    def is_valid(self, look_at_filled=True):
        filled_valid = (
            look_at_filled
            and self.host is not None
            and self.filled.is_valid(look_at_filled=False)
        )
        host_valid = (
            self.user is not None
            and self.hostname is not None
            and self.port is not None
        )
        return filled_valid or host_valid

    @property
    def filled(self) -> "HostData":
        return HostData(
            host=self.host,
            user=self.info("user"),
            hostname=self.info("hostname"),
            port=int(self.info("port") or 22),
        )

    def is_online(self):
        return not bool(
            int(
                run_command(
                    f"nc -zw 1 {self.hostname} {self.port} > /dev/null; echo $?"
                )
            )
        )
