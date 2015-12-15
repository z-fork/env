# coding: utf-8

from collections import namedtuple
from contextlib import contextmanager
from distutils.util import strtobool
from os.path import join, dirname
import sys
import urlparse

import requests
from lxml import etree
from fabric.api import cd, env, execute, sudo, task, quiet, run
from fabric.contrib.files import exists
from fabric.colors import red
from fabric.decorators import runs_once

from rsync import Rsync


env.update(
    stage=None,
    sudo_user='root',
    use_ssh_config=False,
)


class Stage(namedtuple('Stage', 'name hosts')):

    PARENT_DIR = '/srv'

    @property
    def project_root(self):
        return join(self.PARENT_DIR, self.name)

STAGES = {
    stage.name: stage
    for stage in [
        # Stage('online', hosts=['115.159.159.12', '115.159.161.183'])
        Stage('online', hosts=['115.159.159.12'])
    ]
}


@task
def stage(name):
    if name not in STAGES:
        raise Exception('unknown stage name')
    env.stage = STAGES[name]
    env.hosts = env.stage.hosts


FILE_DIR = '/home/mongoo/downloads'
CONFIG_DIR = dirname(__file__) + '/configs'


@task
def base_env():
    # time_zone()
    base_update()
    # yum_install()
    # setup_python()
    # rewrite_bashrc()
    # setup_pip()
    # setup_venv()
    # setup_nginx()
    # copy_nginx_configs()
    # copy_supervisord_service()


def time_zone():
    sudo('chkconfig ntpd on')
    sudo('service ntpd start')
    sudo('ntpdate -u  pool.ntp.org')
    sudo('cp -f /usr/share/zoneinfo/Asia/Shanghai /etc/localtime')
    sudo('ntpdate -u  pool.ntp.org')


def base_update():
    sudo('yum -y update')


def yum_install():
    package_list = ['vim', 'gcc', 'gcc-c++', 'make', 'tmux','libevent-devel.x86_64',
                    'libevent.x86_64', 'libxml2-devel.x86_64', 'libxslt-devel.x86_64',
                    'java', 'zlib-devel.x86_64', 'zlib-devel.i686', 'bzip2-devel.x86_64',
                    'sqlite-devel.x86_64', 'gettext.x86_64', 'openssl', 'openssl-devel', 'pcre-devel']
    for p in package_list:
        sudo('yum -y install {p}'.format(p=p))


def setup_python():
    run('mkdir -p {dir}'.format(dir=FILE_DIR))

    suffix = '.tgz'
    filename = 'Python-2.7.8'
    python_file = '{filename}{suffix}'.format(filename=filename, suffix=suffix)
    python_source_url = 'https://www.python.org/ftp/python/2.7.8/{file}'.format(file=python_file)

    with cd(FILE_DIR):
        run('wget -c {url}'.format(url=python_source_url))
    with cd(FILE_DIR):
        run('tar -zxvf {file}'.format(file=python_file))
    with cd('{dir}/{filename}'.format(dir=FILE_DIR, filename=filename)):
        params = '--prefix=$HOME/local'
        run('./configure {params}'.format(params=params))
        run('make && make install')


def rewrite_bashrc():
    Rsync().sync("{dir}/bash/.bashrc".format(dir=CONFIG_DIR), "~/.")
    run('source ~/.bashrc')


