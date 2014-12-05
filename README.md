Starting to add the pox controller file to git repository.
The rules should be written in rules.csv.
each line in rules.csv:
switch number;sending host; receiving host; host to forward the traffic; port used for the communication
* we should do that for intermediate switches too.

port_forwarding.csv file contains all of the necessary to output to correct direction.
each line in port_forwarding.csv:
switch number; source; destination; switch port that packets should be sent out

staticmapping.csv file contains information of the ip and mac address for all of the hosts.
each line in staticmapping.csv
host name; ip address; mac address

* * for new network configurations all csv files should be changed.
