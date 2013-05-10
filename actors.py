# -*- coding: utf-8 -*-
# Get actors of James Bond movies and create as gexf.
import requests, requests_cache, json, itertools
import networkx as nx

requests_cache.configure('freebase')

films = []
actormap = {}
edgemap = {}
# exclude films generally not counted as part of the series
blacklist = ('/en/casino_royale_1967', '/en/casino_royale_1954', '/en/never_say_never_again')

query = {}
with open('actors.mql') as f:
    query = json.load(f)

query[0]['!pd:/film/film_series/films_in_series'][0]['id'] = '/en/james_bond_film_series'
r = requests.get('https://www.googleapis.com/freebase/v1/mqlread', params={'query': json.dumps(query)})
response = json.loads(r.text)
results = response['result']

seriesname = results[0]['!pd:/film/film_series/films_in_series'][0]['name']

for r in results:
    if r['id'] in blacklist: continue

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

outputfile = seriesname.replace(' ','')+'.gexf'
nx.write_gexf(G, outputfile, version='1.2draft')

