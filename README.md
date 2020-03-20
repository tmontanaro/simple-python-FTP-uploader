# Simple python FTP uploader

This project implements a simple python script that monitors a folder and, in case of changes, upload the changed file on an FTP folder.
It works also with **Windows XP** with **Python 2.7** (the reason why I created it ...).

It allows, through the configuration file to:
- insert multiple folders to monitor
- enable or disable the synchronization at startup
- enable or disable the usage of TLS protocol
- specify a directory in which the script can store a copy of the file before sending it
- insert a delay to be respected among different send operations
- specify an interval in which the files should not be sent (for instance, to perform a backup on the FTP server)

This script was made starting from the code published in the following forums:
  - [Using Python's Watchdog to monitor changes to a directory by Michael Cho](https://www.michaelcho.me/article/using-pythons-watchdog-to-monitor-changes-to-a-directory)
  - [Simple FTP directory synch (Python recipe) by EyePulp ](http://code.activestate.com/recipes/327141-simple-ftp-directory-synch/)
