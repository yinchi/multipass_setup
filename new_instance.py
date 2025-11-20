#!/usr/bin/env python3
# Create a new Multipass instance with specified resources and add SSH key

import re
import pathlib
import sys
import click
import subprocess

################################################################################

# EDITABLE SETTINGS

# Define the path to the SSH public key relative to the user's home directory
SSH_PATH = '.ssh/id_ed25519.pub'
DEFAULT_CPUS = 4
DEFAULT_MEM_GB = 4
DEFAULT_DISK_GB = 10

################################################################################

CONTEXT_SETTINGS = {
    'help_option_names': ['-h', '--help']
}

name_pattern = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*')

@click.command(
    context_settings=CONTEXT_SETTINGS
)
@click.argument('name')
@click.option('--ssh-path', '-s', default=SSH_PATH,
              help='Path to the SSH public key relative to the user\'s home directory. ')
@click.option('--dry-run', '-d', is_flag=True,
              help='If set, the script will only print the commands without executing them.')
@click.option('--cpus', '-c',
              help='The number of CPUs for the new instance. (default: 4)',
              default=DEFAULT_CPUS, type=int)
@click.option('--memory', '-m',
              help='The amount of memory for the new instance in GB. (default: 4)',
              default=DEFAULT_MEM_GB, type=int)
@click.option('--disk', '-d',
              help='The amount of disk space for the new instance in GB. (default: 10)',
              default=DEFAULT_DISK_GB, type=int)
def create_instance(name, cpus, memory, disk, ssh_path, dry_run):
    """Create a new Multipass instance with the given name.

    To enable SSH access, the script reads the SSH public key from the path
    defined by SSH_PATH (default: ~/.ssh/id_ed25519.pub) and adds it to the
    authorized_keys of the new instance.
    """

    ssh_path = pathlib.Path.home() / ssh_path
    if not ssh_path.exists():
        click.echo(f'❌  SSH public key not found at {ssh_path}. Please run setup.sh to '
                   'generate one.', err=True)
        sys.exit(1)
    else:
        click.echo(f'🔑  Found SSH public key at {ssh_path}.')

    with open(ssh_path, 'r') as f:
        ssh_key = f.read().strip()
    click.echo('🔑  Read SSH public key:')
    click.echo(ssh_key)
    click.echo('')

    if not name_pattern.fullmatch(name):
        raise click.BadParameter('Instance name can only contain groups of lowercase letters and '
                                 'numbers, separated by hyphens, e.g. ubuntu2404-1.')
    click.echo(f'🔨  Creating a new instance named {name}: ')
    click.echo(f'    CPUs:   {cpus}')
    click.echo(f'    Memory: {memory} GB')
    click.echo(f'    Disk:   {disk} GB')
    click.echo('')

    # Launch the instance using multipass
    command = ["multipass", "launch",
               "--name", name,
               "--cpus", str(cpus),
               "--memory", f"{memory}G",
               "--disk", f"{disk}G"]
    if dry_run:
        click.echo(" ".join(command))
    else:
        ret = subprocess.run(command)
        if ret.returncode != 0:
            click.echo(f'❌  Failed to create the instance. Return code: {ret.returncode}',
                       err=True)
            sys.exit(ret.returncode)

        click.echo(f'✅  Instance {name} created successfully.')

    command = ["multipass", "exec", name, "--", "bash", "-c",
               f'echo "{ssh_key}" >> /home/ubuntu/.ssh/authorized_keys']
    if dry_run:
        click.echo(" ".join(command))
    else:
        ret = subprocess.run(command)
        if ret.returncode != 0:
            click.echo(f'❌  Failed to add SSH key to the instance. Return code: {ret.returncode}',
                       err=True)
            sys.exit(ret.returncode)
        click.echo(f'✅  SSH key added to the instance {name}.')
    
    command = ["multipass", "transfer", "init.sh", f"{name}:/home/ubuntu/init.sh"]
    if dry_run:
        click.echo(" ".join(command))
    else:
        ret = subprocess.run(command)
        if ret.returncode != 0:
            click.echo('❌  Failed to transfer init.sh to the instance. '
                       f'Return code: {ret.returncode}',
                       err=True)
            sys.exit(ret.returncode)
        click.echo(f'✅  init.sh transferred to the instance {name}.')
    
    command = ["multipass", "exec", name, "--", "/home/ubuntu/init.sh"]
    if dry_run:
        click.echo(" ".join(command))
    else:
        click.echo(f'🚀  Running init.sh on the instance {name}...')
        ret = subprocess.run(command)
        if ret.returncode != 0:
            click.echo(f'❌  Failed to run init.sh on the instance. Return code: {ret.returncode}',
                       err=True)
            sys.exit(ret.returncode)
        click.echo(f'✅  init.sh executed on the instance {name}.')

    command = ["multipass", "restart", name]
    if dry_run:
        click.echo(" ".join(command))
    else:
        click.echo(f'🔄  Restarting the instance {name} to apply changes...')
        ret = subprocess.run(command)
        if ret.returncode != 0:
            click.echo(f'❌  Failed to restart the instance. Return code: {ret.returncode}',
                       err=True)
            sys.exit(ret.returncode)
        click.echo(f'✅  Instance {name} restarted successfully.')

if __name__ == '__main__':
    create_instance()
