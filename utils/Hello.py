from fabric.api import *

env.hosts = ['192.168.12.200']
env.port = 22
env.user = 'root'
env.password = '123456'


def hostname():
    run('hostname')


def ls(path='.'):
    run('ls {0}'.format(path))


def install():
    b = 1 + 2
    print(b)


def create():
    run("touch /usr/local/111.conf")
    # run("echo 'asdasdasd' >> /usr/local/111.conf")


def close(pName):
    """
        输入要关闭的进程名
        关闭进程
    """
    res = run("ps -ef | grep "+pName)
    pid = res[11:16]
    # print(pid)
    run('kill -9 '+ pid.strip())


def test():
    put(remote_path='')
