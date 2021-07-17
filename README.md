# psync

What is `psync`? A simple tool to quickly synchronize your project across one or multiple machines.

## Example config
```yml
project: ~/projects/psync  # local project path
default: remote2           # default remote name (optional; in case there is only one remote, that is selected as default)

remotes:
  remote1:
    path: /path/to/project
    host:
      host: host_in_ssh_config
  remote2:
    path: ~/my-projects/psync
    host:
      hostname: 192.168.1.223
      port: 10333
      user: root

general:
  compress: true      # whether to use -c flag in rsync (enables compression)
  ask_confirm: false  # whether to show the rsync command and ask permission before execution
  debug: false        # prints the parsed arguments to the command plus path info (also enables ask_confirm)
```
