import streamlit as st
import pandas as pd

st.set_page_config(page_title="DRE Mensal de Campanhas", layout="wide")

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

st.title("📊 DRE Detalhado e Mensal")
st.markdown("---")

# Configurações na Sidebar
st.sidebar.header("Parâmetros")
tamanho = st.sidebar.selectbox("Tamanho do Saquinho", list(dados_custos.keys()))
tiragem = st.sidebar.selectbox("Tiragem", list(dados_custos[tamanho]["precos"].keys()))
duracao = st.sidebar.selectbox("Duração da Campanha (meses)", [1, 3])
preco_venda = st.sidebar.number_input("Preço de Venda por Módulo (R$)", min_value=0.0, value=500.0)

# Cálculos Base
mod_por_mes = dados_custos[tamanho]["modulos"]
custo_prod = dados_custos[tamanho]["precos"][tiragem]
frete = 600.00
fixo_mensal = 399 + 81 + 500 + 200 # Royalties, MEI, Gasolina, Outros

# Lógica Mensal para a Tabela DRE
lista_dre = []
faturamento_total = 0
custo_total_acumulado = 0

for mes in range(1, duracao + 1):
    receita_mes = mod_por_mes * preco_venda
    
    # Custos do Mês
    c_prod_mes = custo_prod if mes == 1 else 0
    c_frete_mes = frete if mes == 1 else 0
    c_fixo_mes = fixo_mensal
    
    total_custos_mes = c_prod_mes + c_frete_mes + c_fixo_mes
    lucro_mes = receita_mes - total_custos_mes
    
    lista_dre.append({
        "Mês": f"Mês {mes}",
        "Receita (R$)": receita_mes,
        "Custo Prod/Frete (R$)": c_prod_mes + c_frete_mes,
        "Custos Fixos (R$)": c_fixo_mes,
        "Lucro Líquido (R$)": lucro_mes
    })
    
    faturamento_total += receita_mes
    custo_total_acumulado += total_custos_mes

# Ponto de Equilíbrio
# Total de módulos vendidos na campanha inteira = mod_por_mes * duracao
total_modulos_campanha = mod_por_mes * duracao
preco_equilibrio = custo_total_acumulado / total_modulos_campanha

# --- EXIBIÇÃO ---

col1, col2, col3 = st.columns(3)
col1.metric("Faturamento Total", f"R$ {faturamento_total:,.2f}")
col2.metric("Lucro Total", f"R$ {faturamento_total - custo_total_acumulado:,.2f}")
col3.metric("Preço Mínimo (Módulo)", f"R$ {preco_equilibrio:,.2f}")

st.subheader("📅 Demonstrativo de Resultado Mensal (DRE)")
df_dre = pd.DataFrame(lista_dre)
st.table(df_dre.style.format({
    "Receita (R$)": "{:,.2f}",
    "Custo Prod/Frete (R$)": "{:,.2f}",
    "Custos Fixos (R$)": "{:,.2f}",
    "Lucro Líquido (R$)": "{:,.2f}"
}))

st.info(f"💡 **Nota:** Na campanha de {duracao} meses, o franqueado vende um total de **{total_modulos_campanha} módulos**. O ponto de equilíbrio de R$ {preco_equilibrio:,.2f} considera a diluição dos custos iniciais ao longo de todo o período.")
