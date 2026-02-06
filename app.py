import streamlit as st
import pandas as pd

st.set_page_config(page_title="Simulador Financeiro Executivo", layout="wide")

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

st.title("📊 Simulador de Campanhas - DRE e Viabilidade")
st.markdown("---")

# --- SIDEBAR: CONFIGURAÇÕES ---
st.sidebar.header("⚙️ Configurações")
tamanho = st.sidebar.selectbox("Tamanho do Saquinho", list(dados_custos.keys()))
tiragem = st.sidebar.selectbox("Tiragem (unidades)", list(dados_custos[tamanho]["precos"].keys()))
duracao = st.sidebar.selectbox("Duração da Campanha", [1, 3, 6], format_func=lambda x: f"{x} meses")

st.sidebar.markdown("---")
st.sidebar.header("🎯 Parâmetros de Venda")
margem_alvo = st.sidebar.slider("Margem de Lucro Alvo (%)", 5, 80, 30)
comissao_percent = st.sidebar.slider("Comissão do Representante (%)", 0, 25, 10)

# --- CUSTOS FIXOS E SETUP ---
C_ROY, C_MEI, C_GAS, C_OUT, C_FRETE = 399.00, 81.00, 500.00, 200.00, 600.00
custo_prod = dados_custos[tamanho]["precos"][tiragem]
mod_max = dados_custos[tamanho]["modulos"]

# --- LÓGICA DE SUGESTÃO DE PREÇO (Custo + Margem) ---
# A comissão é tratada como custo no DRE, não altera a lógica de markup da venda do módulo
custo_total_periodo = custo_prod + C_FRETE + ((C_ROY + C_MEI + C_GAS + C_OUT) * duracao)
preco_total_sugerido = (custo_total_periodo / mod_max) / (1 - (margem_alvo / 100))

# --- INPUT DO VALOR PRATICADO ---
v_total_venda = st.sidebar.number_input(f"Valor Total do Contrato (por módulo)", min_value=0.0, value=float(preco_total_sugerido))
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
    
    lucro_mes = receita_mes - (p_prod + p_frete + C_ROY + C_MEI + C_GAS + C_OUT + comis_mes)
    
    df_dre[f"Mês {i}"] = [
        receita_mes, p_prod, p_frete, C_ROY, C_MEI, C_GAS, C_OUT, comis_mes, lucro_mes
    ]

# Coluna de Total
df_dre["TOTAL ACUMULADO"] = df_dre.sum(axis=1)

# --- PONTO DE EQUILÍBRIO (MÊS 1 EM VALOR) ---
custos_fixos_setup_mes1 = custo_prod + C_FRETE + C_ROY + C_MEI + C_GAS + C_OUT
# PE financeiro: quanto vender para cobrir custos + comissão do que foi vendido
faturamento_pe_mes1 = custos_fixos_setup_mes1 / (1 - (comissao_percent / 100))

# --- FORMATAÇÃO E CORES ---
def highlight_lucro(val):
    if isinstance(val, (int, float)):
        # Verde claro para positivo, vermelho claro para negativo
        color = '#90EE90' if val >= 0 else '#FFB6C1'
        return f'background-color: {color}'
    return ''

st.subheader("📋 Demonstrativo de Resultados (DRE)")
styled_df = df_dre.style.format("{:,.2f}")\
    .applymap(highlight_lucro, subset=pd.IndexSlice[['LUCRO LÍQUIDO'], :])

st.dataframe(styled_df, use_container_width=True)

# --- MÉTRICAS DE RESUMO ---
st.markdown("---")
c1, c2, c3 = st.columns(3)

with c1:
    st.metric("Sugestão de Venda (Total)", f"R$ {preco_total_sugerido:,.2f}")
    st.caption(f"Valor para {duracao} meses (garante {margem_alvo}% de margem bruta)")

with c2:
    st.metric("Ponto Equilíbrio (Mês 1)", f"R$ {faturamento_pe_mes1:,.2f}")
    st.caption("Faturamento bruto necessário no 1º mês para pagar tudo")

with c3:
    lucro_acumulado = df_dre.loc["LUCRO LÍQUIDO", "TOTAL ACUMULADO"]
    st.metric("Lucro Líquido Final", f"R$ {lucro_acumulado:,.2f}")
    st.caption(f"Resultado total após {duracao} meses")

# Botão de Download
csv = df_dre.to_csv().encode('utf-8')
st.download_button("📥 Baixar DRE em CSV", data=csv, file_name='dre_campanha.csv', mime='text/csv')
