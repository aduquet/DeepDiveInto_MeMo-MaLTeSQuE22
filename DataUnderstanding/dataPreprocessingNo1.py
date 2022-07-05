import pandas as pd
import glob as gl
import pathlib
import json
import os

""" This program orginise the json files from MeMo's 
repo and save it in a csv
"""

here_iam = str(pathlib.Path().absolute())
PathfileName = here_iam + '\\' + 'JsonFiles-From-MeMo-Repo'

def process(input_path, output_name):

    if os.path.exists(input_path):
        datasetsFiles = gl.glob(input_path + '\\*')

    dataKey = ['signature', 'name', 'containingClass', 'targetClass', 'isVarArgs', 'parameters', 'equivalence']
    dataSubKey_containingClass = ['qualifiedName', 'name', 'isArray']
    dataSubKey_equivalence = ['member', 'comment', 'kind', 'condition']

    aux = []
    for pathfile in datasetsFiles:
        fileName = pathfile.split('\\')[-1]
        # print(fileName)
        datasetJsonFiles = gl.glob(pathfile + '\\*')
        # print(datasetJsonFiles)
        for jsonFile in datasetJsonFiles:
            jsonFileName = jsonFile.split('\\')[-1]
            with open(jsonFile) as json_file:
                data = json.load(json_file)
                
                for i in data:
                    mainDic = {'library':fileName,
                            'jsonFileName':jsonFileName,
                            'signature':i['signature'],
                            'name':i['name'],
                            'targetClass':i['targetClass'],
                            'equivalence.comment':i['equivalence']['comment'],
                            'equivalence.kind':i['equivalence']['kind'],
                            'equivalence.condition':i['equivalence']['condition']}
                    
                    aux.append(mainDic)

    df = pd.DataFrame(aux, index=None)

    df.to_csv(output_name + '.csv')
    print('File saved in: \n' + here_iam + '\\' +output_name + '.csv')

if __name__ == '__main__':
    import click
    
    @click.command()
    @click.option('-i', '--input', 'input', help = 'Path input to JsonFiles')
    @click.option('-o', '--output', 'output', help = 'Name of the output file .csv')
    
    def main(input, output):
        
        if os.path.exists(input):
            process(input, output)
        
        else:
            try:
                ROOT_DIR = os.path.abspath(os.curdir)
                
                if os.path.exists(str(pathlib.Path().absolute()) + '\\' + input):
                    process(input, output)
                
                else:
                    PARENT_DIR = pathlib.Path(ROOT_DIR).parent
                    print('\n*** Reading Data ***')
                    inputPath = str(PARENT_DIR) + '\\' + input
                    process(inputPath, output)
            except print('\n ************* \n\n Check you path! it seems that the file\path does not exist \n\n ************* \n'):
                pass
    
        

main()