import hashlib
import glob as gl
import numpy as np
import pandas as pd
from sympy import false

from nltk.tokenize import sent_tokenize
    
""" This program takes as a input dataset_noCleaned.csv, and it does the following:
    1. Generates a unique sentences id by encoding the method's signature of certain Class
    2. It tokenizes by sentence each comment
    3. When a comment has more than one sentence, it creates a new row in the dataframe with the same sentence id, for intance:
    comment = "Sets all cells to the state specified by values. values is required to have the form values[row][column] and 
                have exactly the same number of rows and columns as the receiver.  The values are copied. So subsequent changes 
                in values are not reflected in the matrix, and vice-versa."
    sent_tokenaizer = ['Sets all cells to the state specified by values.', 
                       'values is required to have the form values[row][column] and have exactly the same number of rows and columns as the receiver.', 
                       'The values are copied.', 
                       'So subsequent changes in values are not reflected in the matrix, and vice-versa.']
    dataFrame:
    sentenceID, other Columns, sentence
    9fa8dbc1ad9c7186a43212a8b7948650, ... , Sets all cells to the state specified by values.
    9fa8dbc1ad9c7186a43212a8b7948650, ... , values is required to have the form values[row][column] and have exactly the same number of rows and columns as the receiver.
    9fa8dbc1ad9c7186a43212a8b7948650, ... , The values are copied.
    9fa8dbc1ad9c7186a43212a8b7948650, ... , So subsequent changes in values are not reflected in the matrix, and vice-versa.

"""

# Generic method for savind info in csv files
def save_df_csv(df, name):
    df.to_csv(name + '.csv')  

# idGenerator method Creates an unique id by encoding the method's signature of certain Class  
def idGenerator(signature):
 
    # sentence_id = (hashlib.md5((row['signature']).encode('utf-8'))).hexdigest()
    # return sentence_id
    return (hashlib.md5((signature).encode('utf-8'))).hexdigest()

def sentTokenazer(df):
    # little example on how it look like a javadoc comment, and how look like the sentences when is tokenaized
    # text = "Sets all cells to the state specified by values. values is required to have the form values[row][column] and have exactly the same number of rows and columns as the receiver.  The values are copied. So subsequent changes in values are not reflected in the matrix, and vice-versa."
    # expected output :
    # ['Sets all cells to the state specified by values.', 'values is required to have the form values[row][column] and have exactly the same number of rows and columns as the receiver.', 'The values are copied.', 'So subsequent changes in values are not reflected in the matrix, and vice-versa.']
    aux = []
    for index, row in df.iterrows():

        # Here starts the processing in the comments
        comment = row['equivalence.comment']
        # calls sent_tokenize from nltk library for tokenizing the comment into sentences
        sentTokenize = sent_tokenize(comment)
        #this creates a list of dictionaries, it keeps the same key from the initial dataframe, and it adds
        #two new keys: sentenceID and sentece. Also, it adds new rows, each rows with a different sentence, 
        # if the row has the same sentence ID, it means that those sentence belogons to the same comment
        for sent in sentTokenize:
            auxDic = {
                'sentenceID': idGenerator(row['signature']),
                'library':row['library'],
                'jsonFileName':row['jsonFileName'],
                'signature':row['signature'],
                'name':row['name'],
                'targetClass':row['targetClass'],
                'equivalence.comment':row['equivalence.comment'],
                'equivalence.kind':row['equivalence.kind'],
                'equivalence.condition':row['equivalence.condition'],
                'sentence': sent
                }
            
            aux.append(auxDic)
    df_final = pd.DataFrame(aux, index=None)
    return(df_final)
    # save_df_csv(df_final, 'dataset_cleaned3')
    
def ds_statistics(dataNoCleaned, df, df_clean):
    libNames = ['colt', 'elastic', 'gs', 'guava', 'gwt', 
                'hibernate', 'jdk', 'math', 'sbes-guava', 'weka']
    aux = []
    for i in libNames:
        
        df_aux_noCleaned = dataNoCleaned.loc[dataNoCleaned['library'] == i]
        df_aux_df = df.loc[df['library'] == i]
        df_aux_clean = df_clean.loc[df_clean['library'] == i]
        
        main_df_aux = df_aux_df.dropna(subset=["equivalence.condition"]).reset_index()
        save_df_csv(main_df_aux, i)
        
        df_aux_noCleaned_value_cont = df_aux_noCleaned['targetClass'].value_counts()
        df_aux_df_value_cont = df_aux_df['targetClass'].value_counts()
       
        statisticsDic_noCleaned = {
            'libary': i,
            'Total_NumClasses': len(df_aux_noCleaned_value_cont),
            'Total_NumMeth': df_aux_noCleaned_value_cont.sum(),
            'Total_NumMeth_With_Comments': df_aux_df_value_cont.sum(),
            'Total_NumMeth_WithOut_Comments': df_aux_noCleaned['equivalence.comment'].isnull().sum(),
            'Total_NumSentences': len(df_aux_clean),
            'TMRs': df_aux_df['equivalence.condition'].value_counts().sum()
            }
        aux.append(statisticsDic_noCleaned)
    # print(pd.DataFrame(aux, index=None))
    save_df_csv(pd.DataFrame(aux, index=None), 'fullDataset_Info')
    
    for i in libNames:
        df_aux_df = df.loc[df['library'] == i] # does not have splited the sences
        df_aux_clean = df_clean.loc[df_clean['library'] == i] # the sentences are in different rows
        
        df_aux_df_value_count = df_aux_df['targetClass'].value_counts()

        listClass = df_aux_df_value_count.keys()
        aux = []
        
        for c in listClass:
            
            sentence_analisys = df_aux_clean.loc[df_aux_clean['targetClass'] == c]
            auxDic = {
                'Libary': i,
                'Class': c,
                'Total_NumMeth': df_aux_df_value_count[c],
                'Sentences_min':sentence_analisys['sentenceID'].value_counts().min(),
                'Sentences_avg':np.round(sentence_analisys['sentenceID'].value_counts().mean(),2) ,
                'Sentences_max':sentence_analisys['sentenceID'].value_counts().max(),
                'Total_sentences': sentence_analisys['sentenceID'].value_counts().sum(),
                'TMRs': sentence_analisys['equivalence.condition'].value_counts().sum()
            }
            
            aux.append(auxDic)
        
        save_df_csv(pd.DataFrame(aux, index=None), 'Info_' + i)
        print(pd.DataFrame(aux, index=None))
    # print(pd.DataFrame(aux, index=None))

dataNoCleaned = pd.read_csv('fullDataset.csv', index_col=0)

if dataNoCleaned['equivalence.comment'].isnull().values.any():
    df = dataNoCleaned.dropna(subset=["equivalence.comment"]).reset_index()
    df_clean = sentTokenazer(df)
    ds_statistics(dataNoCleaned, df, df_clean)
else:
    sentTokenazer(dataNoCleaned)
    
# Eliminating NaN values in equivalence.comments column, i.e., eliminates all the rows (clasess) which has not comments
# df_aux = dataNoCleaned.dropna(subset=["equivalence.comment"]).reset_index()




