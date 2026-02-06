import streamlit as st
import pandas as pd

st.set_page_config(page_title="Simulador Financeiro de Franquia", layout="wide")

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

st.title("📊 Calculadora de Margem e Viabilidade")
st.markdown("---")

# --- SIDEBAR: CONFIGURAÇÕES ---
st.sidebar.header("⚙️ Configurações da Campanha")
tamanho = st.sidebar.selectbox("Tamanho do Saquinho", list(dados_custos.keys()))
tiragem = st.sidebar.selectbox("Tiragem (unidades)", list(dados_custos[tamanho]["precos"].keys()))
duracao = st.sidebar.selectbox("Duração da Campanha", [1, 3, 6], format_func=lambda x: f"{x} meses")

st.sidebar.markdown("---")
st.sidebar.header("💰 Entrada de Valores")
# Valor total inserido manualmente pelo franqueado
v_total_venda_input = st.sidebar.number_input(f"Valor Total do Contrato por Módulo (R$)", min_value=0.0, value=1500.0, step=50.0)
comissao_percent = st.sidebar.slider("Comissão do Representante (%)", 0, 30, 10)

# --- CUSTOS FIXOS E SETUP ---
C_ROY, C_MEI, C_GAS, C_OUT, C_FRETE = 399.00, 81.00, 500.00, 200.00, 600.00
mod_max = dados_custos[tamanho]["modulos"]
custo_prod = dados_custos[tamanho]["precos"][tiragem]
v_mensal_venda = v_total_venda_input / duracao

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
    p_prod_mes = custo_prod if i == 1 else 0.0
    p_frete_mes = C_FRETE if i == 1 else 0.0
    
    lucro_mes = receita_mes - (p_prod_mes + p_frete_mes + C_ROY + C_MEI + C_GAS + C_OUT + comis_mes)
    
    df_dre[f"Mês {i}"] = [
        receita_mes, p_prod_mes, p_frete_mes, C_ROY, C_MEI, C_GAS, C_OUT, comis_mes, lucro_mes
    ]

# Coluna de Total Acumulado
df_dre["TOTAL ACUMULADO"] = df_dre.sum(axis=1)

# --- CÁLCULOS DE RESULTADO ---
faturamento_total_campanha = df_dre.loc["Faturamento Bruto", "TOTAL ACUMULADO"]
lucro_total_campanha = df_dre.loc["LUCRO LÍQUIDO", "TOTAL ACUMULADO"]
margem_real = (lucro_total_campanha / faturamento_total_campanha * 100) if faturamento_total_campanha > 0 else 0

# Ponto de Equilíbrio Financeiro (Baseado no Mês 1)
custos_setup_fixos_mes1 = custo_prod + C_FRETE + C_ROY + C_MEI + C_GAS + C_OUT
faturamento_pe_mes1 = custos_setup_fixos_mes1 / (1 - (comissao_percent / 100))

# --- FORMATAÇÃO E CORES ---
def highlight_lucro(val):
    if isinstance(val, (int, float)):
        color = '#90EE90' if val >= 0 else '#FFB6C1'
        return f'background-color: {color}'
    return ''

st.subheader(f"📋 DRE Comparativo - {tamanho} / {tiragem} un. / {duracao} meses")
styled_df = df_dre.style.format("{:,.2f}")\
    .applymap(highlight_lucro, subset=pd.IndexSlice[['LUCRO LÍQUIDO'], :])

st.dataframe(styled_df, use_container_width=True)

# --- DASHBOARD DE MÉTRICAS ---
st.markdown("---")
c1, c2, c3 = st.columns(3)

with c1:
    st.metric("Margem Líquida Real", f"{margem_real:.1f}%")
    st.caption("Margem final acumulada do projeto")

with c2:
    st.metric("Ponto de Equilíbrio (Mês 1)", f"R$ {faturamento_pe_mes1:,.2f}")
    st.caption("Faturamento necessário no 1º mês p/ lucro zero")

with c3:
    st.metric("Lucro Líquido Total", f"R$ {lucro_total_campanha:,.2f}")
    st.caption("Valor final que sobra no bolso")

# Alerta de Viabilidade do Mês 1
lucro_mes1 = df_dre.loc["LUCRO LÍQUIDO", "Mês 1"]
if lucro_mes1 >= 0:
    st.success(f"✅ Operação Saudável: O primeiro mês já gera lucro positivo!")
else:
    st.warning(f"⚠️ Atenção ao Caixa: O Mês 1 terá um déficit de R$ {abs(lucro_mes1):,.2f}.")

# --- BOTÃO DE DOWNLOAD (APENAS CSV) ---
st.markdown("---")
csv = df_dre.to_csv().encode('utf-8')
st.download_button(
    label="📊 Baixar Relatório DRE (CSV/Excel)",
    data=csv,
    file_name='dre_campanha_franquia.csv',
    mime='text/csv',
    use_container_width=True
)
