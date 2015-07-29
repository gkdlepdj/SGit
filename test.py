# coding: utf-8
import sys 
import os 
reload(sys)
sys.setdefaultencoding('utf-8')
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive 
import glob 

DIRECTORY_MIMETYPE = 'application/vnd.google-apps.folder'
g_cur_directory_id = 'root'

def get_file_id(parents_id, search_name,directory=False ):
    search_name=search_name.strip()
    if directory :
        qurystring = "'%s' in parents and trashed=false and mimeType='%s' and title='%s'" \
            % (parents_id, DIRECTORY_MIMETYPE,search_name)
    else :
        qurystring = "'%s' in parents and trashed=false and mimeType!='%s' and title='%s'" \
            % (parents_id, DIRECTORY_MIMETYPE,search_name)
    flist = drive.ListFile({'q': qurystring }).GetList()
    if flist :
        return flist[0]['id'].strip()
    else:
        return None

def get_parent(id):    
    f = drive.CreateFile({'id':id}) # Create GoogleDriveFile instance with file id of file1
    # print 'title: %s, mimeType: %s' % (file2['title'], file2['mimeType']) # title: HelloWorld.txt, mimeType: text/plain
    
    if f :
        for item in f['parents']:
            if isinstance(item, dict):
                # for k,v in item.items():
                #     print k,"===",v 
                return item['id']
    else:
        return None




def fills(s,width):
    if width < 0 :
        width = width*-1
        Right = False
    else:
        Right = True     
    nCnt=0
    i=0
    nLast=0
    for ch in s :
        if 0 <= ord(unicode(ch)) <= 0x7f :
            nLast = 1 
        else:
            nLast = 2
        nCnt += nLast
        if nCnt > width:
            nCnt -= nLast
            s = s[:i]
            break
        i += 1
    nSpace = width-nCnt
    return (' '*nSpace+s) if Right else (s+' '*nSpace)

def show_list(drive,parents='root'): 
    # file_list = drive.ListFile({'q': "'0B3TOE2du_D-zfjNtVWV1U3IzNThqV2NmQzJNWU5iMXZCX3JvWFlpZ0doSjFvc290OFZ3RGs' in parents and trashed=false"}).GetList()   
    qurystring = "'%s' in parents and trashed=false" % (parents)
    hwidth=142
    file_list = drive.ListFile({'q': qurystring }).GetList()   
    print '='*hwidth
    print '|%s|%s|%s|%s|' % ( fills('no',2), fills('Title',-15),   fills('mimeType',-40),fills('id',-80)   )
    print '-'*hwidth
    for i,file1 in enumerate( file_list ):
        if file1['mimeType'] == DIRECTORY_MIMETYPE :
            filetitle = '['+ file1['title']+']' 
        else:
            filetitle=file1['title']
        print '|%s|%s|%s|%s|' % ( fills(str(i+1),2),fills(  filetitle ,-15),fills( file1['mimeType'],-40),fills(file1['id'],-80)   )
    print '='*hwidth
    return file_list




#gauth = GoogleAuth() #default:"settings.yaml"
gauth = GoogleAuth("my2.yaml")
# gauth.LocalWebserverAuth()  
drive = GoogleDrive(gauth)


file_list=show_list(drive,g_cur_directory_id)
get_parent('0B3TOE2du_D-zfjNtVWV1U3IzNThqV2NmQzJNWU5iMXZCX3JvWFlpZ0doSjFvc290OFZ3RGs')

while True :
    cmd_text = raw_input(">>")
    cmd = cmd_text.split()
    if not cmd :
        continue
    if cmd[0] == 'exit': 
        break
    elif cmd[0] =='cd':
        if not cmd[1]:
            print 'command needs arg'
        elif cmd[1]=='root':
            g_cur_directory_id='root'
            print 'directory change to %s' % (cmd[1])
        elif cmd[1]=='..':
            pid = get_parent(g_cur_directory_id)
            if pid :
                g_cur_directory_id = pid 
                print 'move to parent directory'
        else:
            result_id= get_file_id(g_cur_directory_id, cmd[1],True)
            if result_id :
                g_cur_directory_id=result_id 
                print 'directory change to %s' % (cmd[1])
            else:
                print 'cannot find directory'
    elif cmd[0] == 'list' or cmd[0] == 'dir' or cmd[0] == 'ls':
        file_list =show_list( drive , g_cur_directory_id )
    elif cmd[0] == 'down':
        try :
            index = int(cmd[1])-1
            cho_file = file_list[index]
            print index, cho_file['id'],cho_file['title'] 
            file6 = drive.CreateFile({'id': cho_file['id']}) 
            file6.GetContentFile( cho_file['title']) # Download file as 'catlove.png'
            print 'success'
        except :
            print 'download fail'  
    else:
        print 'bad command'





# upinfo={
#   "title" : "p.png",
#   # "mimeType" : "application/zip",
#   "parents": [{
#     "kind": "drive#fileLink",
#     "id": "0B3TOE2du_D-zfjNtVWV1U3IzNThqV2NmQzJNWU5iMXZCX3JvWFlpZ0doSjFvc290OFZ3RGs"
#   }]
# }

# path='D:\\local\\SGitRep\\SGit\\'
# for filename in glob.glob( path + '*.zip' )  :
#         print filename 
#         upinfo['title']=os.path.split(filename)[1]
#         print upinfo
#         f = drive.CreateFile(upinfo)
#         f.SetContentFile(filename)
#         f.Upload()




# d={
#   "title" : "cat.png",
#   "mimeType" : "image/png",
#   "parents": [{
#     "kind": "drive#fileLink",
#     "id": "0B3TOE2du_D-zfjNtVWV1U3IzNThqV2NmQzJNWU5iMXZCX3JvWFlpZ0doSjFvc290OFZ3RGs"
#   }]
# }


# f = drive.CreateFile(d)
# f.SetContentFile('cat.png')
# f.Upload()



# file5 = drive.CreateFile()
# file5.SetContentFile('python.zip') # Read file and set it as a content of this instance.
# file5.Upload() # Upload it
# print 'title: %s, mimeType: %s' % (file5['title'], file5['mimeType']) # title: cat.png, mimeType: image/png



# choice_file = file_list[0]
# print choice_file['id']
# downfile = drive.CreateFile({'id':choice_file['id']}) # Initialize GoogleDriveFile instance with file id
# print downfile 
# downfile.GetContentFile( "aaaaaaaaaaaa.png" ) # Download file as 'catlove.png'


# file4 = drive.CreateFile({'title':'appdata.json', 'mimeType':'application/json'})
# file4.SetContentString('{"firstname": "John", "lastname": "Smith"}')
# file4.Upload() # Upload file
# file4.SetContentString('{"firstname": "Claudio", "lastname": "Afshar"}')
# file4.Upload() # Update content of the file

# file5 = drive.CreateFile()
# file5.SetContentFile('cat.png') # Read file and set it as a content of this instance.
# file5.Upload() # Upload it
# print 'title: %s, mimeType: %s' % (file5['title'], file5['mimeType']) # title: cat.png, mimeType: image/png

# file6 = drive.CreateFile({'id': file5['id']}) # Initialize GoogleDriveFile instance with file id
# file6.GetContentFile('catlove.png') # Download file as 'catlove.png'
