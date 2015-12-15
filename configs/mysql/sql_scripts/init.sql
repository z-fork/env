create database hunter character set=utf8;

CREATE USER 'hunter'@'localhost' IDENTIFIED BY '3vUbY52IoP3mw7KwWPeItNrz8';
CREATE USER 'hunter'@'115.159.%' IDENTIFIED BY '3vUbY52IoP3mw7KwWPeItNrz8';
CREATE USER 'hunter'@'114.242.%' IDENTIFIED BY '3vUbY52IoP3mw7KwWPeItNrz8';

GRANT ALL ON hunter.* to 'hunter'@'localhost';
GRANT ALL ON hunter.* to 'hunter'@'115.159.%';
GRANT ALL ON hunter.* to 'hunter'@'114.242.%';

FLUSH PRIVILEGES;