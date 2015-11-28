import os
import subprocess
import getpass
import time
import sys
import datetime

############################################
#
# Author: Benjamin Lykins
# Date: 11/16/2015
# Version 0.10
#
# Notes: For this program to work, the settings of the computers
# where the passwords must allow for remote users to run commands
#
############################################


#Variables
#the username always taken from the file
username = ""
#the password used in the pspasswd call. Set in the file for autorun or the
#user in getpassword() for manual runs
newPassword = ""
#the variable that keeps track of if it is a user run or automatic run
autorun = True
#the list of ip addresses of the computers. Always taken from file. Never changed
computers = []
#the list of previous passwords of the computers. Changed when pspasswd is
#sucessfully run.
passwords = []
#set to yes or no at beginning. Changed to maybe if pspasswd needs to be run
#on the given computer. Set to yes if pspasswd successful or no or ping or
#pspasswd doesn't work
changed = []

MAINCOMPUTERFILE = "computers.txt"
LOGFILE = "log.txt"
log = open(LOGFILE, "a")
log.write("--------------------------------------------------------------------\n")

#Gets the password from the user
def getPassword():
    global newPassword
    newPassword = getpass.getpass()
    print "Please re-enter password"
    passwordCheck = getpass.getpass()
    if newPassword != passwordCheck:
        print 'The passwords do not match'
        getPassword()

#initializes variables for the program when run by the user
def start():
    global MAINCOMPUTERFILE
    compFile = open(MAINCOMPUTERFILE)
    tempLines = compFile.read().splitlines()
    global username
    username = tempLines.pop(0)
    global log
    global autorun
    if autorun == True:
        global newPassword
        newPassword = tempLines.pop(0)
        log.write("User Run" + str(datetime.date.today()))
    else:
        tempLines.pop(0)
        log.write("Auto run " + str(datetime.date.today()))

    global computers
    global passwords
    global changed
    for x in xrange(0, len(tempLines)):
        computers.append(tempLines[x].split()[0])
        passwords.append(tempLines[x].split()[1])
        changed.append(tempLines[x].split()[2])
        if autorun == False:
            changed[x] = "maybe"
        else:
            if changed[x] == "no":
                changed[x] = "maybe"

#Pings the comptuers to see if they are online
def pingComputers():
    global computers
    global changed
    for x in xrange(0, len(computers)):
        if changed[x] == "maybe":
            print "pinging: " + computers[x]
            ping = os.popen("ping " + computers[x])
            j = ping.read()
            ping.close()
            if "unreachable" not in j:
                print computers[x] + " found" #changed stays as maybe
            else:
                print computers[x] + " not found"
                changed[x] = "no" # it means it couldn't find the comp

def writeFiles():
    global MAINCOMPUTERFILE
    global newPassword
    global username
    global computers
    global passwords
    global changed
    outfile = open(MAINCOMPUTERFILE, "w")
    outfile.write(username + "\n")
    outfile.write(newPassword + "\n")
    for x in xrange(0, len(computers)):
        outfile.write(computers[x] + " " + passwords[x] + " " + changed[x] + "\n")
    outfile.close()

def changePasswords():
    global username
    global comptuers
    global passwords
    global changed
    global newPassword
    global log

    for x in xrange(0, len(computers)):
        if changed[x] == "maybe":
            #print ("pspasswd " + "\\\\" + computers[x] + " -u " + username + " -p " + passwords[x] + " " + username + " " + newPassword + "\n")
            log.write("pspasswd " + "\\\\" + computers[x] + " -u " + username + " -p " + passwords[x] + " " + username + " " + newPassword + "\n")
            stream = subprocess.Popen("pspasswd " + "\\\\" + computers[x] + " -u " + username + " -p " + passwords[x] + " " + username + " " + newPassword + "", shell=True, stderr = subprocess.PIPE, stdout=subprocess.PIPE)
            return_code = stream.wait()
            output = stream.stdout.read()
            print stream.stderr.read()
            print stream.stdout.read()
            log.write(stream.stdout.read())
            log.write(stream.stderr.read())
            #stream.close()
            if "successfully changed" in output:
                print "Sucessfully changed password for " + computers[x]
                passwords[x] = newPassword
                changed[x] = "yes"
            else:
                print "Can't change password for " + computers[x]
                changed[x] = "no"

if(len(sys.argv) != 1):
    if sys.argv[1] == "auto":
        autorun = True
        start()
    else:
        print "Error"
        log.close()
        sys.exit(1)
else:
    autorun = False
    start()
    getPassword()

pingComputers()
#check is any are available
changePasswords()
#print ", ".join(computers)
#print ", ".join(passwords)
#print ", ".join(changed)
writeFiles()
log.write("COMPLETED\n")
log.write("--------------------------------------------------------------------\n")
log.close()
