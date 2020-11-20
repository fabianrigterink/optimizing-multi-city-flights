"""
Instance for the top 20 cities in Euromonitor's International Top 100 City Destinations 2019 report.
See https://www.cnn.com/travel/article/most-visited-cities-euromonitor-2019/index.html
and https://go.euromonitor.com/white-paper-travel-2019-100-cities.
"""

from datetime import date, timedelta

instance_name = 'top20_20201117'

mapping = {
    'Hong Kong'                      : 'HKGA-sky', # Includes Macau
    'Bangkok'                        : 'BKKT-sky', # Includes Pattaya
    'London'                         : 'LOND-sky',
    'Singapore'                      : 'SINS-sky',
    'Paris'                          : 'PARI-sky',
    'Dubai'                          : 'DXBA-sky',
    'New York City'                  : 'NYCA-sky',
    'Kuala Lumpur'                   : 'KULM-sky',
    'Istanbul'                       : 'ISTA-sky',
    'New Delhi'                      : 'IDEL-sky',
    'Antalya'                        : 'ANTA-sky',
    'Shenzhen Bao\'an International' : 'CSZX-sky',
    'Mumbai'                         : 'IBOM-sky',
    'Phuket'                         : 'HKTT-sky',
    'Rome'                           : 'ROME-sky',
    'Tokyo'                          : 'TYOA-sky',
    'Taipei'                         : 'TPET-sky',
    'Jeddah'                         : 'JEDA-sky'
}

place_names = mapping.keys()
city_ids    = mapping.values()

home = 'NYCA-sky'

stays_min = {city_id: 2 for city_id in city_ids if city_id != home}
stays_max = {city_id: 3 for city_id in city_ids if city_id != home}

tic = date(2021, 1,  1)
toc = tic + timedelta(days=sum(stays_max.values()))