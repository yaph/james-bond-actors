# -*- coding: utf-8 -*-
# Get actors of all movies in a series and create as gexf.
import requests, requests_cache, json, itertools
import networkx as nx

requests_cache.configure('freebase')
series = ['/en/james_bond_film_series',
          '/en/the_three_mesquiteers',
          '/en/carry_on_films',
          '/en/the_pink_panther',
          '/m/0hn_rv_', # Star Trek
          '/en/star_wars',
          '/m/01rb9m', # Nightmare on Elm Street
          '/wikipedia/en_title/Tomie_$0028film_series$0029',
          '/m/0g_sz63', # Jerry Cotton
          '/m/0lmfcgx',  # Tsuribaka Nisshi
          '/m/02676m4', # Harry Potter
          '/en/american_pie_film_series',
          '/en/the_whistler_film_series',
          '/wikipedia/en/The_Fast_and_the_Furious_$0028film_series$0029',
          '/m/0j_l7cw', # Hellraiser
          '/wikipedia/en_title/The_Texas_Chainsaw_Massacre_$0028franchise$0029',
          '/en/x_men_film_series',
          '/en/superman_film_series',
          '/m/0gyjf4v', # Batman

          '/m/0j7ylh0' # Emmanule
          ]

# exclude films generally not counted as part of the series
blacklist = ('/en/casino_royale_1967', '/en/casino_royale_1954', '/en/never_say_never_again')

query = {}
with open('actors.mql') as f:
    query = json.load(f)

def dump_actors_to_gexf(id):
    films = []
    actormap = {}
    edgemap = {}

    query[0]['!pd:/film/film_series/films_in_series'][0]['id'] = id
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
        attr = {'label': actormap[a]['label'],
                    'films': '|'.join(actormap[a]['films'])
                    }
        G.add_node(a, attr)
        G.node[a]['viz'] = {'size': len(actormap[a]['films'])}

    for e in edgemap:
        G.add_edge(e[0], e[1], {'weight': edgemap[e]})

    outputfile = seriesname.replace(' ','')+'.gexf'
    nx.write_gexf(G, outputfile, version='1.2draft')
    return outputfile

def main():
    for id in series:
        print "Dumping ",id
        filename = dump_actors_to_gexf(id)
        print "  dumped", filename

if __name__ == "__main__":
    main()
