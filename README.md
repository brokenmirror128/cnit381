# CNIT 381 Final Project
This is Team 5's GitHub Repository for the CNIT 381 Final Project. 
We welcome all contributors to submit a Pull Request for the repository, which will be reviewed by the project team. 

# Setup 
You will need several packages for this application to run. 
```
apt install ngrok -y
pip install ansible
pip install ansible-runner
pip install webexteamsbot
pip install webexteamssocket
pip install paramiko
```

A Webex API token will need to be created and updated in ```381Bot.py```. A ngrok tunnel will also need to be created, using the command ```ngrok http 5000``` in a new terminal. Take the web address from ngrok, update the bot address in ```381Bot.py```, then run ```python 381Bot.py``` to start the application. 

# Commands

```create loopbacks```

This will create loopback interfaces on both routers. 


```check ligma```

This will check the status of the Ligma server. 

```monitor```

This will identify changes in the interface ip address and allow


```quit monitor```

This will stop the monitoring of the vpn.

```o7```

This will nuke the environment. 
