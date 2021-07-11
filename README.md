# psync

What is `psync`? A simple tool to quickly synchronize your project across one or multiple machines.

## Example config
```yml
project: ~/projects/psync
default: remote2

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
  ask_confirm: false
  compress: true
```
