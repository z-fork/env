# 创建用户
CREATE USER 'kratos_v2'@'localhost' IDENTIFIED BY 'd9U6ooizh7v6SrCYdr8iC5Wwh';
CREATE USER 'kratos_v2'@'%' IDENTIFIED BY 'd9U6ooizh7v6SrCYdr8iC5Wwh';

# 设置权限
GRANT ALL ON router.* to 'kratos_v2'@'localhost';
GRANT ALL ON router.* to 'kratos_v2'@'%';

GRANT ALL ON db1.* to 'kratos_v2'@'localhost';
GRANT ALL ON db1.* to 'kratos_v2'@'%';

GRANT ALL ON db2.* to 'kratos_v2'@'localhost';
GRANT ALL ON db2.* to 'kratos_v2'@'%';

GRANT ALL ON db3.* to 'kratos_v2'@'localhost';
GRANT ALL ON db3.* to 'kratos_v2'@'%';

GRANT ALL ON db4.* to 'kratos_v2'@'localhost';
GRANT ALL ON db4.* to 'kratos_v2'@'%';

# 更新权限缓存
FLUSH PRIVILEGES;