import socket
import time
import sys
import os
import select
import threading
import random
import msvcrt
import math
from threading import Thread
messageHistory = []
ip = '127.0.0.1'    # The IP of the server to connect to.
portNum = 9023      # The port number of the server to connect to.
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)    # Staple for sockets all that good stuff.
buffSize = 256      # The size of the send and receive buffer as defined by our protocol.
syncing = 0         # Flag that shows whether the client is syncing with the server or not. - Is this still used?
lastPrinted = 0     # Determines what the last printed message was.
lastReceived = 0    # Determines what the last received message was.
userInput = ''      # The input of the user.
sendThis = ''       # The message to send to the server.
inputThread = 0     # This is the thread that repeatedly loops and gets user input.
resultThread = 0    # This is the thread that repatedly loops and processes messages sent from the server to the client.
mainThread = 0      # This is the thread that starts the other threads.
processThread = 0   # This is the thread that repeatedly loops and sends whatever messages need to be sent to the server.
receiving = False   # Flag that determines whether the client is current receiving information or not.
continueRunning = True      # Flag that determines whether the program should continue running.

def main():
    global ip
    global portNum
    # Allows changing IP and port via command line args/flags.
    if len(sys.argv) == 3:
        ip = str(sys.argv[1])
        portNum = int(sys.argv[2])
    else:
        print 'usage: ./filename.py (--ip | --port)'
        
    # Information.
    print 'Attempting to start client.'
    print 'Server IP: ' + str(ip)
    print 'Server PORT: ' + str(portNum)
    initializeClient()

    while continueRunning:
        'True'
    print 'Connection to the server has been closed. Press any two keys to exit...'
    quitNow = False
    while quitNow == False:
        quitNow = msvcrt.getch()
    inputThread.join()
    resultThread.join()
    mainThread.join()
    processThread.join()
    sys.exit(-1)

# Initialize the threads and start the main one.
def initializeClient():
    global mainThread
    global inputThread
    global processThread
    global resultThread
    global continueRunning
    connectTo(ip, portNum)
    #Start the main thread.
    inputThread = Thread(target=inputLoop, args=())
    resultThread = Thread(target=receptionLoop, args=())
    mainThread = Thread(target=start, args=())
    processThread = Thread(target=processCommands, args=())
    
    mainThread.start()
# Start the other threads and loop repeatedly.
def start():
    global userInput
    global inputThread
    global processThread
    global continueRunning
    inputThread.start()
    processThread.start()
    resultThread.start()
    print 'To send a message, type in anything.'
    print 'To change your username, type: /NICK username password'
    print 'To see online users, type: /STATUS'
    print 'To retrieve the last 20 messages, type: /LAST'
    print 'To quit, press the X on the top right corner of the screen.'
    while continueRunning:
        'Pass.'

# Process what is held in sendThis.
def processCommands():
    global sendThis
    global resultThread
    global continueRunning
    sendToServer('/LAST') #Get history
    while continueRunning:
        if len(sendThis)>0: # If there is something to send...
            sendThis = sendThis.strip() # Get rid of leading white space.
            command = sendThis.split(' ')   # Split into command and content.
            if len(command)>0:  # If there are things to split...
                if command[0]=='/NICK':
                    sendToServer(sendThis)
                elif command[0]=='/LAST':
                    sendToServer(sendThis)
                elif command[0]=='/STATUS':
                    sendToServer(sendThis)
                elif command[0] =='/HELP':
                    displayHelp()
                elif len(command[0])>0 and command[0][0]=='/':
                    'Dump' #Invalid / command.
                else: #All other text.
                    sendThis = '/MSG ' + sendThis
                    sendToServer(sendThis)
            sendThis = '' # flush the sendThis buffer so that it doesn't repeatedly loop.

def displayHelp():
    printNew('To send a message, type in anything.')
    printNew('To change your username, type: /NICK username password')
    printNew('To see online users, type: /STATUS')
    printNew('To retrieve the last 20 messages, type: /LAST')
    printNew('To quit, press the X on the top right corner of the screen.')
    printNew('To repeat these instructions, type: /HELP')
    
# Process user input.        
def inputLoop():
    global userInput
    global sendThis
    global continueRunning
    while continueRunning:
        try:
            newChar = msvcrt.getche()   # get and echo whatever key the user pressed. #TODO: Disallow backspace, delete, etc.
            if newChar==chr(8): #backspace
                if len(userInput)>0: #if there is something to erase....
                    userInput = userInput[:-1]
                    sys.stdout.write(chr(0))
                    sys.stdout.write(chr(8)) 
            elif newChar=='\r': # is enter
                sys.stdout.write(chr(13)) # Bring to front
                for pos in range(len(userInput)):
                    sys.stdout.write(chr(0)) #Erase all chars written
                sys.stdout.write(chr(13)) # bring to front
                sys.stdout.write('\r') # enterrrr
                sendThis = userInput
                userInput = ''
            elif (ord(newChar)>=32 and ord(newChar)<=126): #alpha numerics
                userInput = userInput + newChar
            else:#  Erase the echo.
                sys.stdout.write(chr(8)) 
                sys.stdout.write(chr(0))
                sys.stdout.write(chr(8)) 
            newChar = ''
        except:
            'Input error.'

def receptionLoop():
    while continueRunning:
        receiveResult()

def receiveResult():
    global sock
    global messageHistory
    global lastReceived
    global continueRunning
    eachMsg = ''
    try:
        eachMsg = sock.recv(buffSize)
        eachMsg =  eachMsg.strip()
        first = eachMsg.find('/')
        eachMsg = eachMsg[first-2:] # Formatting fix for 0's that kept getting prefixed.
        lastReceived = lastReceived+1
    except:
        'Connection closed.'
        abortProgram()
    try: # Test to see if the message is an actual message and not a result of an empty socket.
        float(eachMsg)
        'lol invalid'
    except:
        if len(eachMsg)>10:
            messageHistory.append(eachMsg)
            printNew(eachMsg)
    eachMsg = ''

# This prints out a new message. There were formatting issues when multiple people were talking at once.
def printNew(eachMsg):
    #consoleWidth = getConsoleWidth()
    #length = len(userInput)
    #numLines = 1
    #if(length>consoleWidth):
     #   numLines = math.ceil(length/consoleWidth) # Determine how many lines are taken by the user's input.
    #for each in range(numLines):
    #    sys.stdout.write(chr(13)) # Go up that many lines.
    ############################################################################
    ############################################################################
    sys.stdout.write(chr(13)) # Go down to new line.
    sys.stdout.write(eachMsg)# Write new message.
    remaining = 80-len(eachMsg)
    for pos in range(remaining):
        sys.stdout.write(chr(0))
    if remaining<0:
        sys.stdout.write(chr(10)) # Go down to new line.
    sys.stdout.write(userInput) # write what you were typing.
    
def abortProgram():
    global continueRunning
    continueRunning = False
   
def sendToServer(msg):
    if len(msg)<buffSize-2:
        difference = buffSize - len(msg)
        strDiff = ' '*difference
        newMSG = str(msg)+''+str(strDiff)+'\n'
        sock.send(newMSG)
    else:
        print 'Message too long. Limit is 256 chars.'
        
def connectTo(serverIP, serverPort):
    try:
        sock.connect((serverIP, serverPort))
    except:
        print 'ERROR: Unable to connect to the server.'


def getTime():
    curTime = time.ctime()
    curTime = time.strftime("%d/%b/%y - %H:%M:%S")
    return str(curTime)

if __name__ == "__main__":
    main()
