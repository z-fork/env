# 创建用户
CREATE USER 'kratos_v2'@'localhost' IDENTIFIED BY '3vUbY52IJ2fJq7KwWPeItNrz8';
CREATE USER 'kratos_v2'@'50.22.158.%' IDENTIFIED BY '3vUbY52IJ2fJq7KwWPeItNrz8';
CREATE USER 'kratos_v2'@'10.28.%' IDENTIFIED BY '3vUbY52IJ2fJq7KwWPeItNrz8';

# 设置权限
GRANT ALL ON db3.* to 'kratos_v2'@'localhost';
GRANT ALL ON db3.* to 'kratos_v2'@'50.22.158.%';
GRANT ALL ON db3.* to 'kratos_v2'@'10.28.%';


GRANT ALL ON db4.* to 'kratos_v2'@'localhost';
GRANT ALL ON db4.* to 'kratos_v2'@'50.22.158.%';
GRANT ALL ON db4.* to 'kratos_v2'@'10.28.%';


# 更新权限缓存
FLUSH PRIVILEGES;