-- The official mariadb image only grants MARIADB_USER privileges on MARIADB_DATABASE.
-- Django's test runner needs to create/drop a separate test database, so grant that too.
GRANT ALL PRIVILEGES ON `alexia_test`.* TO 'alexia'@'%';
FLUSH PRIVILEGES;
