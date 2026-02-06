import streamlit as st
import pandas as pd

st.set_page_config(page_title="Simulador de Franquia", layout="wide")

# Tabela de Custos Reais
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

st.title("📈 Simulador de Campanhas e Comissões")
st.markdown("---")

# Sidebar - Parâmetros
st.sidebar.header("⚙️ Configuração")
tamanho = st.sidebar.selectbox("Tamanho do Saquinho", list(dados_custos.keys()))
tiragem = st.sidebar.selectbox("Tiragem (unidades)", list(dados_custos[tamanho]["precos"].keys()))
duracao = st.sidebar.selectbox("Duração da Campanha (meses)", [1, 3, 6])
preco_venda = st.sidebar.number_input("Preço de Venda/Módulo (R$)", min_value=0.0, value=500.0)

st.sidebar.markdown("---")
st.sidebar.header("👤 Representante")
comissao_percent = st.sidebar.slider("Comissão do Representante (%)", 0, 50, 10)

# Custos Fixos e Variáveis
frete_total = 600.00
royalties_mensal = 399.00
mei_mensal = 81.00
gasolina_mensal = 500.00
outros_mensal = 200.00
custo_prod = dados_custos[tamanho]["precos"][tiragem]
mod_por_mes = dados_custos[tamanho]["modulos"]

# Processamento do DRE Mensal
dados_dre = []
faturamento_total = 0
custo_total_acumulado = 0

for mes in range(1, duracao + 1):
    receita_mes = mod_por_mes * preco_venda
    valor_comissao = receita_mes * (comissao_percent / 100)
    
    # Investimento inicial (Mês 1)
    c_prod = custo_prod if mes == 1 else 0
    c_frete = frete_total if mes == 1 else 0
    
    total_custos_mes = c_prod + c_frete + royalties_mensal + mei_mensal + gasolina_mensal + outros_mensal + valor_comissao
    lucro_mes = receita_mes - total_custos_mes
    
    dados_dre.append({
        "Mês": f"Mês {mes}",
        "Receita (R$)": receita_mes,
        "Produção/Frete (R$)": c_prod + c_frete,
        "Custos Fixos (R$)": royalties_mensal + mei_mensal + gasolina_mensal + outros_mensal,
        "Comissão (R$)": valor_comissao,
        "Lucro Líquido (R$)": lucro_mes
    })
    
    faturamento_total += receita_mes
    custo_total_acumulado += total_custos_mes

# --- RESUMO VISUAL ---
lucro_final = faturamento_total - custo_total_acumulado
margem_final = (lucro_final / faturamento_total * 100) if faturamento_total > 0 else 0

c1, c2, c3 = st.columns(3)
c1.metric("Faturamento Total", f"R$ {faturamento_total:,.2f}")
c2.metric("Lucro Líquido Total", f"R$ {lucro_final:,.2f}", delta=f"{margem_final:.1f}% Margem")
c3.metric("Preço de Equilíbrio", f"R$ {(custo_total_acumulado / (mod_por_mes * duracao)):,.2f}")

st.subheader("📋 Demonstrativo Mensal Detalhado")
df_dre = pd.DataFrame(dados_dre)
st.table(df_dre.style.format({
    "Receita (R$)": "{:,.2f}",
    "Produção/Frete (R$)": "{:,.2f}",
    "Custos Fixos (R$)": "{:,.2f}",
    "Comissão (R$)": "{:,.2f}",
    "Lucro Líquido (R$)": "{:,.2f}"
}))

# Mensagem de Ponto de Equilíbrio
modulos_totais = mod_por_mes * duracao
pe_vendas = custo_total_acumulado / preco_venda
st.warning(f"📌 Para cobrir todos os custos (incluindo a comissão de {comissao_percent}%), o franqueado precisa vender **{pe_vendas:.1f} módulos** de um total de {modulos_totais} disponíveis nos {duracao} meses.")