def setup_pip():
    suffix = '.tar.gz'
    filename = 'setuptools-3.4.4'
    setuptools_file = '{filename}{suffix}'.format(filename=filename, suffix=suffix)
    setuptools_source_url = 'https://pypi.tuna.tsinghua.edu.cn/packages/source/s/setuptools/{file}'.format(file=setuptools_file)  # NOQA
    with cd(FILE_DIR):
        run('wget -c {url}'.format(url=setuptools_source_url))
    with cd(FILE_DIR):
        run('tar -zxvf {file}'.format(file=setuptools_file))
    with cd('{dir}/{filename}'.format(dir=FILE_DIR, filename=filename)):
        run("~/local/bin/python setup.py install")

    filename = 'pip-1.5.4'
    pip_file = '{filename}{suffix}'.format(filename=filename, suffix=suffix)
    pip_source_url = 'https://pypi.tuna.tsinghua.edu.cn/packages/source/p/pip/{file}'.format(file=pip_file)
    with cd(FILE_DIR):
        run('wget -c {url}'.format(url=pip_source_url))
    with cd(FILE_DIR):
        run('tar -zxvf {file}'.format(file=pip_file))
    with cd('{dir}/{filename}'.format(dir=FILE_DIR, filename=filename)):
        run("~/local/bin/python setup.py install")


def setup_venv():
    mirror = 'https://pypi.tuna.tsinghua.edu.cn/simple'
    run('~/local/bin/pip install -i {mirror} virtualenv'.format(mirror=mirror))


def setup_nginx():
    suffix = '.tar.gz'
    filename = 'pcre-8.12'
    pcre_file = '{filename}{suffix}'.format(filename=filename, suffix=suffix)
    pcre_source_url = 'http://exim.mirror.fr/pcre/{file}'.format(file=pcre_file)
    with cd(FILE_DIR):
        run('wget -c {url}'.format(url=pcre_source_url))
    with cd(FILE_DIR):
        run('tar -zxvf {file}'.format(file=pcre_file))

    filename = 'nginx-1.9.8'
    nginx_file = '{filename}{suffix}'.format(filename=filename, suffix=suffix)
    nginx_source_url = 'http://mirrors.sohu.com/nginx/{file}'.format(file=nginx_file)
    with cd(FILE_DIR):
        run('wget -c {url}'.format(url=nginx_source_url))
    with cd(FILE_DIR):
        run('tar -zxvf {file}'.format(file=nginx_file))
    with cd('{dir}/{filename}'.format(dir=FILE_DIR, filename=filename)):
        params = "--prefix=$HOME/local/nginx " \
                 "--with-http_ssl_module " \
                 "--with-http_realip_module " \
                 "--with-http_stub_status_module " \
                 "--with-pcre=$HOME/downloads/pcre-8.12"
        run("./configure {params}".format(params=params))
        run("make && make install")


def copy_nginx_configs():
    Rsync().sync(CONFIG_DIR + '/nginx_configs/conf/', '/home/mongoo/local/nginx/conf/')


def copy_supervisord_service(kind='kratos'):
    if kind not in ('kratos', 'web_proxy'):
        print "Error type: %s" % kind

    Rsync().sync(CONFIG_DIR + '/supervisord/kratos-supervisord', '/home/kratos/kratos-supervisord')
    sudo('mv /home/kratos/kratos-supervisord /etc/init.d/kratos-supervisord')
    sudo('chmod a+x /etc/init.d/kratos-supervisord')

    remote_supervisor_dir = '/home/kratos/local/supervisor/'
    local_supervisor_dir = CONFIG_DIR + "/supervisord/supervisor/"

    if not exists(remote_supervisor_dir):
        run("mkdir -p %s"%remote_supervisor_dir)

    Rsync().sync(local_supervisor_dir, remote_supervisor_dir)


@task
def mysql_env():
    # remove_default()
    # install_mysql()
    copy_mysql_cnf()
    change_data_dir()


def remove_default():
    sudo('rpm -qa | grep -i mysql | xargs yum -y remove')


def install_mysql():
    urls = [
        'http://dev.mysql.com/get/Downloads/MySQL-5.5/MySQL-server-5.5.30-1.el6.x86_64.rpm',
        'http://dev.mysql.com/get/Downloads/MySQL-5.5/MySQL-client-5.5.30-1.el6.x86_64.rpm',
        'http://dev.mysql.com/get/Downloads/MySQL-5.5/MySQL-devel-5.5.30-1.el6.x86_64.rpm'
    ]

    with cd(FILE_DIR):
        for url in urls:
            run('wget -c {url}'.format(url=url))

    with cd(FILE_DIR):
        for pk in run('ls').split():
            if pk.endswith('.rpm') and pk.startswith('MySQL'):
                sudo('rpm -ivh {dir}/{pk}'.format(dir=FILE_DIR, pk=pk))


