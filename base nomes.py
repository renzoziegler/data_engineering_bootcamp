import os
import pandas as pd


os.chdir('C:\\Users\\renzo.ziegler\\Documents\\FIAP')

nomes = pd.read_json('nomes.txt', encoding = 'UTF-8')

nomes1 = nomes

nomes2 = nomes
nomes2 = nomes2[0:365]

nomes2['nome_split'] = nomes2.nome.str.split()

for nome_split in nomes2.nome_split:
    for idx, item in enumerate(nome_split):
        if item in ('de', 'dos', 'da', 'do'):
            #print(item)
            nome_split.pop(idx)

for nome_split in nomes2.nome_split[330:]:
    if len(nome_split) > 3:
        nome_split[1] = nome_split[1][0]

nomes2 = nomes2.sample(frac=1).reset_index(drop=True)

nomes2.nome = nomes2.nome_split.str.join(' ')        

nomes2.nome = nomes2.nome.str[0:30]
nomes2[320:].nome = nomes2[320:].nome.str.replace('y', 'i')
nomes2.nome = nomes2.nome.str.replace('ç', 'c')
nomes2.nome = nomes2.nome.str.replace('ê', 'e')
nomes2.nome = nomes2.nome.str.replace('â', 'a')

nomes2 = nomes2.sample(frac=1).reset_index(drop=True)

nomes2.cpf = nomes2.cpf.astype(str)
nomes2.loc[300:, 'cpf'] = '00000000000'

nomes2 = nomes2.sample(frac=1).reset_index(drop=True)


nomes2.data_nasc = nomes2.data_nasc.str.replace('-','/')
nomes2[300:].data_nasc = '01/01/1900'

nomes2 = nomes2.sample(frac=1).reset_index(drop=True)

nomes2[340:].data_nasc = nomes2[340:].data_nasc.str[0:6] + '1900'

nomes2 = nomes2.sample(frac=1).reset_index(drop=True)

for idx, pessoa in nomes2[340:].iterrows():
    if int(pessoa.data_nasc[0:2]) < 12:
        nomes2.at[idx, 'data_nasc'] = pessoa.data_nasc[3:5] + '/' + pessoa.data_nasc[0:2] + '/' + pessoa.data_nasc[6:]

nomes2 = nomes2[['nome', 'data_nasc', 'cpf', 'tipo_sanguineo', 'peso', 'altura']]
nomes1 = nomes1[['nome', 'data_nasc', 'cpf', 'mae', 'celular', 'email', 'telefone_fixo']]

nome_gemeos2 = [{'nome' : 'Antonio Albuquerque Silva', 'data_nasc' : '24-07-1980', 'cpf' : '58762423819',
               'tipo_sanguineo' : 'A-', 'peso' : '80', 'altura' : '1,82'},
                {'nome' : 'Enzo Albuquerque Silva', 'data_nasc' : '19-01-2015', 'cpf' : '58762423819',
               'tipo_sanguineo' : 'A-', 'peso' : '14', 'altura' : '1,04'},
                {'nome' : 'Matheus Albuquerque Silva', 'data_nasc' : '19-01-2015', 'cpf' : '58762423819',
               'tipo_sanguineo' : 'A-', 'peso' : '13', 'altura' : '1,07'}]
nome_gemeos1 = [{'nome' : 'Antonio Albuquerque Silva', 'data_nasc' : '24-07-1980', 'cpf' : '58762423819',
               'mae' : 'Laura Albuquerque Cardoso', 'celular' : '11998970549', 'email' : 'antonio.silva@gmail.com', 'telefone_fixo' : '1135494656'},
                {'nome' : 'Enzo Albuquerque Silva', 'data_nasc' : '19-01-2015', 'cpf' : '58762423819',
               'mae' : 'Mariana Santos Albuquerque', 'celular' : '11998970549', 'email' : 'antonio.silva@gmail.com', 'telefone_fixo' : '1135494656'},
                {'nome' : 'Matheus Albuquerque Silva', 'data_nasc' : '19-01-2015', 'cpf' : '58762423819',
               'mae' : 'Mariana Santos Albuquerque', 'celular' : '11998970549', 'email' : 'antonio.silva@gmail.com', 'telefone_fixo' : '1135494656'}]
    
nomes1 = nomes1.append(nome_gemeos1)
nomes2 = nomes2.append(nome_gemeos2)

nomes2 = nomes2.sample(frac=1).reset_index(drop=True)
nomes1 = nomes1.sample(frac=1).reset_index(drop=True)

csv_temp = nomes1.to_csv('cadastro.csv', index = False)
csv_temp = nomes2.to_csv('dados_medicos.csv', index = False)
