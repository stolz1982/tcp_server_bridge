import socket
import sys
import os
from time import sleep
import time




SDFN_GetStatus = 0
SDFN_ReadTime = 1
SDFN_SetTime = 2
SDFN_ReadVatRates = 3
SDFN_SetVatRates = 4
SDFN_SetHeaders = 5
SDFN_ReadStartEndfmData = 6
SDFN_ReadHeaders = 7
SDFN_ReadDeviceID = 8
SDFN_VersionInfo = 9
SDFN_SignDocument = 10
SDFN_SignRecoverDocument = 11
SDFN_SignELineDocument = 12
SDFN_SendTotals = 13
SDFN_ReadSignEntry = 14
SDFN_ReadSignEntryTotals = 15
SDFN_ReadSummary = 16
SDFN_ReadClosure = 17
SDFN_IssueXReport = 18
SDFN_IssueZReport = 19
SDFN_FiscalRepByZ = 20
SDFN_FiscalRepByDate = 21

#indataValue
startPos=-1
endPos = -1
stx=2
etx=3
EsdIP=""
PathABC=""
esdStatus=""
portNo=int('11001')
retries=5
reqBytes = bytearray()
esdBytesAns = bytearray()
dummyBytes=bytearray()

escConnected=0;


def send_Command_To_ESD(esdSocket,esdCommand,EsdCommandData):
    if pingEsd() == 0:
        if esdCommand == SDFN_SetHeaders:
            esdString="H/1/"
            esdString=esdString+EsdCommandData.replace("/","/1/")
            errorNum = sendStringToESD(esdSocket,esdString)
            if errorNum > 0:
                retData = get_error_text(errorNum)
            else:
                retStr = "Headers Set OK."
                retData = bytearray()
                retData.extend(retStr.encode('ascii'))
                retData.extend((b'\x03'))
    else:
        errorNum = 1003
        retData = get_error_text(errorNum)
    return retData

def getStatus(esdSocket):
    busyStr="IDLE"
    esdID=""
    softVersion=""
    if pingEsd() == 0:
        errorNum = sendStringToESD(esdSocket, "a") # get deviceID
        if errorNum > 0:
            retData = get_error_text(errorNum)
        else:
            if errorNum==-1:
                busyStr="BUSY"
            else:
                ansString = esdBytesAns.decode('ascii')
                ansArray = ansString.split('/')
                esdID=ansArray[3]
                errorNum = sendStringToESD(esdSocket, "v")  # get software version
                if errorNum > 0:
                    retData = get_error_text(errorNum)
                else:
                    if errorNum == -1:
                        busyStr = "BUSY"
                    else:
                        ansString = esdBytesAns.decode('ascii')
                        ansArray = ansString.split('/')
                        softVersion = ansArray[5]

        if errorNum<1:
            retStr= busyStr+" "+esdID+" "+softVersion
            retData = bytearray()
            retData.extend(retStr.encode('ascii'))
            retData.extend((b'\x03'))
    else:
        errorNum=1003
        retData = get_error_text(errorNum)
    return retData


def issueZReport(esdSocket):
    if pingEsd() == 0:
        errorNum=sendStringToESD(esdSocket,"x/2///")
        if errorNum>0:
            retData = get_error_text(errorNum)
        else:
            errorNum = sendStringToESD(esdSocket, "Z/")
            if errorNum>0:
                retData = get_error_text(errorNum)
            else:
                esdAns = esdBytesAns.decode('ascii')
                esdAp = esdAns.split('/')
                lastZNo = esdAp[3]
                esdString = "R/" + lastZNo
                errorNum = sendStringToESD(esdSocket, esdString)
                if errorNum > 0:
                    retData = get_error_text(errorNum)
                else:
                    retData = make_C_File(esdBytesAns, lastZNo)
    else:
        errorNum=1003
        retData = get_error_text(errorNum)
    return retData


def sendStringToESD(esdSocket,dataStr):
    global retries
    global esdBytesAns
    tries=0
    esdBytesAns=bytearray()
    while tries<retries:
        toESDBytes = bytearray()
        toESDBytes.extend(dataStr.encode('ascii'))
        toESDBytes.extend(b'\x03')
        try:
            esdSocket.sendall(toESDBytes)
            esdData = get_data_from_socket(esdSocket)
            errorNum = ESD_Errors_Found(esdData)
            if errorNum == -1:
                tries = tries + 1
                sleep(1)
            if errorNum == 0:
                esdBytesAns = esdData
                break
            if errorNum > 0:
                esdBytesAns = esdData
                break
        except:
            errorNum=-1
            tries = tries + 1
            sleep(1)
    if errorNum==-1: # if busy after retries device offline
        errorNum=1003
    return errorNum

