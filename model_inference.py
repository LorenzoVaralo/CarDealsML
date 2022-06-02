import numpy as np
import joblib
import pandas as pd
import json
import sqlite3
from sklearn.metrics import r2_score
import os


def path(*files):
    #return absolute path of file
    return os.path.join(os.path.abspath(os.path.dirname(__file__)), *files)

def unnormalize(arr, mean, std):
    return (arr * std) + mean

with open(path('models', 'best_model.txt')) as f:
    model_file = f.read()
    f.close()

#load best model
model = joblib.load( path('models', model_file) )

input_file = sorted(os.listdir( path('model_input') ))[-1]
print('input_file: ', input_file)
output_file = input_file.replace('dataNLP', 'inference')
print('output_file: ', output_file)


df_nlp = pd.read_csv(path('model_input', input_file))

pred = model.predict(df_nlp)

y_true = df_nlp['pricewrtfipe']

print(r2_score(y_true, pred))

df = pd.read_csv(path('clean_data', input_file.replace('dataNLP', 'cleanData')))

with open(path('col_jsons', 'standardParams_pricewrtfipe.json'), 'r') as j:
    #get parameters to reverse the Standard Normalization
    standard = json.load(j)
    mean = standard['mean']
    std = standard['std']

pred = unnormalize(pred, mean, std)
y_true = unnormalize(y_true, mean, std)

df['pricewrtfipe'] = y_true
df['error'] = y_true - pred
df['listId'] = df.listId.astype(str)

con = sqlite3.connect(path('database'))

links = pd.read_sql('SELECT olx_code, href FROM links;', con, index_col='olx_code').to_dict()

df['links'] = df['listId'].map(links['href'])

df[['links',
    'price',
    'vehicle_model',
    'regdate',
    'mileage',
    'motorpower',
    'valorFipe',
    'pricewrtfipe',
    'error']].sort_values(by='error').to_csv(path('inference', output_file))


