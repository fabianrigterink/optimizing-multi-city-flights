from client_quotes import ClientQuotes
from client_solver import ClientSolver

from datetime import timedelta

import itertools
import os
import pandas as pd
import sys
import time
import tqdm

"""
Main parameters
"""

# Which instance?
#from instance_top10 import *
from instance_top20 import *

# Which formulation?
#formulation=ClientSolver.FORMULATION_DFJ
formulation=ClientSolver.FORMULATION_MTZ

# Flags
flag_get_city_ids = False # Use place_names to assign city_ids?
flag_get_quotes   = False # Get quotes for every combination of city_ids and day?
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

    quotes = None
    
    # Check if the quotes file exists
    if not os.path.exists(quotes_file):
        print('Quotes file doesn\'t exist. Create it.')

        def get_dates(tic=None, toc=None):
            delta = toc - tic
            for i in range(delta.days + 1):
                yield tic + timedelta(days=i)

        dates = list(get_dates(tic=tic, toc=toc))
        tuples = [(origin, destination, outbound_date) for (origin, destination, outbound_date) in list(itertools.product(city_ids, city_ids, dates)) if origin != destination]

        quotes = pd.DataFrame(tuples, columns=['origin', 'destination', 'outbound_date'])
        # Initialize the DataFrame with None entries
        quotes['quote'] = None

        quotes.to_csv(quotes_file, index=False)
    else:
        print('Quotes file exists. Read it.')

        quotes = pd.read_csv(quotes_file)

        # Keep only the None entries
        quotes_null = quotes[quotes['quote'].isnull()]
        
        tuples = list(zip(quotes_null['origin'], quotes_null['destination'], quotes_null['outbound_date']))

    checkpoint = 10
    for t in tqdm.trange(len(tuples)):
        (origin, destination, outbound_date) = tuples[t]
        while True:
            status_code, result = client_quotes.get_quote(origin=origin, destination=destination, outbound_date=outbound_date)
            if status_code == 200:
                break
            else:
                time.sleep(60) # Sleep for 60 seconds, then retry
        
        quotes.loc[(quotes['origin'] == origin) & (quotes['destination'] == destination) & (quotes['outbound_date'] == outbound_date), 'quote'] = result if result is not None else sys.maxsize
        if (t + 1) % checkpoint == 0:
            print(quotes)
            quotes.to_csv(quotes_file, index=False)

    print(quotes)
    quotes.to_csv(quotes_file, index=False)

# 3. Solve

if flag_solve:
    quotes = pd.read_csv(quotes_file)

    client_solver = ClientSolver(formulation=formulation)

    print('Generating model...')
    client_solver.generate_model()

    print('Generating instance...')
    client_solver.generate_instance(instance_name=instance_name, home=home, quotes=quotes, stays_min=stays_min, stays_max=stays_max)

    print('Solving...')
    tic = time.time()
    client_solver.solve()
    toc = time.time()
    print('Solve time: {} seconds'.format(toc - tic))