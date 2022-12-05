import paramiko 
host1 = '172.16.0.1'
host2 = '172.16.0.2'
user = 'cisco'
secret = 'Cisco123'
port = 22

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy()) 
ssh.connect(hostname=host1, username=user, password=secret, port=port)
stdin, stdout, stderr = ssh.exec_command('erase startup-config')
stdin, stdout, stderr = ssh.exec_command('/n')
stdin, stdout, stderr = ssh.exec_command('reload')
stdin, stdout, stderr = ssh.exec_command('/n')
list = stdout.readlines()
ssh.connect(hostname=host2, username=user, password=secret, port=port)
stdin, stdout, stderr = ssh.exec_command('erase startup-config')
stdin, stdout, stderr = ssh.exec_command('/n')
stdin, stdout, stderr = ssh.exec_command('reload')
stdin, stdout, stderr = ssh.exec_command('/n')
list = stdout.readlines()
print(list)
