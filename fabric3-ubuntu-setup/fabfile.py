import os
import time
import random
from fabric.api import require, env, sudo, put, get, local
from fabric.context_managers import cd, settings, shell_env, quiet
from fabric.contrib import files

# Global environment
env.project = 'aws_ec2_default'
env.hosts = [os.getenv('SSH_HOST')]
env.key = os.getenv('SSH_KEY')
env.sudo_password = os.getenv('SSH_SUDO_PASS')

def upgrade():
    sudo('apt-get update')
    sudo('apt-get upgrade -y')

def setup_docker():
    sudo('apt-get remove -y docker docker-engine docker.io')
    sudo('apt-get install -y apt-transport-https ca-certificates curl software-properties-common')
    sudo('curl -fsSL https://get.docker.com -o get-docker.sh')
    sudo('sh get-docker.sh')

def setup_docker_compose():
    sudo('curl -L "https://github.com/docker/compose/releases/download/1.22.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose')
    sudo('chmod +x /usr/local/bin/docker-compose')

def setup_swap():
    sudo('fallocate -l 2G /swapfile')
    sudo('chmod 600 /swapfile')
    sudo('mkswap /swapfile')
    sudo('swapon /swapfile')
    sudo('cp /etc/fstab /etc/fstab.bak')
    sudo("echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab")

def setup_ufw():
    sudo('ufw default deny incoming')
    sudo('ufw default allow outgoing')
    sudo('ufw allow 22')
    sudo('ufw allow 80')
    sudo('ufw allow 443')
    sudo('ufw enable')

def setup_ssh():
    random_port = random.randint(10000, 20000)
    local(f'echo Setting up SSH on port {random_port}')

    sudo(f'ufw allow {random_port}')

    ssh_config_base_path = '/etc/ssh'
    with cd(ssh_config_base_path):
        sudo('cp sshd_config sshd_config.bak')
        sudo('grep -v "Port 22" sshd_config > sshd_config.tmp')
        sudo(f'echo "Port {random_port}" >> sshd_config.tmp')
        sudo('cp sshd_config.tmp sshd_config')
        sudo('service sshd restart')

def setup():
    upgrade()
    setup_docker()
    setup_docker_compose()
    setup_swap()
    setup_ufw()
    setup_ssh()
