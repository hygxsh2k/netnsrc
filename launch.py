#!/usr/bin/env python

import json
import subprocess

def main():
    netns = json.load(open('netns.json', 'r'))
    veth = json.load(open('veth.json', 'r'))
    for ns in netns:
        name = ns['name']
        subprocess.run(['ip', 'netns', 'add', name])
        subprocess.run(['ip', 'netns', 'set', name, str(ns['id'])])

    it = iter(veth)
    for veth1, veth2 in zip(it, it):
        ns1 = [ns['name'] for ns in netns if ns['id'] == veth2['link_netnsid']].pop()
        ns2 = [ns['name'] for ns in netns if ns['id'] == veth1['link_netnsid']].pop()
        subprocess.run(['ip', 'link', 'add', 'name', veth1['ifname'], 
            'type', 'veth', 'peer', 'name', veth2['ifname']])
        subprocess.run(['ip', 'link', 'set', veth1['ifname'], 'netns', ns1])
        subprocess.run(['ip', 'link', 'set', veth2['ifname'], 'netns', ns2])
        subprocess.run(['ip', 'netns', 'exec', ns1, 
            'ip', 'link', 'set', veth1['ifname'], 'up'])
        subprocess.run(['ip', 'netns', 'exec', ns2, 
            'ip', 'link', 'set', veth2['ifname'], 'up'])
        for addr1 in veth1['addr_info']:
            ip1 = "{}/{}".format(addr1['local'], addr1['prefixlen'])
            subprocess.run(['ip', 'netns', 'exec', ns1, 
                'ip', 'address', 'add', ip1, 'dev', veth1['ifname']])
        for addr2 in veth2['addr_info']:
            ip2 = "{}/{}".format(addr2['local'], addr2['prefixlen'])
            subprocess.run(['ip', 'netns', 'exec', ns2, 
                'ip', 'address', 'add', ip2, 'dev', veth2['ifname']])

if __name__ == '__main__':
    main()
