import requests
import time
from netmiko import ConnectHandler
from flask import Flask,request,render_template

def longest_path_http():
    #connection parameters
    params = {
        'device_type': 'linux',
        'ip': '192.168.236.9',
        'username': 'netman',
        'password': 'netman',
        'secret': 'netman',
        'port': '22'
        }
    #connect to the vm using netmiko
    conn = ConnectHandler(**params)

    #clear existing mininet topologies
    ch_op1 = conn.send_config_set(["echo mininet | sudo mn -c",])

    #spin up the custom topology using remote ryu sdn controller
    conn.write_channel("sudo mn --custom mytopo.py --topo=mytopo --controller=remote,ip=127.0.0.1,port=6653 --switch=ovs,protocols=OpenFlow13\n")
    time.sleep(1)
    ch_op2 = conn.read_channel()
    if "word" in ch_op2:
        conn.write_channel("mininet\n")
        time.sleep(1)

    #assign ip address on switch 1 and switch 5 for them to act as default gateways for host and server respectively
    #host and server are already using the ip addresses assigned below as default gatways supplied through custom topology

    #switch1 ip assignment
    url_s2 = 'http://192.168.236.9:8080/router/0000000000000002'
    add_ip_s2 = '{"address":"10.0.0.2/24"}'
    resp1 = requests.post(url = url_s2, data = add_ip_s2)

    #switch5 ip assignment
    url_s3 = 'http://192.168.236.9:8080/router/0000000000000003'
    add_ip_s3 = '{"address":"1.1.1.2/24"}'
    resp2 = requests.post(url = url_s3, data = add_ip_s3)

    pingl1 = conn.send_command("h2 ping 10.0.0.2 -c 10\n")
    print(pingl1)

    #default path next hop out ports for respective network destinations
    #keys are switches
    #values within keys are networks and out ports
    default_path = {3:{"10.0.0.0/24":2},2:{"1.1.1.0/24":3}}
    longest_path = {3:{"10.0.0.0/24":3}, 1:{"1.1.1.0/24":3, "10.0.0.0/24":2},2:{"1.1.1.0/24":2}}
    
    #url for rest call to add flow, associates with the dpid provided in the data
    url_add_flow = "http://192.168.236.9:8080/stats/flowentry/add"

    #change cookie values for each flow entry on the switches
    ckie_val = 1000
    for keys in default_path:
        for val in default_path[keys]:
            #associate respective out_ports with the network destination from default path
            add_flow = '{"dpid":'+str(keys)+', "cookie":'+str(ckie_val)+', "table_id":0, "priority":500, "match": { "dl_type":0x800, "nw_dst":"'+str(val)+'", }, "actions":[{"type":"OUTPUT", "port":'+str(default_path[keys][val])+', }]}'
            resp = requests.post(url = url_add_flow, data = add_flow)
            ckie_val += 1
            
    #change cookie values for each flow entry on the switches
    ckie_val = 2000
    for keys in longest_path:
        for val in longest_path[keys]:
            add_flow = '{"dpid":'+str(keys)+', "cookie":'+str(ckie_val)+', "table_id":0, "priority":100, "match": { "dl_type":0x800, "nw_dst":"'+str(val)+'", }, "actions":[{"type":"OUTPUT", "port":'+str(longest_path[keys][val])+', }]}'
            resp = requests.post(url = url_add_flow, data= add_flow)
            ckie_val += 1
            
    #check if ping works now --> should work
    pingl = conn.send_command("h2 ping h3 -c 10\n")
    print(pingl)
longest_path_http()