def copy_mysql_cnf():
    local_mysql_dir = CONFIG_DIR + '/mysql/'
    remote_cnf_path = '/etc/my.cnf'
    Rsync().sync(local_mysql_dir + 'my.cnf', '/home/mongoo/my.cnf')
    sudo('mv /home/mongoo/my.cnf %s' % remote_cnf_path)
    sudo('chmod 0755 %s' % remote_cnf_path)
    sudo('chown root:root %s' % remote_cnf_path)


def change_data_dir():
    sudo('rm -rf /idata/mysql')
    sudo('cp -r /var/lib/mysql/mysql /idata')

    with cd('/idata/mysql'):
        sudo('mkdir data')

    sudo('chown -R mysql:mysql /idata/mysql')
    sudo('mysql_install_db --user=mysql --datadir=/idata/mysql/data/')


@task
def redis_env():
    setup_redis()


def setup_redis():
    suffix = '.tar.gz'
    filename = '2.8.23'
    redis_file = '{filename}{suffix}'.format(filename=filename, suffix=suffix)
    redis_source_url = 'https://github.com/antirez/redis/archive/{file}'.format(file=redis_file)
    with cd(FILE_DIR):
        run('wget -c {url}'.format(url=redis_source_url))
    with cd(FILE_DIR):
        run('tar -zxvf {file}'.format(file=redis_file))
    with cd('{dir}/redis-{filename}'.format(dir=FILE_DIR, filename=filename)):
        run('make')
        run('make PREFIX=/home/mongoo/local/redis install')


@task
def rabbitmq_env():
    install_rabbitmq()
    install_rabbitmq_mgmt_plugin()
    start_rabbitmq()
    create_rabbitmq_user()


def install_rabbitmq():
    """
    安装RabbitMQ，需要先安装Erlang
    refer: http://www.rabbitmq.com/install-rpm.html
    """
    rabbitmq_download_uri = \
        "http://www.rabbitmq.com/releases/rabbitmq-server/v3.3.1/rabbitmq-server-3.3.1-1.noarch.rpm"
    epel_download_uri = \
        "http://mirror.itc.virginia.edu/fedora-epel/6/i386/epel-release-6-8.noarch.rpm"

    install_dir = "/home/mongoo/downloads"

    if not exists(install_dir):
        run("mkdir %s" % install_dir)

    with cd(install_dir):
        # enable EPEL
        sudo("rpm -Uvh %s" % epel_download_uri)
        # install erlang
        sudo("yum -y install erlang")
        # Install rabbitmq-server
        run("wget -c %s" % rabbitmq_download_uri)
        sudo("rpm --import http://www.rabbitmq.com/rabbitmq-signing-key-public.asc")
        sudo("yum -y install rabbitmq-server-3.3.1-1.noarch.rpm")


def install_rabbitmq_mgmt_plugin():
    sudo("rabbitmq-plugins enable rabbitmq_management")


def start_rabbitmq():
    sudo("service rabbitmq-server start")


def create_rabbitmq_user():
    """
    删除guest用户，创建mongoo用户
    参考：http://celery.readthedocs.org/en/latest/getting-started/brokers/rabbitmq.html#setting-up-rabbitmq
    """
    sudo("rabbitmqctl delete_user guest")

    user = 'mongoo'
    password = 'GZLxVSdOQTIIKGpeoC3vv5Myh'
    tag = "administrator"
    sudo("rabbitmqctl add_user %s %s" % (user, password))
    sudo("rabbitmqctl set_user_tags %s %s" % (user, tag))
    sudo("""rabbitmqctl set_permissions mongoo ".*" ".*" ".*" """)

