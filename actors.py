# -*- coding: utf-8 -*-
# Get actors of James Bond movies and create as gexf.
import requests, requests_cache, json, itertools
import networkx as nx

requests_cache.configure('freebase')

films = []
actormap = {}
edgemap = {}
gexf = 'jamesbond.gexf'

with open('actors.mql') as f:
    query = f.read()
r = requests.get('https://www.googleapis.com/freebase/v1/mqlread', params={'query': query})
#r = requests.get('https://www.googleapis.com/freebase/v1/mqlread/?lang=%2Flang%2Fen&query=%5B%7B+%22!pd%3A%2Ffilm%2Ffilm_series%2Ffilms_in_series%22%3A+%5B%7B+%22!index%22%3A+null%2C+%22id%22%3A+%22%2Fen%2Fjames_bond_film_series%22%2C+%22name%22%3A+null%2C+%22type%22%3A+%22%2Ffilm%2Ffilm_series%22+%7D%5D%2C+%22id%22%3A+null%2C+%22initial_release_date%22%3A+null%2C+%22name%22%3A+null%2C+%22sort%22%3A+%22!pd%3A%2Ffilm%2Ffilm_series%2Ffilms_in_series.!index%22%2C+%22starring%22%3A+%5B%7B+%22actor%22%3A+%7B+%22id%22%3A+null%2C+%22name%22%3A+null%2C+%22optional%22%3A+true+%7D%2C+%22id%22%3A+null%2C+%22index%22%3A+null%2C+%22limit%22%3A+500%2C+%22optional%22%3A+true%2C+%22sort%22%3A+%22index%22%2C+%22type%22%3A+%22%2Ffilm%2Fperformance%22+%7D%5D%2C+%22type%22%3A+%22%2Ffilm%2Ffilm%22+%7D%5D')
res = json.loads(r.text)['result']

for r in res:
    # exclude 2 Casino Royal films generally not counted as part of the series
    if r['id'] in ('/en/casino_royale_1967', '/en/casino_royale_1954', '/en/never_say_never_again'): continue

    actors = []
    for s in r['starring']:
        if s['actor'] is None: continue

        aid = s['actor']['id']
        alabel = s['actor']['name']
        actors.append({
            'id': aid,
            'label': alabel
        })
        if aid not in actormap:
            actormap[aid] = {'label': alabel, 'size': 0, 'films': []}
        actormap[aid]['size'] += 1
        actormap[aid]['films'].append(r['name'])

    films.append({
        'id': r['id'],
        'label': r['name'],
        'actors': actors
    })

actorids = list(actormap.keys())

for f in films:
    comb = itertools.combinations(f['actors'], 2)
    for c in comb:
        e = tuple(sorted([c[0]['id'], c[1]['id']]))
        edgemap[e] = edgemap.get(e, 0) + 1

G = nx.Graph()
for a in actormap:
    G.add_node(a, {'label': actormap[a]['label'], 'films': '|'.join(actormap[a]['films'])})
    G.node[a]['viz'] = {'size': actormap[a]['size']}

for e in edgemap:
    G.add_edge(e[0], e[1], {'weight': edgemap[e]})

nx.write_gexf(G, gexf, version='1.2draft')

