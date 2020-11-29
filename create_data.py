import os
import pyphen
import re
from pathlib import Path
from sklearn.model_selection import train_test_split
import unicodedata
import pandas as pd
import sentencepiece as spm

def read_txt(path):
    lines = []
    with open(path, 'r') as f:
        for line in f.read().split('\n'):
            if len(line):
                lines.append(line)
    
    return lines

def save_f(path, arr):
    cont = 0
    with open(path, 'w') as f:
        for l in arr:
            if len(l):
                print(l, file=f)

def read_multi_txt(path_1, path_2, use_max_sent=True, max_sent=5000):
    lines = []
    cont = 0
    with open(path_1, 'r') as f1, open(path_2, 'r') as f2:
        for line_1, line_2 in zip(f1.read().split('\n'), f2.read().split('\n')):
            if len(line_1) and len(line_2) and cont < max_sent:
                lines.append(line_1 + '\t' + line_2)
                if use_max_sent:
                    cont += 1    
    return lines

def save_word_transfer(status, word_dir, train_in, dev_in, test_in, train_out, dev_out, test_out, use_max_sent):
    os.makedirs(word_dir / status, exist_ok=True)

    train = read_multi_txt(train_in, train_out, use_max_sent, 5000)
    valid = read_multi_txt(dev_in, dev_out, use_max_sent, 500)
    test = read_multi_txt(test_in, test_out, use_max_sent, 500)

    save_f(word_dir / status / 'train.tsv', train)
    save_f(word_dir / status / f'train.{lang_in}', [line.split('\t')[0].strip() for line in train if len(line)])
    save_f(word_dir / status / f'train.{lang_out}', [line.split('\t')[1].strip() for line in train if len(line)])

    save_f(word_dir / status / 'test.tsv', test)
    save_f(word_dir / status / f'test.{lang_in}', [line.split('\t')[0].strip() for line in test if len(line)])
    save_f(word_dir / status / f'test.{lang_out}', [line.split('\t')[1].strip() for line in test if len(line)])

    save_f(word_dir / status / 'valid.tsv', valid)
    save_f(word_dir / status / f'valid.{lang_in}', [line.split('\t')[0].strip() for line in valid if len(line)])
    save_f(word_dir / status / f'valid.{lang_out}', [line.split('\t')[1].strip() for line in valid if len(line)])
    
def save_word_translation(word_dir, lang_in, lang_out):

    os.makedirs(word_dir, exist_ok=True)
        
    p_lines = []
    with open(file_path) as f:
        for line in f.read().split('\n'):
            line = re.sub(r'([.¡!¿?;,:])', r' \1 ', line)
            line = ' '.join([w for w in line.split(' ')])
            line = line.replace('  ', ' ')
            line = line.strip(' ')
            p_lines.append(line)

    train, temp = train_test_split(p_lines, test_size=0.1, random_state=0)
    valid, test = train_test_split(temp, test_size=0.5, random_state=0)

    save_f(word_dir / 'train.tsv', train)
    save_f(word_dir / f'train.{lang_in}', [line.split('\t')[1].strip() for line in train if len(line)])
    save_f(word_dir / f'train.{lang_out}', [line.split('\t')[0].strip() for line in train if len(line)])

    save_f(word_dir / 'test.tsv', test)
    save_f(word_dir / f'test.{lang_in}', [line.split('\t')[1].strip() for line in test if len(line)])
    save_f(word_dir / f'test.{lang_out}', [line.split('\t')[0].strip() for line in test if len(line)])

    save_f(word_dir / 'valid.tsv', valid)
    save_f(word_dir / f'valid.{lang_in}', [line.split('\t')[1].strip() for line in valid if len(line)])
    save_f(word_dir / f'valid.{lang_out}', [line.split('\t')[0].strip() for line in valid if len(line)])
    
def save_char_segments(word_dir, char_dir, list_status):
    
    for [lang_in, lang_out], status in list_status:
        os.makedirs(char_dir / status, exist_ok=True)
        for lang in [lang_out, lang_in]:
            spm.SentencePieceTrainer.Train(f'--input={word_dir / status}/train.{lang} --model_prefix=m --vocab_size=1000 --character_coverage=1.0 --model_type=char')   

            sp = spm.SentencePieceProcessor()
            sp.Load("m.model")
            for file in [f'train.{lang}', f'valid.{lang}', f'test.{lang}']:
                f_in = open(word_dir / status / file, 'r')
                f_out = open(char_dir / status / file, 'w')

                for line in f_in.read().split('\n'):
                    temp = []
                    for word in sp.EncodeAsPieces(line.replace('<unk>', '<unknown>')):
                        if str('\u2581') in word:
                            word = word.replace(str('\u2581'), '@@')
                        temp.append(word)
                    f_out.write(" ".join(temp) + "\n")

                f_in.close()
                f_out.close()

