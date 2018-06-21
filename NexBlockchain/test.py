from ftplib import FTP
import os # allows me to use os.chdir

port=21
ip="10.23.77.30"
password='milan'

#os.chdir() #changes the active dir - this is where downloaded files will be saved to
ftp = FTP("10.23.77.30")
ftp.login('milan',password)
print("File List:")
files = ftp.dir()

directory ="/home/milan/Desktop/" #dir i want to download files from, can be changed or left for user input
filematch = '*.py' # a match for any file in this case, can be changed or left for user to input

ftp.cwd(directory)

for filename in ftp.nlst(filematch): # Loop - looking for matching files
    fhandle = open(filename, 'wb')
    print('Getting ' + filename) #for confort sake, shows the file that's being retrieved
    ftp.retrbinary('RETR ' + filename, fhandle.write)
    fhandle.close()