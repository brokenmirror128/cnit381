import paramiko
import time
import getpass

ssh_client = paramiko.SSHClient()
ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ip = '172.16.0.2'
ip2 = '172.16.0.5'
username = 'cisco'
password = 'cisco123!'


ssh_client.connect(ip,username=username,password=password, look_for_keys=False, allow_agent=False)
shell = ssh_client.invoke_shell()
shell.send('erase startup-config\n')
shell.send('reload\n')
shell.send('\n')
shell.send('\n')
time.sleep(1)
output = shell.recv(10000)
output = output.decode('utf-8') 
print(output)
if print(ssh_client.get_transport().is_active()) == True:
    print('Closing connection')
    ssh_client.close()
    
    
ssh_client.connect(ip2,username=username,password=password, look_for_keys=False, allow_agent=False)
shell = ssh_client.invoke_shell()
shell.send('erase startup-config\n')
shell.send('reload\n')
shell.send('\n')
shell.send('\n')
time.sleep(1)
output = shell.recv(10000)
output = output.decode('utf-8') 
print(output)
if print(ssh_client.get_transport().is_active()) == True:
    print('Closing connection')
    ssh_client.close()
