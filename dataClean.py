from datetime import datetime
start = datetime.now()
import ast
import json
import os
import re
import sqlite3
from unicodedata import normalize
import matplotlib.pyplot as plt
import nltk
import numpy as np
import pandas as pd
import regex
import requests


def valorFipe(row):
    cod = row[0]
    ano = int(row[1][:4])
    anos = fipe.AnoModelo.loc[fipe.CodigoFipe == cod].values
    if anos.size == 0:
        return None
    #ano = anos[np.abs(anos - ano).argmin()] #: Ano mais próximo
    return fipe.Valor.loc[(fipe.CodigoFipe == cod)&(fipe.AnoModelo == ano)].values.any()

def treat_nones(dfo, col):
    mode_by_version = dfo.groupby('vehicle_model')[col].agg(pd.Series.mode)
    dfo.loc[dfo[col].isna(), col] = dfo.loc[dfo[col].isna(), 'vehicle_model'].apply(lambda x: mode_by_version[x])

    dfo.loc[:, col] = dfo[col].apply(lambda x: x if isinstance(x, str) else x.any())
    # str -> False ; False -> True
    dfo.loc[~dfo[col].astype(bool), col] = dfo.brand.loc[~df[col].astype(bool)].map(df.groupby('brand')[col].agg(pd.Series.mode))
    dfo.loc[:, col] = dfo[col].apply(lambda x: x if isinstance(x, str) else None)
    dfo.dropna(inplace=True, subset=[col])
    return dfo

def gearbox_in_name(dfo, lista, gear):
    for term in lista:
        dfo.loc[(df.vehicle_model.str.endswith(term))&(df.gearbox != gear), 'gearbox'] = gear
    return dfo


#limit = 'LIMIT 10000'
limit = 'LIMIT 20000'

DIRECTORY_PATH = os.path.abspath(os.path.dirname(__file__))

con = sqlite3.connect(os.path.join(DIRECTORY_PATH, 'database'))
curr = con.cursor()

df = pd.read_sql(f'SELECT * FROM CarInfoRaw {limit};', con, index_col='Id')
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

df['CodFipe'] = [fipe['CodigoFipe'].loc[fipe.Modelo == x.replace('/', '\/')].values.any() for x in df['versao'].replace(conv_list)]

df['valorFipe'] = df[['CodFipe', 'regdate']].apply(valorFipe, axis=1)

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

print(df.isna().sum())

df = treat_nones(df, 'car_steering')

df = treat_nones(df, 'doors')

df.loc[:, 'doors'] = df.doors.apply(lambda x: 1 if x == '4 portas' else 0)

print(df.isna().sum())

df = treat_nones(df, 'fuel')
#Se existe "DIE" no nome do carro, é diesel
df.loc[(df.vehicle_model.str.find('DIE') > -1)&(df.fuel != 'Diesel'), 'fuel'] = 'Diesel'
#Se existe "FLEX" no nome do carro, é Flex
df.loc[(df.vehicle_model.str.find('FLEX') > -1)&(df.fuel != 'Flex'), 'fuel'] = 'Flex'
#Se não é Flex, Diesel ou Gasolina, é considerado "Outro"
df.loc[(df.fuel != 'Flex')&(df.fuel != 'Gasolina')&(df.fuel != 'Diesel'), 'fuel'] = 'Outro'

df.to_csv('Dataframe.csv')

print(df.__len__())
print(datetime.now() - start)