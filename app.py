import streamlit as st

# Configuração da página
st.set_page_config(page_title="Calculadora de Precificação", layout="centered")

# Dados de Custos
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

st.title("📊 Precificação de Campanhas")
st.markdown("---")

# Colunas de Input
col1, col2 = st.columns(2)

with col1:
    tamanho = st.selectbox("Tamanho do Saquinho", list(dados_custos.keys()))
    tiragens_disponiveis = list(dados_custos[tamanho]["precos"].keys())
    tiragem = st.selectbox("Tiragem (unidades)", tiragens_disponiveis)

with col2:
    duracao = st.radio("Duração da Campanha", [1, 3], format_func=lambda x: f"{x} mês(es)")
    preco_venda = st.number_input("Preço de Venda por Módulo (R$)", min_value=0.0, value=500.0)

# Cálculos
modulos = dados_custos[tamanho]["modulos"]
custo_producao = dados_custos[tamanho]["precos"][tiragem]
frete = 600.00
custos_fixos_mensais = 399 + 81 + 500 + 200  # Royalties, MEI, Gasolina, Outros
custo_fixo_total = custos_fixos_mensais * duracao

faturamento_total = modulos * preco_venda
custo_total_projeto = custo_producao + frete + custo_fixo_total
lucro_total = faturamento_total - custo_total_projeto
lucratividade = (lucro_total / faturamento_total * 100) if faturamento_total > 0 else 0
pe_modulos = custo_total_projeto / preco_venda if preco_venda > 0 else 0

# Exibição do DRE
st.subheader("📋 DRE da Campanha")
c1, c2, c3 = st.columns(3)
c1.metric("Faturamento", f"R$ {faturamento_total:,.2f}")
c2.metric("Lucro Líquido", f"R$ {lucro_total:,.2f}", delta=f"{lucratividade:.1f}%")
c3.metric("Ponto Equilíbrio", f"{pe_modulos:.1f} mod.")

with st.expander("Ver Detalhes dos Custos"):
    st.write(f"**Custo Produção:** R$ {custo_producao:,.2f}")
    st.write(f"**Frete:** R$ {frete:,.2f}")
    st.write(f"**Custos Fixos Totais ({duracao}m):** R$ {custo_fixo_total:,.2f}")
    st.info(f"O custo fixo inclui: Royalties, MEI, Gasolina e Outros (R$ {custos_fixos_mensais:,.2f}/mês)")

if lucro_total < 0:
    st.error("Atenção: Esta configuração resulta em prejuízo!")
else:
    st.success("Configuração de campanha lucrativa.")
