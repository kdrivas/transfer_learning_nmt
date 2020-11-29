import re
import numpy
            
import os
from pathlib import Path
import pandas as pd
from sklearn.model_selection import train_test_split
import numpy as np

def read_txt(path):
    lines = []
    with open(path) as f:
        for line in f.read().split('\n'):
            if len(line):
                line = line.replace('*', '')
                line = line.replace('´', '\"')
                line = re.sub(r'([.¡!¿?;,:\"])', r' \1 ', line)
                line = ' '.join([w for w in line.split(' ')])
                line = re.sub(' +', ' ', line)
                line = line.strip(' ')
                line = line.strip(',')
                line = line.strip(':')
                line = line.replace('. .', '.')
                line = line.replace('. ,', '.')
                lines.append(line)
            
    return lines

def clean_accent(w):
    chars = list(w)
    replacement = []
    for i,c in enumerate(chars):
        if c == "á": 
            replacement.append((i,c))
            chars[i] = "a"
        elif c == "é": 
            replacement.append((i,c))
            chars[i] = "e"
        elif c == "í": 
            replacement.append((i,c))
            chars[i] = "i"
        elif c == "ó": 
            replacement.append((i,c))
            chars[i] = "o"
        elif c == "ú": 
            replacement.append((i,c))
            chars[i] = "u"
    w = "".join(chars)
    return w, replacement

def put_accent(syl, replacement):
    lens = [len(s) for s in syl]
    w = "".join(syl)
    chars = list(w)
    for (i,c) in replacement:
        chars[i] = c
    w = "".join(chars)
    syllables = []
    pos = 0
    for l in lens:
        syllables.append(w[pos:pos+l])
        pos+=l
    return syllables

def silabificar(palabraVC):
    sibilantes = ['m','n', 's', 'sh', 'x']
    silabas = []
    silaba = ""
    posActual = len(palabraVC) - 1
    if len(palabraVC) == 1:
        silabas.append(palabraVC[0][0])
        return silabas
    while posActual >= 0 and palabraVC:
        #Se revisa si es vocal
        if palabraVC[posActual][1] == 'V':
            silaba = palabraVC[posActual][0]
            del palabraVC[-1]
            #Se revisa las siguientes letras
            posActual = posActual - 1
            #Si es vocal alargada
            if palabraVC and (palabraVC[posActual][0] == silaba or
                              palabraVC[posActual][0] == tildar(silaba)):
                if (len(palabraVC) > 1):
                    silabas.insert(0, silaba)
                    silaba = ""
                    #Si es consonante
                else:
                    silabas.insert(0, silaba)
                    silaba = ""
            elif palabraVC and palabraVC[posActual][1] == 'C':          
                if (palabraVC[posActual][0] == 'u' or
                        palabraVC[posActual][0] == tildar('u') or palabraVC[posActual][0] == 'h'):                    
                    silabas.insert(0, silaba)
                    silaba = ""
                else:                   
                    #Se agrega a la silaba CV
                    silaba = palabraVC[posActual][0] + silaba  #C
                    posActual = posActual - 1
                    del palabraVC[-1]
                    silabas.insert(0, silaba)
                    silaba = ""
            else:
                if (len(palabraVC) < 2 and posActual != 0):  #es sílaba sóla
                    silabas.insert(0, silaba)
                    silaba = ""
                    posActual = posActual - 1
                    if (palabraVC):
                        del palabraVC[-1]
                else:
                    silabas.insert(0, silaba)
                    silaba = ""
        else:  #Se revisa si es consonante           
            if palabraVC[posActual][0] in sibilantes:
                silaba = palabraVC[posActual][0] + silaba
                posActual = posActual - 1
                if (palabraVC):
                    del palabraVC[-1]
                # Se ve primero CVC 
                if palabraVC and palabraVC[posActual][1] == 'V':
                    silaba = palabraVC[posActual][0] + silaba  #V
                    posActual = posActual - 1
                    del palabraVC[-1]
                    #silaba = VC
                    if len(palabraVC) and palabraVC[posActual][1] == 'C':
                        if palabraVC[posActual][0] == 'u' or palabraVC[
                                posActual][0] == tildar('u') or palabraVC[posActual][0] == 'h':
                            silabas.insert(0, silaba)
                            silaba = ""
                        else:
                            # es CVC
                            silaba = palabraVC[posActual][0] + silaba  #V
                            silabas.insert(0, silaba)
                            silaba = ""
                            posActual = posActual - 1
                            del palabraVC[-1]
                    else:  #es VC
                        silabas.insert(0, silaba)
                        silaba = ""
                else:
                    if palabraVC and (palabraVC[posActual][0] == 'u' or
                                      palabraVC[posActual][0] == tildar('u')):
                        silabas.insert(0, silaba)
                        silaba = ""
                        posActual = posActual - 1
                        del palabraVC[-1]
            else:
                if (palabraVC[posActual][0] == 'h'):
                    silaba = palabraVC[posActual][0]
                    posActual = posActual - 1
                    del palabraVC[-1]
                elif (palabraVC[posActual][0] == 'u' or
                        palabraVC[posActual][0] == tildar('u')):                   
                    silaba = palabraVC[posActual][0]
                    silabas.insert(0, silaba)
                    silaba = ""
                    posActual = posActual - 1
                    if (palabraVC):
                        del palabraVC[-1]
                else:
                    if len(silabas):
                        if palabraVC[posActual][0] == 't' and silabas[0][0] == 's':
                            silabas[0] = palabraVC[posActual][0] + silabas[0]
                        if palabraVC[posActual][0] == 'c' and silabas[0][0] == 'h':
                            silabas[0] = palabraVC[posActual][0] + silabas[0]
                        if palabraVC[posActual][0] == 's' and silabas[0][0] == 'h':                        
                            silabas[0] = palabraVC[posActual][0] + silabas[0]
                    posActual = posActual - 1
                    if (palabraVC):
                        del palabraVC[-1]
    return silabas

