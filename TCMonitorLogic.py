import paramiko
import time
import re

IP_ADDRESS_REGEX='^(([01]?\d{1,2}|2[0-4]\d|25[0-5])\.){3}([01]?\d{1,2}|2[0-4]\d|25[0-5])$'
CMD_GET_MEMORY = "free -h"

class PUViewer:
    """
    PUViewer class description
    """
    def __init__(self):
        """
        constructor
        """
        self._ssh = paramiko.SSHClient()
        self._ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self._connected = False
        self._connStatus = 'Client was initalized'
        self._host = ''


    def _connect(self,host='127.0.0.1',port='22',username='root', password='root'):
        """
        connection
        """
        self._connected = False
        try:
            self._ssh.connect(host, port, username, password)
            self._connected = True
            self._host = host
        except:
            print("_connect: Exception was catched")

        return self._connected

    def _disconnect(self):
        """
        disconnection
        """
        self._connected = False
        self._connStatus = f'Connection to target {self._host} was closed'

        try:
            self._ssh.close()
        except:
            print("_disconnect: Exception was catched")

    def _executeCmd(self,command=''):

        stdin, stdout, stderr = self._ssh.exec_command(command)

        lines = stdout.readlines()

        return lines

    def disconnect(self):
        self._disconnect()

    def getConnection(self, host='127.0.0.1',port='22',username='root', password='root'):
        """
        getConnection
        """
        self._connected = False

        # call connect method only if ipaddress is in valid format
        if(re.match(IP_ADDRESS_REGEX, host)):

            if( self._connect(host=host,port=port,username=username,password=password) ):
                self._connStatus = 'Connection is ok'
                self._connected = True
            else:
                self._connStatus = f'Connection to target {host} is not possible'

        else:
            self._connStatus = (f'IPaddress {host} format is invalid')

        return self._connStatus

    def isConnected(self):
        """
        getConnectionState
        """
        return self._connected

    def getConnectionStatus(self):
        """
        getConnectionStatus
        """
        return self._connStatus

    def getMemory(self, host='127.0.0.1',port='22',username='root', password='root'):
        """
        getMemory
        """
        if (self._connected == False):
            return "Please connect to target first"

        else:
            return self._executeCmd(self, command=CMD_GET_MEMORY)

