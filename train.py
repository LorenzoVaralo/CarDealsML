from sklearn.model_selection import train_test_split
from pycaret.regression import *
import pandas as pd
import os


def path(*files):
    DIRECTORY_PATH = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(DIRECTORY_PATH, *files)

input_data = sorted(os.listdir(path('model_input')))[-1]
print('input_data:   ', input_data)

output_model = input_data.replace('dataNLP_', 'model_').replace('.csv', '')
print('output_model: ', output_model)

df = pd.read_csv( path('model_input', input_data), index_col='Unnamed: 0')

X ,test = train_test_split(df, test_size=1000)

s = setup(X, target='pricewrtfipe',feature_selection=True, feature_selection_threshold=0.3, silent=True, html=False)

#best = compare_models(turbo=True, n_select=5, include=['lightgbm','br','ridge'])

model = create_model('lightgbm')

predict_model(model, data=test)

finalize_model(model)

save_model(model, path('models', output_model))

print("Model trained Succesfully!")
