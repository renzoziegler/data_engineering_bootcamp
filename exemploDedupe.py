import dedupe
import os
import re
import collections
import time
import logging
import optparse
import pandas as pd
import csv

os.chdir('C:\\Users\\renzo.ziegler\\Documents\\FIAP\\BootCamp Eng Dados')

from unidecode import unidecode

settings_file = 'convenio_settings.txt'
training_file = 'convenio_training.json'

def preProcess(column):
#
    try : # python 2/3 string differences
        column = column.decode('utf8')
    except AttributeError:
        pass
    column = unidecode(column)
    column = re.sub('  +', ' ', column)
    column = re.sub('\n', ' ', column)
    column = column.strip().strip('"').strip("'").lower().strip()
    if not column:
        column = None
    return column

def readData(filename):
#
    data_d = {}
    with open(filename, encoding = 'utf-8') as f:
        reader = csv.DictReader(f, delimiter = ';')
        i = 0
        for row in reader:
            clean_row = [(preProcess(k), preProcess(v)) for (k, v) in row.items()]
            #row_id = int(row['Id'])
            #data_d[row_id] = dict(clean_row)
            data_d[i] = dict(clean_row)
            i = i+1
    return data_d

print('importing data ...')
data_d = readData('convenios_FULL.csv')

if os.path.exists(settings_file):
    print('reading from {}'.format(settings_file))
    with open(settings_file) as sf :
        deduper = dedupe.StaticDedupe(sf)

else:
    fields = [
        {'field' : 'cod_ans', 'type': 'String', 'has missing' : True},
        {'field' : 'convenio', 'type': 'String'},
        {'field' : 'cnpj', 'type': 'String', 'has missing' : True}
        ]

    deduper = dedupe.Dedupe(fields)

    deduper.sample(data_d, 15000)

    if os.path.exists(training_file):
        print('reading labeled examples from {}'.format(training_file))
        with open(training_file) as tf :
            deduper.readTraining(tf)

    print('starting active labeling...')

    dedupe.consoleLabel(deduper)

    deduper.train()
    
    with open(training_file, 'w') as tf :
        deduper.writeTraining(tf)

    with open(settings_file, 'wb') as sf :
        deduper.writeSettings(sf)

print('blocking...')

threshold = deduper.threshold(data_d, recall_weight=2)

print('clustering...')
clustered_dupes = deduper.match(data_d, threshold)

print('# duplicate sets: {}'.format(len(clustered_dupes)))
      
cluster_membership = {}
cluster_id = 0
for (cluster_id, cluster) in enumerate(clustered_dupes):
    id_set, scores = cluster
    cluster_d = [data_d[c] for c in id_set]
    canonical_rep = dedupe.canonicalize(cluster_d)
    for record_id, score in zip(id_set, scores):
        cluster_membership[record_id] = {
            "cluster id" : cluster_id,
            "canonical representation" : canonical_rep,
            "confidence": score
        }

singleton_id = cluster_id + 1

with open('convenio_dedupe.csv', 'w', encoding = 'utf-8') as f_output, open('convenios_FULL.csv', encoding='utf-8') as f_input:
    writer = csv.writer(f_output)
    reader = csv.reader(f_input)

    heading_row = next(reader)
    heading_row.insert(0, 'confidence_score')
    heading_row.insert(0, 'Cluster ID')
    canonical_keys = canonical_rep.keys()
    for key in canonical_keys:
        heading_row.append('canonical_' + key)

    writer.writerow(heading_row)
    i = 0
    for row in reader:
        row_id = i #int(row[0])
        if row_id in cluster_membership:
            cluster_id = cluster_membership[row_id]["cluster id"]
            canonical_rep = cluster_membership[row_id]["canonical representation"]
            row.insert(0, cluster_membership[row_id]['confidence'])
            row.insert(0, cluster_id)
            for key in canonical_keys:
                row.append(canonical_rep[key].encode('utf8'))
        else:
            row.insert(0, None)
            row.insert(0, singleton_id)
            singleton_id += 1
            for key in canonical_keys:
                row.append(None)
        writer.writerow(row)
        i=i+1
