import os
import pandas as pd
from fuzzywuzzy import fuzz

os.chdir('C:\\Users\\renzo.ziegler\\Documents\\FIAP\\BootCamp Eng Dados')

cadastro = pd.read_csv('cadastro.csv')
dados_medicos = pd.read_csv('dados_medicos.csv')

#Análise Exploratória
print(cadastro.shape) #393 regitros
print(dados_medicos.shape) #368 registros

print(cadastro.columns) #'nome', 'data_nasc', 'cpf', 'mae', 'celular', 'email', 'telefone_fixo'
print(dados_medicos.columns) #'nome', 'data_nasc', 'cpf', 'tipo_sanguineo', 'peso', 'altura'

print(cadastro.iloc[0])
print(dados_medicos.iloc[0])

print(cadastro.nome)
print(dados_medicos.nome)

print(cadastro.dtypes)
print(dados_medicos.dtypes)

#Temos no máximo 368 matches possíveis
#E temos 144.624 possíveis combinações (393 x 368)

#Pré-processamento
#Tamanhos dos campos
#Nome: Quebrar em nome e sobrenomes??
cadastro['nome_array'] = cadastro.nome.str.split()
cadastro['primeiro_nome'] = cadastro.nome_array.str[0]
cadastro['sobrenome'] = cadastro.nome_array.str[-1]

dados_medicos['nome_array'] = dados_medicos.nome.str.split()
dados_medicos['primeiro_nome'] = dados_medicos.nome_array.str[0]
dados_medicos['sobrenome'] = dados_medicos.nome_array.str[-1]

#CPF: Tem delimitador? está como tipo número ou tipo string? Tamanho 11 caracteres?
cadastro.cpf = cadastro.cpf.astype(str).apply(lambda x: x.zfill(11))
dados_medicos.cpf = dados_medicos.cpf.astype(str).apply(lambda x: x.zfill(11))

#Data Nascimento: Está como data?
cadastro.data_nasc = pd.to_datetime(cadastro.data_nasc, format = '%d-%m-%Y')
#dados_medicos.data_nasc = pd.to_datetime(dados_medicos.data_nasc, format = '%d/%m/%Y')
dados_medicos.data_nasc = pd.to_datetime(dados_medicos.data_nasc.str.replace('/','-'), format = '%d-%m-%Y')

cadastro['nasc_ano'] = cadastro.data_nasc.apply(lambda x : x.year)
cadastro['nasc_mes'] = cadastro.data_nasc.apply(lambda x : x.month)
cadastro['nasc_dia'] = cadastro.data_nasc.apply(lambda x : x.day)

dados_medicos['nasc_ano'] = dados_medicos.data_nasc.apply(lambda x : x.year)
dados_medicos['nasc_mes'] = dados_medicos.data_nasc.apply(lambda x : x.month)
dados_medicos['nasc_dia'] = dados_medicos.data_nasc.apply(lambda x : x.day)

#Altura como número?
dados_medicos.altura = dados_medicos.altura.str.replace(',','.').astype(float)

#Peso como número? OK

#Indexação

#mês de nascimento
cadastro.groupby('nasc_mes').size()
dados_medicos.groupby('nasc_mes').size() #Muitas pessoas com nascimento em 1900
dados_medicos[dados_medicos['nasc_mes'] == 1]['data_nasc'].sort_values(ascending = False)

blocos = pd.concat([cadastro.groupby('nasc_mes').size(), dados_medicos.groupby('nasc_mes').size()], axis = 1)
blocos.columns = ['cadastro', 'dados_medicos']
print(sum(blocos.cadastro * blocos.dados_medicos)) #12.254 ao invés de 144.624

dados_medicos[dados_medicos['data_nasc'] == '1900-01-01']

cadastro['cpf_0'] = cadastro.cpf.str[0]
dados_medicos['cpf_0'] = dados_medicos.cpf.str[0]
cadastro.groupby('cpf_0').size()
dados_medicos.groupby('cpf_0').size()

