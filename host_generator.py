#!/usr/bin/python

from datetime import datetime
import os
import yaml

output_array = {}

def process_static(data):
    # String to be returned
    new_output_str = ""
    # We already know the type, pop it out
    data.pop("type")
    # Get the header key, and if we have it dump it into the return string and pop the key
    header = data.get("header")
    if header != None:
        new_output_str = ('%s\n%s' % (new_output_str, "################################################################################"))
        new_output_str = ('%s\n# %s' % (new_output_str, header))
        new_output_str = ('%s\n%s' % (new_output_str, "################################################################################"))
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

# Sting to hold the full output
output_hosts_file = ""

# Generate the header to the file
output_hosts_file = ('%s\n%s' % (output_hosts_file, "################################################################################"))
output_hosts_file = ('%s\n%s%s' % (output_hosts_file, "# Generated on ", dt_string))
output_hosts_file = ('%s\n%s' % (output_hosts_file, "################################################################################"))
output_hosts_file = ('%s\n' % (output_hosts_file))
output_hosts_file = ('%s\n' % (output_hosts_file))

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

print(output_hosts_file)