#Función que recibe una palabra y devuelve una lista con [letra: V o C]
def convertir_a_VC(palabra):
    estructura = []
    vocales = ['a', 'e', 'i', 'o']
    acentuado = ["á", "é", "í", "ó"]
    #acentuado = ['á', 'é', 'í', 'ó']
    especiales = ['ch', 'hu', 'sh', 'ts', 'qu']  #,'bu']
    posConsonanteEspecial = -1
    transformacion = {
        "ch": "1",
        "hu": "2",
        "sh": "3",
        "ts": "4",
        "qu": "5"
    }  #,"bu":"6"}
    for especial in especiales:
        if especial in palabra:
            palabra = palabra.replace(especial, transformacion[especial])
    for pos in range(0, len(palabra)):
        #Se pone +1 para que se pueda juntar los consonantes especiales
        if (posConsonanteEspecial != -1):
            if pos != posConsonanteEspecial + 1:
                if palabra[pos] in vocales or palabra[pos] in acentuado:
                    estructura.append([palabra[pos], "V"])
                else:
                    if palabra[pos] == " ":
                        estructura.append([palabra[pos], " "])
                    else:
                        if palabra[pos] == "-":
                            estructura.append([palabra[pos], "-"])
                        else:
                            estructura.append([palabra[pos], "C"])
            else:  #Aquí se escribe el consonante especial
                estructura[pos - 1] = [palabra[pos - 1] + palabra[pos], "C"]
        else:
            if palabra[pos] in vocales or palabra[pos] in acentuado:
                estructura.append([palabra[pos], "V"])
            else:
                if palabra[pos] == " ":
                    estructura.append([palabra[pos], " "])
                else:
                    if palabra[pos] == "-":
                        estructura.append([palabra[pos], "-"])
                    else:
                        estructura.append([palabra[pos], "C"])
    for silaba in estructura:
        silaba[0] = cambiar(silaba[0])
    #print(estructura)
    return estructura

def cambiar(silaba):
    if "1" in silaba:
        silaba = silaba.replace("1", "ch")
    elif "2" in silaba:
        silaba = silaba.replace("2", "hu")
    elif "3" in silaba:
        silaba = silaba.replace("3", "sh")
    elif "4" in silaba:
        silaba = silaba.replace("4", "ts")
    elif "5" in silaba:
        silaba = silaba.replace("5", "qu")
    else:
        silaba = silaba.replace("6", "bu")
    return silaba

def tildar(letra): #    acentuado = ["á", "é", "í", "ó"]
    if letra == "a":
        letra = "á"
    if letra == "e":
        letra = "é"
    if letra == "i":
        letra = "í"
    if letra == "o":
        letra = "ó"
    if letra == "u":
        letra = "ú"
    return letra

def syllabification(w):
    w, replacement = clean_accent(w)
    #print(w,replacement)
    syl = silabificar(convertir_a_VC(w))
    #print(syl)
    syl = put_accent(syl, replacement)
    return syl, w

def syllabification_pairs(pairs, path_out=None, path_word_to_syl_out=None):
    sentences = []
    
    for pair in pairs:
        line = pair[1]
        flag_error = False
        for w in line.strip().split():
            w, replacement = clean_accent(w)
            syl = silabificar(convertir_a_VC(w))
            if len("".join(syl)) < len(w):
                flag_error = True

        if not flag_error:
            sentences.append(pair)
    
    return sentences

def csv_to_txt(df, path, file):
    with open(path / (file + '.es'), 'w') as f:
        for line in df.iloc[:, 0]:
            print(line, file=f)
            
    with open(path / (file + '.shp'), 'w') as f:
        for line in df.iloc[:, 1]:
            print(line, file=f)

filter_pairs= True
base = Path('../data/translate/raw')

for folder in ['Religioso', 'Educativo']:
    folder_path = base / folder
    print(folder_path)
    es_all = []
    shi_all = []
    for partition in ['train', 'test', 'dev']:
        es = read_txt(folder_path / (partition + '.original.es'))
        shi = read_txt(folder_path / (partition + '.original.shi'))
        es_all.extend(es)
        shi_all.extend(shi)
    print(len(es_all), len(shi_all))
        
    sentences = list(zip(es_all, shi_all))
    if filter_pairs:
        sentences = syllabification_pairs(sentences)
    else:
        sentences = sentences    
    
    sentences = np.array(sentences)
    df = pd.DataFrame(sentences, columns=['es', 'shi'])
    print('Tamaño df:', df.shape)
    #df['es'] = sentences[:, 0]
    #df['shi'] = sentences[:, 1]
    df = df.drop_duplicates()
    df.to_csv(folder_path / 'all.txt', index=False, sep='\t', header=None)
    
    train, temp = train_test_split(df, test_size=0.1, random_state=0)
    test, dev = train_test_split(temp, test_size=0.5, random_state=0)
    train.to_csv(folder_path / 'train.txt', index=False, sep='\t', header=None)
    test.to_csv(folder_path / 'test.txt', index=False, sep='\t', header=None)
    dev.to_csv(folder_path / 'dev.txt', index=False, sep='\t', header=None)
    
    csv_to_txt(train, folder_path, 'train')
    csv_to_txt(test, folder_path, 'test')
    csv_to_txt(dev, folder_path, 'dev')
    
    print(len(train), len(dev), len(test), df.drop_duplicates().shape)