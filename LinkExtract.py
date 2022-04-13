import requests
from bs4 import BeautifulSoup
import sqlite3
import re

con = sqlite3.connect('CarDealsML/database')
curs = con.cursor()

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36'
    }

hjs = 999
pg = 1

while True:
    url = f'https://rs.olx.com.br/autos-e-pecas/carros-vans-e-utilitarios?o={pg}&sf=1'
    
    page = requests.get(url, headers=headers)

    html = page.text

    hjs = len([*re.finditer('Anúncio publicado em\: Hoje', str(html))])
    
    if hjs == 0:
        break
    
    soup = BeautifulSoup(html, 'html.parser')
    
    links = [(x.get('href'),) for x in soup.find_all('a', href= True, class_='fnmrjs-0 fyjObc', limit=hjs)]

    curs.executemany('INSERT INTO links(href) VALUES(?);', links)

    print(f'Página {pg} foi um SUCESSO! +{hjs} links')
    con.commit()
    pg += 1
    
print('CONCLUÍDO!')
con.close()