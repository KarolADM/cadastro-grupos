import pandas as pd
import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds_dict = dict(st.secrets["gcp_service_account"])
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

sheet = client.open("dados dos grupos de trabalho").sheet1

def listar_grupos():
    dados = sheet.get_all_values()
    if len(dados) <= 1:
        return []
    return dados[1:]

def salvar_grupo(nome, integrantes):
    dados = listar_grupos()
    novo_id = len(dados) + 1
    integrantes = integrantes + [""] * (6 - len(integrantes))

    sheet.append_row([
        novo_id,
        nome,
        *integrantes
    ])

st.title("Cadastro de Grupos")

nome_grupo = st.text_input("Nome do grupo")
qtd = st.number_input("Quantidade de integrantes", 1, 6)

integrantes = []
for i in range(int(qtd)):
    integrantes.append(st.text_input(f"Integrante {i+1}"))

if st.button("Salvar grupo"):
    salvar_grupo(nome_grupo, integrantes)
    st.success("Salvo!")
    st.rerun()

st.subheader("Grupos cadastrados")

dados = listar_grupos()

if dados:
    df = pd.DataFrame(dados, columns=[
        "ID", "Grupo", "Integrante 1", "Integrante 2",
        "Integrante 3", "Integrante 4", "Integrante 5", "Integrante 6"
    ])
    st.dataframe(df)
else:
    st.info("Nenhum grupo cadastrado")