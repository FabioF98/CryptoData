from datetime import datetime
import json
import requests
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import schedule
import time


# Definisco una funzione necessaria per poi usare il modulo schedule e automatizzare il processo ogni giorno alla
# stessa ora
def crypto_report():
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'

    # Definisco due set di parametri, il secondo con parametro 'sort' : 'percent_change_24h'
    # per ordinare le migliori e peggiori criptovalute in base al cambiamento percentuale. Ho specificato
    # 'cryptocurrency_type' : 'coins', perché ho notato che i token avevano valori elevati di volume
    # e di cambiamenti percentuali nelle ultime 24h quindi ho pensato di tenere solo i coins
    params = {
        'start': '1',
        'limit': '1000',
        'convert': 'USD',
        'cryptocurrency_type': 'coins'
    }
    sorted24h_params = {
        'start': '1',
        'limit': '1000',
        'convert': 'USD',
        'cryptocurrency_type': 'coins',
        'sort': 'percent_change_24h',
        'sort_dir': 'desc',
    }
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': 'ff863e6a-78a4-4992-ad62-5cae52cada4f'
    }

    # Seguendo la documentazione ufficiale di coinmarketcap ho implementato una clausola try/except, ho aggiunto un
    # else così da proseguire con l'esecuzione del programma solo nel caso in cui non ci siano errori
    try:
        sorted24h_currencies = requests.get(url=url, headers=headers, params=sorted24h_params).json()['data']
        currencies = requests.get(url=url, headers=headers, params=params).json()['data']
    except (ConnectionError, Timeout, TooManyRedirects) as e:
        print(e)
    else:
        # Dizionario per raccogliere i dati, che ogni giorno alle 10:00 sarà compilato e salvato con il nome
        # del giorno della sua creazione. Ho cercato di utilizzare nomi appropriati per ogni chiave. Per le
        # criptovalute con volume superiore a 76kk ho anche definito una chiave 'info' nella quale riporto i
        # componenti del total_price, per chiarezza.
        data = {'highest_volume': None,
                'best_ten_crypto': {},
                'worst_ten_crypto': {},
                'totalprice_first20': None,
                'price_1each_over76kk': {
                    'info': {},
                    'total_price': None
                },
                'logbook': {
                    'prices_today': {},
                    'prices_yesterday': {},
                    'percent_change_24h': {},
                    'net_percentage': None
                }
                }

        # Creo un counter che mi servirà per tenere traccia di quante criptovalute sto salvando ma anche per
        # assegnare ad ognuna un nome diverso, ed inserisco all'interno di 'best_ten_crypto' tutti i dati relativi
        # ad ognuna delle prime dieci criptovalute
        best_counter = 0
        for b_currency in sorted24h_currencies:
            if best_counter < 10:
                crypto_best_name = 'best_' + str(best_counter)
                data['best_ten_crypto'][crypto_best_name] = b_currency
                best_counter += 1

        # Faccio la stessa cosa per le peggiori, invertendo l'ordine di sorted24h_currencies
        worst_counter = 0
        for w_currency in reversed(sorted24h_currencies):
            if worst_counter < 10:
                crypto_worst_name = 'worst_' + str(worst_counter)
                data['worst_ten_crypto'][crypto_worst_name] = w_currency
                worst_counter += 1

        # Ho inserito all'interno di questo for loop tutte le altre informazioni richieste per il programma, quindi:
        # 1) La quantità di denaro neccessaria per acquistare una unità di ciascuna delle prime 20 criptovalute,
        #    aggiornando allo stesso tempo il logbook con i prezzi attuali e con quelli della giornata precedente
        # 2) La quantità di denaro necessaria per acquistare una unità di tutte le criptovalute il cui volume delle
        #    ultime 24 ore sia superiore a 76.000.000$
        # 3) Le informazioni relative alle criptovalute con volume delle ultime 24 ore superiore a 76.000.000$
        first20_counter = 0
        for currency in currencies:
            crypto_name = currency['name']
            crypto_volume24h = currency['quote']['USD']['volume_24h']
            today_value = currency['quote']['USD']['price']
            perc_change24h = currency['quote']['USD']['percent_change_24h']
            yesterday_value = today_value + (today_value * perc_change24h / 100)
            if first20_counter < 20:
                data['logbook']['prices_today'][crypto_name] = today_value
                data['logbook']['prices_yesterday'][crypto_name] = yesterday_value
                data['logbook']['percent_change_24h'][crypto_name] = perc_change24h
                first20_counter += 1
            if not data['highest_volume'] or crypto_volume24h > data['highest_volume']['quote']['USD']['volume_24h']:
                data['highest_volume'] = currency
            if crypto_volume24h > 76000000:
                data['price_1each_over76kk']['info'][crypto_name] = today_value

        # Calcolo la quantità di denaro necessaria per l'acquisto
        data['totalprice_first20'] = sum(data['logbook']['prices_today'].values())
        data['price_1each_over76kk']['total_price'] = sum(data['price_1each_over76kk']['info'].values())

        # definisco il nome del file
        today = datetime.today().strftime('%d.%m.%Y')
        today_filename = today + '.json'
        total_today = sum(data['logbook']['prices_today'].values())
        total_yesterday = sum(data['logbook']['prices_yesterday'].values())
        # calcolo la perdita o il guadagno netto percentuale
        data['logbook']['net_percentage'] = ((total_today - total_yesterday)/total_yesterday) * 100

        #riporto tutto all'interno del file, con parametro indent = 4 per rendere il file più leggibile
        with open(today_filename, 'w') as outfile:
            json.dump(data, outfile, indent=4)

# utilizzo il modulo schedule per fare in modo che ogni giorno alla stessa ora venga eseguita la funzione
schedule.every().day.at('10:00').do(crypto_report)

while True:
    schedule.run_pending()
    time.sleep(1)
