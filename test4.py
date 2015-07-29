import readline
import os 
import logging

LOG_FILENAME = 'completer.log'
logging.basicConfig(filename=LOG_FILENAME,
                    level=logging.DEBUG,
                    )


class SimpleCompleter(object):
    
    def __init__(self, options):
        # self.options = sorted(options)
        self.options = self.get_list(".\\")
        logging.debug(self.options)
        return

    def complete(self, text, state):
        response = None

        buffer = readline.get_line_buffer()
        line = readline.get_line_buffer().split()
        logging.debug("buffer:%s line:%s",buffer,line)
        logging.debug("text:%s stat:%s",text,state)
        # if state == 0:
        #     # This is the first time for this text, so build a match list.
        #     if text:
        #         # swiself.matches = [s 
        #         #                 for s in self.options
        #         #                 if s and s.startth(text)]

        #         self.matches = self.get_list(text) 
        #         logging.debug('%s matches: %s', repr(text), self.matches)
        #     else:
        #         self.matches = self.options[:]
        #         logging.debug('(empty input) matches: %s', self.matches)

        if state == 0:
            # This is the first time for this text, so build a match list.
            if buffer:
                # swiself.matches = [s 
                #                 for s in self.options
                #                 if s and s.startth(text)]

                self.matches = self.get_list(buffer) 
                logging.debug('%s matches: %s', repr(buffer), self.matches)
            else:
                self.matches = self.options[:]
                logging.debug('(empty input) matches: %s', self.matches)
        
        # Return the state'th item from the match list,
        # if we have that many.
        try:
            response = self.matches[state]
        except IndexError:
            response = None
        logging.debug('complete(%s, %s) => %s', 
                      repr(text), state, repr(response))
        return response

    def get_list(self,text) :
        lst =[]
        path,suffix  = os.path.split(text)
        for fname in os.listdir(path):
            if fname.startswith(suffix):
                lst.append(os.path.join(path, fname))
        return lst

def input_loop():
    line = ''
    while line != 'stop':
        line = raw_input('Prompt ("stop" to quit): ')
        print 'Dispatch %s' % line

# Register our completer function
readline.set_completer(SimpleCompleter(['start', 'stop', 'list', 'print']).complete)

# Use the tab key for completion
readline.parse_and_bind('tab: complete')

# Prompt the user for text
input_loop()