#!/sharedData2/nshakoor/.conda/envs/wildfireenv3/bin/python

# -*- coding: utf-8 -*-
import re
import sys
import time
from subprocess import Popen, PIPE

def main():
    pid = Popen("ls", shell=True, stdout=PIPE)
    output = pid.communicate()
    print('this is the output', output)
    
        
        

if __name__ == '__main__':
    main()
