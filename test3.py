import os
import re
import readline


g={
    'local_path':'None',
    'remote_path':'None',
    'remote_userid':'None',
    'remote_password':'None',
    'project_name':'None',
    'local_repository':'D:\\local\\SGitRep\\',}
PROPERTIES =[ k for k in g.keys() ]
COMMANDS = ['set', 'get', 'showallproperty', 'commit', 'exit'] 
RE_SPACE = re.compile('.*\s+$', re.M)

class Completer(object):

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


  

comp = Completer()
readline.set_completer(comp.complete)


# print comp._complete_path( path = 'd:\\local' )
# print comp.get_list('d:\\local')
raw_input('Enter section name: ')
