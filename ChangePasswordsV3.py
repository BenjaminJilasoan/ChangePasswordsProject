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
# Version 1.02
#
# Notes: For this program to work, the settings of the computers
# where the passwords are being changed must allow for remote users
# to run commands
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

def encrypt(key, msg):
    encryped = []
    for i, c in enumerate(msg):
        key_c = ord(key[i % len(key)])
        msg_c = ord(c)
        encryped.append(chr((msg_c + key_c) % 127))
    return ''.join(encryped)

def decrypt(key, encryped):
    msg = []
    for i, c in enumerate(encryped):
        key_c = ord(key[i % len(key)])
        enc_c = ord(c)
        msg.append(chr((enc_c - key_c) % 127))
    return ''.join(msg)

#Gets the password from the user and sets it to newPassword
def getPassword():
    global newPassword
    newPassword = getpass.getpass()
    print "Please re-enter password"
    passwordCheck = getpass.getpass()
    #Makes sure the password is right twice
    if newPassword != passwordCheck:
        print 'The passwords do not match'
        getPassword()

#Initializes variables for the program when run by the user
def start():
    global MAINCOMPUTERFILE
    compFile = open(MAINCOMPUTERFILE)
    #used for reading all the lines and setting the right values
    tempLines = compFile.read().splitlines()
    global username
    username = tempLines.pop(0)
    global log
    global autorun
    if autorun == True:
        #for autorun, the new password is in the file
        global newPassword
        encNewPassword = tempLines.pop(0)
        newPassword = decrypt("XKQF5gA9nC", encNewPassword)
        log.write("Autorun" + str(datetime.date.today()) + "\n")
    else:
        tempLines.pop(0)
        log.write("User Run " + str(datetime.date.today()) + "\n")

    global computers
    global passwords
    global changed
    for x in xrange(0, len(tempLines)):
        computers.append(tempLines[x].split()[0])
        passwords.append(decrypt("XKQF5gA9nC", tempLines[x].split()[1]))
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
    outfile.write(encrypt("XKQF5gA9nC", newPassword) + "\n")
    for x in xrange(0, len(computers)):
        outfile.write(computers[x] + " " + encrypt("XKQF5gA9nC", passwords[x]) + " " + changed[x] + "\n")
    outfile.close()

def changePasswords():
    global username
    global comptuers
    global passwords
    global changed
    global newPassword
    global log

    #This changes the password of the local computer
    if autorun == False:
        log.write("Command: pspasswd " + username + " " + newPassword + "\n")
        streamLocal = subprocess.Popen("pspasswd " + username + " " + newPassword + "", shell=True, stderr = subprocess.PIPE, stdout=subprocess.PIPE)
        return_code = streamLocal.wait()
        output = streamLocal.stdout.read()
        outputErr = streamLocal.stdout.read()
        log.write(output)
        log.write(outputErr)

        if "successfully changed" in output:
            print "Sucessfully changed password for local computer"
        else:
            print "Couldn't change local password. Please make sure you are running the program as an administrator."
            sys.exit(1)

    for x in xrange(0, len(computers)):
        if changed[x] == "maybe":
            log.write("pspasswd " + "\\\\" + computers[x] + " -u " + username + " -p " + passwords[x] + " " + username + " " + newPassword + "\n")
            stream = subprocess.Popen("pspasswd " + "\\\\" + computers[x] + " -u " + username + " -p " + passwords[x] + " " + username + " " + newPassword + "", shell=True, stderr = subprocess.PIPE, stdout=subprocess.PIPE)
            return_code = stream.wait()
            output = ""
            outputErr = ""
            output = stream.stdout.read()
            outputErr = stream.stderr.read()
            log.write(output)
            log.write(outputErr)
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
changePasswords()
writeFiles()
log.write("New Password: " + newPassword + "\n")
log.write("COMPLETED\n")
log.write("--------------------------------------------------------------------\n")
log.close()
