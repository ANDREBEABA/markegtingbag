import streamlit as st
import pandas as pd

st.set_page_config(page_title="Simulador de Campanhas Profissional", layout="wide")

# Tabela de Custos Reais (Anexo 1)
dados_custos = {
    "5kg (36 Módulos)": {
        "modulos": 36,
        "precos": {10000: 4531.50, 15000: 5177.10, 20000: 6319.60, 30000: 8306.40,
                   40000: 9744.40, 50000: 12180.50, 100000: 20663.00, 200000: 40928.00}
    },
    "4kg (32 Módulos)": {
        "modulos": 32,
        "precos": {20000: 5225.00, 30000: 7122.30, 40000: 9496.40, 
                   50000: 10066.50, 100000: 17069.00, 200000: 33810.00}
    }
}

st.title("📊 Simulador de Precificação e DRE")
st.markdown("---")

# --- SIDEBAR: CONFIGURAÇÕES ---
st.sidebar.header("⚙️ Parâmetros Base")
tamanho = st.sidebar.selectbox("Tamanho do Saquinho", list(dados_custos.keys()))
tiragem = st.sidebar.selectbox("Tiragem (unidades)", list(dados_custos[tamanho]["precos"].keys()))
duracao = st.sidebar.selectbox("Duração da Campanha", [1, 3, 6], format_func=lambda x: f"{x} meses")

st.sidebar.markdown("---")
st.sidebar.header("💰 Estratégia de Preço")
# Margem Alvo começando em 0% como solicitado
margem_alvo = st.sidebar.slider("Margem de Lucro Alvo (%)", 0, 80, 30)
comissao_percent = st.sidebar.slider("Comissão do Representante (%)", 0, 30, 10)

# --- CUSTOS FIXOS E SETUP ---
C_ROY, C_MEI, C_GAS, C_OUT, C_FRETE = 399.00, 81.00, 500.00, 200.00, 600.00
mod_max = dados_custos[tamanho]["modulos"]
custo_prod = dados_custos[tamanho]["precos"][tiragem]

# --- LÓGICA DE SUGESTÃO DE PREÇO (VALOR TOTAL) ---
# 1. Custo total acumulado no período
custo_total_periodo = custo_prod + C_FRETE + ((C_ROY + C_MEI + C_GAS + C_OUT) * duracao)
# 2. Sugestão de Preço TOTAL por módulo para atingir a margem alvo
# Fórmula de Markup Divisor aplicada sobre o custo total do período
preco_total_sugerido = (custo_total_periodo / mod_max) / (1 - (margem_alvo / 100)) if margem_alvo < 100 else 0

# --- INPUT DO VALOR DE VENDA TOTAL ---
st.sidebar.markdown(f"**Sugestão de Venda Total: R$ {preco_total_sugerido:,.2f}**")
v_total_venda = st.sidebar.number_input(f"Valor Total da Venda por Módulo ({duracao} meses)", min_value=0.0, value=float(preco_total_sugerido))

# Valor mensal para o cálculo do DRE
v_mensal_venda = v_total_venda / duracao

# --- PROCESSAMENTO DO DRE ---
indices = [
    "Faturamento Bruto", 
    "(-) Produção", 
    "(-) Frete", 
    "(-) Royalties", 
    "(-) MEI", 
    "(-) Gasolina", 
    "(-) Outros Custos", 
    "(-) Comissão Representante", 
    "LUCRO LÍQUIDO"
]
df_dre = pd.DataFrame(index=indices)

for i in range(1, duracao + 1):
    receita_mes = mod_max * v_mensal_venda
    comis_mes = receita_mes * (comissao_percent / 100)
    p_prod = custo_prod if i == 1 else 0.0
    p_frete = C_FRETE if i == 1 else 0.0
    
    total_despesas_mes = p_prod + p_frete + C_ROY + C_MEI + C_GAS + C_OUT + comis_mes
    lucro_mes = receita_mes - total_despesas_mes
    
    df_dre[f"Mês {i}"] = [
        receita_mes, p_prod, p_frete, C_ROY, C_MEI, C_GAS, C_OUT, comis_mes, lucro_mes
    ]

# Coluna de Total Acumulado
df_dre["TOTAL ACUMULADO"] = df_dre.sum(axis=1)

# --- PONTO DE EQUILÍBRIO FINANCEIRO (Mês 1) ---
# Custos que precisam ser pagos no Mês 1
custos_setup_fixos_mes1 = custo_prod + C_FRETE + C_ROY + C_MEI + C_GAS + C_OUT
# Faturamento bruto necessário no Mês 1 para lucro zero (considerando comissão)
faturamento_pe_mes1 = custos_setup_fixos_mes1 / (1 - (comissao_percent / 100))

# --- FORMATAÇÃO E CORES ---
def highlight_lucro(val):
    if isinstance(val, (int, float)):
        color = '#90EE90' if val >= 0 else '#FFB6C1' # Verde ou Vermelho claro
        return f'background-color: {color}'
    return ''

st.subheader(f"📋 DRE Detalhado - Campanha {duracao} meses")
styled_df = df_dre.style.format("{:,.2f}")\
    .applymap(highlight_lucro, subset=pd.IndexSlice[['LUCRO LÍQUIDO'], :])

st.dataframe(styled_df, use_container_width=True)

# --- DASHBOARD DE MÉTRICAS ---
st.markdown("---")
c1, c2, c3 = st.columns(3)

with c1:
    st.metric("Venda Sugerida (Total)", f"R$ {preco_total_sugerido:,.2f}")
    st.caption(f"Valor total por módulo para {duracao} meses")

with c2:
    st.metric("Ponto Equilíbrio (Mês 1)", f"R$ {faturamento_pe_mes1:,.2f}")
    st.caption("Faturamento bruto necessário no 1º mês")

with c3:
    lucro_total = df_dre.loc["LUCRO LÍQUIDO", "TOTAL ACUMULADO"]
    st.metric("Lucro Líquido Final", f"R$ {lucro_total:,.2f}")
    st.caption(f"Resultado acumulado da campanha")

# Botão de Download
csv = df_dre.to_csv().encode('utf-8')
st.download_button("📥 Baixar Relatório (CSV)", data=csv, file_name='dre_campanha.csv', mime='text/csv')
