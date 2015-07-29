import os
import zipfile
import time 
import glob 
import re
import readline
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive 
g_property = {
    # project name 
    'project_name':'None', 
    # local repository path 
    'local_repository':'None',
    # google drive folder id 
    'remote_repository_id':'None'
}
# list of properties
PROPERTIES =[ k for k in g_property.keys() ]
# list of commands 
COMMANDS = ['set', 'get', 'showallproperty', 'commit', 'exit','showcommit','push','commit','version']
# PN<project name>-PS< 3 digits sequence number>-VR< 1.2.12 >-DT<yyyymmdd_hhmmss>-DC<dsecripition of commit>
# PNSGit-PS001-VR0.3.2-DT20150301_111134-DSNone.zip 
PATTERN_ZIP = r'^PN[\w]{1,30}-PS[\d]{3,3}-VR[\d]{1,4}\.[\d]{1,4}\.[\d]{1,4}-DT[\d]{8,8}_[\d]{6,6}-DC[\w_]{1,30}$'
PATTERN_VERSION=r'^[\d]{1,4}\.[\d]{1,4}\.[\d]{1,4}$'
PATTERN_DESC=r'^[\w_]{1,30}$'
RE_SPACE = re.compile('.*\s+$', re.M)
class Completer(object):
    """class for commandline auto-completion 

        complete_XXXX    XXXX is commands     
        ref: stackoverflow.com  
    """

    def __init__(self):
        readline.set_completer_delims(' \t\n;')
        readline.parse_and_bind("tab: complete")
        readline.parse_and_bind('set editing-mode vi')

    def _listdir(self, root):
        "List directory 'root' appending the path separator to subdirs."
        res = []
        for name in os.listdir(root):
            path = os.path.join(root, name)
            if os.path.isdir(path):
                name += os.sep
            res.append(name)
        return res

    def _complete_path(self, path=None):
        "Perform completion of filesystem path."
        if not path:
            return self._listdir('.')
        dirname, rest = os.path.split(path)
        tmp = dirname if dirname else '.'
        res = [os.path.join(dirname, p)
                for p in self._listdir(tmp) if p.startswith(rest)]
        # more than one match, or single match which does not exist (typo)
        if len(res) > 1 or not os.path.exists(path):
            return res
        # resolved to a single directory, so return list of files below it
        if os.path.isdir(path):
            return [os.path.join(path, p) for p in self._listdir(path)]
        # exact file match terminates this completion
        return [path + ' ']

    def complete_extra(self, args):
        "Completions for the 'extra' command."
        if not args:
            return self._complete_path('.')
        # treat the last arg as a path and complete it
        return self._complete_path(args[-1])

    def complete_set(self, args):
        if not args:
            return PROPERTIES
        # treat the last arg as a path and complete it
        lst =[]
        for property in  PROPERTIES:
            if property.startswith(args[-1]):
                lst.append(property)
        return lst

    def complete_get(self, args):
        if not args:
            return PROPERTIES
        # treat the last arg as a path and complete it
        lst =[]
        for property in  PROPERTIES:
            if property.startswith(args[-1]):
                lst.append(property)
        return lst

    def complete_exit(self, args):
            return []

    def complete_showallproperty(self, args):
            return []

    def complete(self, text, state):
        "Generic readline completion entry point."
        buffer = readline.get_line_buffer()
        line = readline.get_line_buffer().split()
        # show all commands
        if not line:
            return [c + ' ' for c in COMMANDS][state]
        # account for last argument ending in a space
        if RE_SPACE.match(buffer):
            line.append('')
        # resolve command to the implementation function
        cmd = line[0].strip()
        if cmd in COMMANDS:
            impl = getattr(self, 'complete_%s' % cmd)
            args = line[1:]
            if args:
                return (impl(args) + [None])[state]
            return [cmd + ' '][state]
        results = [c + ' ' for c in COMMANDS if c.startswith(cmd)] + [None]
        return results[state]

