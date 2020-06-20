import paramiko
import psutil

if __name__ == '__main__':
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect("192.168.254.201", 22, 'root', '123456')
    # stdin, stdout, stderr = client.exec_command(cmd)
    # ##读取信息
    # for line in stdout:
    #     data = json.loads(line)
    #     # print(type(data))
    #     print(data["available"])
    # ##关闭连接
    print(psutil.cpu_count())
    client.close()
