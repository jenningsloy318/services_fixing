#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# Jennings Liu@ 2016-10-10 15:09:09

import socket
import fcntl
import struct
import re
import subprocess
import sys
def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15])
    )[20:24])

def get_current_mount():
    cmd='mount|awk \'{if($5~/nfs/)print $0}\'|awk \'{print $1,$NF}\'|tr -d "(|)"| tr -s ":" " "|tr -s "=" " "| awk \'{print $1,$NF}\''
#    curMount=subprocess.check_output(cmd,shell=True,stderr=subprocess.STDOUT)
    MountOut=subprocess.Popen(cmd,shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()
    Mounts={}
    for Mount_line in MountOut:
        if Mount_line:
            for item in Mount_line.strip().split('\n'):
                MountHost=item.split(' ')[0]
                MountIP=item.split(' ')[1]
                Mounts[MountHost]=MountIP
    return Mounts

def umount_nfs(curMount,FutureMount):
    if curMount==FutureMount:
        print("No need to change anything !\n")
        sys.exit()
    else:
        print("Umounting old nfs firstly!\n ")
        for cur_host in curMount.keys():
            for future_host in FutureMount.keys():
                if cur_host ==future_host:
                    curMount.pop(cur_host)
        if curMount:
            for server in curMount.keys():
                print('Umount %s:/logs/flume !'%curmount)
                umount_out=subprocess.Popen('umount -l '+server+':/logs/flume',shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()
                if not umount_out[1]:
        	    print('Umount successfully '+server+umount_out[0]+'!') 
                else:
    	            print("Umount "+server+" Failed!\n")
def mount_nfs(MountDict):
    for host in MountDict.keys():
        print('Mounting the nfs share!')
        print('mount '+host+':/logs/flume '+MountDict[host])
        mount_out=subprocess.Popen('mount '+host+':/logs/flume '+MountDict[host],shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()
        if not mount_out[1]:
            print('Operated successfully: '+mount_out[0].rstrip()+'!\n') 
        else:
            print("Operated  failed:  "+mount_out[0],mount_out[1].rstrip()+'!\n') 

if __name__ == "__main__":
    All_server_mount={'cron2.synnex.org':'/mnt/uscron2_spool',
                      'cron3.synnex.org':'/mnt/uscron3_spool',
                      'cron1.hyvesolutions.org':'/mnt/hycron1_spool',
                      'gis.synnex.org':'/mnt/edigis_spool',
                      'fca-vm-prod-esearch-index.synnex.org':'/mnt/esearch_spool',
                      'mxcron.synnex.org':'/mnt/mxcron_spool',
                      'cacron1.synnex.org':'/mnt/cacron1_spool',
                      'cron1-uk.synnex.org':'/mnt/ukcron1_spool',
                      'caedi.synnex.org':'/mnt/caedi_spool'
                      }
    
    Final_server_mount=All_server_mount
    All_server_IP={}
    Final_server_IP=All_server_IP


    # regex expression to determine pattern which is used to filter the correct nfs server 
    LocalNet=('.').join(get_ip_address('eth0').split('.')[:2])
    if LocalNet=='10.88':
        pattern=re.compile(r'10.88')
    elif LocalNet=='10.84':
        pattern=re.compile(r'10.84|10.93|192.168.18')
    else:
        pattern=re.compile('')


    ##modify the dictionary according to the pattern
    for host in Final_server_mount.keys():
        #hostIP=socket.gethostbyname_ex(host)[2][0]
        hostIP=socket.gethostbyname(host)
        All_server_IP[host]=hostIP
        if not pattern.search(hostIP):
            Final_server_mount.pop(host)
            Final_server_IP.pop(host)
    ##fetch current nfs mount server and its ip address
    curmount=get_current_mount()
 
    ## umount old nfs share if neccessary
    umount_nfs(curmount,Final_server_IP)

   ##mount final nfs share 
    mount_nfs(Final_server_mount)

   ##check the nfs mounting 
    df_out=subprocess.Popen('df -h',shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()
    for df_line in df_out:
        if  df_line:
	    print(df_line)