def pingEsd():
    hostname = EsdIP
    tries=0
    while tries < 2:
        response = os.system("ping -c 1 " + hostname)
        if response >0:
            tries=tries + 1
        else:
            break
    return response


def make_C_File(esdAns,lastZ):
    global PathABC
    ansString = esdAns.decode('ascii')
    ansArray = ansString.split('/')
    ZDate = ansArray[5]
    ZDateForFile = ZDate[4:] + ZDate[2:4] + ZDate[0:2]
    ZTime = ansArray[6]
    ZTimeForFile=ZTime[0:2]+ZTime[2:4]
    CFilename=ansArray[9]+ZDateForFile+ZTimeForFile+paddedWithZeros(4,lastZ)+"_c.txt"
    f = open(os.path.join(PathABC, CFilename), "+w")
    f.write(ansArray[7])
    f.close()
    retStr="Issue Z# "+lastZ+" ok."
    FromESDBytes = bytearray()
    FromESDBytes.extend(retStr.encode('ascii'))
    FromESDBytes.extend((b'\x03'))
    return FromESDBytes



def signText(esdSocket,EsdCommandData):
    global esdBytesAns
    errorsFound = 0
    if pingEsd() == 0:
        signatureData = EsdCommandData
        errorNum = sendStringToESD(esdSocket, "{/0")
        if errorNum > 0:
            retData = get_error_text(errorNum)
        else:
            while len(signatureData)>0:
                if len(signatureData)< 500:
                    toESDBytes = bytearray()
                    esdString = "@/"
                    esdString=esdString+signatureData
                    errorNum = sendStringToESD(esdSocket, esdString)
                    if errorNum > 0:
                        retData = get_error_text(errorNum)
                        errorsFound=1
                    break
                else:
                    esdString = "@/"
                    esdString = esdString + signatureData[0:500]
                    errorNum = sendStringToESD(esdSocket, esdString)
                    if errorNum > 0:
                        esdData = get_error_text(errorNum)
                        errorsFound=1
                        break
                    else:
                        signatureData = signatureData[500:]

            if errorsFound==0:
                errorNum = sendStringToESD(esdSocket,"}")
                if errorNum > 0:
                    retData = get_error_text(errorNum)
                else:
                    retData = make_AB_files(EsdCommandData, esdBytesAns)
                    errorNum = sendStringToESD(esdSocket, "{/2")
                    if errorNum > 0:
                        dummyBytes = get_error_text(errorNum)
                    else:
                        errorNum = sendStringToESD(esdSocket, "@/1234567890")
                        if errorNum > 0:
                            dummyBytes = get_error_text(errorNum)
                        else:
                            errorNum = sendStringToESD(esdSocket, "}")
                            if errorNum > 0:
                                dummyBytes = get_error_text(errorNum)
    else:
        errorNum = 1003
        retData = get_error_text(errorNum)
    return retData

def make_AB_files(commandData,esdBAns):
    global PathABC
    ansString=esdBAns.decode('ascii')
    ansArray=ansString.split('/')
    sigDateTime=ansArray[5]
    strForFile=sigDateTime[4:]+sigDateTime[2:4]+sigDateTime[0:2]
    ABFilename=ansArray[8]+strForFile+paddedWithZeros(4,ansArray[9])+paddedWithZeros(4,ansArray[4])
    # create _A file
    aFile=ABFilename+"_a.txt"

    f = open(os.path.join(PathABC, aFile),"+w")
    f.write(commandData)
    f.close()

    strTime=ansArray[6]
    retStr = ansArray[7]+" "
    retStr = retStr+paddedWithZeros(4,ansArray[9])+" "
    retStr = retStr+paddedWithZeros(4,ansArray[4])+" "
    retStr = retStr+strForFile+strTime[0:4]+" "
    retStr = retStr + ansArray[8]
    # create _B file
    bFile = ABFilename + "_b.txt"
    f = open(os.path.join(PathABC, bFile), "+w")
    f.write(retStr)
    f.close()
    retData = bytearray()
    retData.extend(retStr.encode('ascii'))
    retData.extend((b'\x03'))
    return retData


