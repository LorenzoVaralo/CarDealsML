import pandas as pd
import numpy as np
from pycaret.regression import *
import joblib
import os
import json
from datetime import datetime
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error

'''compare all models in the models folder by r2_score, and save the best model into a txt file'''

def path(*files):
    DIRECTORY_PATH = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(DIRECTORY_PATH, *files)


input_data = sorted(os.listdir(path('model_input')))[-1]
print('input_data:   ', input_data)

df = pd.read_csv(path('model_input', input_data), index_col='Unnamed: 0')


test = df.sample(5000)

model_list = os.listdir(path('models'))
model_list.remove('best_model.txt')
print(model_list)

y_true = test['pricewrtfipe']

best_model = {'model': '' , 'r2': 0.0}

for m in model_list:
    start = datetime.now()

    model = joblib.load(path('models' , m))
    print('       ', m)
    try:
        pred = model.predict(test)
    except:
        print(f'Model {m} failed to predict')
        continue
    r2 = r2_score(y_true, pred)
    mse = mean_squared_error(y_true, pred)
    mae = mean_absolute_error(y_true, pred)
    
    if r2 > best_model['r2']:
        best_model['model'] = m
        best_model['r2'] = r2
    
    print('R2 Score: ',  r2)
    print('MSE Score: ', mse)
    print('MAE Score: ', mae)
    
    print(datetime.now() -start, '\n')
    
print('Best Model: ', best_model['model'])
print("Best Model's R2: ", best_model['r2'])

with open( path('models', 'best_model.txt'), 'w') as f:
    f.write(best_model['model'])
    
    print(f'\n\nSaved model {best_model["model"]} as the best model, with R2 score of: {best_model["r2"]}')
    f.close()




