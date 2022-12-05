import threading
import time
import json
import requests
import os
import yaml

### teams Bot ###
from webexteamsbot import TeamsBot
from webexteamsbot.models import Response

### Utilities Libraries
import routers
import useless_skills as useless
import useful_skills as useful
from BGP_Establish import BGP_Neighbors_Established
from Monitor_int import MonitorInterfaces

# Router Info 
device_address = routers.router1['host']
device_username = routers.router1['username']
device_password = routers.router1['password']

### Table building ###
from tabulate import tabulate

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
bot_url = "https://895e-96-41-242-188.ngrok.io/"
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
    response.markdown = "Hello {}, I'm a friendly NetIntern .  ".format(
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
    """Check the Ligma Server
    """
    sender = bot.teams.people.get(incoming_msg.personId)

    # Create a Response object and craft a reply in Markdown.
    response = Response()
           
    response.markdown = "Whats Ligma?"
    return response

def ligmaResponse(incoming_msg):
    """Check the Ligma Server
    """
    sender = bot.teams.people.get(incoming_msg.personId)

    # Create a Response object and craft a reply in Markdown.
    response = Response()
           
    response.markdown = ":("
    return response

def sys_info(incoming_msg):
    """Return the system info
    """
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
    os.system('ansible-playbook -i ./inventory apply-loopbacks.yaml')
    response.text = "The interfaces have been created"
    return response

def check_bgp(incoming_msg):
    """Return BGP Status
    """
    response = Response()
    response.text = "Gathering BGP Information from BGP peers...\n\n"

    bgp = BGP_Neighbors_Established()
    status = bgp.setup('routers.yml')
    if status != "":
        response.text += status
        return response

    status = bgp.learn_bgp()
    if status != "":
        response.text += status

    response.text += bgp.check_bgp()

    return response

def check_int(incoming_msg):
    """Find down interfaces
    """
    response = Response()
    response.text = "Gathering  Information...\n\n"

    mon = MonitorInterfaces()
    status = mon.setup('testbed/routers.yml')
    if status != "":
        response.text += status
        return response

    status = mon.learn_interface()
    if status == "":
        response.text += "All Interfaces are OK!"
    else:
        response.text += status

    return response

def monitor_int(incoming_msg):
    """Monitor interfaces in a thread
    """
    response = Response()
    response.text = "Monitoring interfaces...\n\n"
    monitor_int_job(incoming_msg)
    th = threading.Thread(target=monitor_int_job, args=(incoming_msg,))
    threads.append(th)  # appending the thread to the list

    # starting the threads
    for th in threads:
        th.start()

    # waiting for the threads to finish
    for th in threads:
        th.join()

    return response

def monitor_int_job(incoming_msg):
    response = Response()
    msgtxt_old=""
    global exit_flag
    while exit_flag == False:
        msgtxt = check_int(incoming_msg)
        if msgtxt_old != msgtxt:
            print(msgtxt.text)
            useless.create_message(incoming_msg.roomId, msgtxt.text)
        msgtxt_old = msgtxt
        time.sleep(20)

    print("exited thread")
    exit_flag = False

    return response

def monitor_bgp_job(incoming_msg):
    response = Response()
    msgtxt_old=""
    global exit_flag
    while exit_flag == False:
        msgtxt = check_bgp(incoming_msg)
        if msgtxt_old != msgtxt:
            print(msgtxt.text)
            useless.create_message(incoming_msg.roomId, msgtxt.text)
        msgtxt_old = msgtxt
        time.sleep(20)

    print("exited thread")
    exit_flag = False

    return response

def stop_monitor(incoming_msg):
    """Monitor interfaces in a thread
    """
    response = Response()
    response.text = "Stopping all Monitors...\n\n"
    global exit_flag
    exit_flag = True
    time.sleep(5)
    response.text += "Done!..\n\n"

    return response

def monitor_bgp(incoming_msg):
    """Monitor interfaces in a thread
    """
    response = Response()
    response.text = "Monitoring bgp...\n\n"
    monitor_bgp_job(incoming_msg)
    th = threading.Thread(target=monitor_bgp_job, args=(incoming_msg,))
    threads.append(th)  # appending the thread to the list

    # starting the threads
    for th in threads:
        th.start()

    # waiting for the threads to finish
    for th in threads:
        th.join()

    return response

def nuke(incoming_msg):
    response = Response()
    response.text = "Are you sure you want to do this? THIS WILL FLATTEN THE NETWORK!!!\n\n"
    response.text += "Type ' o7 ' to nuke the network."
    
    return response
           
           
def o7(incoming_msg):
    response = Response()
    response.text = "      _.-^^---....,,--      \n"
    response.text += "  _--                  --_   \n"
    response.text += " <                        >) \n"
    response.text += " |                         | \n"
    response.text += "  \._                   _./ \n"
    response.text += "     ```--. . , ; .--``` \n"
    response.text += "           | |   |  \n"
    response.text += "        .-=||  | |=-. \n"
    response.text += "        `-=#$%&%$#=-` \n"
    response.text += "           | ;  :|   \n"
    response.text += "  _____.,-#%&$@%#&#~,._____ \n"
    
   # response += curl -H "Authorization: NDBjMWEwZWUtMTNhMS00YTgwLTk4MjQtY2RjYWVlZDdjZTRiN2FjNzRiNTYtYjVh_P0A1_b34062fa-24f1-480f-a815-05d10d8cf4f2" https://webexapis.com/v1/contents/Y2lzY29zcGFyazovL3VybjpURUFNOnVzLXdlc3QtMl9yL0NPTlRFTlQvZWZjODU5ZDAtNzRiOS0xMWVkLTgzNjgtNTM3MTEzZjljMDRhLzA
    
    return response


    

# Set the bot greeting.
bot.set_greeting(greeting)

# Add Bot's Commmands
bot.add_command(
    "arp list", "See what ARP entries I have in my table.", arp_list)
bot.add_command(
    "system info", "Checkout the device system info.", sys_info)
bot.add_command(
    "show interfaces", "List all interfaces and their IP addresses", get_int_ips)
bot.add_command("attachmentActions", "*", useless.handle_cards)
bot.add_command("showcard", "show an adaptive card", useless.show_card)
bot.add_command("dosomething", "help for do something", useless.do_something)
bot.add_command("time", "Look up the current time", useless.current_time)
bot.add_command("Check Ligma", "Check the Ligma Server", ligma)
bot.add_command("LIGMA BALLS", ":(", ligmaResponse)
bot.add_command("monitor bgp","begin monitoring bgp",monitor_bgp)
bot.add_command("monitor ints","monitor interfaces",monitor_int)
bot.add_command("stop monitoring","end monitoring jobs",stop_monitor)
bot.add_command("NUKE","FLATTEN THE NETWORK",nuke)
bot.add_command("o7","FLATTEN THE NETWORK",o7)
bot.add_command("create loopbacks","create lo",loopback)



# Every bot includes a default "/echo" command.  You can remove it, or any
bot.remove_command("/echo")

if __name__ == "__main__":
    # Run Bot
    bot.run(host="0.0.0.0", port=5000)
