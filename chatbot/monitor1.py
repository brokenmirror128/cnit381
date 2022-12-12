import requests
import json
import time
import routers
import yaml
from ruamel.yaml import YAML
from urllib3.exceptions import InsecureRequestWarning
from ansible_playbook_runner import Runner

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

def run_monitor():
    # Router Info 
    device_address = routers.router2['host']
    device_username = routers.router2['username']
    device_password = routers.router2['password']

    # RESTCONF Setup
    port = '443'
    url_base = "https://{h}/restconf".format(h=device_address)
    headers = {'Content-Type': 'application/yang-data+json',
            'Accept': 'application/yang-data+json'}


    url = url_base + "/data/ietf-interfaces:interfaces"
    global brach_g2_ip
    global old_g2_ip
    branch_g2_ip = "172.16.0.2"
    old_g2_ip = ""


    #Start a timer to run the request per the time set
    starttime = time.time()
    #Make this a global to be called in webextbot.py
    global monitor_flag
    
    monitor_flag = True

    while monitor_flag == True:

        # this statement performs a GET on the specified url
        response = requests.get(url,
                            auth=(device_username, device_password),
                            headers=headers,
                            verify=False
                            )

        intf_list = response.json()["ietf-interfaces:interfaces"]["interface"]

        

        #Checking the list of interfaces for Gig2 and comparing to see if it changes
        
        for intf in intf_list:
            if intf["name"] == "GigabitEthernet2":
                g2_ip_new = intf["ietf-ip:ipv4"]["address"][0]["ip"]

                if g2_ip_new != branch_g2_ip:

                    #Set New IP
                    old_g2_ip = branch_g2_ip
                    branch_g2_ip = g2_ip_new
                    print("IP address for GigabitEthernet2 has been updated to " + g2_ip_new,
                    ", and the vpn configuration has been updated")

                    #Edit the ansible monitor file and update with the correct new IP address using ruamel.yaml
                    yaml = YAML()
                    yaml.preserve_quotes = True

                    with open("ansiblevpnreset.yaml") as f:
                        list_file = yaml.load(f)
                        f.close()

                    for i in list_file:
                        i["vars"]["address"] = g2_ip_new

                    with open("ansiblevpnreset.yaml","w") as f:
                        yaml.dump(list_file, f)
                        f.close()

                    Runner(['inventory'],'ansiblevpnreset.yaml').run()
                    #CALL THE ANSIBLE SCRIPT HERE


        #Setting up the sleep time after executing the above code
        time.sleep(10 - time.time() % 10)
