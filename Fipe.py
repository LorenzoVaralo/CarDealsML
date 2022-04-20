import requests
import json
import ast
import queue
from threading import Thread

def treat_resp(resp):
    dicionario = {}
    if 'modelos' in resp:
        resp = resp['modelos']
    for i in resp:
        dicionario[i['nome'].upper()] = i['codigo']
    return dicionario

# Source: https://towardsdatascience.com/parallel-web-requests-in-python-4d30cc7b8989

def perform_web_requests(addresses, no_workers):
    class Worker(Thread):
        def __init__(self, request_queue):
            Thread.__init__(self)
            self.queue = request_queue
            self.results = {}

        def run(self):
            while True:
                content = self.queue.get()
                if content == "":
                    break
                response = requests.get(list(content.values())[0], headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36'})
                self.results[list(content.keys())[0]] = treat_resp(ast.literal_eval(response.text))
                self.queue.task_done()

    # Create queue and add addresses
    q = queue.Queue()
    for k, v in addresses.items():
        q.put({k:v})

    # Workers keep working till they receive an empty string
    for _ in range(no_workers):
        q.put("")

    # Create workers and add tot the queue
    workers = []
    for _ in range(no_workers):
        worker = Worker(q)
        worker.start()
        workers.append(worker)
    # Join workers to wait till they finished
    for worker in workers:
        worker.join()

    # Combine results from all workers
    r = {}
    for worker in workers:
        
        r.update(worker.results)
    return r


brands_dict = perform_web_requests({'marcas':'https://parallelum.com.br/fipe/api/v1/carros/marcas'}, 1)['marcas']


for marca, cod in brands_dict.items():
    brands_dict[marca] = f'https://parallelum.com.br/fipe/api/v1/carros/marcas/{cod}/modelos' 
print('Marcas OK!')

models_dict = perform_web_requests(brands_dict, 8)
for marca, modelos in models_dict.items():
    models_dict[marca] = {}
    for modelo, cod in modelos.items():
        models_dict[marca].update({modelo: f'{brands_dict[marca]}/{cod}/anos'})
print('Modelos OK!')

years_dict = {}
for marca, modelos in models_dict.items():
    years_dict[marca] = perform_web_requests(modelos, 8)
    for modelo, anos in years_dict[marca].items():
        print(marca, modelo)
        years_dict[marca][modelo] = {}
        for ano, cod in anos.items():

            years_dict[marca][modelo].update({ano : f'{modelos[modelo]}/{cod}'})
            
print('CONCLUIDO!')
        

with open('CarDealsML/Fipe.json' ,'w') as f:
    json.dump(years_dict, f)
    f.close()

