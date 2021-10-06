#!/usr/bin/python2
# -*- coding: utf-8 -*-
""" Python script will send a disk report where the server mount points are >=90% used"""

__author__ = "Abilash Venu"
__date__ = "2020-10-28"
__version__ = "0.5"

#Import required Python libraries
import spur
import os
import time
import smtplib
import re
from os import path
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText

#Define variable contains server details,logon info and fetched data
serlist = "/home/username/diskrep/serlist.txt"
freport = "/home/username/diskrep/freport.txt"
logon = "/home/username/diskrep/logon.txt"

#Function to fetch details from remote server and write it to a file
def getinfo():
        global report
        report = "/home/username/diskrep/report.txt"
        if path.exists(report):
                os.remove(report)
        with open(serlist, "r+") as sl, open(logon, "r") as lg:
                usr = lg.readline().strip('\n')
                passwd = lg.readline().strip('\n')
                for line in sl:
                        shell = spur.SshShell(hostname=line.strip(), username=usr, password=passwd, missing_host_key=spur.ssh.MissingHostKey.accept)
                        sername = shell.run(["sh", "-c", "echo -n Server:; hostname"])
                        result = shell.run(["sh", "-c", "df -Ph | awk '+$5 >= 90'"])
                        with open(report, "a+") as rep:
                                rep.write(sername.output)
                                rep.write(result.output + '\n')

#Function to format the raw report
def formatrep():
        rawfile = open(report, "r")
        rawtxt = rawfile.read()
        rawfile.close()
        matches = re.sub(r'Server:\w+\n\n', '', rawtxt).strip()
        with open (freport, "w") as frep:
                frep.write(matches)


#Check if the final report is empty
        if os.stat(freport).st_size == 0:
                with open(freport, "w") as fr:
                        fr.write("All Mount Points are OK!!")


#Function to send the mail to recipients with final formatted report
def sndmail():
        fromaddr = "user@mail.com"
        toaddr = open('/home/username/diskrep/emails.txt', 'r')
        emails = toaddr.read().strip().split('\n')
        msg = MIMEMultipart()
        msg['From'] = fromaddr
        msg['To'] =  ','.join(emails)
        msg['Subject'] = "Disk Report for " + time.strftime("%d/%m/%Y")
        body = open(freport, "r")
        msg.attach(MIMEText(body.read(), 'plain'))
        try:
                server = smtplib.SMTP('SMTP_Mail_Server')
                text = msg.as_string()
                server.sendmail(fromaddr, emails, text)
                print "Successfully sent email"
        except smtplib.SMTPException:
                print "Error: unable to send email"


#Calling the getinfo function to fetch the details from remote servers
getinfo()

#Calling the formatrep function to format the raw report
formatrep()

#Calling the sndmail fuction to send mail finally
sndmail()