from client_quotes import ClientQuotes
from client_solver import ClientSolver

from datetime import timedelta

import itertools
import pandas as pd
import time
import tqdm

"""
Main parameters
"""

# Which instance?
from instance_top10 import *
#from instance_top20 import *

# Flags
flag_get_city_ids = True # Use place_names to assign city_ids?
flag_get_quotes   = True # Get quotes for every combination of city_ids and day?
flag_solve        = True # Solve the problem?

"""
/Main parameters
"""

client_quotes = ClientQuotes()

# 1. Get city IDs

if flag_get_city_ids:
    print('### Getting city IDs...')

    city_ids = []

    for place_name in place_names:
        found, result = client_quotes.get_city_id(place_name=place_name)
        if found:
            city_ids.append(result)
        else:
            print('Could not find city ID for place name \'{}\'. Pick from the following place names:'.format(place_name))
            print(result)
    
    print(city_ids)

# 2. Get quotes

quotes_file = 'data/quotes_{}.csv'.format(instance_name)

if flag_get_quotes:
    print('### Getting quotes...')

    quotes = pd.DataFrame()

    def get_dates(tic=None, toc=None):
        delta = toc - tic
        for i in range(delta.days + 1):
            yield tic + timedelta(days=i)

    dates = list(get_dates(tic=tic, toc=toc))
    tuples = [(origin, destination, outbound_date) for (origin, destination, outbound_date) in list(itertools.product(city_ids, city_ids, dates)) if origin != destination]
    
    for t in tqdm.trange(len(tuples)):
        (origin, destination, outbound_date) = tuples[t]
        while True:
            status_code, result = client_quotes.get_quote(origin=origin, destination=destination, outbound_date=outbound_date)
            if status_code == 200:
                break
            else:
                print(quotes)
                time.sleep(60) # Sleep for 60 seconds, then retry
        d = {
            'origin'        : origin,
            'destination'   : destination,
            'outbound_date' : outbound_date,
            'quote'         : result
        }
        quotes = quotes.append(d, ignore_index=True)

    print(quotes)

    quotes.to_csv(quotes_file, index=False)

# 3. Solve

if flag_solve:
    print('### Solving...')

    quotes = pd.read_csv(quotes_file)

    client_solver = ClientSolver()
    client_solver.generate_model()
    client_solver.generate_instance(instance_name=instance_name, home=home, quotes=quotes, stays_min=stays_min, stays_max=stays_max)
    client_solver.solve()