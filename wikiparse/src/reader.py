
def vertex_name_generator(f):
    '''
    Given a text file of format "{id}\t{name}"
    return a generator of pairs (vertex_id, vertex_name)
    '''
    return (
        (int(a), b.strip())
        for a, b in
        (l.split('\t')
        for l in
        f)
    )


def adjacency_list_generator(f):
    '''
    Given a binary file of 4 byte ints representing pairs of vertices
    connected by edges, produce a generator of pairs:

    (vertex, set_of_vertices)

    which represents an adjacency list.
    '''
    vs = set()
    x0 = None
    while True:
        a = f.read(4)
        b = f.read(4)
        if not a or not b: break
        x = int.from_bytes(a, byteorder='big')
        y = int.from_bytes(b, byteorder='big')
        if x0 != x:
            if x0:
                yield x0, vs
            x0 = x
            vs = set()
        vs.add(y)
    yield x0, vs


def load_vertices_into_redis(verts, r):
    for v, name in verts:
        r.set(f'vn-{v}', name)


def load_edges_into_redis(adjlist, r):
    for v, vs in adjlist:
        r.sadd(f'out-{v}', *vs)