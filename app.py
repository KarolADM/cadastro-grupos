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
# Estilo visual
# -----------------------------
st.markdown("""
    <style>
    .stApp {
        background-color: #d9d9d9;
    }

    .titulo {
        text-align: center;
        color: #1f1f1f;
        font-size: 34px;
        font-weight: 700;
        margin-bottom: 8px;
    }

    .subtitulo {
        text-align: center;
        color: #333333;
        font-size: 17px;
        margin-bottom: 3px;
        font-weight: 600;
    }

    .info-disciplina {
        text-align: center;
        color: #444444;
        font-size: 15px;
        margin-bottom: 2px;
    }

    .caixa {
        background-color: white;
        padding: 20px;
        border-radius: 14px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.08);
        margin-bottom: 20px;
    }

    div[data-testid="stDataFrame"] div[role="columnheader"] {
        background-color: #e8eefc !important;
        color: #1f3c88 !important;
        font-weight: 700 !important;
    }
    </style>
""", unsafe_allow_html=True)

# -----------------------------
# Configuração da planilha
# -----------------------------
URL_PLANILHA = "COLE_AQUI_A_URL_DA_SUA_PLANILHA"
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
# Cabeçalho
# -----------------------------
st.markdown('<div class="titulo">Cadastro de Grupos</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitulo">Turma: 45370 - GRAD.14767 - Metodologia do Trabalho Científico e Técnico</div>',
    unsafe_allow_html=True
)
st.markdown(
    '<div class="info-disciplina">Profª Karolyne Vasconcelos</div>',
    unsafe_allow_html=True
)

# -----------------------------
# Cadastro
# -----------------------------
st.markdown('<div class="caixa">', unsafe_allow_html=True)
st.subheader("Novo grupo")

nome_grupo = st.text_input("Nome do grupo")
quantidade = st.number_input(
    "Quantidade de integrantes",
    min_value=1,
    max_value=6,
    step=1
)

st.caption("Máximo permitido: 6 integrantes por grupo.")

integrantes = []
for i in range(int(quantidade)):
    nome = st.text_input(f"Nome do integrante {i+1}")
    integrantes.append(nome)

if st.button("Salvar grupo", use_container_width=True):
    if not nome_grupo.strip():
        st.error("Digite o nome do grupo.")
    elif any(not nome.strip() for nome in integrantes):
        st.error("Preencha todos os nomes dos integrantes.")
    else:
        salvar_grupo(
            nome_grupo.strip(),
            [nome.strip() for nome in integrantes]
        )
        st.success("Grupo cadastrado com sucesso.")
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# Tabela
# -----------------------------
st.markdown('<div class="caixa">', unsafe_allow_html=True)
st.subheader("Grupos cadastrados")

dados = listar_grupos()

if dados:
    df = pd.DataFrame(dados, columns=[
        "ID", "Grupo", "Integrante 1", "Integrante 2",
        "Integrante 3", "Integrante 4", "Integrante 5", "Integrante 6"
    ])
    st.dataframe(df, use_container_width=True, hide_index=True)
else:
    st.info("Nenhum grupo cadastrado.")

st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# Exclusão
# -----------------------------
st.markdown('<div class="caixa">', unsafe_allow_html=True)
st.subheader("Exclusão de cadastro")

st.caption(
    "Para excluir um cadastro, informe o número de identificação do grupo (ID) e a senha de exclusão. "
    "A exclusão deve ser realizada apenas em caso de erro no cadastro."
)

id_exclusao = st.text_input("Número do grupo (ID)")
senha_exclusao = st.text_input("Senha de exclusão", type="password")

if st.button("Excluir grupo", use_container_width=True):
    if not id_exclusao.strip():
        st.error("Informe o ID do grupo.")
    elif not id_exclusao.strip().isdigit():
        st.error("O ID deve ser numérico.")
    elif not senha_exclusao.strip():
        st.error("Informe a senha.")
    elif senha_exclusao.strip() != SENHA_EXCLUSAO:
        st.error("Senha incorreta.")
    else:
        sucesso = excluir_grupo(int(id_exclusao))
        if sucesso:
            st.success("Grupo excluído com sucesso.")
            st.rerun()
        else:
            st.error("Grupo não encontrado.")

st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# Exportar
# -----------------------------
st.markdown('<div class="caixa">', unsafe_allow_html=True)
st.subheader("Exportar dados")

if dados:
    df_export = pd.DataFrame(dados, columns=[
        "ID", "Grupo", "Integrante 1", "Integrante 2",
        "Integrante 3", "Integrante 4", "Integrante 5", "Integrante 6"
    ])
    csv = df_export.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Baixar CSV",
        data=csv,
        file_name="grupos.csv",
        mime="text/csv",
        use_container_width=True
    )

st.markdown('</div>', unsafe_allow_html=True)