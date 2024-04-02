import pandas as pd
import psycopg2
from psycopg2 import sql
import streamlit as st
import streamlit.components.v1 as html
import time
from streamlit_autorefresh import st_autorefresh
import os


tema_front_flux = """
<style>
[data-testid="stAppViewContainer"]{
  background-image: url("https://wallpaper.dog/large/973644.jpg");
  background-size: cover;
}
  
[data-testid="stHeader"]{
  background-color: rgb(107, 107, 105, 0.4);
}
[data-testid="stToolbar"]{
  right: 2rem;
  background-color: rgb(107, 107, 105, 0.2);
  background-size: cover;
}
[data-testid="stMetric"]{
  background-color: rgb(130, 130, 130, 0.5);
  padding: 15px;
  text-align: center;
}
"""
st.markdown(tema_front_flux, unsafe_allow_html=True)


# Substitua os valores abaixo com as informações do seu banco de dados
db_params = {
    'host': 'localhost',
    'database': 'DBMercadologic',
    'user': 'postgres',
    'password': 'local'
}

# Construa a string de conexão
conn_string = "host={host} dbname={database} user={user} password={password}".format(
    **db_params)

# Conecte-se ao banco de dados
conn = psycopg2.connect(conn_string)

# Crie um cursor para executar comandos SQL
cursor = conn.cursor()

#### Header nome empresa #######

if "temp" not in st.session_state:
    st.session_state["temp"] = ""


def clear_text():
    st.session_state["temp"] = st.session_state["text"]
    st.session_state["text"] = ""


st.session_state
st.text_input("Passe o código de barras do produto no leitor",
              key="text", on_change=clear_text)

ean_produto = st.session_state["temp"]


def mkt_imgs():
    # Lista de arquivos de imagem no diretório "images"
    image_files = [f for f in os.listdir("images") if f.endswith(
        ('.jpg', '.jpeg', '.png', '.gif'))]

    # Loop para apresentar imagens em loop contínuo
    while True:
        for image_name in image_files:
            image_path = f"images/{image_name}"
            with st.empty():
                st.image(image_path, use_column_width=True)
                time.sleep(3)
                # Intervalo de 3 segundos entre as imagens
                with st.empty():
                    st.write()


@st.cache_data
def consulta_preco(self):
    # Consulta EAN no Banco de Dados do Cliente
    busca_ean = """
        SELECT 
        e.ean, 
        i.descricao,
        i.preco, 
        i2.precopromocao,
        (((i.preco - i2.precopromocao) / i.preco) * 100)::int AS desconto
        FROM item i 
        INNER JOIN ean e ON i.id = e.iditem 
        INNER JOIN itempromocao i2 ON i.id = i2.iditem 
        WHERE i.desativado IS NULL AND e.ean = %s
        limit 1;
    """

    cursor.execute(busca_ean, (ean_produto,))
    # Obtenha os resultados
    results = cursor.fetchall()
    # Crie um DataFrame do pandas com os resultados
    columns = ["EAN", "Descricao", "Preço", "Preço Promoção", "Desconto"]
    lista_produtos_exibir = pd.DataFrame(results, columns=columns)
    # Transforma dados do DataFrame
    nome_prod = lista_produtos_exibir['Descricao'][0]
    preco_prod = lista_produtos_exibir['Preço'][0]
    preco_prod = "{:.2f}".format(preco_prod)
    preco_promo_prod = lista_produtos_exibir['Preço Promoção'][0]
    preco_promo_prod = "{:.2f}".format(preco_promo_prod)
    desc_prod = lista_produtos_exibir['Desconto'][0]

    with st.container():
        st.markdown(f"## {nome_prod}")
    col01, col02 = st.columns(2)
    with col01:
        st.image('produto_siloute_m.jpg')
    with col02:
        st.markdown(
            f"<h3 style='text-align: center; border-radius: 5px; padding: 6px; font-size: 30px;'> DE: {preco_prod}</h3>", unsafe_allow_html=True)
        st.markdown(
            f"<h3 style='text-align: center; border-radius: 5px; padding: 6px; font-size: 50px; background-color: green'> POR: {preco_promo_prod}</h3>", unsafe_allow_html=True)

        if preco_promo_prod != preco_prod:
            st.markdown(
                f"<h3 style='text-align: center; border-radius: 5px; padding: 6px; font-size: 20px;'> OLHA O DESCONTO !!!!</h3>", unsafe_allow_html=True)
            st.markdown(
                f"<h3 style='text-align: center; border-radius: 5px; padding: 6px; font-size: 60px; background-color: red'> {desc_prod}% </h3>", unsafe_allow_html=True)
            st.write()
        else:
            st.image('logo_mkt_poni.png', width=80)
    with st.container():
        if desc_prod > 40:
            st.markdown(
                f"<h3 style='text-align: center; border-radius: 5px; padding: 6px; font-size: 60px; background-color: red'> Ta Muito Barato!!!!!! </h3>", unsafe_allow_html=True)
        else:
            st.write("")


def monta_tela_mkt():
    with st. container():
        col01, col02 = st.columns(2)
        with col01:
           # st.markdown(f"<h3 style='text-align: center; border-radius: 5px; padding: 6px; font-size: 40px; background-color: rgb(244, 246, 247, 0.1)'>Supermercado PICNIC</h3>", unsafe_allow_html=True)
            st.image('logo_mkt_poni_m.png')
        with col02:
            mkt_imgs()


if ean_produto != '':
    consulta_preco()
    time.sleep(5)
    st.cache_data.clear()
    st_autorefresh(interval=2000, limit=10)
    with st.empty():
        st.write()
else:
    monta_tela_mkt()
