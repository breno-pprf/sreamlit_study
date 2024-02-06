import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# functions

st.set_page_config(layout='wide',
                   page_title='Dashboard de Vendas',
                   initial_sidebar_state='expanded')

st.title('DASHBOARD TESTE')


def formata_numero(valor, prefixo = ''):
    for unidade in ['', 'mil']:
        if valor<1000:
            return f'{prefixo} {valor:.2f} {unidade}'
        valor/=1000
    return f'{prefixo} {valor:.2f} mi'

# inputs e manipulaçao de dados
url = 'https://labdados.com/produtos'


todas_regioes = ['Brasil','Centro-Oeste','Nordeste','Norte','Sudeste','Sul']
st.sidebar.title('Filtros')
regiao_filtro = st.sidebar.selectbox('Regiões', todas_regioes)
if regiao_filtro == 'Brasil':
    regiao_filtro = ''

todos_anos = st.sidebar.checkbox('Dados de todo o período', value = True)
if todos_anos:
    ano_filtro = ''
else:
    ano_filtro = st.sidebar.slider('Ano', 2020, 2024)

query_string = {'regiao':regiao_filtro.lower(),'ano':ano_filtro}


response = requests.get(url,params=query_string)
dados = pd.DataFrame.from_dict(response.json())
dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format = '%d/%m/%Y')

filtro_vendedores =  st.sidebar.multiselect('Vendedores',dados['Vendedor'].unique())
if filtro_vendedores: 
    dados = dados[dados['Vendedor'].isin(filtro_vendedores)]

# variaveis
receita = formata_numero(dados["Preço"].sum(),'R$')
qtd_vendas = formata_numero(dados.shape[0])


# tabelas
receita_estados = dados.groupby('Local da compra')[['Preço']].sum()
receita_estados = dados.drop_duplicates(subset='Local da compra')[['Local da compra','lat','lon']].merge(receita_estados,left_on='Local da compra', right_index = True).sort_values('Preço',ascending=False)

receita_mensal = pd.DataFrame(dados.set_index('Data da Compra').groupby(pd.Grouper(freq = 'ME'))['Preço'].sum()).reset_index()
receita_mensal['Ano'] = receita_mensal['Data da Compra'].dt.year
receita_mensal['Mes'] = receita_mensal['Data da Compra'].dt.month

receita_categorias = dados.groupby('Categoria do Produto')[['Preço']].sum().sort_values('Preço',ascending=False)

vendas_estados = dados.groupby('Local da compra')[['Preço']].count()
vendas_estados = dados.drop_duplicates(subset='Local da compra')[['Local da compra','lat','lon']].merge(vendas_estados,left_on='Local da compra', right_index = True).sort_values('Preço',ascending=False)

vendas_mensal = pd.DataFrame(dados.set_index('Data da Compra').groupby(pd.Grouper(freq = 'ME'))['Preço'].count()).reset_index()
vendas_mensal['Ano'] = vendas_mensal['Data da Compra'].dt.year
vendas_mensal['Mes'] = vendas_mensal['Data da Compra'].dt.month

vendas_categorias = dados.groupby('Categoria do Produto')[['Preço']].count().sort_values('Preço',ascending=False)

vendedores = pd.DataFrame(dados.groupby('Vendedor')['Preço'].agg(['sum', 'count']))

# Graficos
fig_mapa_receita = px.scatter_geo(receita_estados,
                                  lat = 'lat',
                                  lon = 'lon',
                                  scope = 'south america',
                                  size = 'Preço',
                                  template = 'seaborn',
                                  hover_name='Local da compra',
                                  hover_data={'lat': False, 'lon': False},
                                  title = 'Receita por Estado'
                                  )

fig_receita_estados = px.bar(receita_estados.head(),
                             x = 'Local da compra',
                             y = 'Preço',
                             text_auto = True,
                             title = 'Top estados (Receita)'
                             )
fig_receita_estados.update_layout(yaxis_title = 'Receita')

fig_receita_mensal =  px.line(receita_mensal,
                              x = 'Mes',
                              y = 'Preço',
                              markers = True,
                              range_y = (0,receita_mensal[['Preço']].max()),
                              color = 'Ano',
                              line_dash = 'Ano',
                              title = 'Receita mensal'
                              )
fig_receita_mensal.update_layout(yaxis_title = 'Receita')

fig_receita_categorias = px.bar(receita_categorias.head(),
                             text_auto = True,
                             title = 'Top Categorias (Receita)'
                             )
