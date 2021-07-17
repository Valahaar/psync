import subprocess
from typing import Optional


def run_command(
    cmd: str, get_result: bool = True, from_stderr: bool = False
) -> Optional[str]:
    command = subprocess.run(cmd, shell=True, capture_output=get_result)

    try:
        command.check_returncode()

        out = command.stderr if from_stderr else command.stdout

        if get_result:
            return out.decode("utf-8").rstrip()

    except subprocess.CalledProcessError as _:
        print(f'Command "{cmd}" failed with exit code {command.returncode}')
        return None
