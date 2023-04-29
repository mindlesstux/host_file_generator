#!/usr/bin/python

from datetime import datetime
import json
import os
import requests
import time
import yaml


output_array = {}

# Generate header bars
def generate_header(title="DEFAULT TEXT", width=80, character="#", newlinestart=True, newlineend=False):
    new_output_str = ""
    if newlinestart:
        new_output_str = ('%s\n' % (new_output_str))
    new_output_str = ('%s\n%s' % (new_output_str, character*width))
    new_output_str = ('%s\n%s %s' % (new_output_str, character, title))
    new_output_str = ('%s\n%s' % (new_output_str, character*width))
    if newlineend:
        new_output_str = ('%s\n' % (new_output_str))
    return new_output_str


def process_sl1_appliance(data):
    # String to be returned
    new_output_str = ""
    # We already know the type, pop it out
    data.pop("type")
    # Get the header key, and if we have it dump it into the return string and pop the key
    header = data.get("header")
    if header != None:
        new_output_str +=  generate_header(title=header)
        data.pop("header")

    api_host = data.get("API_HOST")
    api_path = data.get("API_PATH_1")
    api_cugs = data.get("API_PATH_2")
    api_user = data.get("API_USER")
    api_pass = data.get("API_PASS")
    if api_host != None and api_path != None and api_cugs != None and api_user != None and api_pass != None:
        data.pop("API_HOST")
        data.pop("API_PATH_1")
        data.pop("API_PATH_2")
        data.pop("API_USER")
        data.pop("API_PASS")
    else:
        return

    # Build the URL
    url = "https://%s%s" % (api_host, api_path)
    response = requests.request("GET", url, auth=(api_user, api_pass), verify=False)
    tmp = response.text
    tmp_apps = json.loads(tmp)
    tmp_data = {}
    tmp_data['cu'] = {}
    tmp_data['mc'] = {}
    tmp_data['db'] = {}
    tmp_data['ap'] = {}
    for k, v in tmp_apps.items():
        module_id = k.split('/')[3]
        module_ip = v['ip']
        module_name = v['name']
        module_descr = v['descr']
        tmp_data[v['type']][module_ip] = [module_id, module_ip, module_name, module_descr]            

    ## TODO: Add a sort here by IP address
    ## TODO: Overrides (someway, somehow)
    ## TODO: Group toggle by type or collector group
    #### Group by: none, ip, cugid, cugname

    z = {"cu": "Data Collectors (CUs)", "mc": "Message Collectors (MCs)", "db": "Database (DBs)", "ap": "Admin Portals (APs)", }
    for g, h in z.items():
        new_output_str +=  generate_header(title=h, width=30)
        x = tmp_data[g]
        for k, v in x.items():    
            # My work specific shortener
            y = str(v[2]).split("-")
            y.pop(0)
            y = '.'.join(y)
            new_output_str = ('%s\n %-16s  module-%-6s mod-%-5s %-30s  %-30s   # %s' % (new_output_str, v[1], v[0], v[0], y, v[2], v[3]))

    # x.x.x.x   module-YY   em7-cu1-ral     # descr
    time.sleep(1)
    return new_output_str

def process_static(data):
    # String to be returned
    new_output_str = ""
    # We already know the type, pop it out
    data.pop("type")
    # Get the header key, and if we have it dump it into the return string and pop the key
    header = data.get("header")
    if header != None:
        new_output_str +=  generate_header(title=header, width=80)
        data.pop("header")
    
    # TODO: Clean this up
    output_array = data
    # TODO: Clean this up
    # Sort the data
    myKeys = list(output_array.keys())
    myKeys.sort()
    sorted_dict = {i: output_array[i] for i in myKeys}

    # Loop over the array getting the keys that are really ips
    for key in sorted_dict:
        # New empty str to use as the str for the host file "row"
        val_row = ""
        # Loop over all items in the key, as we could have multiple domains for a single IP
        for value in sorted_dict[key]:
            # Add the value to the end of the string to be used with the ip
            val_row = "%s %s" % (val_row, value)
        # Combine the key (ip) with the hostnames
        new_row = "%s %s" % (key, val_row)
        # Add the the new row to the return string
        new_output_str = ('%s\n%s' % (new_output_str, new_row))

    return new_output_str

# datetime object containing current date and time
now = datetime.now()
# dd/mm/YY H:M:S
dt_string = now.strftime("%Y-%m-%d %H:%M:%S%z %Z")
gen_string = "Generated on %s" % (dt_string)
# Sting to hold the full output
output_hosts_file = ""

# Generate the header to the file
output_hosts_file +=  generate_header(title=gen_string, width=80, newlineend=True)

# List/Loop all the files in the configs directory
for filename in os.listdir('configs'):

    # Build path+filename
    x_file = 'configs/%s' % (filename)

    # Open the file
    with open(x_file) as f:
        # Process/Load the YAML
        data = yaml.load(f, Loader=yaml.FullLoader)

        # If the 'type' call function set of things
        if data['type'] == "static":
            x = process_static(data)
            output_hosts_file = ('%s\n%s' % (output_hosts_file, x))
        elif data['type'] == "sl1_appliance":
            x = process_sl1_appliance(data)
            output_hosts_file = ('%s\n%s' % (output_hosts_file, x))
        else:
            print("Unkown type: %s" % (data['type']))

print(output_hosts_file)