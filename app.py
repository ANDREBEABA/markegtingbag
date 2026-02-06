import streamlit as st
import pandas as pd

st.set_page_config(page_title="DRE Executivo", layout="wide")

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

st.title("📊 Demonstrativo de Resultados (DRE)")
st.markdown("---")

# --- SIDEBAR: INPUTS ---
st.sidebar.header("⚙️ Configurações")
tamanho = st.sidebar.selectbox("Tamanho do Saquinho", list(dados_custos.keys()))
tiragem = st.sidebar.selectbox("Tiragem (unidades)", list(dados_custos[tamanho]["precos"].keys()))
duracao = st.sidebar.selectbox("Duração da Campanha", [1, 3, 6], format_func=lambda x: f"{x} meses")
preco_venda_mensal = st.sidebar.number_input("Valor Mensal por Módulo (R$)", min_value=0.0, value=500.0)

st.sidebar.markdown("---")
st.sidebar.header("👤 Representante")
comissao_percent = st.sidebar.slider("Comissão (%)", 0, 50, 10)

# --- VALORES FIXOS ---
C_ROY = 399.00
C_MEI = 81.00
C_GAS = 500.00
C_OUT = 200.00
C_FRETE = 600.00

mod_base = dados_custos[tamanho]["modulos"]
custo_prod_base = dados_custos[tamanho]["precos"][tiragem]

# --- PREPARAÇÃO DOS DADOS (TRANSPOSTOS) ---
# Criamos um dicionário onde cada chave é uma linha do DRE
dre_data = {
    "Faturamento (Receita)": [],
    "(-) Produção": [],
    "(-) Frete": [],
    "(-) Royalties": [],
    "(-) MEI": [],
    "(-) Gasolina": [],
    "(-) Outros Custos": [],
    "(-) Comissão Representante": [],
    "LUCRO LÍQUIDO": []
}

colunas_meses = [f"Mês {i}" for i in range(1, duracao + 1)]
custo_total_acumulado = 0
faturamento_total_acumulado = 0

for i in range(1, duracao + 1):
    receita_mes = mod_base * preco_venda_mensal
    comissao_mes = receita_mes * (comissao_percent / 100)
    prod_mes = custo_prod_base if i == 1 else 0.0
    frete_mes = C_FRETE if i == 1 else 0.0
    
    despesas_mes = prod_mes + frete_mes + C_ROY + C_MEI + C_GAS + C_OUT + comissao_mes
    lucro_mes = receita_mes - despesas_mes
    
    dre_data["Faturamento (Receita)"].append(receita_mes)
    dre_data["(-) Produção"].append(prod_mes)
    dre_data["(-) Frete"].append(frete_mes)
    dre_data["(-) Royalties"].append(C_ROY)
    dre_data["(-) MEI"].append(C_MEI)
    dre_data["(-) Gasolina"].append(C_GAS)
    dre_data["(-) Outros Custos"].append(C_OUT)
    dre_data["(-) Comissão Representante"].append(comissao_mes)
    dre_data["LUCRO LÍQUIDO"].append(lucro_mes)
    
    custo_total_acumulado += despesas_mes
    faturamento_total_acumulado += receita_mes

# Criar DataFrame e adicionar coluna de Total
df_dre = pd.DataFrame(dre_data, index=colunas_meses).T
df_dre["TOTAL ACUMULADO"] = df_dre.sum(axis=1)

# --- EXIBIÇÃO ---
lucro_final = faturamento_total_acumulado - custo_total_acumulado
margem_final = (lucro_final / faturamento_total_acumulado * 100) if faturamento_total_acumulado > 0 else 0
receita_por_modulo_total = preco_venda_mensal * duracao
pe_modulos = custo_total_acumulado / receita_por_modulo_total if receita_por_modulo_total > 0 else 0

c1, c2, c3 = st.columns(3)
c1.metric("Faturamento Total", f"R$ {faturamento_total_acumulado:,.2f}")
c2.metric("Lucro Líquido Final", f"R$ {lucro_final:,.2f}", delta=f"{margem_final:.1f}% Margem")
c3.metric("Ponto de Equilíbrio", f"{pe_modulos:.1f} Módulos")

st.subheader("📋 Tabela DRE Comparativa")
st.dataframe(df_dre.style.format("{:,.2f}"), use_container_width=True)

st.info(f"""
💡 **Resumo Estratégico:**
Para esta campanha de **{duracao} meses**, o franqueado tem um custo total de **R$ {custo_total_acumulado:,.2f}**. 
Como ele tem **{mod_base} módulos** para vender, o ponto de equilíbrio é de **{pe_modulos:.1f} módulos**.
""")
