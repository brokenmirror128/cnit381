import threading
import time
import json
import requests
import os
import yaml
import subprocess
import ansible_runner

### teams Bot ###
from webexteamsbot import TeamsBot
from webexteamsbot.models import Response

### Utilities Libraries
import routers
import monitor1 as monitor1
import useless_skills as useless
import useful_skills as useful


# Router Info 
device_address = routers.router1['host']
device_username = routers.router1['username']
device_password = routers.router1['password']

# Make Thread list
threads = list()
exit_flag = False # Exit flag for threads

# RESTCONF Setup
port = '443'
url_base = "https://{h}/restconf".format(h=device_address)
headers = {'Content-Type': 'application/yang-data+json',
           'Accept': 'application/yang-data+json'}

# Bot Details
bot_email = '381bot11@webex.bot'
teams_token = 'NDBjMWEwZWUtMTNhMS00YTgwLTk4MjQtY2RjYWVlZDdjZTRiN2FjNzRiNTYtYjVh_P0A1_b34062fa-24f1-480f-a815-05d10d8cf4f2'
bot_url = "https://8656-96-41-242-188.ngrok.io/"
bot_app_name = 'CNIT-381 Network Auto Chat Bot'

# Create a Bot Object
#   Note: debug mode prints out more details about processing to terminal
bot = TeamsBot(
    bot_app_name,
    teams_bot_token=teams_token,
    teams_bot_url=bot_url,
    teams_bot_email=bot_email,
    debug=True,
    webhook_resource_event=[
        {"resource": "messages", "event": "created"},
        {"resource": "attachmentActions", "event": "created"},],
)

# Create a function to respond to messages that lack any specific command
# The greeting will be friendly and suggest how folks can get started.
def greeting(incoming_msg):
    # Loopkup details about sender
    sender = bot.teams.people.get(incoming_msg.personId)

    # Create a Response object and craft a reply in Markdown.
    response = Response()
    response.markdown = "Hello {}, I'm a friendly NetIntern.".format(
        sender.firstName
    )
    response.markdown += "\n\nSee what I can do by asking for **/help**."
    return response

def arp_list(incoming_msg):
    """Return the arp table from device
    """
    response = Response()
    arps = useful.get_arp(url_base, headers,device_username,device_password)

    if len(arps) == 0:
        response.markdown = "I don't have any entries in my ARP table."
    else:
        response.markdown = "Here is the ARP information I know. \n\n"
        for arp in arps:
            response.markdown += "* A device with IP {} and MAC {} are available on interface {}.\n".format(
               arp['address'], arp["hardware"], arp["interface"]
            )

    return response

def ligma(incoming_msg):
    sender = bot.teams.people.get(incoming_msg.personId)
    response = Response()
    response.markdown = "Whats Ligma?"
    return response

def ligmaResponse(incoming_msg):
    sender = bot.teams.people.get(incoming_msg.personId)
    response = Response()
    response.markdown = ":("
    return response

def sys_info(incoming_msg):
    """Return the system info"""
    response = Response()
    info = useful.get_sys_info(url_base, headers,device_username,device_password)

    if len(info) == 0:
        response.markdown = "I don't have any information of this device"
    else:
        response.markdown = "Here is the device system information I know. \n\n"
        response.markdown += "Device type: {}.\nSerial-number: {}.\nCPU Type:{}\n\nSoftware Version:{}\n" .format(
            info['device-inventory'][0]['hw-description'], info['device-inventory'][0]["serial-number"], 
            info['device-inventory'][4]["hw-description"],info['device-system-data']['software-version'])

    return response

def get_int_ips(incoming_msg):
    response = Response()
    intf_list = useful.get_configured_interfaces(url_base, headers,device_username,device_password)

    if len(intf_list) == 0:
        response.markdown = "I don't have any information of this device"
    else:
        response.markdown = "Here is the list of interfaces with IPs I know. \n\n"
    for intf in intf_list:
        response.markdown +="*Name:{}\n" .format(intf["name"])
        try:
            response.markdown +="IP Address:{}\{}\n".format(intf["ietf-ip:ipv4"]["address"][0]["ip"],
                                intf["ietf-ip:ipv4"]["address"][0]["netmask"])
        except KeyError:
            response.markdown +="IP Address: UNCONFIGURED\n"
    return response

def loopback(incoming_msg):
    response = Response()
    ansible_runner.run(private_data_dir='./', playbook='apply-loopbacks.yaml')
    response.text = "The interfaces have been created"
    return response

def start_monitor(incoming_msg):

    response = Response()
    response.markdown = "Monitor starting..."
    #Start the thread for the monitor
    th = threading.Thread(target=monitor1.run_monitor)
    threads.append(th)

    th.start()

    return response

def stop_monitor(incoming_msg):

    response = Response()
    response.markdown = "Stopping the monitor, please wait...\n" 
    monitor1.monitor_flag = False
    for th in threads:
        th.join()
        del(th)
    time.sleep(5)
    return response

def nuke(incoming_msg):
    response = Response()
    response.text = "Are you sure you want to do this? THIS WILL FLATTEN THE NETWORK!!!\n\n"
    response.text += "Type ' o7 ' to nuke the network."
    return response
           
           
def o7(incoming_msg):
    response = Response()
    response.text = "RIP"
    u = "https://giphy.com/gifs/lil-wayne-XrNry0aqYWEhi"
    response.link = u
    exec(open('./nuke.py').read())
    return response
 

# Set the bot greeting.
bot.set_greeting(greeting)

# Add Bot's Commmands
bot.add_command("arp list", "See what ARP entries I have in my table.", arp_list)
bot.add_command("system info", "Checkout the device system info.", sys_info)
bot.add_command("show interfaces", "List all interfaces and their IP addresses", get_int_ips)
bot.add_command("attachmentActions", "*", useless.handle_cards)
bot.add_command("showcard", "show an adaptive card", useless.show_card)
bot.add_command("dosomething", "help for do something", useless.do_something)
bot.add_command("time", "Look up the current time", useless.current_time)
bot.add_command("Check Ligma", "Check the Ligma Server", ligma)
bot.add_command("LIGMA BALLS", ":(", ligmaResponse)
bot.add_command("NUKE","FLATTEN THE NETWORK",nuke)
bot.add_command("o7","FLATTEN THE NETWORK",o7)
bot.add_command("create loopbacks","create lo",loopback)
bot.add_command("monitor", "Start monitoring for network change",start_monitor)
bot.add_command("quit monitor", "Stop running monitor", stop_monitor)


# Every bot includes a default "/echo" command.  You can remove it, or any
bot.remove_command("/echo")

if __name__ == "__main__":
    # Run Bot
    bot.run(host="0.0.0.0", port=5000)
