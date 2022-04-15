import requests
import sqlite3
import re
import json

headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36'}


con = sqlite3.connect('CarDealsML/database')
curr = con.cursor()


curr.execute('SELECT Id, href FROM links WHERE explored = 0;')

idx_list, url_list = map(list, zip(*[x for x in curr.fetchall()]))


for idx, url in zip(idx_list, url_list):
    page = requests.get(url, headers= headers)
    html = page.text

    script = re.search('<script>window.dataLayer.*?<\/script>', html).group()
    
    try:
        data = json.loads(re.search('\[.*?]', script).group()[1:-1])['page']['adDetail']
        meta = re.search('<meta property="og:description" content=".*?">', html).group()
        
        user_type = re.search('"dfp_vas_user_type":"\d"', html).group()
        data['pro_vendor'] = int(re.search('\d', user_type).group())

        data['addesc'] = re.search('content=".*?"', meta).group().replace('content=', '')
        
    except:
        print(idx, 'X')
        curr.execute(f'UPDATE links SET explored=2 WHERE Id = {idx};')
        continue
    
    curr.execute(f'UPDATE links SET explored=1 WHERE olx_code = {data["listId"]};')
    
    keys = list(data.keys())
    
    if 'state' in keys:
        data['estado'] = data.pop('state')
    if 'version' in keys:
        data['versao'] = data.pop('version')
    if 'subject' in keys:
        data['titulo'] = data.pop('subject')
    if 'owner' in keys:
        data['dono'] = data.pop('owner')
    
    rows = tuple(data.keys())
    
    values = str(tuple(data.values())).replace('None', 'null') #null = equivalente de None do SQL
    
    query = f"INSERT OR IGNORE INTO CarInfoRaw{rows} VALUES{values}"
    print(idx, '✔️')
    curr.execute(query)
    con.commit()

con.close()

#         #         #         #         #         #         #         #         #         #         !