"""
Name : simplefullbackup v1 

Author : Anjar Fiandrianto / @anjarwebid

Version : 1.0

Date : 11-12-2012

Full backup for file and database, run by cron.
"""

import sys, os, time, ConfigParser, tarfile, ftplib

#global variable here
folder = ""
server = ""
usr = ""
passwd = ""
path = ""
ftphost = ""
ftpuser = ""
ftppassword = ""
ftpport = ""
ftpdirectory = ""
appname = "fullbackup.py"

def chkcfg():
    global folder
    global server
    global usr
    global passwd
    global path
    global ftphost
    global ftpuser
    global ftppassword
    global ftpport
    global ftpdirectory
    if not os.path.isfile(os.path.abspath(__file__).strip(appname)+"fullbackup-config.cfg"):
        #create config file
        writecfg = ConfigParser.RawConfigParser()
        folder = raw_input("[DB]Enter your folder address (without ""/"" or slash on the end):")
        server = raw_input("[DB]Server :")
        usr = raw_input("[DB]MySQL User :")
        passwd = raw_input("[DB]MySQL Password :")
        path = raw_input("[FILE]Target folder backup :")
        ftphost = raw_input("[FTP]Host :")
        ftpuser = raw_input("[FTP]User FTP :")
        ftppassword = raw_input("[FTP]Password FTP :")
        ftpport = raw_input("[FTP]Port FTP :")
        ftpdirectory = raw_input("[FTP]Directory FTP :")
        writecfg.add_section('basic')
        writecfg.set('basic','folder', folder)
        writecfg.set('basic','server', server)
        writecfg.set('basic','user', usr)
        writecfg.set('basic','password', passwd)
        writecfg.set('basic','path', path)
        writecfg.set('basic','ftphost', ftphost)
        writecfg.set('basic','ftpuser', ftpuser)
        writecfg.set('basic','ftppassword', ftppassword)
        writecfg.set('basic','ftpport', ftpport)
        writecfg.set('basic','ftpdirectory', ftpdirectory)
        with open(os.path.abspath(__file__).strip(appname)+'fullbackup-config.cfg', 'wb') as configfile:
            writecfg.write(configfile)
        backupdb()
    else:
        #if config file exist, just read config file
        readcfg = ConfigParser.ConfigParser()
        readcfg.read(os.path.abspath(__file__).strip(appname)+'fullbackup-config.cfg')
        folder = readcfg.get('basic', 'folder')
        server = readcfg.get('basic', 'server')
        usr = readcfg.get('basic', 'user')
        passwd = readcfg.get('basic', 'password')
        path = readcfg.get('basic','path')
        ftphost = readcfg.get('basic','ftphost')
        ftpuser = readcfg.get('basic','ftpuser')
        ftppassword = readcfg.get('basic','ftppassword')
        ftpport = readcfg.get('basic','ftpport')
        ftpdirectory = readcfg.get('basic','ftpdirectory')
        backupdb()

def backupdb():
    #check and create log
    f = open("/var/log/fullbackup", "w") 
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
        newpath = "%s/%s/database" % (folder,filestamp) 
        if not os.path.exists(newpath): 
            os.makedirs(newpath)
        filename = "%s/%s-%s.sql" % (newpath, database, filestamp)
        #generate backup file
        os.popen("mysqldump -u %s -p%s -h %s -e --opt -c %s | gzip -c > %s.gz" % (usr, passwd, server, database, filename))
        f.write ("Backup database "+database+" finished\n")
    f.write ("Database Backup finished\n")
    f.close
    backupfile()

def backupfile():
    f = open("/var/log/fullbackup", "w") 
    filestamp = time.strftime('%Y-%m-%d')
    filestamplog = time.strftime('%Y-%m-%d %H:%M')
    folderdata = os.listdir(path)
    for foldername in folderdata:
        full_dir = os.path.join(path, foldername)
        newpath = "%s/%s/file" % (folder,filestamp)
        if not os.path.exists(newpath):
            os.makedirs(newpath)
        tar = tarfile.open(os.path.join(newpath, foldername+'.tar.gz'), 'w:gz')
        tar.add(full_dir)
        tar.close()
        f.write ("Backup folder "+foldername+" finished\n")
        print foldername
    f.write ("All finished\n")
    f.close
    uploadbackup()

def uploadbackup():
    filestamp = time.strftime('%Y-%m-%d')
    tar = tarfile.open(os.path.join(folder, filestamp+'.tar.gz'), 'w:gz')
    tar.add(os.path.join(folder, filestamp))
    tar.close()
    ftp = ftplib.FTP()
    ftp.connect(ftphost, ftpport)
    ftp.login(ftpuser, ftppassword)
    ftp.cwd(ftpdirectory)
    fp = open(os.path.abspath(__file__).strip(appname)+filestamp+'.tar.gz','rb')
    ftp.storbinary('STOR '+filestamp+'.tar.gz', fp)
    fp.close()
    ftp.quit()
    

if __name__ == "__main__":
	chkcfg()
