# -*- coding: utf-8 -*-
# Script doesn't work  as intended since the size values of nodes were changed
# during processing with Gephi
import sys, itertools
import networkx as nx

def remove_actor_from_film(G, aid, film):
    for n in G.nodes(True):
        if n[0] == aid:
            films = n[1]['films'].split('|')
            if film in films:
                # remove film from node
                del films[films.index(film)]
                G.node[aid]['films'] = '|'.join(films)
                print G.node[aid]


if len(sys.argv) != 2:
    print('Usage: %s gexffile' % sys.argv[0])
    sys.exit()

gexf = sys.argv[1]
G = nx.read_gexf(gexf, node_type=None)
remove_actor_from_film(G, '/en/timothy_dalton', 'A View to a Kill')
