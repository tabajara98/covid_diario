import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime 
import datetime

dados = pd.read_excel('HIST_PAINEL_COVIDBR_24jul2020.xlsx',usecols=['estado','codmun','data','casosNovos','obitosNovos'])
dados = dados[(dados['estado'].isin(['RJ']))&(dados['codmun'].astype(str)=='nan')]
dados = dados.reset_index(drop=True)

dados_data = dados.groupby('data').sum()

dados_data['casosCum'] = dados_data['casosNovos'].cumsum()
dados_data['obitosCum'] = dados_data['obitosNovos'].cumsum()

dados_data['%casos_diario'] = dados_data['casosCum'].pct_change()
dados_data['%obitos_diario'] = dados_data['obitosCum'].pct_change()

dados_data['MM7_casos'] = dados_data['%casos_diario'].rolling(7).mean()
dados_data['MM14_casos'] = dados_data['%casos_diario'].rolling(14).mean()
dados_data['std_MM7_casos'] = dados_data['%casos_diario'].rolling(7).std()
dados_data['upper_MM7_casos'] = dados_data['MM7_casos'] + 2*dados_data['std_MM7_casos']
dados_data['lower_MM7_casos'] = dados_data['MM7_casos'] - 2*dados_data['std_MM7_casos']

dados_data['MM7_obitos'] = dados_data['%obitos_diario'].rolling(7).mean()
dados_data['std_MM7_obitos'] = dados_data['%obitos_diario'].rolling(7).std()
dados_data['upper_MM7_obitos'] = dados_data['MM7_obitos'] + 2*dados_data['std_MM7_obitos']
dados_data['lower_MM7_obitos'] = dados_data['MM7_obitos'] - 2*dados_data['std_MM7_obitos']

fases_reabertura = {i:j for i,j in zip([datetime.datetime(2020,6,2),datetime.datetime(2020,6,17),datetime.datetime(2020,7,2),datetime.datetime(2020,7,17)],['Fase 1','Fase 2','Fase 3','Fase 4'])}
fases_reabertura_fim = {i:j for i,j in zip([datetime.datetime(2020,6,16),datetime.datetime(2020,7,1),datetime.datetime(2020,7,16),datetime.datetime(2020,8,1)],['Fase 1','Fase 2','Fase 3','Fase 4'])}

from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

dados_data_loc = dados_data.loc[(dados_data.index>=datetime.datetime(2020,5,21))]

f,ax = plt.subplots(figsize=(15,6))

sns.lineplot(x=dados_data_loc.index,y=dados_data_loc['%casos_diario'],linewidth=1,alpha=0.6)
sns.lineplot(x=dados_data_loc.index,y=dados_data_loc['MM7_casos'],linewidth=2)
#sns.lineplot(x=dados_data_loc.index,y=dados_data_loc['MM14_casos'],linewidth=2)
plt.fill_between(dados_data_loc.index, dados_data_loc['lower_MM7_casos'], 
                dados_data_loc['upper_MM7_casos'], color='#ADCCFF', alpha='0.4')

plt.annotate('Antes da Reabertura:   {:.2%}'.format(dados_data_loc.loc[(dados_data_loc.index<list(fases_reabertura.keys())[0])]['%casos_diario'].mean()),xy=(datetime.date(2020,5,16),dados_data_loc.loc[(dados_data_loc.index<list(fases_reabertura.keys())[0])]['%casos_diario'].max()))

for fase,fase_fim in zip(fases_reabertura,fases_reabertura_fim):
    ax.axvline(fase,color='black',linewidth=0.5,alpha=0.5)
    plt.annotate('{}:  {:.2%}'.format(fases_reabertura[fase],dados_data_loc.loc[(dados_data_loc.index>fase)&(dados_data_loc.index<=fase_fim)]['%casos_diario'].mean()),xy=(fase+datetime.timedelta(days=1),dados_data_loc['%casos_diario'].max()+0.01))

plt.annotate('Hoje:  {:.2%}'.format(dados_data_loc.iloc[-1]['%casos_diario']),
             xy=(datetime.datetime.today()-datetime.timedelta(days=4),dados_data_loc.iloc[-1]['%casos_diario']+0.005),
            bbox=dict(facecolor='white', edgecolor='orange',pad=5)) 
ax.axhline(dados_data_loc.iloc[-1]['MM7_casos'],linewidth=1,color='orange',alpha=0.75,linestyle='dashed')

ax.axhline(0,linewidth=1,color='black',alpha=1,linestyle='dashed')

plt.xticks(rotation=20)
plt.yticks([x/100 for x in range(-6,20,1)],[str(x)+'%' for x in range(-6,20,1)])
plt.ylim(-0.02,0.12)
plt.ylabel('Taxa Diária')
plt.xlabel('Data')
plt.legend(['Taxa Diária','MM da Taxa Diária (7 dias)'],loc=2,fontsize=9)
plt.title('Evolução da Taxa Diária de Casos de COVID no Rio de Janeiro, RJ',fontsize=15)
plt.show()

print('No dia {} a Média Móvel dos últimos 7 dias é {:.2%}'.format(dados_data_loc.iloc[-1].name.strftime('%d/%m'),
                                                      dados_data_loc.iloc[-1]['MM7_casos']))
