import os
import time

from fabric.api import *

import Getcnf

env.hosts = ['192.168.254.201']
env.port = 22
env.user = 'root'
env.password = '123456'


# env.hosts = ['192.168.10.33']
# env.hosts = ['129.28.162.13']
# env.port = 22
# env.user = 'root'
# env.password = '123456'
# env.password = '@Fjmxkj1220@'

# env.hosts = ['192.168.254.200']
# env.port = 22
# env.user = 'root'
# env.password = '123456'


def ls(path='.'):
    run('ls {0}'.format(path))


def close_process(pName):
    """
    输入进程名，关闭进程
    :param pName: 进程名
    :return:
    """
    res = run("ps -ef | grep " + pName + " | grep -v grep | awk '{print $2}'")
    run('kill -9 ' + res)


def install_redis(version="redis-5.0.8.tar.gz"):
    """
    安装redis，控制台输出安装地址
    :return:
    """
    run("yum install gcc gcc-c++ -y")
    put(remote_path="/tmp", local_path="../redis/" + version + "")
    with cd("/tmp"):
        dir = _unzip_("/tmp/" + version + "")
        # 递归创建目录
        run("mkdir -p /usr/local/redis/etc")
        with cd(dir):
            run("make MALLOC=libc && make install PREFIX=/usr/local/redis")
            run("mv redis.conf /usr/local/redis/etc/")
        res = run("ls /usr/local/redis/bin")
        if res.strip() != '':
            _replace_("daemonize yes", "daemonize no", "/usr/local/redis/etc/redis.conf")
            put("安装完成 path=/usr/local/redis")
        else:
            abort("安装失败，请使用make test检查安装错误")


def _replace_(original, now, path):
    """
    私有方法，替换文件内容
    :param original:修改文件查找的项目，部分符号需要转义“\=”
    :param now: 改成什么样
    :param path: 路径
    :return:
    """
    run("sed -i 's/" + original + "/" + now + "/g' " + path + "")


def _unzip_(dir):
    with settings(hide('everything'), warn_only=True):
        if ".tar.gz" in dir or ".tar.xz" in dir:
            filename =run("tar -vxf " + dir +"| cut -d '/' -f1")
            filename = filename.split("\r\n")
            unzip_dirname = filename[0]
            return unzip_dirname
        # if ".zip" in dir:
        #     run("unzip -c " + dir +" | cut -d '/' -f1")


def set_cd_repo():
    """
    设置光盘为yum源头
    :return:
    """
    res = run("ls -l /etc/yum.repos.d")
    aa = res.rsplit("\r\n")
    for a in aa:
        if a.endswith(".repo"):
            run("mkdir /etc/yum.repos.d/old")
            run("mv /etc/yum.repos.d/*.repo /etc/yum.repos.d/old/")
            break
    run("mount /dev/cdrom /mnt")
    run("touch /etc/yum.repos.d/rhel-cdrom.repo")
    run("echo [rhel-cdrom] >> /etc/yum.repos.d/rhel-cdrom.repo")
    run("echo name=redhat7.4 >> /etc/yum.repos.d/rhel-cdrom.repo")
    run( "echo baseurl=file:///mnt >> /etc/yum.repos.d/rhel-cdrom.repo")
    run("echo enabled=1 >> /etc/yum.repos.d/rhel-cdrom.repo")
    run("echo gpgcheck=0 >> /etc/yum.repos.d/rhel-cdrom.repo")
    run("yum clean all")


def install_mysql(version = "mysql-5.7.29-el7-x86_64.tar.gz"):
    """
    mysql 安装
    :return:
    """
    with settings(show('everything'), warn_only=True):
        execute(uninstall_app, "mariadb")
        run("groupadd mysql && useradd -g mysql mysql")
        put(local_path="../mysql/" + version + "", remote_path="/tmp")
        put(local_path="../mysql/my.cnf", remote_path="/etc")
        with cd("/tmp"):
            dir_name = _unzip_("/tmp/" + version + "")
            run("mv " + dir_name + " /usr/local/mysql/")
        run("mkdir -p /usr/local/mysql/data")
        run("chown -R mysql:mysql /usr/local/mysql")
        run("mkdir -p /var/lib/mysql/")
        run("touch /var/lib/mysql/mysql.sock")
        run("chown -R mysql:mysql  /var/lib/mysql")
        with cd("/usr/local"):
            install_log = run("./mysql/bin/mysqld --initialize --user=mysql "
                              "--basedir=/usr/local/mysql --datadir=/usr/local/mysql/data")
        mysql_password = install_log[-12:]
        puts("随机mysql密码：" + mysql_password)
        run("echo '[client]' >> /etc/my.cnf")
        run("echo 'user=root' >> /etc/my.cnf")
        run("echo 'password=" + mysql_password + "' >> /etc/my.cnf")
        # todo 输出生成mysql密码文件
        execute(after_install_mysql_step)
        # puts("修改mysql密码语句ALTER USER USER() IDENTIFIED BY '123456';  并且打入exit")
        # run("mysql")
        # for i in range(0, 3):
        #     run("sed -i '$d' /etc/my.cnf")
        # puts("安装完成 path=/usr/local/mysql")


