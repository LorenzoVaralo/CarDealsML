from datetime import datetime
start = datetime.now()
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.feature_extraction.text import *
from nltk.stem import RSLPStemmer
import pandas as pd
import numpy as np
import argparse
import pickle
import regex
import json
import re
import os

import nltk
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)
nltk.download('rslp', quiet=True)


def path(*files):
    DIRECTORY_PATH = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(DIRECTORY_PATH, *files)

def normalize_chars(texto):
    texto = texto.lower()
    texto = texto.replace('&lt;', ' ').replace('br&gt;', ' ')
    tokens = nltk.tokenize.word_tokenize(texto, language='portuguese', )
    texto =  ' '.join([stemmer.stem(x) for x in tokens if x not in sw])
    #texto = ''.join(char for char in unicodedata.normalize('NFD', texto) if unicodedata.category(char) != 'Mn')
    texto = re.sub('4\s?x\s?4', ' QUATROPORQUATRO ', texto)#[4x4, 4 x 4] -> QUATROPORQUATRO
    texto = re.sub('[3-9]\d\d\d.?\d\d\d\d', ' NUMTELEFONE ', texto)
    texto = re.sub('w(ha|a).+?\s', ' WHATS ', texto)#[whats, watt, whatsapp, wats] -> WHATS
    texto = re.sub('www\..+?(\.com\.br|\.com)', ' URL ', texto)
    texto = pattern.sub(' ', texto)
    return re.sub('\s+', ' ', texto).strip()

def StandardScale(series):
    # Calculate and save params if fit=True, else load and use saved params
    json_path = path('col_jsons', f"standardParams_{series.name}.json")
    
    if fit:
        mean = series.mean()
        std = series.std()
        with open(json_path, 'w') as f:
            json.dump({"mean" :mean, "std": std}, f)
    else:
        with open(json_path, 'rb') as f:
            params = json.load(f)
        mean = params['mean']
        std = params['std']
    
    return (series - mean) / std
    

def normalize_number_cols(df, gausify=True):
    data = df.copy()
    if gausify:
        data['regdate'] = data.regdate.apply(lambda x: np.log1p(data.regdate.max() - x))
        data['mileage'] = data.mileage.apply(np.sqrt)
    
    data['regdate'] = StandardScale(data['regdate'])
    data['mileage'] = StandardScale(data['mileage'])
    data['pricewrtfipe'] = StandardScale(data['pricewrtfipe'])
    return data


def main():
    input_file = sorted(os.listdir( path('clean_data') ))[-1]
    print('input file: ', input_file)
    output_file = input_file.replace('cleanData', 'dataNLP')
    print('output file: ', output_file)
    
    df = pd.read_csv(path('clean_data', input_file))
    desc = df.addesc
    
    desc = desc.apply(normalize_chars)

    if fit:
        tfidfVect = TfidfVectorizer(max_features=1000, strip_accents='unicode', dtype=np.float32)
        vectorizer = tfidfVect.fit(desc)
        
        with open(path('TfIdf_fit.pkl'), 'wb') as f:
            pickle.dump(vectorizer, f) #Save fitted Tfidf
        
    else:
        with open(path('TfIdf_fit.pkl'), 'rb') as f:
            vectorizer = pickle.load(f)
    
    TfIdf = vectorizer.transform(desc).toarray()

    vocab = vectorizer.get_feature_names()
    vocab = ['word_'+w for w in vocab]#prefixo "word_" para cada palavra

    df = df[['gearbox','regdate','mileage','motorpower','fuel','car_steering','doors', 'price', 'valorFipe']]

    df['pricewrtfipe'] = (df.loc[:,'price']/df.loc[:,'valorFipe'])
    df.drop(['price','valorFipe'], axis='columns', inplace=True)

    df = pd.get_dummies(df)
    if 'motorpower_1.7' in df.columns:
        del df['motorpower_1.7']
    if 'motorpower_1.9' in df.columns:
        del df['motorpower_1.9']
        
    df = normalize_number_cols(df)

    df = pd.concat((df['pricewrtfipe'], df.drop('pricewrtfipe', axis='columns'), pd.DataFrame(TfIdf, columns=vocab)), axis=1)

    df.to_csv( path('model_input', output_file) )
    
parser = argparse.ArgumentParser()
parser.add_argument('-f','--fit', default=False, type=bool)

args = parser.parse_args()

sw = nltk.corpus.stopwords.words('portuguese')
sw.remove('sem')
sw.remove('nem')

stemmer = RSLPStemmer()
pattern = regex.compile(r'[^\p{L}]+', re.UNICODE)

fit = bool(args.fit)
if not fit:
    print('Inference Mode.')
main()
print(datetime.now() - start)