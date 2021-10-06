#!/usr/bin/python2
# -*- coding: utf-8 -*-
""" Python script will show who is on call duty for the given group"""

__author__ = "Abilash Venu"
__date__ = "2020-12-10"
__version__ = "0.3"

#Import the required libraries
import sys, requests, argparse, os.path
from requests.auth import HTTPBasicAuth
from base64 import b64encode

#Enable Proxy
def setproxy():
    os.environ['http_proxy'] = "http://<proxy_addr>"
    os.environ['https_proxy'] = os.getenv('http_proxy')

#Read file function which will check for the file path and returning base_URL,user and password.
def rfile(fpath):
    if os.path.exists(fpath):
        with open(fpath, 'r') as f:
            base_URL  = f.readline().strip('\n')
            user = f.readline().strip('\n')
            passwd = f.readline().strip('\n')
            userAndPass = b64encode(b"%s:%s" %(user, passwd)).decode("ascii")
            return base_URL, userAndPass
    else:
        print "Read error on File:", fpath
        exit(1)

#BaseData function which will get the raw json data from the amos-xmatters api and passing the values from readfile function.
def baseData(base_URL, userAndPass):
    url = base_URL + '/api/xm/1/on-call?groups='+ ''.join(grp) + '&embed=shift,members.owner'
    #Username and Password are encoded using base64
    response = requests.get(url, headers = {"Authorization": "Basic %s" % userAndPass })
    if (response.status_code == 200):
        json = response.json();
        checkEmptyGroup(json, grpMembers)
    else:
        print 'Invalid GroupName', ''.join(grp), '\n'
        exit(16)

#CheckEmptyGroup function will check whether shift,members and members are empty in a group.
def checkEmptyGroup(json, grpMembers):
    for rawData in json['data']:
        gname = rawData['group']['targetName']
        if 'shift' in rawData:
           sname = rawData['shift']['name']
           print 'Checking for members in', gname + '...'
           if 'members' in rawData and rawData['members']['count'] != 0:
              cnt = rawData['members']['count']
              if cnt < grpMembers:
                 print 'There are only', cnt , 'members in', gname, 'group for the shift', sname, '\n'
				 exit(32)
              else:
                 getOncall(rawData, gname, sname)
           else:
              print 'Shift', sname, 'has no members' '\n'
        else:
            print 'No Shifts defined for the group', gname, '\n'

#GetOnCall function is called if members are defined in the group and that is passed from CheckEmptyGroup function.
def getOncall(rawData, gname, sname):
    print 'Members who is oncall duty for the group',gname, 'for the shift', sname, '\n'
    for membersData in rawData['members']['data']:
        fname = membersData['member']['firstName'].encode('latin-1')
        lname = membersData['member']['lastName'].encode('latin-1')
        uname = membersData['member']['targetName'].encode('latin-1')
        print uname,':', fname, lname

#Pass and check the command-line arguments, prog='oncall.py' is given to display the help message.
parser = argparse.ArgumentParser(prog='oncall.py', usage='%(prog)s <group name or group1,group2(both groups should be valid)>', description='Will show who is oncall duty for the given group or multiple groups')
parser.add_argument('grpname', type=str, nargs='?', default='no group', help=argparse.SUPPRESS)
parser.add_argument('nmem', type=int, nargs='?', help=argparse.SUPPRESS)
args = parser.parse_args()
#Assigning names to the arguments passed.
grp = (args.grpname)
grpMembers = (args.nmem)

#Calling the setproxy function to set the proxy.
setproxy()
#Assigning the baseurl,user and password values from the file located and passing it to the rfile function.
base_URL, userAndPass = rfile("path to xmatters credentials.txt")
#Calling the baseData function to fetch the rawJson data by passing baseurl,username,password from the rfile function.
baseData(base_URL, userAndPass)
