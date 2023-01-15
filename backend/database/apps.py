import os
import sys

import docker
import psycopg2
from django.apps import AppConfig
from docker import DockerClient
from dotenv import load_dotenv

load_dotenv()


class DatabaseConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'database'
    db_container = 'postgres_db'

    def ready(self):
        docker_client = docker.from_env()
        try:
            db_container_running = self.check_if_database_container_is_running(docker_client)
            if not db_container_running:
                container = docker_client.containers.get(DatabaseConfig.db_container)
                container.start()
                container_state = container.attrs["State"]
                if container_state != "running":
                    raise RuntimeError(
                        "Database container couldn't be started. Final status: {}".format(container_state))
            else:
                print("Database container up and running.")

            self.setup_database()
        except RuntimeError as e:
            print(str(e))
            sys.exit(1)

    def check_if_database_container_is_running(self, docker_client: DockerClient):
        try:
            container = docker_client.containers.get(DatabaseConfig.db_container)
        except docker.errors.NotFound as e:
            print("Database container not present. Trying to init.")
            exit_code = os.system("docker-compose --env-file .env -f database/stack.yml up --detach")
            if exit_code != 0:
                raise RuntimeError("Setting up containers failed. "
                                   "Process exited with exit code {} and message: {}".format(exit_code, str(e)))
        finally:
            container = docker_client.containers.get(DatabaseConfig.db_container)
            container_state = container.attrs["State"]
            return container_state["Status"] == "running"

    def setup_database(self):
        # Postgres superuser part of the setup
        try:
            postgres_conn = psycopg2.connect("dbname='postgres' user='postgres' "
                                             "host='localhost' password='{postgres_user_pass}'".format(
                postgres_user_pass=os.getenv('POSTGRES_PASSWORD')))
            postgres_conn.autocommit = True
        except psycopg2.Error:
            raise RuntimeError("Unable to connect ot the postgres superuser.")

        with postgres_conn.cursor() as cur:
            cur.execute("SELECT true FROM pg_database WHERE datname = 'spadvisor'")
            if cur.rowcount == 0:
                cur.execute("CREATE DATABASE spadvisor")
            else:
                print("Database spadvisor already created.")

        with postgres_conn.cursor() as cur:
            cur.execute("SELECT true FROM pg_roles WHERE rolname='spa_user'")
            if cur.rowcount == 0:
                cur.execute("CREATE USER spa_user WITH PASSWORD %s", (os.getenv('SPA_DB_USER_PASSWORDS'),))
            else:
                print("User spa_user already exists.")

        # SPA dedicated database setup
        try:
            spa_conn = psycopg2.connect("dbname='spadvisor' user='postgres' "
                                        "host='localhost' password='{postgres_user_pass}'".format(
                postgres_user_pass=os.getenv('POSTGRES_PASSWORD')))
            spa_conn.autocommit = True
        except psycopg2.Error:
            raise RuntimeError("Unable to connect ot the postgres superuser.")

        with spa_conn.cursor() as cur:
            cur.execute("ALTER ROLE spa_user SET client_encoding TO 'utf8'")
            cur.execute("ALTER ROLE spa_user SET default_transaction_isolation TO 'read committed'")
            cur.execute("ALTER ROLE spa_user SET timezone TO 'UTC'")
            cur.execute("GRANT ALL ON SCHEMA public TO spa_user")
            cur.execute("GRANT ALL PRIVILEGES ON DATABASE spadvisor TO spa_user")
