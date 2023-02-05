import paramiko
import time
import re
import string

IP_ADDRESS_REGEX='^(([01]?\d{1,2}|2[0-4]\d|25[0-5])\.){3}([01]?\d{1,2}|2[0-4]\d|25[0-5])$'
CMD_GET_MEMORY = "free -h"
CMD_GET_DISK_USAGE = "df -h"

class SSHConnector:
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


    def _connect(self,host='127.0.0.1',port='22',username='root12', password='root'):
        """
        connection
        """
        self._connected = False
        try:
            self._ssh.connect(host, port, username, password, timeout=3.1)
            print(username)
            self._connected = True
            self._host = host
        except paramiko.ssh_exception.AuthenticationException as ae:
            self._connStatus =(f"Error connection, {ae}")
        except Exception as e:
            self._connStatus = (f"Exception {e} was catched, is SSH target reachable?")

        return self._connected

    def _disconnect(self):
        """
        disconnection
        """
        self._connected = False
        self._connStatus = f'Connection to target {self._host} was closed'

        try:
            self._ssh.close()
        except Exception as e:
            self._connStatus = f"Closing exception: {e}"

    def _executeCmd(self,command=''):

        lines = []

        try:
            lines = []
            stdin, stdout, stderr = self._ssh.exec_command(command)

            lines = stdout.readlines()
        except:
            self._connStatus = f'Invalid command {command} was called'

        return lines

    def closeConnection(self):
        self._disconnect()

    def getConnection(self, host='127.0.0.1',port='22',username='root', password='root'):
        """
        getConnection
        """
        self._connected = False

        # call connect method only if ipaddress is in valid format
        if(re.match(IP_ADDRESS_REGEX, host)):

            if( self._connect(host=host,port=port,username=username,password=password) ):
                self._connStatus = f'Connection to target {host} was estabilished'
                self._connected = True
            #else:
                #self._connStatus = f'Connection to target {host} is not possible'

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

    def getMemorySnapshot(self):
        """
        getMemory
        """
        value = ['-1', '-1', '-1', '-1', '-1', '-1', '-1']

        if (self._connected == True):
            lines = self._executeCmd(CMD_GET_MEMORY)

            line1 = lines[1].split()
            line2 = lines[2].split()

            line1.remove('Mem:')
            line2.remove('Swap:')

            value = line1+line2
            #print(value)

        return value

    def getCmdByLines(self, command):
        """
        getCmdByLines
        """

        lines = []

        if (self._connected == True):
            lines = self._executeCmd(command)

            print(lines)

        return lines

    def getCmdByLinesHeader(self, command):
        """
        getCmdByLinesHeader
        ['Filesystem                Size      Used Available Use% Mounted on\n', '/dev/root               985.4M    358.6M    571.7M  39% /\n', 'devtmpfs                372.0M         0    372.0M   0% /dev\n', 'tmpfs                   500.5M         0    500.5M   0% /dev/shm\n', 'tmpfs                   200.2M      2.2M    198.0M   1% /run\n', 'tmpfs                     4.0M         0      4.0M   0% /sys/fs/cgroup\n', 'tmpfs                   200.2M      2.2M    198.0M   1% /etc/machine-id\n', 'tmpfs                   500.5M         0    500.5M   0% /tmp\n', 'tmpfs                     1.0M         0      1.0M   0% /etc/dropbear\n', 'tmpfs                     5.0M     64.0K      4.9M   1% /home/ppc50-user/.cache\n', 'tmpfs                     5.0M         0      5.0M   0% /home/ppc50-user/.local\n', 'tmpfs                     5.0M         0      5.0M   0% /home/ppc50-user/.dbus\n', 'tmpfs                     5.0M         0      5.0M   0% /home/ppc50-user/.pki\n', 'tmpfs                    70.0M      5.4M     64.6M   8% /var/volatile\n', 'tmpfs                    70.0M      5.4M     64.6M   8% /var/cache\n', 'tmpfs                    70.0M      5.4M     64.6M   8% /srv\n', 'tmpfs                    70.0M      5.4M     64.6M   8% /var/spool\n', '/dev/mmcblk0p1          120.0M     23.0M     88.0M  21% /mnt/sysconfig\n', '/dev/mmcblk0p3          120.0M      1.5M    109.5M   1% /mnt/config\n', '/dev/mmcblk0p4          487.9M    396.0K    451.7M   0% /mnt/user\n', 'tmpfs                    70.0M      5.4M     64.6M   8% /var/lib\n', 'tmpfs                   100.1M     48.0K    100.1M   0% /run/user/1000\n']

        """

        header = []
        lines = []

        if (self._connected == True):
            receivedList = self._executeCmd(command)
        else:
            receivedList = ['Filesystem                Size      Used Available Use% Mounted on\n', '/dev/root               985.4M    358.6M    571.7M  39% /\n', 'devtmpfs                372.0M         0    372.0M   0% /dev\n', 'tmpfs                   500.5M         0    500.5M   0% /dev/shm\n', 'tmpfs                   200.2M      2.2M    198.0M   1% /run\n', 'tmpfs                     4.0M         0      4.0M   0% /sys/fs/cgroup\n', 'tmpfs                   200.2M      2.2M    198.0M   1% /etc/machine-id\n', 'tmpfs                   500.5M         0    500.5M   0% /tmp\n', 'tmpfs                     1.0M         0      1.0M   0% /etc/dropbear\n', 'tmpfs                     5.0M     64.0K      4.9M   1% /home/ppc50-user/.cache\n', 'tmpfs                     5.0M         0      5.0M   0% /home/ppc50-user/.local\n', 'tmpfs                     5.0M         0      5.0M   0% /home/ppc50-user/.dbus\n', 'tmpfs                     5.0M         0      5.0M   0% /home/ppc50-user/.pki\n', 'tmpfs                    70.0M      5.4M     64.6M   8% /var/volatile\n', 'tmpfs                    70.0M      5.4M     64.6M   8% /var/cache\n', 'tmpfs                    70.0M      5.4M     64.6M   8% /srv\n', 'tmpfs                    70.0M      5.4M     64.6M   8% /var/spool\n', '/dev/mmcblk0p1          120.0M     23.0M     88.0M  21% /mnt/sysconfig\n', '/dev/mmcblk0p3          120.0M      1.5M    109.5M   1% /mnt/config\n', '/dev/mmcblk0p4          487.9M    396.0K    451.7M   0% /mnt/user\n', 'tmpfs                    70.0M      5.4M     64.6M   8% /var/lib\n', 'tmpfs                   100.1M     48.0K    100.1M   0% /run/user/1000\n']

        if len(receivedList) > 1:
            header = receivedList[:1]
            lines = receivedList[1:]


        return header, lines