#libraries and utilites 
import requests
import json
import time
import xrouters
import yaml
from urllib3.exceptions import InsecureRequestWarning
from ansible_runner import Runner

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

def run_monitor():
    # Router Info 
    device_address = xrouters.router2['host']
    device_username = xrouters.router2['username']
    device_password = xrouters.router2['password']

    # RESTCONF Setup
    port = '443'
    url_base = "https://{h}/restconf".format(h=device_address)
    headers = {'Content-Type': 'application/yang-data+json',
            'Accept': 'application/yang-data+json'}

    #set global variable of interface ip address of new vs old
    url = url_base + "/data/ietf-interfaces:interfaces"
    global brach_g1_ip
    global old_g1_ip
    branch_g1_ip = "172.16.0.2"
    old_g1_ip = ""


    #Start a timer to schedule event checks
    starttime = time.time()
    global monitor_flag
    monitor_flag = True

    while monitor_flag == True:

        # GET on the url
        response = requests.get(url,
                            auth=(device_username, device_password),
                            headers=headers,
                            verify=False
                            )
        #grab all interfaces
        intf_list = response.json()["ietf-interfaces:interfaces"]["interface"]

        

        #Checking list of interfaces for Gig1 and see if it changed
        for intf in intf_list:
            if intf["name"] == "GigabitEthernet1":
                g1_ip_new = intf["ietf-ip:ipv4"]["address"][0]["ip"]

                if g1_ip_new != branch_g1_ip:

                    #Setting ip address
                    old_g1_ip = branch_g1_ip
                    branch_g1_ip = g1_ip_new
                    print("IP address for GigabitEthernet2 has been updated to " + g1_ip_new,
                    ", and the vpn configuration has been updated")

                    yaml = YAML()
                    yaml.preserve_quotes = True

                    with open("vpnreset.yaml") as f:
                        list_file = yaml.load(f)
                        f.close()

                    for i in list_file:
                        i["vars"]["address"] = g1_ip_new

                    with open("vpnreset.yaml","w") as f:
                        yaml.dump(list_file, f)
                        f.close()

                    Runner(['inventory'],'vpnreset.yaml').run()
                    

        #sleep timer
        time.sleep(10 - time.time() % 10)
