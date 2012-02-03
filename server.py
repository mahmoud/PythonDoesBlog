import os
from bottle import get, post, route, run
from subprocess import Popen, PIPE

from generate import generate
from settings import SOURCE_DIR, OUTPUT_DIR, REMOTE_DIR, SERVER_PORT
SOURCE_DIR = os.path.abspath(SOURCE_DIR)
OUTPUT_DIR = os.path.abspath(OUTPUT_DIR)

def git_pull():
    proc = Popen('git pull', shell=True, cwd=SOURCE_DIR, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    out, err = proc.communicate()

def rsync():
    TO_UPLOAD = os.path.join(OUTPUT_DIR, '*')
    proc = Popen(('rsync -r '+TO_UPLOAD+' '+ REMOTE_DIR),
                 shell=True, cwd=OUTPUT_DIR, 
                 stdin=None, stdout=PIPE, stderr=PIPE)
    out, err = proc.communicate()

@get('/publish')
@post('/publish')
def publish():
    print "Updating repo... ",
    git_pull()
    print "done."
    print "Generating site... ",
    generate()
    print "done."
    print "Uploading...",
    rsync()
    print "done."

if __name__ == '__main__':
    run(host='0.0.0.0', port=SERVER_PORT)
