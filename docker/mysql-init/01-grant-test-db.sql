-- The official mysql image only grants MYSQL_USER privileges on MYSQL_DATABASE.
-- Django's test runner needs to create/drop a separate test database, so grant that too.
GRANT ALL PRIVILEGES ON `alexia_test`.* TO 'alexia'@'%';
FLUSH PRIVILEGES;
