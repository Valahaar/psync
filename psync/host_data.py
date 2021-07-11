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
        hn = self.host or "<unknown>"
        return f"{hn} --- {self.user}@{self.hostname}"

    def remote_run_command(self, command):
        return run_command(f"ssh -p {self.port} {self.user}@{self.hostname} {command}")

    @classmethod
    def extract(cls, host, info):
        res = run_command(f'ssh -G {host} | grep "^{info} "')
        return res.rstrip()[len(info) + 1 :]

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

    @property
    def filled(self) -> "HostData":
        return HostData(
            host=self.host,
            user=self.info("user"),
            hostname=self.info("hostname"),
            port=int(self.info("port")),
        )

    def is_online(self):
        return not bool(
            int(
                run_command(
                    f"nc -zw 1 {self.hostname} {self.port} > /dev/null; echo $?"
                )
            )
        )
