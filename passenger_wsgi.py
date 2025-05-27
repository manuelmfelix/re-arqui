import imp
import os
import sys

# Add the project directory to the path
INTERP = os.path.expanduser("/home/rearquip/virtualenv/repositories/rearqui/3.11/bin/python")
if sys.executable != INTERP:
    os.execl(INTERP, INTERP, *sys.argv)

sys.path.insert(0, os.path.dirname(__file__))

wsgi = imp.load_source('wsgi', 're_arqui/wsgi.py')
application = wsgi.application