def zipdir(path, ziph):
    """zip all files include sub-directory and files it contain
    @param path: target path
    @param ziph: zip object 
    @return: True success or False 
    """
    try:
        for root, dirs, files in os.walk(path):
            for file in files:
                ziph.write(os.path.join(root, file))
    except Exception, e:
        print e 
        return False
    return True 
    
    

def get_next_proj_seq(path):
    """get next project sequence no. 

        -PS003-  ---> return 4  

    @param path: dir. path
    @return: seq no
    """
    #   PNSGit-PS001-VR0.3.2-DT20150301_111134-DSNone.zip    
    p=re.compile(PATTERN_ZIP)
    flist=[]
    for f in glob.glob(path + '*.zip' )  :
        filename = os.path.split(f)[1][:-4] #filename only
        if p.match(filename) :
            flist.append(filename)
    if not flist : return 1,"0.0.1" 
    flist.sort(reverse=True)
    elements = flist[0].split('-')    
    ps =int(elements[1][2:])
    v1,v2,v3 = map(int,elements[2][2:].split('.'))
    return ps+1,"{}.{}.{}".format(v1,v2,v3+1)

def create_deposit_filename(desc='None',  version='auto'):
    """get new deposit filename 

        seq +1 and version +1  

    @param version: version  format) N.N.N
    @param desc: commit description 
    @return: filename example) PNSGit-PS001-VR0.3.2-DT20150301_111134-DSNone.zip
             fail return None,"err string"
    """
    p_desc = re.compile(PATTERN_DESC)
    p_version = re.compile(PATTERN_VERSION)
    if desc!='None' and not p_desc.match(desc) :
        return None,"bad desc pattern"  
    if version!='auto' and not p_version.match(version) : 
        return None,"bad version pattern"
      
    project_path = g_property['local_repository'] + g_property['project_name']+ '\\'
    next_ps,next_vr = get_next_proj_seq(project_path)
    if version != 'auto': next_vr = version
    PN = 'PN{0}'.format( g_property['project_name'] )
    PS = 'PS{0:03}'.format( next_ps )
    VR = 'VR{0}'.format( next_vr )
    DT =  time.strftime( "DT%Y%m%d_%H%M%S", time.localtime())
    DC = 'DC{}'.format(desc)
    filename ="{}{}-{}-{}-{}-{}.zip".format(project_path,PN,PS,VR,DT,DC)
    return filename,"OK"   

def commit_local(desc='None',  version='auto'):
    """make new deposit file 

        make xxx.zip in project deposit path  

    @param version: version  format) N.N.N
    @param desc: commit description 
    """
    filename,err = create_deposit_filename(desc,version)
    if not filename : 
        print err 
        return False 
    with zipfile.ZipFile(filename, 'w') as zipf:
        if zipdir('.', zipf):
            print "+created " + filename
            return True 
        else:
            print "fail"
    return False

def rollback(project_seq_no):
    return True

def set_config(property , value):
    """set property 
    @param property: property
    @param value: value
    @return:
    """
    if property in g_property:
        if property=='local_repository':
            if not os.path.isdir(value) : return "not exist directory"
            if value.strip()[-1] != os.sep:
                value+=os.sep
        g_property[property] =  value
        return "success"
    else :
        return "undefined property"

def show_config():
    """print all properties and its values
    """
    for p,v in g_property.items():
        print p + '='+ v

def get_config( property ):
    """get value of property 

        this function for 'get' command

    @param property: property
    @return: value or error string
    """
    if property in g_property:
        return g_property[property]
    else :
        return "Undefined property"

def load_config():
    """load property from ini files 
    """
    try:
        with open("config.ini",'r') as f:
            lines = f.readlines()
            for line in lines:
                p,v = line.split('=')
                p = p.strip()
                v = v.strip()
                if p in g_property.keys():
                    g_property[p] = v 
    except (OSError, IOError) as e:
        save_config()

def save_config():
    """save property to ini files
    """
    with open('config.ini','w') as f :
        for p,v in g_property.items():
            f.writelines( '{}={}\n'.format(p,v) )

