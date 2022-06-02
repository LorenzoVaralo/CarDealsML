from datetime import datetime
start = datetime.now()
import json
import os
import time
import sqlite3
import argparse
import pandas as pd

DIRECTORY_PATH = os.path.abspath(os.path.dirname(__file__))

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--inference', type=bool, default=False)
arg = parser.parse_args()

inference = arg.inference
if inference:
    print('Inference Mode')

def valorFipe(row):
    cod = row[0] #coluna CodFipe
    ano = int(row[1][:4]) # ano do carro, pegar 4 primeiros caracteres
    anos = fipe.AnoModelo.loc[fipe.CodigoFipe == cod].values
    if anos.size == 0:
        return None
    #ano = anos[np.abs(anos - ano).argmin()] #: Ano mais próximo
    return fipe.Valor.loc[(fipe.CodigoFipe == cod)&(fipe.AnoModelo == ano)].values.any()


def treat_nones(dfo, col):
    json_path = os.path.join(DIRECTORY_PATH, 'col_jsons', f'{col}.json')
    
    with open(json_path) as f:
        mode_dict = json.load(f)
        f.close()

    #Os que não estão em mode_dict, agrupar por modelo e pegar [col] mais frequente de cada modelo:
    # Se um modelo empatar em frequencia em valores de [col], e retornar uma lista, pegar o primeiro valor
    # Se um modelo não apresentar em nenhum momento um valor de [col], agrupar pela marca
    # Se pela marca empatar em frequencia em valores de [col] (Extremamente improvável), drop row 
    new_modes = df.loc[~df.vehicle_model.isin(mode_dict.keys())].groupby('vehicle_model')[col].agg(pd.Series.mode)
    #Os que não são nulos, retornará em formato string ou none
    # String -> String
    # List -> List[0] -> String
    # None -> False
    new_modes_dict = new_modes.apply(lambda x: x if isinstance(x, str) else x.any()).loc[new_modes.notna()].to_dict()
    for k,v in new_modes_dict.items():
        mode_dict[k] = v
    
    dfo.loc[:, col] = dfo.vehicle_model.map(mode_dict)
    
    #Se não tiver valores suficientes, agrupar por marca e pegar o valor de [col] para preencher na's.
    dfo.loc[dfo[col].isna(), col] = dfo.brand.loc[dfo[col].isna()].map(dfo.groupby('brand')[col].agg(pd.Series.mode))
    dfo.loc[:, col] = dfo[col].apply(lambda x: x if isinstance(x, str) else None)#Não aturar listas
    dfo.dropna(inplace=True, subset=[col])
    
    if len(new_modes_dict) > 0: # Se houve mudanças, reescrever json
        with open(json_path, 'w') as f:
            json.dump(dict(mode_dict), f)
            f.close()  
    return dfo

def gearbox_in_name(dfo, lista, gear):
    for term in lista:
        dfo.loc[(df.vehicle_model.str.endswith(term))&(df.gearbox != gear), 'gearbox'] = gear
    return dfo


con = sqlite3.connect(os.path.join(DIRECTORY_PATH, 'database'))

if inference:
    with open(os.path.join(DIRECTORY_PATH, 'logs', 'inference_num.log'), 'r') as f:
        num = int(f.read())
    
    df = pd.read_sql(f'SELECT * FROM CarInfoRaw LIMIT {num};', con, index_col='Id')
else:
    df = pd.read_sql(f'SELECT * FROM CarInfoRaw;', con, index_col='Id')

fipe = pd.read_sql('SELECT * FROM fipe;', con)
fipe.Modelo = fipe.Modelo.str.upper()

with open(os.path.join(DIRECTORY_PATH, 'Convertion_list.json'), 'br') as f:
    conv_list = json.load(f)
    f.close()

print('files loaded')

useless_cols = ['mainCategory', 
                'subCategory', 
                'mainCategoryID', 
                'subCategoryID', 
                'estado', 
                'category', 
                'sellerName', 
                'adDate', 
                'ddd', 
                'region', 
                'carcolor', 
                'end_tag', 
                'dono', 
                'exchange', 
                'financial']

df = df.drop(useless_cols, axis='columns')
df = df.loc[df['versao'].notna()]

df.mileage = df.mileage.astype(int)
df = df.loc[(df.mileage < 350000)&(df.price != '')]

df.price = df.price.astype(int)
df = df.loc[(df.price >= 1500)&(df.price < 500000)]

print('data clean 1')

df = treat_nones(df, 'motorpower')

df.versao = df.versao.str.replace('.', '', regex=False)
fipe.Modelo = fipe.Modelo.str.replace('.','', regex=False)


start1 = datetime.now()
df['CodFipe'] = [fipe['CodigoFipe'].loc[fipe.Modelo == x.replace('/', '\/')].values.any() for x in df['versao'].replace(conv_list)]

print(datetime.now() - start1)#3:42

start2 = datetime.now()
df['valorFipe'] = df[['CodFipe', 'regdate']].apply(valorFipe, axis=1)

print(datetime.now() - start2)#5:12


df.dropna(inplace=True, subset=['valorFipe'])
df.loc[:,'valorFipe'] = df['valorFipe'].astype(int)
df = df.loc[df.valorFipe >100]

print('data clean 2')

auto = ['AUT','AUT.','AUTOMATICO']

for automatico in auto:
    df.loc[(df.vehicle_model.str.endswith(automatico))&(df.gearbox != 'Automático'), 'gearbox'] = 'Automático'

df = gearbox_in_name(df, ['MEC', 'MEC.'], 'Manual')
df = gearbox_in_name(df, ['AUT', 'AUT.', 'AUTOMATICO'], 'Automático')

df = treat_nones(df, 'gearbox')
df.loc[df.gearbox.str.find('Semi-Automático')>-1, 'gearbox'] = 'Automático'

df = treat_nones(df, 'car_steering')
df = treat_nones(df, 'doors')

df.loc[:, 'doors'] = df.doors.apply(lambda x: 1 if x == '4 portas' else 0)

df = treat_nones(df, 'fuel')
#Se existe "DIE" no nome do carro, é diesel
df.loc[(df.vehicle_model.str.find('DIE') > -1)&(df.fuel != 'Diesel'), 'fuel'] = 'Diesel'
#Se existe "FLEX" no nome do carro, é Flex
df.loc[(df.vehicle_model.str.find('FLEX') > -1)&(df.fuel != 'Flex'), 'fuel'] = 'Flex'
#Se não é Flex, Diesel ou Gasolina, é considerado "Outro"
df.loc[(df.fuel != 'Flex')&(df.fuel != 'Gasolina')&(df.fuel != 'Diesel'), 'fuel'] = 'Outro'

#segs desde inicio de 2022
segs = int(time.time()) - 1640995200

df.to_csv(os.path.join(DIRECTORY_PATH, 'clean_data', f'cleanData_{segs}.csv'))

print(df.__len__()) #em média 10.4% dos dados originais são descartados.
print(datetime.now() - start)
print('output file: ', f'cleanData_{segs}.csv')