def after_install_mysql_step():
    """
    安装mysql后的步骤，将mysql变成服务
    :return:
    """
    # run("chown 777 /etc/my.cnf")
    run(" cp /usr/local/mysql/support-files/mysql.server /etc/rc.d/init.d/mysqld")
    run("chmod +x /etc/rc.d/init.d/mysqld")
    run("chkconfig --add mysqld")
    run("systemctl start mysqld")
    run("echo 'export PATH=$PATH:/usr/local/mysql/bin' >> /etc/profile")
    run("source /etc/profile")


def uninstall_app(appName):
    res = run("rpm -qa |sed -n '/"+appName+"/p'")
    # print(res+"============")
    if res.strip() != '':
        run("rpm -e --nodeps " + res)
    else:
        puts("软件已经卸载/输入错误")


def install_rabbitmq():
    """
    安装rabbitmq
    :return:
    """
    execute(install_erlang)
    put(local_path="../rabbitmq/rabbitmq-server-generic-unix-3.6.2.tar.xz", remote_path="/tmp")
    with cd("/tmp"):
        name = _unzip_("rabbitmq-server-generic-unix-3.6.2.tar.xz")
        run("mv " + name + " /usr/local/rabbitmq")
    run("echo 'export PATH=$PATH:/usr/local/rabbitmq/sbin' >> /etc/profile ")
    run("source /etc/profile")
    run("rabbitmq-plugins enable rabbitmq_management")
    run("rabbitmqctl add_user rabadmin 123456 ")
    run("rabbitmqctl set_user_tags rabadmin administrator")
    run("rabbitmqctl set_permissions -p '/' rabadmin '.*' '.*' '.*'")


def install_erlang():
    """
    安装erlang
    :return:
    """
    put(local_path="../rabbitmq/otp_src_19.2.tar.gz", remote_path="/tmp")
    run("yum install gcc gcc-c++ ncurses-devel perl openssl -y")
    with cd("/tmp"):
        run("tar xf otp_src_19.2.tar.gz")
        with cd("otp_src_19.2"):
            run("mkdir -p  /opt/erlang")
            run("./configure --with-ssl=/usr/lib64/openssl --prefix=/opt/erlang")
            run("make && make install")
        run("echo 'export PATH=$PATH:/opt/erlang/bin' >> /etc/profile")
        run("source /etc/profile")


def install_jdk(version="jdk1.8.0_181.tar.gz"):
    """
    安装jdk
    :param version:
    :return:
    """
    jdk_conf = Getcnf.read_cnf("../jdk/jdk.txt")
    # put("../jdk/" + version + "", "/tmp")
    # with cd("/tmp"):
    #     filename = _unzip_(version)
    #     run("mv " + filename + " /usr/local/jdk")
    # print(jdk_conf)
    _write_content_(jdk_conf, "/etc/profile")
    run("source /etc/profile")
    puts("安装jdk完成 path=/usr/local/jdk")


def install_nginx(pcre_version="pcre-8.33.tar.gz", nginx_version="nginx-1.17.0.tar.gz"):
    """
    安装nginx
    :param pcre_version:
    :param nginx_version:
    :return:
    """
    run("yum install -y gcc gcc-c++ zlib-devel openssl-devel")
    put(local_path="../nginx/" + pcre_version + "", remote_path="/tmp")
    put(local_path="../nginx/" + nginx_version + "", remote_path="/tmp")
    with cd("/tmp"):
        dir_name = _unzip_(pcre_version)
        with cd(dir_name):
            run(" ./configure")
            run("make && make install")
    with cd("/tmp"):
        dir_name = _unzip_(nginx_version)
        with cd(dir_name):
            run("./configure --prefix=/usr/local/nginx --with-http_stub_status_module "
                "--with-http_ssl_module --with-stream")
            run("make && make install")


