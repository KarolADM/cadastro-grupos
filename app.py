import pandas as pd
import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# -----------------------------
# Configuração da página
# -----------------------------
st.set_page_config(
    page_title="Cadastro de Grupos",
    page_icon="📚",
    layout="centered"
)

# -----------------------------
# URL da sua planilha (já configurada)
# -----------------------------
URL_PLANILHA = "https://docs.google.com/spreadsheets/d/1aWex5rzwhxQUMpU0wSOURNkecS7cH_wJs8hXn4HKAbQ/edit"

SENHA_EXCLUSAO = "metodologia2026"

# -----------------------------
# Conexão com Google Sheets
# -----------------------------
@st.cache_resource
def conectar_planilha():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]

    creds_dict = dict(st.secrets["gcp_service_account"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)

    planilha = client.open_by_url(URL_PLANILHA)
    return planilha.sheet1

sheet = conectar_planilha()

# -----------------------------
# Funções auxiliares
# -----------------------------
def normalizar_linha(linha):
    linha = linha[:8]
    while len(linha) < 8:
        linha.append("")
    return linha

def listar_grupos():
    registros = sheet.get_all_values()

    if not registros or len(registros) <= 1:
        return []

    dados = registros[1:]
    dados_normalizados = [normalizar_linha(linha) for linha in dados]
    return dados_normalizados

def gerar_novo_id(dados):
    if not dados:
        return 1

    ids = []
    for linha in dados:
        try:
            ids.append(int(str(linha[0]).strip()))
        except:
            pass

    return max(ids) + 1 if ids else 1

def salvar_grupo(nome_grupo, integrantes):
    dados = listar_grupos()
    novo_id = gerar_novo_id(dados)

    integrantes = integrantes + [""] * (6 - len(integrantes))
    integrantes = integrantes[:6]

    nova_linha = [
        str(novo_id),
        nome_grupo,
        integrantes[0],
        integrantes[1],
        integrantes[2],
        integrantes[3],
        integrantes[4],
        integrantes[5]
    ]

    sheet.append_row(nova_linha)

def buscar_grupo_por_id(id_grupo):
    dados = listar_grupos()

    for indice, linha in enumerate(dados, start=2):
        if str(linha[0]).strip() == str(id_grupo).strip():
            return indice, linha

    return None, None

def excluir_grupo(id_grupo):
    linha_planilha, grupo = buscar_grupo_por_id(id_grupo)

    if linha_planilha:
        sheet.delete_rows(linha_planilha)
        return True

    return False

# -----------------------------
# Interface
# -----------------------------
st.title("Cadastro de Grupos")

nome_grupo = st.text_input("Nome do grupo")
quantidade = st.number_input("Quantidade de integrantes", 1, 6)

integrantes = []
for i in range(int(quantidade)):
    integrantes.append(st.text_input(f"Integrante {i+1}"))

if st.button("Salvar grupo"):
    if not nome_grupo.strip():
        st.error("Digite o nome do grupo.")
    elif any(not nome.strip() for nome in integrantes):
        st.error("Preencha todos os nomes.")
    else:
        salvar_grupo(nome_grupo.strip(), [n.strip() for n in integrantes])
        st.success("Grupo salvo!")
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

# -----------------------------
# Exclusão
# -----------------------------
st.subheader("Excluir grupo")

id_excluir = st.text_input("ID do grupo")
senha = st.text_input("Senha", type="password")

if st.button("Excluir"):
    if senha != SENHA_EXCLUSAO:
        st.error("Senha incorreta")
    elif not id_excluir.isdigit():
        st.error("ID inválido")
    else:
        if excluir_grupo(int(id_excluir)):
            st.success("Grupo excluído")
            st.rerun()
        else:
            st.error("Grupo não encontrado")