import os

import docker
from django.apps import AppConfig
from docker import DockerClient


class DatabaseConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'database'
    db_container = 'postgres_db'

    def ready(self):
        print("Ready section of the database app.")
        docker_client = docker.from_env()
        db_container_running = self.check_if_database_container_is_running(docker_client)
        if not db_container_running:
            container = docker_client.containers.get(DatabaseConfig.db_container)
            container.start()
            container_state = container.attrs["State"]
            if container_state != "running":
                raise RuntimeError("Database container couldn't be started. Final status: {}".format(container_state))
        else:
            print("Database container up and running.")

    def check_if_database_container_is_running(self, docker_client: DockerClient):
        try:
            container = docker_client.containers.get(DatabaseConfig.db_container)
        except docker.errors.NotFound as e:
            print("Database container not present. Trying to init.")
            exit_code = os.system("docker-compose -f database/stack.yml up --detach")
            if exit_code != 0:
                raise RuntimeError("Setting up containers failed. "
                                   "Process exited with exit code {} and message: {}".format(exit_code, str(e)))
        finally:
            container = docker_client.containers.get(DatabaseConfig.db_container)
            container_state = container.attrs["State"]
            return container_state["Status"] == "running"
