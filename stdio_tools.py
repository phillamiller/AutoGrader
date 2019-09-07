# -*- coding: utf-8 -*-

from contextlib import redirect_stdout
import io
import sys
import re
import dis

from threading import Thread
from queue import Queue, Empty
from subprocess import *
from time import sleep

class Keyboard():
    def __init__(self, data):
        self.data = data.split('\n')

    def readline(self):
        line = self.data.pop(0)

        # this will help make the output of controlled_exec 
        # the same as we would see in an interactive session 
        # with the test program
        print(line) 

        return line

def controlled_exec(file_name, input_text):
    source = open(file_name, 'r').read()
    
    # redirect stdin
    stdin = sys.stdin
    sys.stdin = Keyboard(input_text)

    output = io.StringIO()
    with redirect_stdout(output):
        exec(source, dict())
        
    # reset stdin
    sys.stdin = stdin
    
    return output.getvalue()

def evaluate_with_keyboard_input(statement_to_execute, keyboard_input_text, context_dict):
    # redirect stdin
    stdin = sys.stdin
    sys.stdin = Keyboard(keyboard_input_text)
    # redirect stdout
    output = io.StringIO()
    with redirect_stdout(output):
        ret_val = eval(statement_to_execute, context_dict)
        
    # reset stdin
    sys.stdin = stdin
    
    return {'return_value':ret_val, 'printout':output.getvalue()}

def is_number(s):
    return is_float(s) or is_int(s)

def is_float(s):
    try:
        float(s)
        return True
    except ValueError:
        return False
    
def is_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

def get_numbers_in_line(line, token):
    regex_pattern = "[a-zA-Z]*\s*[" + token + "]\s*([0-9]*\.?[0-9]*)"
    parts = re.split(regex_pattern, line)
    numbers = []
    for line_part in parts:
        if is_int(line_part):
            numbers.append(int(line_part))
        elif is_float(line_part):
            numbers.append(float(line_part))
    return numbers
    
def get_prompt(output, prompt):
    pattern_string = "(?i)(" + prompt + "+.*)(?:\n|$)"
    pattern = re.compile(pattern_string)
    parts = pattern.findall(output)
    return parts

def get_line(output, keyword):
    pattern_string = "(?mi)(^.*" + keyword + ".*$)"
    pattern = re.compile(pattern_string)
    parts = pattern.findall(output)
    return parts

class NBStreamReader:

    def __init__(self, stream):
        '''
        stream: the stream to read from.
                Usually a process' stdout or stderr.
        '''

        self._s = stream
        self._q = Queue()

        def _populateQueue(stream, queue):
            '''
            Collect lines from 'stream' and put them in 'quque'.
            '''

            while True:
                line = stream.read(1)
                if line:
                    queue.put(line)
                else:
                    return

        self._t = Thread(target = _populateQueue, args = (self._s, self._q))
        self._t.daemon = True
        self._t.start() #start collecting lines from the stream

    def read(self, timeout = None):
        try:
            return self._q.get(block = timeout is not None,
                    timeout = timeout)
        except Empty:
            return None

class UnexpectedEndOfStream(Exception): pass

class InteractiveExecuter:
    """
    x = InteractiveExecuter('python myfile.py')
    """
    def __init__(self, command):
        # setup things
        self.process = Popen(command.split(), stdin = PIPE, stdout = PIPE, stderr = PIPE, shell = False, universal_newlines=True)
        self.reader = NBStreamReader(self.process.stdout)
        self.returncode = None
        sleep(0.1)
    
    def is_running(self):
        self.process.poll()
        self.returncode = self.process.returncode
        return self.returncode is None
    
    def kill(self):
        self.process.kill()
        self.is_running()
        
    def read(self):
        # read stdout until blocked (end of prompt or end of file.)
        output = ''
        while True:
            next_letter = self.reader.read(0.1)
            if not next_letter:
                return output
                break
            output += next_letter
        return None
    
    def write(self, text):
        # write data to stdin
        if self.is_running():
            self.process.stdin.write(text)
            self.process.stdin.flush()
