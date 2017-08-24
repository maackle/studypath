import re
import xml.sax

from tqdm import tqdm


link_pattern = re.compile(r'\[\[([^|\]]+)(\|([^\]]+))?\]')


def badlink(x):
    return any(x.startswith(p) for p in (
        'file:',
        'image:',
        'wikipedia:',
        'template:',
        'category:',
        'wikt:',
    ))


class VertexHandler(xml.sax.ContentHandler):

    num = 0
    current = None
    page = {}
    got_id = False

    def __init__(self, vertfile):
        self.vertfile = vertfile
        self.reset()

    def reset(self):
        self.page = {'title': '', 'id': ''}
        self.got_id = False

    def handlePage(self):
        title = self.page['title'].strip().lower()
        ident = self.page['id'].strip()
        self.vertfile.write(f'{ident}\t{title}\n')

    def startElement(self, name, attrs):
        self.current = name

    def characters(self, content):
        if self.current == 'title':
            self.page['title'] += content
        elif self.current == 'id' and not self.got_id:
            self.page['id'] += content

    def endElement(self, name):
        if name == 'id':
            self.got_id = True
        if name == 'page':
            self.num += 1
            self.handlePage()
            self.reset()


class EdgeHandler(xml.sax.ContentHandler):

    num = 0
    current = None
    page = {}

    def __init__(self, vertmap, edgefile):
        self.vertmap = vertmap
        self.edgefile = edgefile

    def reset(self):
        self.page = {'title': '', 'text': ''}

    def handlePage(self):
        title = self.page['title'].strip().lower()
        if badlink(title):
            return
        ident = self.vertmap.get(title, f'???:{title}')
        for title2, _, alt in link_pattern.findall(self.page['text']):
            title2 = title2.strip().lower()
            if badlink(title2):
                continue
            ident2 = self.vertmap.get(title2, f'???:{title2}')
            self.edgefile.write(f'{ident}\t{ident2}\n')

    def startElement(self, name, attrs):
        self.current = name
        if name == "page":
            self.reset()

    def characters(self, content):
        if self.current == 'title':
            self.page['title'] += content
        elif self.current == 'text':
            self.page['text'] += content

    def endElement(self, name):
        if name == 'page':
            self.num += 1
            self.handlePage()
            if self.num % 1000 == 0:
                print(self.num)


infilename = '../dumps/enwiki-20170720-pages-articles.xml'


def write_verts():
    vertfilename = 'out/verts.txt'
    with open(infilename, 'r') as f, open(vertfilename, 'w', 8096 * 128) as verts:
        parser = xml.sax.make_parser()
        parser.setContentHandler(VertexHandler(verts))
        while True:
            buffer = f.read(8192)
            if buffer:
                parser.feed(buffer)
            else:
                break


def write_edges():
    vertfilename = '../out/verts.txt'
    edgefilename = '../out/edges.txt'
    with open(infilename, 'r') as f, open(vertfilename, 'r') as vertfile, open(edgefilename, 'w') as edgefile:
        vertmap = {}
        for l in vertfile:
            pieces = l.strip().lower().split('\t')
            if len(pieces) == 2:
                ident, name = pieces
                vertmap[name] = ident
            else:
                print("bad pieces: ", pieces)
        parser = xml.sax.make_parser()
        parser.setContentHandler(EdgeHandler(vertmap, edgefile))
        while True:
            buffer = f.read(8192)
            if buffer:
                parser.feed(buffer)
            else:
                break


def cleanup_edges():
    edgeinname = '../out/edges.txt'
    edgeoutname = '../out/edges-cleaned.txt'
    with open(edgeinname, 'r', 8096 * 32) as infile, open(edgeoutname, 'w', 8096 * 32) as outfile:
        outfile.writelines(
            l for l in infile
            if "???" not in l and l[0].isdigit()
        )


def binary_edges():
    NUM_EDGES_APPROX = 208556217
    edgeinname = '../out/edges-cleaned.txt'
    edgeoutname = '../out/edges.bin'
    with open(edgeinname, 'r', 8096 * 32) as infile, open(edgeoutname, 'wb', 8096 * 32) as outfile:
        for l in tqdm(infile, total=NUM_EDGES_APPROX):
            p = l.split('\t')
            if len(p) == 2:
                a, b = p
                try:
                    x = int(a).to_bytes(4, byteorder='big')
                    y = int(b).to_bytes(4, byteorder='big')
                except ValueError:
                    continue
                outfile.write(x)
                outfile.write(y)

# write_verts()
# write_edges()
# cleanup_edges()
binary_edges()