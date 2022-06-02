from datetime import datetime
import requests
from bs4 import BeautifulSoup
import sqlite3
import re
import os


headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36'
    }
print(datetime.now())

DIRECTORY_PATH= os.path.abspath(os.path.dirname(__file__))

con = sqlite3.connect(os.path.join(DIRECTORY_PATH, 'database'))

curs = con.cursor()

curs.execute('SELECT COUNT(Id) FROM links;')
size_before = curs.fetchall()[0][0]

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
    
    c = 'A'
    hrefs = soup.find_all('a', href= True, class_='sc-12rk7z2-1 kQcyga', limit=hjs)
    
    if len(hrefs) == 0: # Caso não achou nada na classe sc.., deve procurar na classe fn..
        c = 'B'
        hrefs = soup.find_all('a', href= True, class_='fnmrjs-0 fyjObc', limit=hjs)
    
    
    links = [(x.get('href'), x.get('href').split('-')[-1]) for x in hrefs]
    
    curs.executemany('INSERT OR IGNORE INTO links(href, olx_code) VALUES(?, ?);', links)

    print(f'Página {pg} ✔️  +{len(links)} , "{c}"')
    con.commit()
    pg += 1

curs.execute('SELECT COUNT(Id) FROM links;')
size_after = curs.fetchall()[0][0]
collected = size_after - size_before

print(f'CONCLUÍDO! Extraído {collected} Links.')

if collected > 500:
    with open(os.path.join(DIRECTORY_PATH, 'logs', 'inference_num.log'), 'w') as log:
        log.write(str(collected))

con.close()

