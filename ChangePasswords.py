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
username = ""
newPassword = ""
prevPassword = ""
comptuers = []
unavailableComputers = []

MAINCOMPUTERFILE = "computers.txt"
AUTOCOMPUTERFILE = "unavailableComputers.txt"
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
    global computers
    computers = compFile.read().splitlines()
    global username
    username = computers.pop(0)
    global AUTOCOMPUTERFILE
    compFile = open(AUTOCOMPUTERFILE)
    lines = compFile.read().splitlines()
    global prevPassword
    prevPassword = lines[1]
    print (prevPassword)
    log.write("User Run" + str(datetime.date.today()))

#initializes variables when run by the task scheduler
def autoStart():
    global AUTOCOMPUTERFILE
    compFile = open(AUTOCOMPUTERFILE)
    global computers
    computers = compFile.read().splitlines()
    global username
    username = computers.pop(0)
    global newPassword
    newPassword = computers.pop(0)
    global prevPassword
    prevPassword = computers.pop(0)
    compFile.close()
    log.write("Auto run " + str(datetime.date.today()))

#Pings the comptuers to see if they are online
def pingComputers():
    global computers
    tempComputers = list(computers)
    global unavailableComputers
    for x in xrange(0, len(tempComputers)):
        remoteComp = tempComputers[x]
        print "pinging " + remoteComp
        ping = os.popen("ping " + remoteComp)
        j = ping.read()
        ping.close()
        if "unreachable" not in j:
            print tempComputers[x] + " found"
        else:
            print tempComputers[x] + " not found"
            unavailableComputers.append(tempComputers[x])
            computers.remove(tempComputers[x])

def writeFiles():
    global unavailableComputers
    global  AUTOCOMPUTERFILE
    outfile = open(AUTOCOMPUTERFILE, "w")
    outfile.write(username + "\n")
    outfile.write(newPassword + "\n")
    outfile.write(prevPassword + "\n")
    outfile.write("\n".join(unavailableComputers))
    outfile.close()

def changePasswords():
    global comptuers
    global unavailableComputers
    global username
    global prevPassword
    global newPassword
    global log

    log.write("Previous Password: " + prevPassword + "\nNewPassword: " + newPassword + "\n")

    for x in xrange(0, len(computers)):
        remoteComp = computers[x]
        log.write("pspasswd " + "\\\\" + remoteComp + " -u " + username + " -p " + prevPassword + " " + username + " " + newPassword + "\n")
        stream = subprocess.Popen("pspasswd " + "\\\\" + remoteComp + " -u " + username + " -p " + prevPassword + " " + username + " " + newPassword + "", shell=True, stderr = subprocess.PIPE, stdout=subprocess.PIPE)
        return_code = stream.wait()
        output = stream.stdout.read()
        print stream.stderr.read()
        print stream.stdout.read()
        log.write(stream.stdout.read())
        log.write(stream.stderr.read())
        #stream.close()
        if "successfully changed" in output:
            print "Sucessfully changed password for " + computers[x]
        else:
            print "Can't change password for " + computers[x]
            unavailableComputers.append(computers[x])

if(len(sys.argv) != 1):
    if sys.argv[1] == "auto":
        autoStart()
    else:
        print "Error"
        log.close()
        sys.exit(1)
else:
    start()
    getPassword()

pingComputers()
if not len(computers):
    log.close()
    sys.exit(0)
changePasswords()
writeFiles()
log.write("All computers: " + ', '.join(computers) + "\n")
log.write("Unavailable Computers" + ', '.join(unavailableComputers) + "\n")
log.write("--------------------------------------------------------------------\n")
log.close()
