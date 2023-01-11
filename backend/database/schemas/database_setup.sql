CREATE DATABASE spadvisor;
CREATE USER spa_user WITH PASSWORD 'gjLpuhet999MQY7Z';

ALTER ROLE spa_user SET client_encoding TO 'utf8';
ALTER ROLE spa_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE spa_user SET timezone TO 'UTC';

GRANT ALL PRIVILEGES ON DATABASE spadvisor TO spa_user;