def ESD_Errors_Found(ansData):
    ansStr=ansData.decode('ascii')
    ansParts=ansStr.split("/")
    if ansParts[0]=="00":
        return 0   # OK
    elif ansParts[0]=="0E":
        return -1 # device busy
    elif ansParts[0]=="17":
        return 1002 # busy in menu
    elif ansParts[0]=="19":
        return 1001 # paper end
    elif ansParts[0]=="1B":
        return 1003 # device is offline
    elif ansParts[0]=="0A":
        return 1005 # day open
    else:
        return 1004 # other error


def get_error_text(errNo):
    retData=bytearray()
    if errNo==1001:
        retText="ERROR 1001: Paper End or Head Up"
    elif errNo==1002:
        retText="ERROR 1002: Busy in Menu"
    elif errNo == 1003:
        retText = "ERROR 1003: Device Offline"
    elif errNo == 1004:
        retText = "ERROR 1004: General/Unknown Error"
    elif errNo == 1005:
        retText = "ERROR 1005: Day Open"
    else:
        retText = "ERROR 1004: General/Unknown/Undefined Error"
    retData.extend(retText.encode('ascii'))
    retData.extend((b'\x03'))
    return retData

def paddedWithZeros(totalLen,data):
    dlen=len(data)
    padZeros=totalLen-dlen
    return "0"*padZeros+data

def get_data_from_socket(esdSocket):
    timerStart=time.time()
    busyStr="1B/00/00/"
    ansBytes = bytearray()
    while True:
        data = esdSocket.recv(1024)
        if data:
            ansBytes.extend(data)
            break
        else:
            if time.time()-timerStart>5:
                ansBytes=busyStr.encode('ascii')
                break
    return ansBytes


def handle_client_command(esdSocket, commandBytes):
    esdData=bytearray()
    clientCommand=commandBytes.decode('ascii')
    clientParts=clientCommand.split(":")
    if len(clientParts) < 2:
        esdStr="error 1000:unknown command"
        esdData=esdStr.encode('ascii')
    else:
        if clientParts[0] == "issuez":
            esdData=issueZReport(esdSocket)
        elif clientParts[0] == "header":
            esdData = send_Command_To_ESD(esdSocket, SDFN_SetHeaders, clientParts[1])
        elif clientParts[0] == "sign":
            sigdata=get_signature_data(clientCommand)
            esdData = signText(esdSocket, sigdata)
        elif clientParts[0]=="status":
            esdData=getStatus(esdSocket)

    return esdData


def get_signature_data(cliComm):
    colPos=cliComm.find(":")
    return cliComm[colPos+1:]

# read configuration file
def get_script_path():
    return os.path.dirname(os.path.realpath(sys.argv[0]))

confFileName = get_script_path()+"/tcpSig.cfg"
with open(confFileName) as f:
    lines = f.readlines()

for cfgData in lines:
    cfgs=cfgData.strip()
    cfgd=cfgs.split("=")
    if cfgd[0]=="esdIP":
        EsdIP=cfgd[1]
    elif cfgd[0]=="pathABC":
        PathABC=cfgd[1]
    elif cfgd[0]=="port":
        portNo=int(cfgd[1])
    elif cfgd[0]=="retries":
        retries = int(cfgd[1])

def connectToESD():
    global sockCli
    client_address = (EsdIP, 80)
    print('starting client up on {} port {}'.format(*client_address))
    sockCli = socket.socket()
    sockCli.connect(client_address)


# check for pathABC directory if it does not exist create
if not os.path.exists(PathABC):
    os.mkdir(PathABC)


# Bind the socket to the port
server_address = ('127.0.0.1', portNo)
print('starting up on {} port {}'.format(*server_address))
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(server_address)
sock.listen(1)

try:
   connectToESD()
   escConnected = 1
except:
    print ("ESD device not found! Check IP address in configuration file")
    sys.exit(1)


while True:
    # Wait for a connection
    print('waiting for a connection')
    connection, client_address = sock.accept()
    try:
        print('connection from', client_address)
        # Receive the data in small chunks and retransmit it
        while True:
            data = connection.recv(1024)
            if data:
                reqBytes.extend(data)
                startPos=reqBytes.find(stx)
                if startPos > -1:
                    reqBytes=reqBytes[startPos+1:]
                endPos = reqBytes.find(etx)
                if endPos>-1:
                    reqBytes = reqBytes[:endPos]
                    replyBytes=handle_client_command(sockCli,reqBytes)
                    connection.sendall(replyBytes)
                    reqBytes=bytearray()
            else:
                print('no data from', client_address)
                break

    finally:
        # Clean up the connection
        connection.close()