def save_bpe_segments(word_dir, prepro_dir, list_status, n_opers, dropout=False):
    
    command = 'cat'
    for [lang_in, lang_out], status in list_status:
        command += f' {word_dir/status}/train.{lang_in} {word_dir/status}/valid.{lang_in}'
        command += f' {word_dir/status}/train.{lang_out} {word_dir/status}/valid.{lang_out}'
        
    os.system(command + f' > {word_dir}/all.txt')  
    
    for oper in n_opers:
        bpe_dir = prepro_dir / (f'bpe_drop_{oper}' if dropout else f'bpe_{oper}')
        os.makedirs(bpe_dir, exist_ok=True)
        os.system(f'cat {word_dir}/all.txt | subword-nmt learn-bpe -s {oper} -o {bpe_dir}/codes.all')
        
        for [lang_in, lang_out], status in list_status:
            os.makedirs(bpe_dir / status, exist_ok=True)

            for lang in [lang_out, lang_in]:
                os.system(f'subword-nmt apply-bpe --dropout {0.1 if dropout else 0} -c {bpe_dir}/codes.all < {word_dir}/all.{lang} | subword-nmt get-vocab > {bpe_dir}/vocab.{lang}')

                os.system(f'subword-nmt apply-bpe --dropout {0.1 if dropout else 0} -c {bpe_dir}/codes.all < {word_dir/status}/test.{lang} > {bpe_dir/status}/test.bpe.{lang}')
                os.system(f'subword-nmt apply-bpe --dropout {0.1 if dropout else 0} -c {bpe_dir}/codes.all < {word_dir/status}/train.{lang} > {bpe_dir/status}/train.bpe.{lang}')
                os.system(f'subword-nmt apply-bpe --dropout {0.1 if dropout else 0} -c {bpe_dir}/codes.all < {word_dir/status}/valid.{lang} > {bpe_dir/status}/valid.bpe.{lang}')

            for corpus in ['valid', 'test', 'train']:
                l1 = open(f'{bpe_dir/status}/{corpus}.bpe.{lang_out}', 'r').read().split('\n')
                l2 = open(f'{bpe_dir/status}/{corpus}.bpe.{lang_in}', 'r').read().split('\n')
                save_f(bpe_dir /status / f'{corpus}.{lang_out}', l1)
                save_f(bpe_dir /status / f'{corpus}.{lang_in}', l2)            

def save_segmentation(prepro_dir, list_status, n_opers=[5000]):
    print('... Running bpe')
    save_bpe_segments(prepro_dir / 'word', prepro_dir, list_status, n_opers=n_opers)    
    #save_bpe_segments(prepro_dir / 'word', prepro_dir, lang_in, lang_out, n_opers=n_opers, dropout=True)
    print('... Running char')
    save_char_segments(prepro_dir / 'word', prepro_dir / 'char', list_status)                

print('Creating transfer data')
base_dir = Path('data')

raw_dir = base_dir / 'transfer/raw'
prepro_dir = base_dir / 'transfer/preprocessed'

for lang in ['es', 'en']:
    lang_dir = raw_dir / f'splits.{lang}'
    pair_langs = read_txt(lang_dir / f'all.train.{lang}-ll.lang-pairs')
    pair_langs = list(set(pair_langs))
    for pair_lang in pair_langs:
        if 'shp' not in pair_lang:
            lang_o, lang_i = pair_lang.split(' ')
            for [lang_in, lang_out], status in zip([[lang_i, lang_o], [lang_i, 'shp']], ['pretraining', 'training']):
                train_in = lang_dir / 'train' / f'{lang_in}-{lang_out}.train.{lang_in}'
                dev_in = lang_dir / 'dev' / f'{lang_in}-{lang_out}.dev.{lang_in}'
                test_in = lang_dir / 'test' / f'{lang_in}-{lang_out}.test.{lang_in}'

                train_out = lang_dir / 'train' / f'{lang_in}-{lang_out}.train.{lang_out}'
                dev_out = lang_dir / 'dev' / f'{lang_in}-{lang_out}.dev.{lang_out}'
                test_out = lang_dir / 'test' / f'{lang_in}-{lang_out}.test.{lang_out}'

                if 'shp' in pair_lang:
                    use_max_sent = False
                else:
                    use_max_sent = True

                segment_dir = prepro_dir / f'splits.{lang}' / f'{lang_i}-{lang_o}'
                save_word_transfer(status, segment_dir / 'word',\
                                   train_in, dev_in, test_in,\
                                   train_out, dev_out, test_out,\
                                   use_max_sent)
                
            save_segmentation(segment_dir, list(zip([[lang_i,lang_o],[lang_i,'shp']],['pretraining', 'training'])), [5000, 10000])
            

print('Creating translation data')

raw_dir = base_dir / 'translate' / 'raw'
prepro_dir = base_dir / 'translate' / 'preprocessed'

for dir_temp in os.listdir(raw_dir):
    lang_dir = raw_dir / dir_temp
    if os.path.isdir(lang_dir):
        prepro_lang_dir = prepro_dir / dir_temp
        file_path = lang_dir / 'all.txt'#lang_dir / (os.listdir(lang_dir)[0] if 'txt' in os.listdir(lang_dir)[0] else os.listdir(lang_dir)[1])
        lang_in = 'es'
        lang_out = 'shp'
        save_word_translation(prepro_lang_dir / 'word', lang_in, lang_out)
        save_segmentation(prepro_lang_dir, [[[lang_in,lang_out],'']], list(range(1000, 11000, 1000)))

for lang in ['es', 'en']:
    lang_dir = raw_dir / f'splits.{lang}'
    pair_langs = read_txt(lang_dir / f'all.train.{lang}-ll.lang-pairs')
    pair_langs = list(set(pair_langs))
    for pair_lang in pair_langs:
        if 'shp' in pair_lang:
            lang_out, lang_in = pair_lang.split(' ')
            save_word_translation(prepro_dir / pair_lang.replace(' ','_') / 'word', lang_in, lang_out)
            save_segmentation(prepro_dir / pair_lang.replace(' ','_'), [[[lang_in,lang_out],'']], list(range(1000, 11000, 1000)))