centos7 开发环境安装工具

功能如下：

    after_install_mysql_step  安装mysql后的步骤，将mysql变成服务
    after_install_oracle      初始化数据库，oracle systemctl启用
    before_install_oracle     安装oracle之前的环境变量配置
    close_process             输入进程名，关闭进程
    install_erlang            安装erlang
    install_jdk               安装jdk
    install_mysql             mysql 安装
    install_nginx             安装nginx
    install_oracle            安装oracle
    install_rabbitmq          安装rabbitmq
    install_redis             安装redis，控制台输出安装地址
    set_cd_repo               设置光盘为yum源头




使用方法：

fab -f Hello.py -list **查看现有功能**

fab -f Hello.py 上述英文模块名 **调用**



目前还有主要功能已经实现后续将把这些功能组合方便调用