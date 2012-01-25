from blog import Blog
from settings import SOURCE_DIR

def generate():
    from blog import Blog
    b = Blog(SOURCE_DIR)
    b.render()
    #import pdb;pdb.set_trace()

# TODO: automatic linking to other PDWs via syntax PDWxxx where xxx is an integer ID

if __name__ == '__main__':
    generate()
