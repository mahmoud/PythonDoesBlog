import sys, os, time
from functools import wraps
from bottle import get, post, route, run, request, response
from subprocess import Popen, PIPE

# NOTE: certain changes may require you to restart the server.
import settings
from settings import SOURCE_DIR, OUTPUT_DIR, REMOTE_DIR
SOURCE_DIR = os.path.abspath(SOURCE_DIR)
OUTPUT_DIR = os.path.abspath(OUTPUT_DIR)

def git_pull():
    proc = Popen('git pull', shell=True, cwd=SOURCE_DIR, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    out, err = proc.communicate()

def generate():
    # this is a bit of a hack to avoid having to restart the server when blog modules are changed
    proc = Popen('python generate.py', shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    out, err = proc.communicate()

def rsync():
    TO_UPLOAD = os.path.join(OUTPUT_DIR, '*')
    proc = Popen(('rsync -r '+TO_UPLOAD+' '+ REMOTE_DIR),
                 shell=True, cwd=OUTPUT_DIR, 
                 stdin=None, stdout=PIPE, stderr=PIPE)
    out, err = proc.communicate()

def pubsub_ping():
    """
    Ping a PubSub hub. Might be overtailored to Superfeedr docs; 
    your pubsub hub may differ.

    Also, I'd love to use requests here, but this is a bit minor.
    Trying to keep those reqs down.
    """
    hub_url = settings.get('PUBSUB_URL')
    blog_url = settings.get('BLOG_URL')
    if not hub_url or not blog_url:
        print "Need to have BLOG_URL and PUBSUB_URL set for pubsub to work."
        return

    import urllib, urllib2

    rss_url  = blog_url+'feed/rss.xml'
    atom_url = blog_url+'feed/atom.xml'

    rss_args = { 'hub.mode':'publish', 'hub.url': rss_url }
    rss_req = urllib2.Request(hub_url)
    rss_req.add_data(urllib.urlencode(rss_args))
    rss_res = urllib2.urlopen(rss_req).read()

    atom_args = { 'hub.mode':'publish', 'hub.url': atom_url }
    atom_req = urllib2.Request(hub_url)
    atom_req.add_data(urllib.urlencode(atom_args))
    atom_res = urllib2.urlopen(atom_req).read()

    return

def print_timing(f):
    @wraps(f)
    def wrapper(*arg):
        t1 = time.time()
        res = f(*arg)
        t2 = time.time()
        print ' - %s took %0.3f s' % (f.func_name, (t2-t1))
        print
        return res
    return wrapper

@get('/publish')
@post('/publish')
@print_timing
def publish():
    print "Updating repo... ",
    sys.stdout.flush()
    git_pull()
    print "done.\nGenerating site... ",
    sys.stdout.flush()
    generate()
    print "done.\nUploading...",
    sys.stdout.flush()
    rsync()
    print "done.",
    
    if settings.get('PUBSUB_URL'):
        print "\nNotifying PubSub hubs...",
        sys.stdout.flush()
        pubsub_ping()
        print "done."
    else:
        print

@post('/callback')
@get('/callback')
def push_callback():
    # TODO: turn this into an actual test.
    #       subscribe, ping, wait for response.
    ret = request.params.get('hub.challenge')
    print ret
    return ret

if __name__ == '__main__':
    port = settings.get('SERVER_PORT')
    if port:
        run(host='0.0.0.0', port=port)
    else:
        print "You must set SERVER_PORT in settings to use the publish server"