fig_receita_categorias.update_layout(yaxis_title = 'Receita')

fig_mapa_vendas = px.scatter_geo(vendas_estados,
                                  lat = 'lat',
                                  lon = 'lon',
                                  scope = 'south america',
                                  size = 'Preço',
                                  template = 'seaborn',
                                  hover_name='Local da compra',
                                  hover_data={'lat': False, 'lon': False},
                                  title = 'Vendas por Estado'
                                  )

fig_vendas_estados = px.bar(vendas_estados.head(),
                             x = 'Local da compra',
                             y = 'Preço',
                             text_auto = True,
                             title = 'Top estados (Vendas)'
                             )
fig_vendas_estados.update_layout(yaxis_title = 'Vendas')

fig_vendas_mensal =  px.line(vendas_mensal,
                              x = 'Mes',
                              y = 'Preço',
                              markers = True,
                              range_y = (0,vendas_mensal[['Preço']].max()),
                              color = 'Ano',
                              line_dash = 'Ano',
                              title = 'Vendas mensal'
                              )
fig_vendas_mensal.update_layout(yaxis_title = 'Vendas')

fig_vendas_categorias = px.bar(vendas_categorias.head(),
                             text_auto = True,
                             title = 'Top Categorias (Vendas)'
                             )
fig_vendas_categorias.update_layout(yaxis_title = 'Vendas')

# ordem visual

aba1,aba2,aba3 = st.tabs(['Receita', 'Quantidade de Vendas', 'Vendedores'])

with aba1:
    coluna1,coluna2 = st.columns(2)
    with coluna1:
        st.metric(
            label='Receita',
            value=receita,
            help='Receita total de vendas')
        st.plotly_chart(fig_mapa_receita,use_container_width=True)
        st.plotly_chart(fig_receita_estados,use_container_width=True)
        

    with coluna2:
        st.metric(
            label='Quantidade de Vendas',
            value=qtd_vendas,
            help='Quantidade total de produtos vendidos')
        st.plotly_chart(fig_receita_mensal,use_container_width=True)
        st.plotly_chart(fig_receita_categorias,use_container_width=True)
    

with aba2:
    coluna1,coluna2 = st.columns(2)
    with coluna1:
        st.metric(
            label='Receita',
            value=receita,
            help='Receita total de vendas')
        st.plotly_chart(fig_mapa_vendas,use_container_width=True)
        st.plotly_chart(fig_vendas_estados,use_container_width=True)
        

    with coluna2:
        st.metric(
            label='Quantidade de Vendas',
            value=qtd_vendas,
            help='Quantidade total de produtos vendidos')
        st.plotly_chart(fig_vendas_mensal,use_container_width=True)
        st.plotly_chart(fig_vendas_categorias,use_container_width=True)

with aba3:
    qtd_vendedores = st.number_input("Quantidade de Vendedores",2,10,5)
    coluna1,coluna2 = st.columns(2)
    with coluna1:
        st.metric(
            label='Receita',
            value=receita,
            help='Receita total de vendas')
        fig_receita_vendedores = px.bar(vendedores[['sum']].sort_values('sum', ascending=False).head(qtd_vendedores),
                                        x = 'sum',
                                        y = vendedores[['sum']].sort_values('sum', ascending=False).head(qtd_vendedores).index,
                                        text_auto=True,
                                        title = f'Top {qtd_vendedores} Vendedores (Receita)'
                                        )
        fig_receita_vendedores.update_layout(yaxis_title = 'Vendedores')
        fig_receita_vendedores.update_layout(xaxis_title = 'Receita')
        st.plotly_chart(fig_receita_vendedores,use_container_width=True)

    with coluna2:
        st.metric(
            label='Quantidade de Vendas',
            value=qtd_vendas,
            help='Quantidade total de produtos vendidos')
        fig_vendas_vendedores = px.bar(vendedores[['count']].sort_values('count', ascending=False).head(qtd_vendedores),
                                        x = 'count',
                                        y = vendedores[['count']].sort_values('count', ascending=False).head(qtd_vendedores).index,
                                        text_auto=True,
                                        title = f'Top {qtd_vendedores} Vendedores (Vendas)'
                                        )
        fig_vendas_vendedores.update_layout(yaxis_title = 'Vendedores')
        fig_vendas_vendedores.update_layout(xaxis_title = 'Vendas')
        st.plotly_chart(fig_vendas_vendedores,use_container_width=True)


#st.dataframe(dados,use_container_width=True)







# testes