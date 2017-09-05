import csv
import re
import time
import xml.sax

from contexttimer import Timer
from tqdm import tqdm


link_pattern = re.compile(r'\[\[([^|\]]+)(\|([^\]]+))?\]')

def simplify_vertids(vertids, redirects):
    total = len(redirects.keys())
    for k in tqdm(redirects.keys(), total=total):
        ks = [k]
        while True:
            k = redirects.get(k)
            if k and k not in ks:  # end condition and loop breaker
                ks.append(k)
            else:
                break
        for t in reversed(ks):
            ident = vertids.get(t)
            if ident:
                break
        if ident is None:
            print(f'bad key sequence: {ks}')
            continue
        else:
            for t in ks:
                vertids[t] = ident
    return vertids


def write_vertids(vertids, f):
    for title, ident in vertids.items():
        f.write(f'{ident}\t{title}\n')

def write_redirects(vertids, f):
    for title1, title2 in redirects.items():
        f.write(f'{title1}\t{title2}\n')


def read_verts(f):
    for l in f:
        pieces = l.strip().split('\t')
        if len(pieces) == 2:
            ident, name = pieces
            yield name, ident
        else:
            print("bad pieces: ", pieces)

def read_edges(f):
    for l in f:
        pieces = l.strip().split('\t')
        if len(pieces) == 2:
            yield pieces
        else:
            print("bad pieces: ", pieces)

class VertexHandler(xml.sax.ContentHandler):

    num = 0
    current = None
    page = {}
    redirects = {}
    vertids = {}
    got_id = False

    def __init__(self, redirectfile, vertfile):
        self.redirectfile = redirectfile
        self.vertfile = vertfile
        self.reset()

    def reset(self):
        self.page = None
        self.redirect_title = None
        self.got_id = False

    def handlePage(self):
        title = self.page['title'].strip()
        if ':' in title:
            return
        ident = self.page['id'].strip()
        self.vertids[title] = ident
        if self.redirect_title:
            self.redirects[title] = self.redirect_title
        # self.vertfile.write(f'{ident}\t{title}\n')

    def startElement(self, name, attrs):
        self.current = name
        if name == 'page':
            self.page = {'title': '', 'id': ''}
        elif name == 'redirect':
            self.redirect_title = attrs['title'].strip()

    def characters(self, content):
        if self.current == 'title':
            self.page['title'] += content
        elif self.current == 'id' and not self.got_id:
            self.page['id'] += content

    def endElement(self, name):
        if name == 'id':
            self.got_id = True
        elif name == 'page':
            self.num += 1
            self.handlePage()
            self.reset()
        elif name == 'mediawiki':
            write_redirects(self.redirects, self.redirectfile)
            write_vertids(self.vertids, self.vertfile)



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
        title = self.page['title'].strip()
        if ':' in title:
            return
        ident = self.vertmap.get(title, f'???:{title}')
        for title2, _, alt in link_pattern.findall(self.page['text']):
            title2 = title2.strip()
            if ':' in title2:
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
    vertfilename = '../input/verts-raw.txt'
    redirectfilename = '../input/redirects.txt'
    vert2filename = '../input/verts-simplified.txt'

    def get_verts_and_redirects():
        verts = {}
        redirects = {}
        with open(vertfilename, 'r') as vertfile, open(redirectfilename, 'r') as redirectfile:
            for l in vertfile:
                try:
                    pieces = l.strip().split('\t')
                    ident, name = pieces
                except ValueError:
                    print('bad vert:', l)
                    continue
                verts[name] = ident
            for l in redirectfile:
                try:
                    pieces = l.strip().split('\t')
                    t1, t2 = pieces
                except ValueError:
                    print('bad redirect:', l)
                    continue
                redirects[t1] = t2
        return verts, redirects
    try:
        verts, redirects = get_verts_and_redirects()
        print("Loaded existing vert and redirect data!")
    except IOError:
        print("Computing from raw wiki dump...")
        with open(infilename, 'r') as f, open(vertfilename, 'w', 8096 * 128) as vertfile, open(redirectfilename, 'w', 8096 * 128) as redirectfile:
            parser = xml.sax.make_parser()
            handler = VertexHandler(redirectfile, vertfile, vertfile2)
            parser.setContentHandler(handler)

            t0 = time.time()
            while True:
                buffer = f.read(8192)
                if buffer:
                    parser.feed(buffer)
                else:
                    break
            print(f'Finished in {time.time() - t0}')
        verts = handler.vertids
        redirects = handler.redirects
    simplify_vertids(verts, redirects)
    with open(vert2filename, 'w') as v2:
        write_vertids(verts, v2)



def write_edges():
    vertfilename = '../input/verts-simplified.txt'
    edgefilename = '../input/edges.txt'
    with open(infilename, 'r') as f, open(vertfilename, 'r') as vertfile, open(edgefilename, 'w') as edgefile:
        vertmap = {}
        for l in vertfile:
            pieces = l.strip().split('\t')
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
    edgeinname = '../input/edges.txt'
    edgeoutname = '../input/edges-cleaned.txt'
    with open(edgeinname, 'r', 8096 * 32) as infile, open(edgeoutname, 'w', 8096 * 32) as outfile:
        outfile.writelines(
            l for l in infile
            if "???" not in l and l[0].isdigit()
        )


def binary_edges():
    NUM_EDGES_APPROX = 208556217
    edgeinname = '../input/edges-cleaned.txt'
    edgeoutname = '../input/edges.bin'
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


def make_neo4j_csv():
    vertfilename = '../input/verts-simplified.txt'
    edgefilename = '../input/edges-cleaned.txt'
    nodecsvname = '../output/nodes.csv'
    linkcsvname = '../output/links.csv'
    multiquote = re.compile(r"'+")
    with \
        open(vertfilename, 'r') as vertfile, \
        open(edgefilename, 'r') as edgefile, \
        open(nodecsvname, 'w') as nodecsv, \
        open(linkcsvname, 'w') as linkcsv:

        nodewriter = csv.writer(nodecsv, quotechar="|")
        nodewriter.writerow(["wpid:ID", "title"])
        for title, ident in read_verts(vertfile):
            # title = multiquote.sub(r"\'", title)
            nodewriter.writerow([ident, title])

        linkwriter = csv.writer(linkcsv, quotechar="|")
        linkwriter.writerow([":START_ID", ":END_ID"])
        for pair in read_edges(edgefile):
            linkwriter.writerow(pair)


if __name__ == '__main__':
    with Timer() as t:
        # write_verts()
        # write_edges()  # takes about an hour and 20 mins
        # cleanup_edges()  # takes about a minute
        # binary_edges()
        make_neo4j_csv()
        print("Finished in ", t.elapsed, " seconds")