def check_conifg():
    """validate g_property
    @return: False if there is bad property value
    """
    bBadPropertyFlag=False
    for k,v in g_property.items():
        if v=='None': 
            print k,'=',v ,"-> should be set a value"
            bBadPropertyFlag = True    
    if bBadPropertyFlag:
        return False 
    if g_property['local_repository'][-1] != '\\':
        g_property['local_repository'] +='\\'
    if not os.path.isdir(g_property['local_repository']):
        print "%s is not exist directory" % (g_property['local_repository'])
        return False
    return True  

def show_commit_list():
    """print commit list 

        print zip files in project repository

    """
    p=re.compile(PATTERN_ZIP)
    path = g_property['local_repository'] + g_property['project_name'] + '\\'
    print "#project_path = "+path
    for f in glob.glob(path + '*.zip' )  :
        filename = os.path.split(f)[1][:-4] #filename only
        if p.match(filename) :
            print filename

def cmd_loop():
    """command loop 
    """
    while True:
        prompt_text = '({})>'.format( g_property['project_name'] )
        cmd_text = raw_input(prompt_text)
        cmd = cmd_text.split()
        if len(cmd) <= 0 :
            continue
        elif cmd[0] =='set':
            if len(cmd)==3 :
                print set_config( cmd[1],cmd[2] ) 
                save_config()
            else:
                print "example: set <property> <value>\n   set project_name SGit"
        elif cmd[0] =='get':
            if len(cmd)==2:
                print get_config( cmd[1] )
            else:
                print "example: get <property>\n   get project_name"
        elif cmd[0] =='showallproperty':
            show_config()
        elif cmd[0]=='commit':
            desc='None'
            version='auto'
            if len(cmd) > 1 : desc=cmd[1]
            if len(cmd) > 2 : version = cmd[2]
            commit_local(desc,version)
        elif cmd[0]=='push':
            project_path = g_property['local_repository'] + g_property['project_name']+ '\\'
            push_remote( project_path, g_property['remote_repository_id'] )
        elif cmd[0]=='showcommit':
            show_commit_list()
        elif cmd[0]=='exit':
            print 'bye~'
            break;
        elif cmd[0]=='version':
            print "ver 0.1.0"
        else:
            print "undefined command"

def push_remote(local_path,remote_targetdir_id):    
    """copy local zip files to remote ( google drive )

        This function upload all zip-files in local_path except file which is same name on remote 

    @param local_path: local path where zip files stored  ex) d:\local\repository\a_poject
    @param remote_targetdir_id: target directory id. ex) dlkjfaljdflk_dfkdk1334343_ADFD000090
    @return:
    """
    gauth = GoogleAuth("./auth/settings.yaml")
    if not gauth : return None 
    drive = GoogleDrive(gauth)
    upinfo={
        "title" : "exampe.png",
        "parents": [{"kind": "drive#fileLink","id": remote_targetdir_id}]
    }
    qurystring = "'%s' in parents and trashed=false" % (remote_targetdir_id) 
    remote_filelist = [ local_path+f['title'] for f in drive.ListFile({'q': qurystring }).GetList()]   
    local_filelist = [  f for f in glob.glob( local_path + '*.zip' ) ]
    # remove samefiles files 
    upload_file_list = set(local_filelist) - set(remote_filelist)
    nSuccess=0
    nFail=0
    for filname in upload_file_list :
        upinfo['title']= os.path.split(filname)[1]
        fobj = drive.CreateFile(upinfo)
        fobj.SetContentFile(filname)
        print os.path.split(filname)[1]+": #",
        try:
            fobj.Upload()
            nSuccess+=1
            print "########################## 100%"
        except Exception, e:
            nFail+=1
            # raise            
    print "result: %d success %d fail" % (nSuccess,nFail)
    return nSuccess,nFail

if __name__ == '__main__':
    # load ini file 
    load_config()
    check_conifg() 
    # for command auto-completion
    readline.set_completer_delims(' \t\n;')
    readline.parse_and_bind("tab: complete")
    readline.parse_and_bind('set editing-mode vi')
    comp = Completer()
    readline.set_completer(comp.complete)
    # command loop
    cmd_loop()
    # save ini file 
    save_config()