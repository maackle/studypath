import redis

import reader

def load_vertices():
    r = redis.Redis()
    with open('../input/verts.txt', 'r') as f:
        vg = reader.vertex_name_generator(f)
        reader.load_vertices_into_redis(vg, r)
    print("loaded verts into redis")

    with open('../input/edges.bin', 'rb') as f:
        adj = reader.adjacency_list_generator(f)
        reader.load_edges_into_redis(adj, r)
    print("loaded edges into redis")


if __name__ == '__main__':
    load_vertices()