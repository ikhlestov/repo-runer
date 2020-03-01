"""Download repository, build Dockerfile from it and run it
"""
import os
import shutil
import logging
from tempfile import mkdtemp
from contextlib import suppress


import click
import docker
from docker.client import DockerClient
from git import Repo


LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)
FORMAT = '%(asctime)-15s %(clientip)s %(user)-8s %(message)s'
formatter = logging.Formatter(
    '%(asctime)s [%(levelname)s] %(message)s',
    "%Y-%m-%d %H:%M:%S")
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
handler.setFormatter(formatter)
LOGGER.addHandler(handler)

DEFAULT_REPO_URL = 'git@github.com:guyyosan/python-cherry-container.git'
DOCKER_IMAGE_TAG = 'test-repo-runner-image'
DOCKER_CONTAINER_TAG = 'test-repo-runner-container'


def __log_and_exit(text):
    """Log some error and exit"""
    LOGGER.error(text)
    exit(1)


def clone_git_repo(repo_url: str, project_path: str):
    try:
        LOGGER.info(f"Clonning repo {repo_url} into {project_path}...")
        Repo.clone_from(url=repo_url, to_path=project_path)
    except Exception as e:
        __log_and_exit(f"Failed to clone repository {repo_url}. Error: {repr(e)}")


def get_docker_client():
    try:
        LOGGER.info("Initializing docker client...")
        return docker.from_env()
    except Exception as e:
        __log_and_exit(f"Failed to initialize docker client. Error: {repr(e)}")


def build_container(docker_client: DockerClient, project_path: str):
    try:
        LOGGER.info("Building docker image...")
        docker_client.images.build(path=project_path, tag=DOCKER_IMAGE_TAG)
    except Exception as e:
        __log_and_exit(f"Failed to build docker image. Error: {repr(e)}")


def run_container(docker_client: DockerClient, docker_port: int, host_port: int):
    try:
        container = docker_client.containers.run(
            DOCKER_IMAGE_TAG, auto_remove=True, detach=True,
            name=DOCKER_CONTAINER_TAG, ports={f'{docker_port}/tcp': host_port})
        LOGGER.info(f"Docker container is running. Check it on 'http://127.0.0.1:{host_port}")
        return container
    except Exception as e:
        __log_and_exit(f"Failed to start docker container. Error: {repr(e)}")


def clean_after_running(container, docker_client, project_path):
    with suppress(Exception):
        container.stop()

    with suppress(Exception):
        docker_client.images.remove(DOCKER_IMAGE_TAG)

    with suppress(Exception):
        shutil.rmtree(project_path)


def worker(repo_url: str, project_path: str, docker_port: int, host_port: int):
    """Main worker that will:
    - create required directories
    - clone repository
    - build Dockerfile
    - start container
    - remove container and temporary directory
    """
    if not project_path:
        project_path = mkdtemp()
    else:
        os.makedirs(project_path, exist_ok=True)

    clone_git_repo(repo_url=repo_url, project_path=project_path)
    docker_client = get_docker_client()
    build_container(docker_client, project_path)
    container = run_container(docker_client, docker_port, host_port)

    with suppress(KeyboardInterrupt):
        LOGGER.info("To stop container press `Ctrl+C`")
        while True:
            pass

    clean_after_running(container, docker_client, project_path)


@click.command(help=__doc__)
@click.option('-r', '--repo_url', default=DEFAULT_REPO_URL,
              help=f'Url to GitHub repository to clone. Default to {DEFAULT_REPO_URL}')
@click.option('-p', '--path', type=click.Path(exists=True),
              help='Path where project will be downloaded. Default to /tmp')
@click.option('-d_p', '--docker_port', default=8080,
              help="Serving port at the Docker container")
@click.option('-h_p', '--host_port', default=9090,
              help="Serving port at the host")
def main(repo_url: str, path: str, docker_port: int, host_port: int):
    """Base commands hanler"""
    worker(repo_url, path, docker_port, host_port)


if __name__ == '__main__':
    main()
