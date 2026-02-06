import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Simulador de Franquia v3", layout="wide")

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

st.title("🚀 Simulador de Viabilidade e DRE")
st.markdown("---")

# --- SIDEBAR: CONFIGURAÇÕES ---
st.sidebar.header("⚙️ Configurações Base")
tamanho = st.sidebar.selectbox("Tamanho do Saquinho", list(dados_custos.keys()))
tiragem = st.sidebar.selectbox("Tiragem (unidades)", list(dados_custos[tamanho]["precos"].keys()))
duracao = st.sidebar.selectbox("Duração da Campanha", [1, 3, 6], format_func=lambda x: f"{x} meses")

st.sidebar.markdown("---")
st.sidebar.header("💰 Estratégia")
margem_alvo = st.sidebar.slider("Margem de Lucro Alvo (%)", 10, 80, 40)
comissao_percent = st.sidebar.slider("Comissão Representante (%)", 0, 30, 10)

# --- CUSTOS FIXOS ---
C_ROY, C_MEI, C_GAS, C_OUT, C_FRETE = 399.00, 81.00, 500.00, 200.00, 600.00
mod_max = dados_custos[tamanho]["modulos"]
custo_prod_base = dados_custos[tamanho]["precos"][tiragem]

# Cálculo do Custo Total da Campanha (Investimento + Operacional)
custo_total_campanha_estimado = custo_prod_base + C_FRETE + ((C_ROY + C_MEI + C_GAS + C_OUT) * duracao)

# --- SUGESTÃO DE PREÇO (Markup sobre faturamento total) ---
# Preço necessário para pagar tudo e sobrar a margem em todos os meses
preco_sugerido = (custo_total_campanha_estimado / (duracao * mod_max)) / (1 - ((margem_alvo + comissao_percent) / 100))

# Input do preço final (preenchido com a sugestão)
preco_venda = st.sidebar.number_input("Preço Mensal por Módulo (R$)", min_value=0.0, value=float(preco_sugerido))

# --- CÁLCULO DO PONTO DE EQUILÍBRIO (TRAVADO) ---
# PE = Custo Total / Faturamento de 1 mês de 1 módulo
pe_calculado = custo_total_campanha_estimado / preco_venda if preco_venda > 0 else 0

# --- PROCESSAMENTO DO DRE ---
dre_data = {
    "Faturamento (Receita)": [],
    "(-) Produção (Mês 1)": [],
    "(-) Frete (Mês 1)": [],
    "(-) Royalties": [],
    "(-) MEI": [],
    "(-) Gasolina": [],
    "(-) Outros Custos": [],
    "(-) Comissão": [],
    "LUCRO LÍQUIDO": []
}

total_receita = 0
total_custo = 0

for i in range(1, duracao + 1):
    receita_mes = mod_max * preco_venda
    comis_mes = receita_mes * (comissao_percent / 100)
    p_prod = custo_prod_base if i == 1 else 0.0
    p_frete = C_FRETE if i == 1 else 0.0
    
    gastos_mes = p_prod + p_frete + C_ROY + C_MEI + C_GAS + C_OUT + comis_mes
    lucro_mes = receita_mes - gastos_mes
    
    dre_data["Faturamento (Receita)"].append(receita_mes)
    dre_data["(-) Produção (Mês 1)"].append(p_prod)
    dre_data["(-) Frete (Mês 1)"].append(p_frete)
    dre_data["(-) Royalties"].append(C_ROY)
    dre_data["(-) MEI"].append(C_MEI)
    dre_data["(-) Gasolina"].append(C_GAS)
    dre_data["(-) Outros Custos"].append(C_OUT)
    dre_data["(-) Comissão"].append(comis_mes)
    dre_data["LUCRO LÍQUIDO"].append(lucro_mes)
    
    total_receita += receita_mes
    total_custo += gastos_mes

# DataFrame Transposto
df_dre = pd.DataFrame(dre_data, index=[f"Mês {i}" for i in range(1, duracao + 1)]).T
df_dre["TOTAL"] = df_dre.sum(axis=1)

# --- EXIBIÇÃO ---
c1, c2, c3 = st.columns(3)
with c1:
    st.metric("Sugestão de Preço", f"R$ {preco_sugerido:,.2f}")
with c2:
    # Lógica de Cor para o PE
    if pe_calculado > mod_max:
        st.error(f"PE: {pe_calculado:.1f} / {mod_max} Módulos")
        st.caption("⚠️ Inviável: Custo excede capacidade no 1º mês.")
    else:
        st.metric("Ponto de Equilíbrio", f"{pe_calculado:.1f} / {mod_max}")
        st.caption(f"Vendas necessárias para pagar a campanha toda.")
with c3:
    margem_real = (lucro_final := (total_receita - total_custo)) / total_receita * 100 if total_receita > 0 else 0
    st.metric("Lucro Total", f"R$ {lucro_final:,.2f}", f"{margem_real:.1f}%")

st.subheader("📋 Demonstrativo Financeiro")
st.dataframe(df_dre.style.format("{:,.2f}"), use_container_width=True)

# Botão de Download
csv = df_dre.to_csv().encode('utf-8')
st.download_button("📥 Baixar Relatório DRE", data=csv, file_name='dre_campanha.csv', mime='text/csv')

if pe_calculado > mod_max:
    st.error(f"🛑 **ALERTA DE INVIABILIDADE:** Para pagar os custos da campanha no primeiro mês, seriam necessários {pe_calculado:.1f} módulos, mas o saquinho só possui {mod_max}. Aumente o preço de venda ou reduza a margem.")
