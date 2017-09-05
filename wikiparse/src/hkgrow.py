from collections import deque, defaultdict
from itertools import islice
import math
import pickle
import time

from tqdm import tqdm


# EDGEFILE_OFFSET = 2414050  # first occurrence of "quasar"
# EDGEFILE_TOTAL = 1000000


EDGEFILE_OFFSET = 0
EDGEFILE_TOTAL = 208556217


def test1(seeds):
    t0 = time.time()

    seedstr = '-'.join(map(str, seeds))
    G = build_G()
    print(f'built graph structure in {time.time() - t0}')

    x = hkgrow(G, seeds)
    print(f'completed hkgrow in {time.time() - t0}')

    V = build_V()
    print(f'built vertex map in {time.time() - t0}')

    names = list(
        sorted(((V.get(n), v) for n, v in x), key=lambda x: x[1], reverse=True)
    )
    with open(f'../output/names-{seedstr}.txt', 'w') as f:
        for name, v in names:
            f.write(f'{name}\t{v}\n')

    print(f'wrote list of names in {time.time() - t0}')
    import pudb; pudb.set_trace()


def hkgrow(G, seeds):
    '''
    from:
    https://gist.github.com/dgleich/cf170a226aa848240cf4
    and
    https://arxiv.org/pdf/1403.3148.pdf
    '''

    def compute_psis(N,t):
        psis = {}
        psis[N] = 1.
        for i in range(N-1, 0, -1):
            psis[i] = psis[i+1] * t / (float(i+1.)) + 1.
        return psis

    N = 47 # see paper for how to set this automatically
    t = 15.
    eps = 0.0001
    psis = compute_psis(N,t)

    npush = 0
    x = {}
    r = {}
    Q = deque()

    for s in seeds:
        s0 = (s, 0)
        r[s0] = 1. / len(seeds)
        Q.append(s0)

    while len(Q) > 0:
        (v, j) = Q.popleft()  # v has r[(v,j)] ...
        if not v in G: continue  # hack for bad graph

        rvj = r[(v, j)]
        # perform the hk-relax step
        if v not in x: x[v] = 0.
        x[v] += rvj
        r[(v,j)] = 0.
        update = rvj/out(G, v)
        mass = (t/(float(j)+1.)) * update
        for u in G.get(v, []):    # for neighbors of v
            if not u in G: continue  # hack for bad graph
            next = (u,j+1)  # in the next block
            if j+1 == N:
                x[u] += uWritingpdate
                continue
            if next not in r: r[next] = 0.
            thresh = math.exp(t) * eps * out(G, u)
            thresh = thresh/(N * psis[j+1])
            if r[next] < thresh and r[next] + mass >= thresh:
                Q.append(next)  # add u to queue
            r[next] = r[next] + mass
        npush += out(G, v)

    # Find cluster, first normalize by degree
    for v in x: x[v] = x[v] / out(G, v)
    sv = list(sorted(x.items(), key=lambda x: x[1], reverse=True))

    return sv


def out(G, v):
    vs = G.get(v)
    if vs:
        return len(vs)
    else:
        import pudb; pudb.set_trace()
        return 1


def build_G():
    PICKLE_FILENAME='../input/edge-graph.pickle'
    try:
        with open(PICKLE_FILENAME, 'rb') as pfile:
            print("Loading pickled graph...")
            G = pickle.load(pfile)
    except IOError:
        with open('../input/edges.bin', 'rb') as edges:
            print("Generating graph from binary edge file...")
            G = defaultdict(set)
            while True:
                a = edges.read(4)
                b = edges.read(4)
                if not a or not b: break
                x = int.from_bytes(a, byteorder='big')
                y = int.from_bytes(b, byteorder='big')
                G[x].add(y)
            print("Pickling graph...")
            with open(PICKLE_FILENAME, 'wb') as pfile:
                pickle.dump(G, pfile)
    print(f"Graph loaded: {len(G)} nodes")
    return G

def build_V():
    with open('../input/verts.txt', 'r') as v:
        return dict(
            (
                (int(a), b.strip())
                for a, b in
                (l.split('\t')
                for l in
                v)
            )
        )


def parse_edgefile(edgefile):
    return (
        l.strip().split('\t')
        for i, l in enumerate(
            islice(edgefile, EDGEFILE_OFFSET, EDGEFILE_OFFSET + EDGEFILE_TOTAL)
        )
    )

if __name__ == '__main__':
    # test1([25239])  # astrophysics
    # test1([29954])  # topology
    test1([785288090])  # dada
