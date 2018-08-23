import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from sys import platform
import json
import ntpath
import unicodedata
import threading
import os

# --- constant connection values
ftpServerName = ""
ftpU = ""
ftpP = ""
directoriesToWatch = []
useTLS = True
dictOfWatchedDir = {}
synchAtStartupBool = False

class Watcher(threading.Thread):
    # DIRECTORY_TO_WATCH = "/home/teo/Desktop/temp"

    def __init__(self, tempLocalDirPath):
        threading.Thread.__init__(self)
        self.observer = Observer()
        self.tempLocalDirPath = tempLocalDirPath

    def run(self):
        event_handler = Handler()
        self.observer.schedule(event_handler, self.tempLocalDirPath, recursive=True)
        self.observer.start()

        try:
            while True:
                time.sleep(5)
        except:
            self.observer.stop()
            print "Error"

        self.observer.join()


class Handler(FileSystemEventHandler):

    @staticmethod
    def on_any_event(event):
        if event.is_directory:
            return None
        elif event.event_type == 'created':
            # Take any action here when a file is first created.
            # when the file is create the "modified" event is also generated
            # so we do not anything
            print "Received created event - %s." % event.src_path
            #if (event.src_path in dictOfWatchedDir):
            #    moveFTPFiles(ftpServerName, ftpU, ftpP, event.src_path, dictOfWatchedDir[event.src_path], useTLS)

        elif event.event_type == 'modified':
            fileToUpload = event.src_path
            # Taken any action here when a file is modified.
            print "Received modified event - %s." % fileToUpload

            path_without_lea = path_without_leaf(fileToUpload)
            if (path_without_lea in dictOfWatchedDir):
                moveFTPFiles(ftpServerName, ftpU, ftpP, fileToUpload, dictOfWatchedDir[path_without_lea], useTLS)
        elif event.event_type == 'moved':
            # on linux, when a file is modified, the system create a temporal file (.goutputstream...) and them move it on the right one
            fileToUpload = event.dest_path

            # Taken any action here when a file is modified.
            print "Received modified event - %s." % fileToUpload

            path_without_lea = path_without_leaf(fileToUpload)
            if (path_without_lea in dictOfWatchedDir):
                moveFTPFiles(ftpServerName, ftpU, ftpP, fileToUpload, dictOfWatchedDir[path_without_lea], useTLS)
        elif event.event_type == 'deleted':
            return None

def path_without_leaf(path):
    head, tail = ntpath.split(path)
    return head

def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)

def moveFTPFiles(serverName, userName, passWord, fileToUpload, remoteDirectoryPath, useTLS=False):
    """Connect to an FTP server and bring down files to a local directory"""
    from ftplib import FTP
    from ftplib import FTP_TLS
    if (serverName!='' and userName!='' and passWord!=''):
        try:
            if useTLS:
                ftp = FTP_TLS(serverName)
            else:
                ftp = FTP(serverName)
        except:
            print "Couldn't find server"
        ftp.login(userName, passWord)
        if useTLS:
            ftp.prot_p()
        ftp.cwd(remoteDirectoryPath)
        ftp.set_pasv(True)
        filesMoved = 0
        delMsg = ''

        try:

            print "Connecting..."

            # create a full local filepath
            localFile = path_leaf(fileToUpload)
            if not localFile.startswith("."):
                # open a the local file
                fileObj = open(fileToUpload, 'rb')
                # Download the file a chunk at a time using RETR
                ftp.storbinary('STOR ' + localFile, fileObj)
                # Close the file
                fileObj.close()
                filesMoved += 1

            print "Files Moved" + delMsg + ": " + str(filesMoved) + " on " + timeStamp()
        except Exception as inst:
            print type(inst)  # the exception instance
            print inst.args  # arguments stored in .args
            print inst  # __str__ allows args to be printed directly
            print "Connection Error - " + timeStamp()
        ftp.close()  # Close FTP connection
        ftp = None
    else:
        print("Maybe you forgot to specify ftpServerName , ftpU or ftpP in the configuration file")

def timeStamp():
    """returns a formatted current time/date"""
    import time
    return str(time.strftime("%a %d %b %Y %I:%M:%S %p"))

def synchAtStartup():
    if (isinstance(directoriesToWatch, list) and len(directoriesToWatch) > 0):
        for dest in directoriesToWatch:
            if ('localDirPath' in dest and 'remoteDirPath' in dest):
                arr = os.listdir(dest['localDirPath'])
                for file in arr:
                    if os.path.isdir(file) != True:
                        moveFTPFiles(ftpServerName, ftpU, ftpP, dest['localDirPath']+"/"+file, dest['remoteDirPath'], useTLS)

if __name__ == '__main__':
    # read configuration parameters from the config.json file
    with open('config.json') as json_data_file:
        data = json.load(json_data_file)
    if 'configuration' in data:
        conf = data['configuration']
        if 'directoriesToWatch' in conf:
            directoriesToWatch = conf['directoriesToWatch']
        if 'ftpServerName' in conf:
            ftpServerName = conf['ftpServerName']
        if 'ftpUser' in conf:
            ftpU = conf['ftpUser']
        if 'ftpPass' in conf:
            ftpP = conf['ftpPass']
        if 'useTLS' in conf:
            useTLS = conf['useTLS']
        if 'synchAtStartup' in conf:
            synchAtStartupBool = conf['synchAtStartup']



    wrongPath = False
    if platform == "win32":
        # Windows...
        if (isinstance(directoriesToWatch, list) and len(directoriesToWatch) > 0):
            for dest in directoriesToWatch:
                if ('/' in dest['localDirPath']):
                    wrongPath = True
                    print("WARNING: in the configuraton file you set a path ("+dest['localDirPath']+") as a linux-like path but you are under linux")
    elif platform == "linux" or platform == "linux2" or platform == "darwin":
        # linux or OSX
        if (isinstance(directoriesToWatch, list) and len(directoriesToWatch) > 0):
            for dest in directoriesToWatch:
                if ('\\' in dest['localDirPath']):
                    wrongPath = True
                    print("WARNING: in the configuraton file you set a path ("+dest['localDirPath']+") as a windows-like path but you are under linux")

    if (wrongPath):
        exit()
    else:

        if synchAtStartupBool:
            synchAtStartup()
        if (isinstance(directoriesToWatch, list) and len(directoriesToWatch) > 0):
            for dest in directoriesToWatch:
                if 'localDirPath' in dest and 'remoteDirPath' in dest:
                    tempLocalDirPath = unicodedata.normalize('NFKD', dest['localDirPath']).encode('ascii', 'ignore')
                    tempRemoteDirPath = unicodedata.normalize('NFKD', dest['remoteDirPath']).encode('ascii', 'ignore')
                    dictOfWatchedDir[tempLocalDirPath] = tempRemoteDirPath

                    w = Watcher(tempLocalDirPath)
                    w.start()