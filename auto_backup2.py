"""
Name : jrBackup v1 

Author : Anjar Fiandrianto / @anjarwebid

Version : 1.0

Date : 14-4-2012

Description: Simple mysql automatic database backup, implementing python daemon with double-fork magic 
from Stevens in "Advanced Programming in the UNIX Environment"
"""

import sys, os, time, ConfigParser

#global variable here
folder = ""
server = ""
usr = ""
passwd = ""
interval = ""

def main():
    #run as daemon
    while 1: 
        backup()
        time.sleep(interval*60) 

def chkcfg():
    global folder
    global server
    global usr
    global passwd
    global interval
    if not os.path.isfile("jrBackupConfig.cfg"):
        #create config file
        writecfg = ConfigParser.RawConfigParser()
        folder = raw_input("Enter your folder address (without ""/"" or slash on the end):")
        server = raw_input("Server :")
        usr = raw_input("MySQL User :")
        passwd = raw_input("MySQL Password :")
        interval = float(raw_input("Interval to backup database (in minutes) :"))
        writecfg.add_section('basic')
        writecfg.set('basic','folder', folder)
        writecfg.set('basic','server', server)
        writecfg.set('basic','user', usr)
        writecfg.set('basic','password', passwd)
        writecfg.set('basic','interval', interval)
        with open('jrBackupConfig.cfg', 'wb') as configfile:
            writecfg.write(configfile)
        startApp()
    else:
        #if config file exist, just read config file
        readcfg = ConfigParser.ConfigParser()
        readcfg.read('jrBackupConfig.cfg')
        folder = readcfg.get('basic', 'folder')
        server = readcfg.get('basic', 'server')
        usr = readcfg.get('basic', 'user')
        passwd = readcfg.get('basic', 'password')
        interval = readcfg.getfloat('basic','interval')
        startApp()
        
def startApp():
	# do the UNIX double-fork magic, see Stevens' "Advanced 
    # Programming in the UNIX Environment" for details (ISBN 0201563177)
    try: 
        pid = os.fork() 
        if pid > 0:
            # exit first parent
            sys.exit(0) 
    except OSError, e: 
        print >>sys.stderr, "fork #1 failed: %d (%s)" % (e.errno, e.strerror) 
        sys.exit(1)

    # decouple from parent environment
    os.chdir("/") 
    os.setsid() 
    os.umask(0) 

    # do second fork
    try: 
        pid = os.fork() 
        if pid > 0:
            # exit from second parent, print eventual PID before
            print "Daemon PID %d" % pid 
            sys.exit(0) 
    except OSError, e: 
        print >>sys.stderr, "fork #2 failed: %d (%s)" % (e.errno, e.strerror) 
        sys.exit(1) 
    # start the daemon main loop
    main() 

def backup():
    #check and create log
    f = open("/var/log/jrBackup", "w") 
    filestamplog = time.strftime('%Y-%m-%d %H:%M')
    f.write ("backup on "+filestamplog+"\n")
    # get database list
    filestamp = time.strftime('%Y-%m-%d')
    database_list_command="mysql -u %s -p%s -h %s --silent -N -e 'show databases'" % (usr, passwd, server)
    #split database list
    for database in os.popen(database_list_command).readlines():
        database = database.strip()
        #skip "information_scema" database backup
        if database == 'information_schema':
            continue
        #set folder for database backup files
        newpath = "%s/%s" % (folder,filestamp) 
        if not os.path.exists(newpath): 
            os.makedirs(newpath)
        filename = "%s/%s-%s.sql" % (newpath, database, filestamp)
        #generate backup file
        os.popen("mysqldump -u %s -p%s -h %s -e --opt -c %s | gzip -c > %s.gz" % (usr, passwd, server, database, filename))
        f.write ("Backup database "+database+" finished\n")
    f.write ("All finished\n")
    f.flush
    f.close
        
if __name__ == "__main__":
	chkcfg()