def install_oracle(version = ["linux.x64_11gR2_database_1of2.zip", "linux.x64_11gR2_database_2of2.zip"]):
    """
    安装oracle
    :param version:
    :return:
    """
    run("mkdir -p /home/tmp")
    for ver in version:
        put(local_path="../oracle/" + ver + "", remote_path="/home/tmp")
        with cd("/home/tmp"):
            run("unzip -q " + ver + " -d /data")
    run("mkdir -p /data/etc")
    run("cp /data/database/response/* /data/etc/")
    put(local_path="../oracle/db_install.rsp", remote_path="/data/etc")
    put(local_path="../oracle/dbca.rsp", remote_path="/data/etc")
    res = run("su - oracle -c \"/data/database/runInstaller -silent "
              "-responseFile /data/etc/db_install.rsp -ignorePrereq\"")
    time.sleep(10)
    res = ""
    while res.strip() == '':
        time.sleep(3)
        res = run("cat /home/oracleapp/app/oracle/inventory/logs/installActions*.log| "
                  "sed -n '/Shutdown Oracle Database/p'")
    res2 = run("cat /home/oracleapp/app/oracle/inventory/logs/oraInstall*.out| "
               "sed -n '/Successfully Setup Software./p'")
    if res2.strip() != "":
        print("下一步")
        run("sh /home/oracleapp/app/oracle/inventory/orainstRoot.sh")
        run("sh /home/oracleapp/app/oracle/product/11.2.0/root.sh")
    else:
        abort('安装失败')


def before_install_oracle():
    """
    安装oracle之前的环境变量配置
    :return:
    """
    conf_dirt = Getcnf.read_cnf("../oracle/conf.txt")
    run("yum install binutils compat-libstdc++ elfutils-libelf elfutils-libelf-devel "
        "elfutils-libelf-devel-static gcc gcc-c++ glibc glibc-common glibc-devel "
        "glibc-headers kernel-headers ksh libaio libaio-devel libgcc libgomp libstdc++ "
        "libstdc++-devel make sysstat unixODBC unixODBC-devel unzip -y")
    run("hostnamectl set-hostname oracledb")
    run("echo '127.0.0.1   oracledb' >>/etc/hosts")
    run("sed -i 's/SELINUX=enforcing/SELINUX=disabled/' /etc/selinux/config ")
    run("setenforce 0")
    run("groupadd oinstall")
    run("groupadd dba")
    run("groupadd oper")
    run("useradd -g oinstall -G dba oracle")
    _write_content_(conf_dirt, '/etc/sysctl.conf')
    run("sysctl -p")
    _write_content_(conf_dirt, '/etc/security/limits.conf')
    run("echo 'session  required   pam_limits.so' >> /etc/pam.d/login")
    _write_content_(conf_dirt, '/etc/profile')
    run("source /etc/profile")
    _write_content_(conf_dirt, '/etc/rc.d/rc.local')
    run("mkdir -p /home/oracleapp")
    run("mkdir -p /home/oracleapp/app")
    run("chown -R oracle:oinstall /home/oracleapp")
    run("chmod -R 775 /home/oracleapp")
    _write_content_(conf_dirt, "/home/oracle/.bash_profile")


def after_install_oracle():
    """
    初始化数据库，oracle systemctl启用
    :return:
    """
    run("su - oracle -c \"netca /silent /responsefile /data/etc/netca.rsp\"")
    run("su - oracle -c \"dbca -silent -responseFile /data/etc/dbca.rsp\"")
    run("su - oracle -c \"lsnrctl status\"")
    run("mkdir -p /etc/init/")
    put(local_path="../oracle/oracle", remote_path="/etc/init")
    put(local_path="../oracle/oracle.service", remote_path="/usr/lib/systemd/system")
    _replace_("ORACLE_HOME_LISTNER=$1", "ORACLE_HOME_LISTNER=$ORACLE_HOME",
              "/home/oracleapp/app/oracle/product/11.2.0/bin/dbstart")
    _replace_("ORACLE_HOME_LISTNER=$1", "ORACLE_HOME_LISTNER=$ORACLE_HOME",
              "/home/oracleapp/app/oracle/product/11.2.0/bin/dbshut")
    _replace_("orcl:\/home\/oracleapp\/app\/oracle\/product\/11.2.0\:N",
              "orcl:\/home\/oracleapp\/app\/oracle\/product\/11.2.0\:Y", "/etc/oratab")
    run("chmod +x /etc/init/oracle ")
    run("chmod 754 /usr/lib/systemd/system/oracle.service  ")
    run("systemctl enable oracle")


