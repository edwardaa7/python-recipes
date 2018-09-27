import os
from fabric.api import *
from fabric.context_managers import cd, settings, shell_env, quiet
from fabric.contrib import files


# Prefix for all application environment variable key name to be passed to
# remote deploy server(s).
APP_ENV_VAR_PREFIX = 'APP_'

# Some Gitlab-CI environment variables that we will be using
CI_REGISTRY = os.getenv('CI_REGISTRY')
CI_REGISTRY_USER = os.getenv('CI_REGISTRY_USER')
CI_REGISTRY_IMAGE = os.getenv('CI_REGISTRY_IMAGE')
CI_COMMIT_REF_NAME = os.getenv('CI_COMMIT_REF_NAME')
CI_JOB_TOKEN = os.getenv('CI_JOB_TOKEN')

# Application specific variables
env.project = 'my_project'
env.app_dir = f'apps/{env.project}'


def _helper_get_gitlab_ci_env_vars():
    """
    Function extracts only the necessary Gitlab CI environment variables to
    be passed to the deploy environment to be used in the docker-compose script
    running on the deployed environment
    """
    ci_env_keys = ['CI_REGISTRY_IMAGE', 'CI_COMMIT_REF_NAME']
    return {key: os.getenv(key) for key in ci_env_keys}


# Gitlab CI environment variables to pass to remote server
env.ci_env_vars = _helper_get_gitlab_ci_env_vars()


# Environments
def production():
    # Server credentials
    env.hosts = [os.getenv('PRODUCTION_SSH_HOST')]
    env.key = os.getenv('PRODUCTION_SSH_KEY')
    env.sudo_password = os.getenv('PRODUCTION_SUDO_PASS')


def staging():
    # Server credentials
    env.hosts = [os.getenv('STAGING_SSH_HOST')]
    env.key = os.getenv('STAGING_SSH_KEY')
    env.sudo_password = os.getenv('STAGING_SUDO_PASS')


# Tasks
def update():
    # Typically docker-compose script and other dependencies
    put('docker-compose.yml', env.app_dir, use_sudo=True)


def setup():
    if not files.exists(env.app_dir):
        sudo(f'mkdir -p {env.app_dir}')
        update()


def deploy():
    setup()
    update()
    docker_login()
    docker_deploy()


def docker_login():
    login_prompts = {
        'Username: ': CI_REGISTRY_USER,
        'Password: ': CI_JOB_TOKEN,
    }

    with settings(prompts=login_prompts):
        sudo(f'docker logout {CI_REGISTRY}')
        with quiet():
            sudo(f'docker login {CI_REGISTRY}')


def docker_deploy():
    require('ci_env_vars')

    sudo(f'docker image pull {CI_REGISTRY_IMAGE}:{CI_COMMIT_REF_NAME}')

    with quiet():
        with cd(env.app_dir):
            with shell_env(**env.ci_env_vars):
                sudo('docker-compose down')
                sudo('docker-compose up -d')
