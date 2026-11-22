# Network automation project

Daily tasks for IOS-XR and IOS-XE routers: interfaces, IGP, iBGP, eBGP,
verification and troubleshooting. Built stage by stage; this is stage 1.

## Layout

```
ansible.cfg            project settings (paths, timeouts, pinned collections)
requirements.yml       pinned Ansible collections
requirements.txt       pinned Python packages
inventory/             hosts, group_vars/, host_vars/   (use your existing files)
playbooks/             00_common.yml, site.yml, later stages 10_ ... 61_
roles/common/          pre-flight checks and backup
backups/  reports/     output (git-ignored)
```

## Setup (once)

```bash
python3 -m venv venv && . venv/bin/activate
pip install -r requirements.txt
ansible-galaxy collection install -r requirements.yml -p collections
```

## What the project needs from your existing inventory

- `ansible_network_os` for every device (`cisco.iosxr.iosxr` or `cisco.ios.ios`),
  best set in group_vars. See `inventory/hosts.example`.
- `ansible_connection: ansible.netcommon.network_cli` (or `network_cli`) and credentials from your vault.
- `host_name` and `router_id` in each host_vars file (the role refuses to run without them).

## Stage 1: pre-flight and backup

```bash
ansible-playbook playbooks/00_common.yml --limit P01_9k          # everything
ansible-playbook playbooks/00_common.yml --tags preflight        # checks only
ansible-playbook playbooks/00_common.yml --tags preflight_vars   # variable checks only, no login
ansible-playbook playbooks/00_common.yml --tags backup           # backup only
ansible-playbook playbooks/00_common.yml -e common_run_backup=false
```

Pre-flight stops only the device that fails; the others continue.
After pre-flight passes, a device carries `common_preflight_passed: true`,
which later roles check before they change anything.

Backups go to `backups/<host>/<host>_<timestamp>.cfg`.

## Checks

```bash
yamllint playbooks roles requirements.yml
ansible-lint playbooks roles
```