blocos_cpf = pd.concat([cadastro.groupby('cpf_0').size(), dados_medicos.groupby('cpf_0').size()], axis = 1)
blocos_cpf.columns = ['cadastro', 'dados_medicos']
print(sum(blocos_cpf.cadastro * blocos_cpf.dados_medicos)) #14.862 ao invés de 144.624

cadastro_blocos = {}
dados_medicos_blocos = {}

for i in range(10):
    cadastro_blocos[i] = cadastro[cadastro['cpf_0'].astype(int) == i]
    dados_medicos_blocos[i] = dados_medicos[dados_medicos['cpf_0'].astype(int) == i]

#Comparação par a par
def comparaRegistros(registro1, registro2):
    #Dictionary com similaridades
    sim = {}
    #Compara o CPF - exatamente igual
    if registro1['cpf'] == registro2['cpf']:
        sim['cpf'] = 1
    else:
        sim['cpf'] = 0
    
    #Compara Data de Nascimento - exatamente igual
    if registro1['data_nasc'] == registro2['data_nasc']:
        sim['data_nasc'] = 1
    elif (registro1['nasc_ano'] == registro2['nasc_ano']) and (registro1['nasc_mes'] == registro2['nasc_dia']) and (registro1['nasc_dia'] == registro2['nasc_mes']):
        #Mês e dia trocado!!
        sim['data_nasc'] = 1
    else:
        sim['data_nasc'] = 0

    #Compara Nomes - similaridade de strings:
    if registro1['nome'] == registro2['nome']:
        sim['nome'] = 1
    else:
        sim['nome'] = fuzz.token_sort_ratio(registro1['nome'], registro2['nome'])/100
        
    return sim

    #Outras possibilidades:
        #Usar nome da mãe na comparação
        #Comparar nome e sobrenome
        #Usar outro algoritmo de similaridade

pares = pd.DataFrame(columns = ['paciente', 'registro', 'similaridade'])

for i in range(0,10):
    print('CPF começando com {}'.format(i))
    #Varrer todos os dados_medicos, comparando com os registros em cadastro:
    for k, paciente in dados_medicos_blocos[i].iterrows():
        for j, registro in cadastro_blocos[i].iterrows():
            #print('Dados médicos: {}, {}, {}'.format(paciente.nome, paciente.cpf, paciente.data_nasc))
            #print('Cadastro: {}, {}, {}'.format(registro.nome, registro.cpf, registro.data_nasc))
            sim = comparaRegistros(paciente, registro)
            #print('Similaridade: {}, {}, {}'.format(sim['nome'], sim['cpf'], sim['data_nasc']))
            par = {'paciente' : paciente, 'registro' : registro, 'similaridade' : sim}
            pares = pares.append(par, ignore_index = True)

pares['simSum'] = 0

matches = pd.DataFrame()
matches_registros = pd.DataFrame()
potenciais = pd.DataFrame()
potenciais_registros = pd.DataFrame()
non_matches = pd.DataFrame()
non_matches_registros = pd.DataFrame()

#Classificação
for idx, par in pares.iterrows():
    sim = par['similaridade']
    simSum = sim['cpf'] + sim['nome'] + sim['data_nasc']
    #Possibilidades - dar peso diferentes aos critérios
    pares.loc[idx, 'simSum'] = simSum
    if simSum == 3:
        matches = matches.append(pares.loc[idx])
        matches_registros = matches_registros.append(pares.loc[idx, 'registro'])
    elif simSum >=2:
        potenciais = potenciais.append(pares.loc[idx])
        potenciais_registros = potenciais_registros.append(pares.loc[idx, 'registro'])
    else:
        non_matches = non_matches.append(pares.loc[idx])
        non_matches_registros = non_matches_registros.append(pares.loc[idx, 'registro'])

is_missing = dados_medicos.merge(matches_registros, how = 'left', 
                on = ['nome', 'cpf', 'data_nasc'], indicator = True)
is_missing = is_missing[is_missing['_merge'] =='left_only'][['nome', 'data_nasc', 'cpf']]


#Avaliação



