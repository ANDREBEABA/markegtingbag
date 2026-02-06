import streamlit as st
import pandas as pd

st.set_page_config(page_title="DRE Detalhado", layout="wide")

# Dados de Custos Reais
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

st.title("📊 Gestão Financeira da Campanha")
st.markdown("---")

# Sidebar - Parâmetros
st.sidebar.header("Parâmetros da Campanha")
tamanho = st.sidebar.selectbox("Tamanho do Saquinho", list(dados_custos.keys()))
tiragem = st.sidebar.selectbox("Tiragem", list(dados_custos[tamanho]["precos"].keys()))
duracao = st.sidebar.selectbox("Duração (meses)", [1, 3])
preco_venda = st.sidebar.number_input("Preço de Venda/Módulo (R$)", min_value=0.0, value=500.0)

# Definição dos Custos Fixos (Conforme sua solicitação)
frete_total = 600.00
royalties_mensal = 399.00
mei_mensal = 81.00
gasolina_mensal = 500.00
outros_mensal = 200.00

# Variáveis de Produção
mod_por_mes = dados_custos[tamanho]["modulos"]
custo_prod = dados_custos[tamanho]["precos"][tiragem]

# Construção do DRE Mensal
dados_dre = []
faturamento_acumulado = 0
custo_acumulado = 0

for mes in range(1, duracao + 1):
    receita_mes = mod_por_mes * preco_venda
    
    # Custo de produção e frete apenas no Mês 1
    c_prod = custo_prod if mes == 1 else 0
    c_frete = frete_total if mes == 1 else 0
    
    # Custos fixos recorrentes
    c_roy = royalties_mensal
    c_mei = mei_mensal
    c_gas = gasolina_mensal
    c_out = outros_mensal
    
    total_custos_mes = c_prod + c_frete + c_roy + c_mei + c_gas + c_out
    lucro_mes = receita_mes - total_custos_mes
    
    dados_dre.append({
        "Mês": f"Mês {mes}",
        "Receita (R$)": receita_mes,
        "Produção (R$)": c_prod,
        "Frete (R$)": c_frete,
        "Royalties (R$)": c_roy,
        "MEI (R$)": c_mei,
        "Gasolina (R$)": c_gas,
        "Outros (R$)": c_out,
        "Lucro Líquido (R$)": lucro_mes
    })
    
    faturamento_acumulado += receita_mes
    custo_acumulado += total_custos_mes

# --- EXIBIÇÃO ---

# Resumo em Cartões
c1, c2, c3 = st.columns(3)
c1.metric("Faturamento Total", f"R$ {faturamento_acumulado:,.2f}")
c2.metric("Investimento Total", f"R$ {custo_acumulado:,.2f}")
lucro_final = faturamento_acumulado - custo_acumulado
c3.metric("Lucro Final", f"R$ {lucro_final:,.2f}", delta=f"{(lucro_final/faturamento_acumulado*100):.1f}%")

st.subheader("📋 Demonstrativo de Resultado (DRE) Detalhado")

# Transformar em DataFrame para mostrar a tabela
df_dre = pd.DataFrame(dados_dre)
st.table(df_dre.style.format({
    "Receita (R$)": "{:,.2f}",
    "Produção (R$)": "{:,.2f}",
    "Frete (R$)": "{:,.2f}",
    "Royalties (R$)": "{:,.2f}",
    "MEI (R$)": "{:,.2f}",
    "Gasolina (R$)": "{:,.2f}",
    "Outros (R$)": "{:,.2f}",
    "Lucro Líquido (R$)": "{:,.2f}"
}))

# Ponto de Equilíbrio
pe_unidades = custo_acumulado / preco_venda
st.warning(f"📌 **Ponto de Equilíbrio:** O franqueado precisa vender um total de **{pe_unidades:.1f} módulos** ao longo da campanha para cobrir todos os custos listados.")