def ls_dir_local(path):
    for _, _, files in os.walk(path):
        print(files)
        return files


def _write_content_(content, remote_path):
    print(content[remote_path]['content'])
    for line in content[remote_path]['content']:
        line = line.replace("$", "\\\\$")
        run("echo \"" + line + "\" >> " + remote_path + "")


def test():
    # with settings(show('everything'), warn_only=True):
    # res = run("ls -l /usr/local/redis/bin")
    # _replace_("daemonize no", "daemonize yes", "/usr/local/redis/etc/redis.conf")
    # put(remote_path='/tmp',local_path='./utils')
    # put(remote_path='/tmp', local_path='./utils')
    # res = run("sed -i '3p' /etc/vsftpd/vsftpd.conf")
    # run("sed -n '/anonymous_enable=/p' /etc/vsftpd/vsftpd.conf.bak")
    # run("sed -i 's/anonymous_enable=NO/anonymous_enable=yes/g' /etc/vsftpd/vsftpd.conf.bak ")
    # _replace_('anonymous_enable=yes', 'anonymous_enable=NO', '/etc/vsftpd/vsftpd.conf.bak')
    # if not res is None:
    #     run("mkdir /etc/yum.repos.d/old")
    #     run("mv *repo /etc/yum.repos.d/old")
    # run("touch /etc/yum.repos.d/rhel-cdrom.repo")
    # run("touch /usr/local/111.conf")
    # run("groupadd mysql && useradd -g mysql:mysql")
    # run("rpm -qa |sed -n '/123/p'")
    # with remote_tunnel(3306):
    # put(local_path="../mysql/updatePassword.sql",remote_path="/tmp")
    # with settings(user="oracle"):
    #     run("who")
    # execute(ls_dir_local, "../mysql")
    # execute(install_erlang)
    # put(remote_path="/tmp", local_path="../redis/redis-5.0.8.tar.gz")
    # run("su - oracle -c \"echo 'export ORACLE_BASE=/home/oracleapp/app/oracle/' >> /home/oracle/.bash_profile\"")
    # run("cat /home/oracleapp/app/oracle/inventory/logs/oraInstall*.out| sed -n '/Successfully Setup Software./p'")
    # run("tail -f /home/oracleapp/app/oracle/inventory/logs/installAction*.log")
    # res = run("cat /home/oracleapp/app/oracle/inventory/logs/installActions*.log| "
    #           "sed -n '/Shutdown Oracle Database/p'")
    # run("ls /var/tmp/.oracle")
    put(local_path="../oracle/dbca.rsp", remote_path="/data/etc")


def main():
    switch = {
        '1': set_cd_repo,
        '2': install_jdk,
        '3': install_nginx,
        '4': install_rabbitmq,
        '5': install_redis,
        '6': install_mysql,
        '7': install_oracle
    }
    choice = input("请输入你要安装的程序\n"
                   "1.设置光盘为yum源头\n"
                   "2.安装jdk\n"
                   "3.安装nginx\n"
                   "4.安装rabbitmq\n"
                   "5.安装redis\n"
                   "6.安装mysql\n"
                   "7.安装oracle\n")
    print(type(choice))
    switch.get(choice)()


if __name__ == '__main__':
    # files = ls_dir_local("../redis")
    # abc = execute(ls)
    # print("hello world")
    # print("安装redis：")
    # for index, file in enumerate(files):
    #     print(str(index)+'.'+file)
    # files_index = int(input("请输入要安装的版本："))
    # version = files[files_index]
    # execute(install_redis, version)
    # execute(set_cd_repo)
    # sys.exit(1)
    main()
    branch = input("按enter回到主菜单，按q退出此程序")
    switch = {
        '': main,
        'e': '退出'
    }


