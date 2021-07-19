# psync

What is `psync`? A simple tool to quickly synchronize your project(s) across one or multiple machines.

## Installation
`pip install git+https://github.com/Valahaar/psync.git` (pypi package coming soon :-) ) 

## Usage
Run `psync init` from the root directory of your project (use `-h` or `--help` if you don't know how it works!).

## Example config
```yml
general:
  local: replica1     # local project path (required!)
  default: replica2   # default remote name (optional; in case there is only one remote, that is selected as default)

  compress: true      # whether to use -c flag in rsync (enables compression)
  ask_confirm: false  # whether to show the rsync command and ask permission before execution
  debug: false        # prints the parsed arguments to the command plus path info (also enables ask_confirm)

replicas:
  replica1:
    path: /path/to/project
    host:
      host: host_in_ssh_config  # you can specify a host in SSH config
  replica2:
    path: ~/my-projects/psync
    host:
      hostname: 192.168.1.223  # or you can configure it yourself
      port: 10333
      user: root
  replica3:
    path: /another/path/to/project
    host:
      host: host_in_ssh_config  # or you can combine the two things!
      port: 12345
```

## Usage
From any subdirectory of `config.project` just execute `psync <push|pull> [destination] [files] [options]`.

```
positional arguments:
  destination           (default: null)
  files                 Files that need to be synced (default: [])

optional arguments:
  -h, --help            Show this help message and exit.
  -H HOST, --host HOST  Remote hostname (in the form of user@host, defaults to $PSYNC_REMOTE_HOST) (default: null)
  -r REMOTE, --remote REMOTE
                        Remote destination (defaults to $PSYNC_REMOTE_PROJECT) (default: null)
  -l LOCAL, --local LOCAL
                        Local source (defaults to $PSYNC_LOCAL_PROJECT) (default: null)
  -x EXCLUDE [EXCLUDE ...], --exclude EXCLUDE [EXCLUDE ...]
                        Exclusion patterns provided to rsync (type: str, default: null)
  -p PORT, --port PORT  SSH port to use (not needed in case of a host configured via ssh config) (type: int, default: null)
  -c, --compress        Activate rsync compression (defaults to $PSYNC_COMPRESS) (default: False)
  -n, --confirm         Print the constructed rsync command before execution (enabled if $PSYNC_ASK_CONFIRM) is set) (default: False)
  --debug               Prints the parsed arguments, some useful information and asks for confirmation before running the command (enabled if $PSYNC_DEBUG) is set) (default: False)
```

By default, `psync` selects `config.default` as the remote to synchronize (both in push and pull). 
In case there is only one remote in the config, `psync` automatically uses that one.

If `files` are provided (e.g., `psync push setup.py .gitignore`), `psync` will only synchronize those. 
If no file is specified, `psync` will synchronize the entire folder from which it is executed.

## FAQs

Q: Why not **git**?

A: git is **great** for all intents and purposes, and should be your go-to tool for version control and moving code around. 
Nevertheless, git does not deal well with large files (e.g., datasets) and requires pushing / pulling to the repository.
`psync` is only intended to be used when moving code **and** data around, and it makes for a great addition for those who use git with 2FA (as it disables HTTPS access).

Besides, don't forget to push your `.psync.yml` file to git! This way, replica info will always be up-to-date :) 

Q: `psync` keeps asking for my password!
A: Please see *Configuring remotes* below. 

## Configuring remotes
It is highly recommended configuring SSH remotes when using `psync`. For example, our `host_in_ssh_config` could be
configured as follows (in `~/.ssh/config`):

```
Host host_in_ssh_config         # probably better to use meaningful names :)
    User username               # defaults to your local username
    HostName server-ip-or-host  # this is required
    Port ssh-port               # defaults to 22
```

It is also advisable to use SSH keys to log in, instead of relying on passwords (as `psync` uses `rsync` under the hood).

To enable key-based log in, first generate an SSH key with `cat /dev/zero | ssh-keygen -q -N ""` (this key will be stored under `~/.ssh/id_rsa[.pub]`),
then run `ssh-copy-id <remote>` (where `<remote>` should be defined in the SSH config) and login using your password for the last time. 
All subsequent logins to `<remote>` from the host you executed `ssh-copy-id` will not require a password, including running `psync`.


## TODOs
- Improve error handling
- Better support for `-H/--host`
- `psync init` / faster psync initialization
- Support .gitignore
- Support changing default exclusions
- Support exclusions from config