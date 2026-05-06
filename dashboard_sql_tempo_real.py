import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import pymssql
from datetime import datetime, date
from streamlit_autorefresh import st_autorefresh

# ══════════════════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Dashboard Distribuição — Tempo Real",
    page_icon="🚚", layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════════════════════════
# CSS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .main .block-container { padding: 1.5rem 2rem 2rem 2rem; max-width: 100%; }
    header[data-testid="stHeader"] {
        background: linear-gradient(135deg, #0F0F1A 0%, #1A1A2E 100%);
        border-bottom: 1px solid rgba(124, 58, 237, 0.2);
    }
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0F0F1A 0%, #12122B 100%);
        border-right: 1px solid rgba(124, 58, 237, 0.15);
    }

    .dash-title {
        background: linear-gradient(135deg, #1A1A2E 0%, #16213E 50%, #1A1A2E 100%);
        border: 1px solid rgba(124, 58, 237, 0.3);
        border-radius: 16px; padding: 1.2rem 2rem;
        margin-bottom: 1.5rem; text-align: center;
        box-shadow: 0 4px 24px rgba(124, 58, 237, 0.08);
    }
    .dash-title h1 {
        margin: 0; font-size: 1.75rem; font-weight: 800;
        background: linear-gradient(135deg, #7C3AED, #A78BFA, #C4B5FD);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        letter-spacing: -0.5px;
    }
    .dash-title p { margin: 0.3rem 0 0; color: #9CA3AF; font-size: 0.85rem; }

    .kpi-card {
        background: linear-gradient(145deg, #1A1A2E, #16213E);
        border: 1px solid rgba(124, 58, 237, 0.2);
        border-radius: 14px; padding: 1.2rem 1.4rem;
        text-align: center; transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.15);
        position: relative; overflow: hidden;
    }
    .kpi-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px; border-radius: 14px 14px 0 0; }
    .kpi-card:hover { transform: translateY(-3px); box-shadow: 0 8px 28px rgba(124, 58, 237, 0.15); border-color: rgba(124, 58, 237, 0.4); }
    .kpi-icon  { font-size: 1.6rem; margin-bottom: 0.3rem; }
    .kpi-label { font-size: 0.72rem; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; color: #9CA3AF; margin-bottom: 0.25rem; }
    .kpi-value { font-size: 2rem; font-weight: 800; line-height: 1.1; }
    .kpi-sub   { font-size: 0.72rem; color: #6B7280; margin-top: 0.2rem; }

    .kpi-total::before    { background: linear-gradient(90deg, #7C3AED, #A78BFA); } .kpi-total .kpi-value    { color: #A78BFA; }
    .kpi-realizado::before{ background: linear-gradient(90deg, #10B981, #34D399); } .kpi-realizado .kpi-value{ color: #34D399; }
    .kpi-pendente::before { background: linear-gradient(90deg, #F59E0B, #FBBF24); } .kpi-pendente .kpi-value { color: #FBBF24; }
    .kpi-entregue::before { background: linear-gradient(90deg, #3B82F6, #60A5FA); } .kpi-entregue .kpi-value { color: #60A5FA; }
    .kpi-nentregue::before{ background: linear-gradient(90deg, #EF4444, #F87171); } .kpi-nentregue .kpi-value{ color: #F87171; }
    .kpi-coletada::before { background: linear-gradient(90deg, #8B5CF6, #A78BFA); } .kpi-coletada .kpi-value { color: #A78BFA; }
    .kpi-ncoleta::before  { background: linear-gradient(90deg, #F59E0B, #FBBF24); } .kpi-ncoleta .kpi-value  { color: #FBBF24; }
    .kpi-frete::before    { background: linear-gradient(90deg, #06B6D4, #22D3EE); } .kpi-frete .kpi-value    { color: #22D3EE; }
    .kpi-vermelho::before { background: linear-gradient(90deg, #EF4444, #F87171); } .kpi-vermelho .kpi-value { color: #F87171; }
    .kpi-amarelo::before  { background: linear-gradient(90deg, #F59E0B, #FBBF24); } .kpi-amarelo .kpi-value  { color: #FBBF24; }
    .kpi-verde::before    { background: linear-gradient(90deg, #10B981, #34D399); } .kpi-verde .kpi-value    { color: #34D399; }

    .farol-badge { display: inline-block; padding: 0.2rem 0.7rem; border-radius: 20px; font-size: 0.72rem; font-weight: 700; letter-spacing: 0.5px; }
    .fb-v { background: rgba(239,68,68,0.15);  color: #F87171; border: 1px solid rgba(239,68,68,0.3); }
    .fb-a { background: rgba(245,158,11,0.15); color: #FBBF24; border: 1px solid rgba(245,158,11,0.3); }
    .fb-g { background: rgba(16,185,129,0.15); color: #34D399; border: 1px solid rgba(16,185,129,0.3); }

    .alert-card {
        background: linear-gradient(145deg, #1A1A2E, #16213E);
        border: 1px solid rgba(124, 58, 237, 0.15);
        border-radius: 12px; padding: 0.7rem 1.1rem; margin-bottom: 0.45rem;
        display: flex; justify-content: space-between; align-items: center;
        transition: all 0.2s;
    }
    .alert-card:hover { border-color: rgba(239,68,68,0.4); transform: translateX(4px); }
    .alert-card .c-name { color: #E0E0E0; font-weight: 600; font-size: 0.85rem; }
    .alert-card .c-info { color: #9CA3AF; font-size: 0.72rem; margin-top: 0.1rem; }
    .alert-card .c-ref  { color: #A78BFA; font-size: 0.72rem; font-weight: 600; margin-top: 0.1rem; }

    .sec-header {
        font-size: 1.05rem; font-weight: 700; color: #E0E0E0;
        margin: 1.5rem 0 0.8rem; padding-bottom: 0.5rem;
        border-bottom: 2px solid rgba(124, 58, 237, 0.25);
    }

    .stTabs [data-baseweb="tab-list"] { gap: 0; background: #1A1A2E; border-radius: 12px; padding: 4px; border: 1px solid rgba(124, 58, 237, 0.2); }
    .stTabs [data-baseweb="tab"] { border-radius: 10px; padding: 0.55rem 1.5rem; font-weight: 600; font-size: 0.85rem; color: #9CA3AF; border: none; background: transparent; }
    .stTabs [aria-selected="true"] { background: linear-gradient(135deg, #7C3AED, #6D28D9) !important; color: #FFFFFF !important; box-shadow: 0 2px 10px rgba(124, 58, 237, 0.35); }

    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: #0F0F1A; }
    ::-webkit-scrollbar-thumb { background: #7C3AED55; border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: #7C3AED; }

    #MainMenu { visibility: hidden; } footer { visibility: hidden; } .stDeployButton { display: none; }

    /* ── FORCE DARK BACKGROUND ON ALL STREAMLIT CONTAINERS ── */
    html, body { background-color: #0F0F1A !important; }
    [data-testid="stApp"],
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"],
    [data-testid="stMainBlockContainer"],
    .main, .block-container,
    [data-testid="block-container"],
    .stApp, .css-1d391kg, .css-fg4pbf,
    div[class*="stVerticalBlock"],
    div[class*="appview-container"] {
        background-color: #0F0F1A !important;
        background: #0F0F1A !important;
    }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# CONSTANTES
# ══════════════════════════════════════════════════════════════════════════════
PLOTLY_BASE = dict(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color="#D1D5DB", size=12),
    margin=dict(l=20, r=40, t=50, b=20),
)
SITUACAO_COLORS = {
    "ENTREGUE": "#34D399", "NÃO ENTREGUE": "#FBBF24",
    "COLETADA": "#34D399", "NÃO COLETADA": "#F87171",
}
COLOR_PAL = ["#7C3AED","#A78BFA","#C4B5FD","#3B82F6","#60A5FA",
             "#10B981","#34D399","#F59E0B","#FBBF24","#EF4444",
             "#F87171","#EC4899","#F472B6","#6366F1","#818CF8"]

# Mapeamento de clientes
CLIENT_MAP = {
    "MACAE": "TEC-MCE", "MATRIZ": "TEC-SAO", "TEC - RIO": "TEC-RIO",
    "TECNOLOG - SSA": "TEC-SSA", "BOA VISTA": "TEC-BVB", "MAO-BASE II": "TEC-MAO",
}
EXCLUDE_CLIENTS = {"NNA", "NNA-BA", "MAO-BASE I"}

# Mapeamento de Tipo_Movimento
CONV_TIPOS = {"EMBARQUE","CONVEN-RODO","MULTIMODAL EMBARQUE","N.F. SERVIÇOS",
              "REENTREGA","SUBCONTRATAÇÃO","COLETA AUTOMATICA"}
PRIO_TIPOS = {"CARRO PRIORITÁRIO","ECONOMICA-PETRO","CONVEN-AEREO",
              "EMERGÊNCIA-PETRO","COLETA PRIORITÁRIA","EXPRESSO-PETRO"}

# ══════════════════════════════════════════════════════════════════════════════
# SQL
# ══════════════════════════════════════════════════════════════════════════════
SQL_QUERY = """
SELECT
    A.id_Manifesto, P.ds_Cliente, A.dt_Saida, A.dt_Finalizado,
    CASE WHEN A.tp_Manifesto='V' THEN 'VIAGEM' ELSE 'DISTRIBUIÇÃO' END AS tp_Descricao,
    B.ds_Tipo,
    CASE WHEN ISNULL(B.id_PedidoColeta,'')='' THEN E.id_PedidoColeta ELSE B.id_PedidoColeta END AS ID_Pedido_Coleta,
    E.nr_Minuta+'/'+E.nr_Conhecimento AS Documento, E.vl_Frete,
    CASE WHEN ISNULL(B.id_PedidoColeta,'')='' THEN S.ds_TipoMovimento ELSE T.ds_TipoPedidoColeta END AS Tipo_Movimento,
    CASE WHEN ISNULL(B.id_PedidoColeta,'')='' THEN E.dt_Movimento ELSE F.dt_PedidoColeta END AS Data_Movimento,
    CASE WHEN ISNULL(B.id_PedidoColeta,'')='' THEN E.dt_PrazoEntrega ELSE F.dt_Limite END AS Prazo,
    C.ds_Pessoa AS Motorista,
    CASE WHEN ISNULL(B.id_PedidoColeta,'')='' THEN U.ds_Pessoa ELSE V.ds_Pessoa END AS Pagador,
    CASE WHEN ISNULL(B.id_PedidoColeta,'')='' THEN H.ds_Pessoa ELSE G.ds_Pessoa END AS Destinatario_Remetente,
    CASE WHEN ISNULL(B.id_PedidoColeta,'')='' THEN H.ds_Bairro ELSE M.ds_BairroColeta END AS Bairro,
    CASE WHEN ISNULL(B.id_PedidoColeta,'')='' THEN I.ds_Cidade ELSE N.ds_Cidade END AS Cidade,
    CASE WHEN ISNULL(B.id_PedidoColeta,'')='' THEN I.UFE_SG ELSE N.UFE_SG END AS UF,
    CASE
        WHEN S.ds_TipoMovimento = 'DESPACHO' OR T.ds_TipoPedidoColeta = 'DESPACHO' THEN 'ENTREGUE'
        WHEN S.ds_TipoMovimento = 'REDESPACHO' OR T.ds_TipoPedidoColeta = 'REDESPACHO' THEN 'ENTREGUE'
        WHEN (SELECT TOP 1 OX.ds_Ocorrencia FROM tbdOcorrencia OX WHERE OX.id_Ocorrencia = B.id_Ocorrencia)
             LIKE '%REDESPACHADA%' THEN 'ENTREGUE'
        WHEN ISNULL(E.id_Movimento,'')=''
            THEN (CASE WHEN F.tp_Coletada='S' THEN 'COLETADA' ELSE 'NÃO COLETADA' END)
        ELSE (CASE WHEN E.dt_Recepcao IS NOT NULL AND E.dt_Recepcao<>''
                   THEN 'ENTREGUE' ELSE 'NÃO ENTREGUE' END)
    END AS Situacao,
    CASE
        WHEN ISNULL(B.id_PedidoColeta,'')=''
            THEN (SELECT TOP 1 Q2.ds_Ocorrencia FROM tbdOcorrenciaNota Q2
                  WHERE Q2.id_Movimento=E.id_Movimento ORDER BY Q2.dt_Abertura DESC)
        ELSE (SELECT TOP 1 R2.cm_OcorrenciaPedidoColeta FROM tbdOcorrenciaPedidoColeta R2
              WHERE R2.id_PedidoColeta=F.id_PedidoColeta AND A.id_Manifesto=R2.id_Manifesto
              ORDER BY R2.dt_OcorrenciaPedidoColeta DESC)
    END AS Detalhe_Ocorrencia,
    (SELECT TOP 1 S2.ds_Ocorrencia FROM tbdOcorrencia S2 WHERE S2.id_Ocorrencia = B.id_Ocorrencia) AS Ocorrencia_Manifesto,
    (SELECT TOP 1 XA.ds_Ocorrencia FROM tbdOcorrenciaNota XS
     LEFT JOIN tbdOcorrencia XA ON XA.id_Ocorrencia = XS.id_Ocorrencia
     WHERE E.id_Movimento = XS.id_Movimento
     ORDER BY dt_Abertura DESC, hr_Abertura DESC) AS Ult_OcorrenciaEntrega,
    E.nr_NotaFiscal,
    CASE WHEN ISNULL(B.id_PedidoColeta,'')='' THEN E.vl_NotaFiscal ELSE 0 END AS Valor_NF,
    CASE WHEN ISNULL(B.id_PedidoColeta,'')='' THEN E.qt_Volume ELSE F.qt_Volume END AS Volumes,
    CASE WHEN ISNULL(B.id_PedidoColeta,'')='' THEN E.kg_Mercadoria ELSE F.kg_Mercadoria END AS Peso,
    R.cd_Placa,
    X.ds_Pessoa AS Transportadora,
    CASE
        WHEN ISNULL(B.id_PedidoColeta,'')='' THEN 'ENTREGA'
        ELSE 'COLETA'
    END AS Tipo_Servico
FROM tbdManifesto A (NOLOCK)
LEFT JOIN tbdManifestoMovimento B (NOLOCK) ON A.id_Manifesto=B.id_Manifesto
LEFT JOIN tbdMovimento E (NOLOCK) ON B.id_Movimento=E.id_Movimento
LEFT JOIN tbdPessoa C (NOLOCK) ON A.id_Motorista=C.id_Pessoa
LEFT JOIN tbdPedidoColeta F (NOLOCK) ON B.id_PedidoColeta=F.id_PedidoColeta
LEFT JOIN tbdPessoa G (NOLOCK) ON F.id_Pessoa=G.id_Pessoa
LEFT JOIN tbdPessoa H (NOLOCK) ON E.id_Destinatario=H.id_Pessoa
LEFT JOIN tbdCidade I (NOLOCK) ON E.id_CidadeDestinatario=I.id_Cidade
LEFT JOIN tbdCidade J (NOLOCK) ON F.id_CidadeColeta=J.id_Cidade
LEFT JOIN tbdPessoa M (NOLOCK) ON F.id_Pessoa=M.id_Pessoa
LEFT JOIN tbdCidade N (NOLOCK) ON M.id_CidadeColeta=N.id_Cidade
LEFT JOIN tbdClienteSistema P (NOLOCK) ON A.id_Cliente=P.id_Cliente
LEFT JOIN tbdMovimento Q (NOLOCK) ON F.id_PedidoColeta=Q.id_PedidoColeta
LEFT JOIN tbdVeiculo R (NOLOCK) ON A.id_Veiculo=R.id_Veiculo
LEFT JOIN tbdTipoPedidoColeta T (NOLOCK) ON F.id_TipoPedidoColeta=T.id_TipoPedidoColeta
LEFT JOIN tbdTipoMovimento S (NOLOCK) ON E.id_TipoMovimento=S.id_TipoMovimento
LEFT JOIN tbdPessoa U (NOLOCK) ON E.id_ClienteFaturamento=U.id_Pessoa
LEFT JOIN tbdPessoa V (NOLOCK) ON F.id_Remetente=V.id_Pessoa
LEFT JOIN tbdPessoa X (NOLOCK) ON E.id_Transportadora=X.id_Pessoa
LEFT JOIN tbdPessoa Y (NOLOCK) ON U.id_FilialResponsavel=Y.id_Pessoa
WHERE
    (Q.id_Transportadora<>50398 OR Q.id_Transportadora IS NULL)
    AND A.dt_Saida>=CAST(%s AS DATE)
    AND A.dt_Saida<DATEADD(DAY,1,CAST(%s AS DATE))
    AND A.tp_Manifesto<>'V'
ORDER BY A.dt_Saida DESC;
"""

# ══════════════════════════════════════════════════════════════════════════════
# FUNÇÕES
# ══════════════════════════════════════════════════════════════════════════════
def _conn():
    cfg = st.secrets["sql"]
    return pymssql.connect(
        server=cfg["server"],
        user=cfg["username"],
        password=cfg["password"],
        database=cfg["database"],
        login_timeout=30,
    )

@st.cache_data(ttl=60, show_spinner=False)
def load_data(data_inicio: str, data_fim: str) -> pd.DataFrame:
    with _conn() as conn:
        df = pd.read_sql(SQL_QUERY, conn, params=[data_inicio, data_fim])
    return df

def transform(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    # Renomear e filtrar clientes
    df["ds_Cliente"] = df["ds_Cliente"].astype(str).str.strip()
    df["ds_Cliente"] = df["ds_Cliente"].map(lambda x: CLIENT_MAP.get(x, x))
    df = df[~df["ds_Cliente"].isin(EXCLUDE_CLIENTS)].copy()
    # Normalizar Situacao
    df["Situacao"] = df["Situacao"].astype(str).str.strip().str.upper()
    # Regra: Motorista ARTUR RIBEIRO SILVA → sempre ENTREGUE
    df.loc[df["Motorista"].astype(str).str.strip().str.upper() == "ARTUR RIBEIRO SILVA", "Situacao"] = "ENTREGUE"

    # ── Regra: REDESPACHO no nível do MANIFESTO → TODAS as NFs são ENTREGUE ──
    _colunas_ocorrencia = [
        "Detalhe_Ocorrencia",
        "Ocorrencia_Manifesto",
        "Ult_OcorrenciaEntrega",
    ]
    _redesp_manifestos = set()
    for _col in _colunas_ocorrencia:
        if _col in df.columns:
            _mask = (
                df[_col]
                .astype(str)
                .str.strip()
                .str.upper()
                .str.contains("REDESPACHADA", na=False)
            )
            _redesp_manifestos.update(df.loc[_mask, "id_Manifesto"].tolist())

    if _redesp_manifestos:
        df.loc[df["id_Manifesto"].isin(_redesp_manifestos), "Situacao"] = "ENTREGUE"

    # Classificação geral
    df["Classificacao"] = df["Situacao"].apply(
        lambda x: "Realizado" if x in ("ENTREGUE","COLETADA") else "Pendente"
    )
    # Categorizar Tipo_Movimento
    def cat_tipo(t):
        if pd.isna(t) or str(t).strip() in ("", "nan", "None"):
            return "CONVENCIONAL"
        t2 = str(t).strip().upper()
        if t2 in CONV_TIPOS: return "CONVENCIONAL"
        if t2 in PRIO_TIPOS: return "PRIORITÁRIO"
        return "CONVENCIONAL"
    df["Categoria_Servico"] = df["Tipo_Movimento"].apply(cat_tipo)
    # Prazo datetime
    df["Prazo"] = pd.to_datetime(df["Prazo"], errors="coerce")
    df["vl_Frete"] = pd.to_numeric(df["vl_Frete"], errors="coerce").fillna(0)
    # Farol
    agora = pd.Timestamp.now()
    fim_hoje = pd.Timestamp(agora.date().strftime("%Y-%m-%d") + " 23:59:59")
    def farol(row):
        if row["Classificacao"] == "Realizado" or pd.isna(row["Prazo"]):
            return None
        if row["Prazo"] < agora:    return "VERMELHO"
        if row["Prazo"] <= fim_hoje: return "AMARELO"
        return "VERDE"
    df["Farol"] = df.apply(farol, axis=1)
    return df

def fmt_brl(v):
    try: return f"R$ {float(v):,.2f}".replace(",","X").replace(".",",").replace("X",".")
    except: return "—"

def kpi(icon, label, value, sub="", variant="total"):
    return f"""<div class="kpi-card kpi-{variant}">
    <div class="kpi-icon">{icon}</div><div class="kpi-label">{label}</div>
    <div class="kpi-value">{value}</div><div class="kpi-sub">{sub}</div></div>"""

def bar_h(df_in, y_col, x_col, title, height=None, color="#3B82F6"):
    fig = go.Figure(go.Bar(
        y=df_in[y_col], x=df_in[x_col], orientation="h",
        marker=dict(color=color, cornerradius=5, line=dict(color="rgba(0,0,0,.15)",width=1)),
        text=df_in[x_col], textposition="outside", textfont=dict(size=11,color="#E0E0E0"),
        cliponaxis=False,
    ))
    fig.update_layout(**PLOTLY_BASE,
        height=height or max(300, len(df_in)*40),
        yaxis=dict(autorange="reversed",gridcolor="rgba(0,0,0,0)",zeroline=False,tickfont=dict(size=11)),
        xaxis=dict(gridcolor="rgba(59,130,246,.06)",zeroline=False,showticklabels=False),
    )
    return fig

# ══════════════════════════════════════════════════════════════════════════════
# AUTO-REFRESH
# ══════════════════════════════════════════════════════════════════════════════
st_autorefresh(interval=300_000, key="ar")

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style="text-align:center;margin-bottom:1rem;">
        <span style="font-size:2rem;">🚚</span>
        <h3 style="margin:.3rem 0 0;font-weight:700;background:linear-gradient(135deg,#7C3AED,#A78BFA);
                   -webkit-background-clip:text;-webkit-text-fill-color:transparent;">Distribuição</h3>
        <p style="color:#6B7280;font-size:.75rem;margin:0;">Monitoramento em Tempo Real</p>
    </div>""", unsafe_allow_html=True)
    st.markdown("---")

    st.markdown("**📅 Período**")
    hoje = date.today()
    data_inicio = st.date_input("De",  value=hoje, max_value=hoje, format="DD/MM/YYYY")
    data_fim    = st.date_input("Até", value=hoje, max_value=hoje, format="DD/MM/YYYY")
    if data_inicio > data_fim:
        st.warning("⚠️ Data inicial maior que a final.")

    st.markdown("---")
    if st.button("🔄 Atualizar Agora", use_container_width=True):
        st.cache_data.clear(); st.rerun()
    st.markdown("""<div style="background:rgba(124,58,237,.08);border-radius:10px;padding:.7rem;
                border:1px solid rgba(124,58,237,.2);margin-top:.5rem;">
        <p style="color:#A78BFA;font-size:.72rem;font-weight:600;margin:0 0 .2rem;">⏱️ ATUALIZAÇÃO AUTOMÁTICA</p>
        <p style="color:#9CA3AF;font-size:.7rem;margin:0;">A cada <b style="color:#A78BFA;">5 minutos</b></p>
    </div>""", unsafe_allow_html=True)

    # Filtros aplicados após carga — preenchidos depois de load
    clientes_sel  = []
    pagadores_sel = []

# ══════════════════════════════════════════════════════════════════════════════
# TÍTULO
# ══════════════════════════════════════════════════════════════════════════════
agora_str = datetime.now().strftime("%d/%m/%Y %H:%M")
periodo_str = (data_inicio.strftime("%d/%m/%Y") if data_inicio==data_fim
               else f"{data_inicio.strftime('%d/%m/%Y')} → {data_fim.strftime('%d/%m/%Y')}")
st.markdown(f"""
<div class="dash-title">
    <h1>🚚 Dashboard Distribuição — Tempo Real</h1>
    <p>📅 {periodo_str} &nbsp;·&nbsp; Atualizado: {agora_str}</p>
</div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# CARGA + TRANSFORMAÇÃO
# ══════════════════════════════════════════════════════════════════════════════
with st.spinner("⏳ Buscando dados no banco..."):
    try:
        raw = load_data(str(data_inicio), str(data_fim))
    except Exception as e:
        st.error(f"❌ Erro ao conectar: `{e}`")
        st.info("💡 Verifique o banco e as credenciais em `.streamlit/secrets.toml`")
        st.stop()

df_all = transform(raw)

if df_all.empty:
    st.warning("📭 Nenhum manifesto encontrado para o período selecionado.")
    st.stop()

# ── Filtros pós-carga na sidebar ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("---")
    st.markdown("**🏢 Bases**")
    lista_cli = sorted(df_all["ds_Cliente"].dropna().unique().tolist())
    clientes_sel = st.multiselect("Selecione (vazio = todos)", options=lista_cli,
                                  placeholder="Todas as bases")

    st.markdown("**💼 Cliente Pagador**")
    lista_pag = sorted(df_all["Pagador"].dropna().unique().tolist())
    pagadores_sel = st.multiselect("Selecione (vazio = todos)", options=lista_pag,
                                   placeholder="Todos os pagadores", key="pag")
    st.markdown("---")
    st.markdown("""
    <div style="background:rgba(59,130,246,.08);border-radius:10px;padding:.7rem;
                border:1px solid rgba(59,130,246,.15);">
        <p style="color:#60A5FA;font-size:.72rem;font-weight:600;margin:0 0 .3rem;">ℹ️ LEGENDA</p>
        <p style="color:#34D399;font-size:.7rem;margin:.1rem 0;">● ENTREGUE / COLETADA = Realizado</p>
        <p style="color:#FBBF24;font-size:.7rem;margin:.1rem 0;">● NÃO ENTREGUE / NÃO COLETADA = Pendente</p>
    </div>""", unsafe_allow_html=True)

# Aplicar filtros
df = df_all.copy()
if clientes_sel:  df = df[df["ds_Cliente"].isin(clientes_sel)]
if pagadores_sel: df = df[df["Pagador"].isin(pagadores_sel)]

# ══════════════════════════════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════════════════════════════
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Visão Geral", "🔍 Análise de Pendentes",
    "🚦 Farol de Serviços", "🚨 Em Atraso",
    "🚗 Por Motorista", "📄 Tabela Completa",
])

# ─────────────────────────────────────────────────────────────────────────────
# TAB 1 — VISÃO GERAL
# ─────────────────────────────────────────────────────────────────────────────
with tab1:
    total      = len(df)
    realizados = len(df[df["Classificacao"]=="Realizado"])
    pendentes  = len(df[df["Classificacao"]=="Pendente"])
    pct_real   = realizados/total*100 if total else 0
    pct_pend   = pendentes/total*100  if total else 0
    frete_tot  = df["vl_Frete"].sum()

    c1,c2,c3,c4 = st.columns(4)
    with c1: st.markdown(kpi("📦","Total de Serviços",f"{total:,}","coletas + entregas","total"), unsafe_allow_html=True)
    with c2: st.markdown(kpi("✅","Realizados",f"{realizados:,}",f"{pct_real:.1f}% do total","realizado"), unsafe_allow_html=True)
    with c3: st.markdown(kpi("⏳","Pendentes",f"{pendentes:,}",f"{pct_pend:.1f}% do total","pendente"), unsafe_allow_html=True)
    with c4: st.markdown(kpi("💰","Frete Total",fmt_brl(frete_tot),"valor acumulado","frete"), unsafe_allow_html=True)

    st.markdown("<div style='height:.6rem'></div>", unsafe_allow_html=True)

    # Donut + Barras situação
    g1,g2 = st.columns([1,1.3])
    sit_c = df["Situacao"].value_counts().reset_index()
    sit_c.columns = ["Situacao","Qtd"]
    colors = [SITUACAO_COLORS.get(s,"#7C3AED") for s in sit_c["Situacao"]]

    with g1:
        st.markdown('<div class="sec-header">🍩 Realizados vs Pendentes</div>', unsafe_allow_html=True)
        fig_d = go.Figure(go.Pie(
            labels=sit_c["Situacao"], values=sit_c["Qtd"], hole=.6,
            marker=dict(colors=colors, line=dict(color="#0A0A1A",width=3)),
            textinfo="label+percent", textfont=dict(size=12,color="#E0E0E0"),
        ))
        fig_d.update_layout(**PLOTLY_BASE, height=320, showlegend=False)
        fig_d.add_annotation(text=f"<b>{total}</b><br><span style='font-size:11px'>Total</span>",
                             x=.5,y=.5,showarrow=False,font=dict(size=22,color="#60A5FA"))
        st.plotly_chart(fig_d, use_container_width=True, config={"displayModeBar":False})

    with g2:
        st.markdown('<div class="sec-header">📊 Detalhamento por Situação</div>', unsafe_allow_html=True)
        fig_b = go.Figure(go.Bar(
            x=sit_c["Situacao"], y=sit_c["Qtd"],
            marker=dict(color=colors,cornerradius=6,line=dict(color="rgba(0,0,0,.2)",width=1)),
            text=sit_c["Qtd"], textposition="outside",
            textfont=dict(size=13,color="#E0E0E0"), cliponaxis=False,
        ))
        fig_b.update_layout(**PLOTLY_BASE, height=340,
            yaxis=dict(gridcolor="rgba(59,130,246,.08)",zeroline=False,showticklabels=False,
                       range=[0,sit_c["Qtd"].max()*1.2]),
            xaxis=dict(gridcolor="rgba(0,0,0,0)",zeroline=False))
        st.plotly_chart(fig_b, use_container_width=True, config={"displayModeBar":False})

    # Serviços por Cliente (Pagador) - Top 5 por Frete
    st.markdown('<div class="sec-header">🏢 Top 5 Clientes por Valor de Frete</div>', unsafe_allow_html=True)
    
    # Agrupar por Pagador e Classificacao
    df["vl_Frete"] = pd.to_numeric(df["vl_Frete"], errors="coerce").fillna(0)
    if "Valor_NF" in df.columns:
        df["Valor_NF"] = pd.to_numeric(df["Valor_NF"], errors="coerce").fillna(0)
    else:
        df["Valor_NF"] = 0

    # Total de frete por pagador para pegar os Top 5
    top_frete = df.groupby("Pagador")["vl_Frete"].sum().nlargest(5).index

    # Filtrar dataframe apenas para os top 5 pagadores
    df_top = df[df["Pagador"].isin(top_frete)]

    cli_c = df_top.groupby(["Pagador","Classificacao"]).agg(
        Qtd=("Pagador", "size"),
        Frete=("vl_Frete", "sum"),
        NF=("Valor_NF", "sum")
    ).reset_index()

    # Ordenar o gráfico baseado nos Top 5 (decrescente para aparecer no topo do gráfico horizontal)
    cli_c["Pagador"] = pd.Categorical(cli_c["Pagador"], categories=top_frete[::-1], ordered=True)
    cli_c = cli_c.sort_values("Pagador")

    # Formatar hover text (moeda BR)
    def _hover(row):
        f_val = f"R$ {row['Frete']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        nf_val = f"R$ {row['NF']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return f"Qtd: {row['Qtd']}<br>Frete: {f_val}<br>NF: {nf_val}"

    cli_c["Hover"] = cli_c.apply(_hover, axis=1)

    fig_cli = px.bar(cli_c, x="Frete", y="Pagador", color="Classificacao", orientation="h",
                     hover_data=["Hover"],
                     color_discrete_map={"Realizado":"#34D399","Pendente":"#FBBF24"},
                     labels={"Pagador":"Cliente","Frete":"Valor Frete (R$)","Classificacao":"Status"})
    
    fig_cli.update_traces(hovertemplate="%{customdata[0]}")
    
    fig_cli.update_layout(**PLOTLY_BASE,
        height=320,
        yaxis=dict(gridcolor="rgba(0,0,0,0)",zeroline=False,tickfont=dict(size=11)),
        xaxis=dict(gridcolor="rgba(59,130,246,.06)",zeroline=False),
        legend=dict(orientation="h",y=-0.1,bgcolor="rgba(17,17,37,.8)"))
    st.plotly_chart(fig_cli, use_container_width=True, config={"displayModeBar":False})

    # Categoria CONVENCIONAL vs PRIORITÁRIO
    st.markdown('<div class="sec-header">🔷 Convencional vs Prioritário</div>', unsafe_allow_html=True)
    cat_c = df["Categoria_Servico"].value_counts().reset_index()
    cat_c.columns = ["Categoria","Qtd"]
    cat_colors = {"CONVENCIONAL":"#3B82F6","PRIORITÁRIO":"#F59E0B"}
    fig_cat = go.Figure(go.Bar(
        x=cat_c["Categoria"], y=cat_c["Qtd"],
        marker=dict(color=[cat_colors.get(c,"#7C3AED") for c in cat_c["Categoria"]],
                    cornerradius=6,line=dict(color="rgba(0,0,0,.2)",width=1)),
        text=cat_c["Qtd"], textposition="outside",
        textfont=dict(size=13,color="#E0E0E0"), cliponaxis=False,
    ))
    fig_cat.update_layout(**PLOTLY_BASE, height=280,
        yaxis=dict(gridcolor="rgba(59,130,246,.08)",zeroline=False,showticklabels=False,
                   range=[0,cat_c["Qtd"].max()*1.2]),
        xaxis=dict(gridcolor="rgba(0,0,0,0)",zeroline=False))
    st.plotly_chart(fig_cat, use_container_width=True, config={"displayModeBar":False})

    # Lista de Serviços Prioritários
    st.markdown('<div class="sec-header">🚨 Casos Prioritários</div>', unsafe_allow_html=True)
    df_prio = df[df["Categoria_Servico"] == "PRIORITÁRIO"].copy()
    if df_prio.empty:
        st.info("Nenhum serviço prioritário no momento.")
    else:
        df_prio["Ord"] = df_prio["Classificacao"].apply(lambda x: 0 if x=="Pendente" else 1)
        df_prio = df_prio.sort_values(["Ord", "Prazo"])
        
        cols_prio = ["ID_Pedido_Coleta", "ds_Cliente", "Situacao", "Prazo", "Cidade", "Motorista", "Tipo_Servico"]
        av_prio = [c for c in cols_prio if c in df_prio.columns]
        st.dataframe(df_prio[av_prio].rename(columns={
            "ID_Pedido_Coleta": "Nº Pedido / Ref",
            "ds_Cliente": "Cliente",
            "Tipo_Servico": "Tipo"
        }), use_container_width=True, height=250, hide_index=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 2 — ANÁLISE DE PENDENTES
# ─────────────────────────────────────────────────────────────────────────────
with tab2:
    df_pend = df[df["Classificacao"]=="Pendente"].copy()

    if df_pend.empty:
        st.success("🎉 Nenhum serviço pendente no período!")
    else:
        total_p  = len(df_pend)
        entr_p   = df_pend[df_pend["Situacao"]=="NÃO ENTREGUE"]
        col_p    = df_pend[df_pend["Situacao"]=="NÃO COLETADA"]

        k1,k2,k3 = st.columns(3)
        with k1: st.markdown(kpi("🚨","Total Pendentes",f"{total_p:,}","entregas + coletas","pendente"), unsafe_allow_html=True)
        with k2: st.markdown(kpi("🚚","Entregas Pendentes",f"{len(entr_p):,}",
                                 f"{len(entr_p)/total_p*100:.1f}% dos pendentes" if total_p else "—","nentregue"), unsafe_allow_html=True)
        with k3: st.markdown(kpi("📥","Coletas Pendentes",f"{len(col_p):,}",
                                 f"{len(col_p)/total_p*100:.1f}% dos pendentes" if total_p else "—","ncoleta"), unsafe_allow_html=True)

        st.markdown("<div style='height:.5rem'></div>", unsafe_allow_html=True)

        ce, cc = st.columns(2)
        with ce:
            st.markdown('<div class="sec-header">🚚 Entregas Pendentes por Cidade Destino</div>', unsafe_allow_html=True)
            if not entr_p.empty:
                c_ent = entr_p["Cidade"].fillna("NÃO INFORMADO").value_counts().reset_index()
                c_ent.columns = ["Cidade","Qtd"]
                st.plotly_chart(bar_h(c_ent,"Cidade","Qtd","",color="#3B82F6"),
                                use_container_width=True, config={"displayModeBar":False})
            else: st.info("Nenhuma entrega pendente.")

        with cc:
            st.markdown('<div class="sec-header">📥 Coletas Pendentes por Cidade Origem</div>', unsafe_allow_html=True)
            if not col_p.empty:
                c_col = col_p["Cidade"].fillna("NÃO INFORMADO").value_counts().reset_index()
                c_col.columns = ["Cidade","Qtd"]
                st.plotly_chart(bar_h(c_col,"Cidade","Qtd","",color="#A78BFA"),
                                use_container_width=True, config={"displayModeBar":False})
            else: st.info("Nenhuma coleta pendente.")

        st.markdown('<div class="sec-header">👤 Serviços Não Realizados por Motorista</div>', unsafe_allow_html=True)
        mot_p = df_pend["Motorista"].fillna("NÃO INFORMADO").value_counts().reset_index()
        mot_p.columns = ["Motorista","Qtd"]
        st.plotly_chart(bar_h(mot_p,"Motorista","Qtd","",color="#FBBF24"),
                        use_container_width=True, config={"displayModeBar":False})

        st.markdown('<div class="sec-header">📄 Detalhamento dos Pendentes</div>', unsafe_allow_html=True)
        cols_p = ["ds_Cliente","Motorista","Tipo_Servico","Situacao","Categoria_Servico",
                  "Cidade","UF","Prazo","Pagador","Detalhe_Ocorrencia"]
        av_p = [c for c in cols_p if c in df_pend.columns]
        st.dataframe(df_pend[av_p].rename(columns={"ds_Cliente":"Cliente",
                                                     "Tipo_Servico":"Coleta/Entrega",
                                                     "Categoria_Servico":"Categoria"}),
                     use_container_width=True, height=420, hide_index=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 3 — FAROL DE SERVIÇOS
# ─────────────────────────────────────────────────────────────────────────────
with tab3:
    df_farol = df[df["Farol"].notna()].copy()

    n_v = len(df_farol[df_farol["Farol"]=="VERMELHO"])
    n_a = len(df_farol[df_farol["Farol"]=="AMARELO"])
    n_g = len(df_farol[df_farol["Farol"]=="VERDE"])

    f1,f2,f3,f4 = st.columns(4)
    with f1: st.markdown(kpi("🚦","Serviços no Farol",f"{len(df_farol):,}","pendentes com prazo","total"), unsafe_allow_html=True)
    with f2: st.markdown(kpi("🔴","Vermelho",f"{n_v:,}","prazo já venceu","vermelho"), unsafe_allow_html=True)
    with f3: st.markdown(kpi("🟡","Amarelo",f"{n_a:,}","vence hoje","amarelo"), unsafe_allow_html=True)
    with f4: st.markdown(kpi("🟢","Verde",f"{n_g:,}","dentro do prazo","verde"), unsafe_allow_html=True)

    st.markdown("<div style='height:.5rem'></div>", unsafe_allow_html=True)

    if df_farol.empty:
        st.success("✅ Nenhum serviço com prazo no farol!")
    else:
        # Farol por cliente
        st.markdown('<div class="sec-header">🏢 Farol por Cliente</div>', unsafe_allow_html=True)
        far_cli = df_farol.groupby(["ds_Cliente","Farol"]).size().reset_index(name="Qtd")
        fig_fc = px.bar(far_cli, x="Qtd", y="ds_Cliente", color="Farol", orientation="h",
                        color_discrete_map={"VERMELHO":"#F87171","AMARELO":"#FBBF24","VERDE":"#34D399"},
                        labels={"ds_Cliente":"Cliente","Qtd":"Qtd"})
        fig_fc.update_layout(**PLOTLY_BASE,
            height=max(300, df_farol["ds_Cliente"].nunique()*45),
            yaxis=dict(autorange="reversed",gridcolor="rgba(0,0,0,0)",zeroline=False,tickfont=dict(size=11)),
            xaxis=dict(gridcolor="rgba(59,130,246,.06)",zeroline=False),
            legend=dict(orientation="h",y=-0.1,bgcolor="rgba(17,17,37,.8)"))
        st.plotly_chart(fig_fc, use_container_width=True, config={"displayModeBar":False})

        # Painel de prioridades (Vermelho + Amarelo)
        df_crit = df_farol[df_farol["Farol"].isin(["VERMELHO","AMARELO"])].sort_values("Prazo")
        if not df_crit.empty:
            st.markdown('<div class="sec-header">🚨 Prioridades — Vermelho e Amarelo</div>', unsafe_allow_html=True)
            html = ""
            for _, row in df_crit.head(30).iterrows():
                fc = "fb-v" if row["Farol"]=="VERMELHO" else "fb-a"
                emoji = "🔴" if row["Farol"]=="VERMELHO" else "🟡"
                prazo = row["Prazo"].strftime("%d/%m %H:%M") if pd.notna(row["Prazo"]) else "—"
                cliente = str(row.get("ds_Cliente",""))[:25]
                cidade  = str(row.get("Cidade",""))
                pedido  = str(row.get("ID_Pedido_Coleta","") or "—")
                html += f"""<div class="alert-card">
                    <div><div class="c-name">{emoji} {cliente}</div>
                    <div class="c-info">Prazo: {prazo} &nbsp;·&nbsp; {cidade} &nbsp;·&nbsp; {row['Situacao']}</div>
                    <div class="c-ref" style="font-size:0.75rem; color:#A78BFA; margin-top:4px;">🔖 Pedido/Ref: {pedido}</div></div>
                    <span class="farol-badge {fc}">{row['Farol']}</span></div>"""
            st.markdown(f'<div style="max-height:500px;overflow-y:auto;">{html}</div>',
                        unsafe_allow_html=True)

        st.markdown('<div class="sec-header">📄 Tabela Farol Completo</div>', unsafe_allow_html=True)
        cols_f = ["ds_Cliente","Motorista","Tipo_Servico","Situacao","Cidade","UF","Prazo","Farol","Pagador"]
        av_f = [c for c in cols_f if c in df_farol.columns]
        st.dataframe(df_farol[av_f].rename(columns={"ds_Cliente":"Cliente","Tipo_Servico":"Tipo"}),
                     use_container_width=True, height=400, hide_index=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 4 — EM ATRASO
# ─────────────────────────────────────────────────────────────────────────────
with tab4:
    agora_ts = pd.Timestamp.now()
    df_atr = df[
        (df["Classificacao"]=="Pendente") &
        (df["Prazo"].notna()) &
        (df["Prazo"] < agora_ts)
    ].sort_values("Prazo").copy()

    a1,a2,a3 = st.columns(3)
    with a1: st.markdown(kpi("🚨","Total em Atraso",f"{len(df_atr):,}","prazo já venceu","vermelho"), unsafe_allow_html=True)
    with a2:
        atr_ent = df_atr[df_atr["Situacao"]=="NÃO ENTREGUE"]
        st.markdown(kpi("🚚","Entregas Atrasadas",f"{len(atr_ent):,}","não entregues","nentregue"), unsafe_allow_html=True)
    with a3:
        atr_col = df_atr[df_atr["Situacao"]=="NÃO COLETADA"]
        st.markdown(kpi("📥","Coletas Atrasadas",f"{len(atr_col):,}","não coletadas","ncoleta"), unsafe_allow_html=True)

    st.markdown("<div style='height:.5rem'></div>", unsafe_allow_html=True)

    if df_atr.empty:
        st.success("✅ Nenhum serviço em atraso no momento!")
    else:
        st.markdown(f'<div class="sec-header">🚨 Alertas — Prazo Vencido ({len(df_atr)} registros)</div>',
                    unsafe_allow_html=True)
        html_a = ""
        for _, row in df_atr.iterrows():
            prazo  = row["Prazo"].strftime("%d/%m %H:%M") if pd.notna(row["Prazo"]) else "—"
            cliente = str(row.get("ds_Cliente","N/A") or "N/A")
            cidade  = str(row.get("Cidade","N/A") or "N/A")
            motor   = str(row.get("Motorista","") or "")
            sit     = str(row.get("Situacao",""))
            pedido  = str(row.get("ID_Pedido_Coleta","") or "—")
            html_a += f"""<div class="alert-card">
                <div>
                    <div class="c-name">⚠️ {cliente}</div>
                    <div class="c-info">Prazo: {prazo} &nbsp;·&nbsp; {cidade} &nbsp;·&nbsp; {sit} &nbsp;·&nbsp; Motorista: {motor}</div>
                    <div class="c-ref">🔖 Pedido/Ref: {pedido}</div>
                </div>
                <span style="color:#FCA5A5;font-weight:700;font-size:.8rem;">ATRASADO</span>
            </div>"""
        st.markdown(f'<div style="max-height:500px;overflow-y:auto;">{html_a}</div>',
                    unsafe_allow_html=True)

        # Atrasos por cliente
        st.markdown('<div class="sec-header">📊 Atrasos por Cliente</div>', unsafe_allow_html=True)
        atr_cli = df_atr["ds_Cliente"].fillna("N/A").value_counts().reset_index()
        atr_cli.columns = ["Cliente","Qtd"]
        st.plotly_chart(bar_h(atr_cli,"Cliente","Qtd","",color="#F87171"),
                        use_container_width=True, config={"displayModeBar":False})

        st.markdown('<div class="sec-header">📄 Detalhamento dos Atrasos</div>', unsafe_allow_html=True)
        cols_a = ["ID_Pedido_Coleta","ds_Cliente","Motorista","Tipo_Servico","Situacao","Cidade","UF","Prazo","Pagador","Detalhe_Ocorrencia"]
        av_a   = [c for c in cols_a if c in df_atr.columns]
        st.dataframe(df_atr[av_a].rename(columns={"ID_Pedido_Coleta":"Pedido/Ref","ds_Cliente":"Cliente","Tipo_Servico":"Tipo"}),
                     use_container_width=True, height=400, hide_index=True)

        csv_a = df_atr[av_a].rename(columns={"ID_Pedido_Coleta":"Pedido/Ref","ds_Cliente":"Cliente","Tipo_Servico":"Tipo"}
                       ).to_csv(index=False, sep=";", decimal=",").encode("utf-8")
        st.download_button("⬇️ Baixar Atrasos CSV", data=csv_a,
                           file_name=f"atrasos_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                           mime="text/csv", use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 5 — POR MOTORISTA
# ─────────────────────────────────────────────────────────────────────────────
with tab5:
    st.markdown('<div class="sec-header">🚗 Serviços por Motorista</div>', unsafe_allow_html=True)
    mot_df  = df.groupby(["Motorista","Classificacao"]).size().reset_index(name="Qtd")
    mot_tot = df.groupby("Motorista").size().reset_index(name="Total").sort_values("Total",ascending=False)

    fig_m = px.bar(mot_df, x="Qtd", y="Motorista", color="Classificacao", orientation="h",
                   color_discrete_map={"Realizado":"#34D399","Pendente":"#FBBF24"},
                   labels={"Motorista":"Motorista","Qtd":"Qtd","Classificacao":"Status"})
    fig_m.update_layout(**PLOTLY_BASE,
        height=max(350, len(mot_tot)*48),
        yaxis=dict(autorange="reversed",gridcolor="rgba(0,0,0,0)",zeroline=False,tickfont=dict(size=11)),
        xaxis=dict(gridcolor="rgba(59,130,246,.06)",zeroline=False),
        legend=dict(orientation="h",y=-0.1,bgcolor="rgba(17,17,37,.8)"))
    st.plotly_chart(fig_m, use_container_width=True, config={"displayModeBar":False})

    st.markdown('<div class="sec-header">📋 Resumo por Motorista</div>', unsafe_allow_html=True)
    try:
        piv = df.pivot_table(index="Motorista",columns="Situacao",values="id_Manifesto",
                             aggfunc="count",fill_value=0).reset_index()
        piv["Total"] = piv.drop(columns="Motorista").sum(axis=1)
        st.dataframe(piv.sort_values("Total",ascending=False),
                     use_container_width=True, height=400, hide_index=True)
    except Exception:
        st.dataframe(mot_tot, use_container_width=True, height=400, hide_index=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 6 — TABELA COMPLETA
# ─────────────────────────────────────────────────────────────────────────────
with tab6:
    st.markdown('<div class="sec-header">🔍 Filtros Adicionais</div>', unsafe_allow_html=True)
    tf1,tf2,tf3 = st.columns(3)
    with tf1:
        opts_sit = ["Todas"]+sorted(df["Situacao"].dropna().unique().tolist())
        sel_sit  = st.selectbox("Situação", opts_sit, key="ts")
    with tf2:
        opts_tip = ["Todos"]+sorted(df["Categoria_Servico"].dropna().unique().tolist())
        sel_tip  = st.selectbox("Categoria", opts_tip, key="tt")
    with tf3:
        opts_mot = ["Todos"]+sorted(df["Motorista"].dropna().unique().tolist())
        sel_mot  = st.selectbox("Motorista", opts_mot, key="tm")

    df_tab = df.copy()
    if sel_sit!="Todas": df_tab = df_tab[df_tab["Situacao"]==sel_sit]
    if sel_tip!="Todos": df_tab = df_tab[df_tab["Categoria_Servico"]==sel_tip]
    if sel_mot!="Todos": df_tab = df_tab[df_tab["Motorista"]==sel_mot]

    st.markdown(f'<div class="sec-header">📄 {len(df_tab):,} registros encontrados</div>',
                unsafe_allow_html=True)
    show = ["id_Manifesto","ds_Cliente","Motorista","Tipo_Servico","Situacao","Classificacao",
            "Categoria_Servico","Cidade","UF","Prazo","vl_Frete","Pagador",
            "Destinatario_Remetente","Detalhe_Ocorrencia","nr_NotaFiscal","cd_Placa"]
    av   = [c for c in show if c in df_tab.columns]
    ren  = {"id_Manifesto":"Manifesto","ds_Cliente":"Cliente","Tipo_Servico":"Tipo",
            "Categoria_Servico":"Categoria","vl_Frete":"Frete(R$)","Classificacao":"Status"}
    st.dataframe(df_tab[av].rename(columns=ren), use_container_width=True, height=500, hide_index=True)

    csv = df_tab[av].rename(columns=ren).to_csv(index=False,sep=";",decimal=",").encode("utf-8")
    st.download_button("⬇️ Baixar CSV", data=csv,
                       file_name=f"dashboard_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                       mime="text/csv", use_container_width=True)
