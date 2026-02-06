import streamlit as st
import pandas as pd

st.set_page_config(page_title="Simulador Financeiro de Franquia", layout="wide")

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

st.title("💰 Simulador de Viabilidade Financeira")
st.markdown("---")

# --- SIDEBAR: CONFIGURAÇÕES ---
st.sidebar.header("⚙️ Configurações")
tamanho = st.sidebar.selectbox("Tamanho do Saquinho", list(dados_custos.keys()))
tiragem = st.sidebar.selectbox("Tiragem (unidades)", list(dados_custos[tamanho]["precos"].keys()))
duracao = st.sidebar.selectbox("Duração da Campanha", [1, 3, 6], format_func=lambda x: f"{x} meses")

st.sidebar.markdown("---")
st.sidebar.header("🎯 Estratégia")
margem_alvo = st.sidebar.slider("Margem de Lucro Alvo (%)", 10, 80, 30)
comissao_percent = st.sidebar.slider("Comissão Representante (%)", 0, 30, 10)

# --- CUSTOS FIXOS ---
C_ROY, C_MEI, C_GAS, C_OUT, C_FRETE = 399.00, 81.00, 500.00, 200.00, 600.00
mod_max = dados_custos[tamanho]["modulos"]
custo_prod = dados_custos[tamanho]["precos"][tiragem]

# --- LÓGICA DE SUGESTÃO DE PREÇO (Foco no Lucro Positivo no Mês 1) ---
# Para o Mês 1 ser positivo: Receita * (1 - Comis) > (Prod + Frete + Fixos)
custos_mes_1 = custo_prod + C_FRETE + C_ROY + C_MEI + C_GAS + C_OUT
preco_sugerido_minimo_mês1 = (custos_mes_1 / mod_max) / (1 - ((margem_alvo + comissao_percent) / 100))

# Input do preço praticado
preco_venda = st.sidebar.number_input("Preço Mensal por Módulo (R$)", min_value=0.0, value=float(preco_sugerido_minimo_mês1))

# --- PROCESSAMENTO DO DRE ---
dre_data = {
    "Faturamento (Receita)": [],
    "(-) Produção e Frete": [],
    "(-) Custos Fixos (Roy/MEI/Gas/Out)": [],
    "(-) Comissão Representante": [],
    "LUCRO LÍQUIDO": []
}

total_fixos_mensais = C_ROY + C_MEI + C_GAS + C_OUT

for i in range(1, duracao + 1):
    receita_mes = mod_max * preco_venda
    comis_mes = receita_mes * (comissao_percent / 100)
    p_setup = (custo_prod + C_FRETE) if i == 1 else 0.0
    
    lucro_mes = receita_mes - p_setup - total_fixos_mensais - comis_mes
    
    dre_data["Faturamento (Receita)"].append(receita_mes)
    dre_data["(-) Produção e Frete"].append(p_setup)
    dre_data["(-) Custos Fixos (Roy/MEI/Gas/Out)"].append(total_fixos_mensais)
    dre_data["(-) Comissão Representante"].append(comis_mes)
    dre_data["LUCRO LÍQUIDO"].append(lucro_mes)

# DataFrame para exibição
df_dre = pd.DataFrame(dre_data, index=[f"Mês {i}" for i in range(1, duracao + 1)]).T
df_dre["TOTAL"] = df_dre.sum(axis=1)

# --- CÁLCULO PONTO EQUILÍBRIO FINANCEIRO (Mês 1) ---
# Quanto preciso faturar no Mês 1 para o lucro ser ZERO?
faturamento_equilibrio_mes1 = custos_mes_1 / (1 - (comissao_percent / 100))
modulos_equilibrio_mes1 = faturamento_equilibrio_mes1 / preco_venda if preco_venda > 0 else 0

# --- EXIBIÇÃO DE MÉTRICAS ---
lucro_mês1 = df_dre.loc["LUCRO LÍQUIDO", "Mês 1"]

c1, c2, c3 = st.columns(3)
with c1:
    st.metric("Sugestão de Preço", f"R$ {preco_sugerido_minimo_mês1:,.2f}", help="Preço para garantir lucro positivo desde o Mês 1")
with c2:
    color = "normal" if lucro_mês1 >= 0 else "inverse"
    st.metric("Lucro Líquido (Mês 1)", f"R$ {lucro_mês1:,.2f}", delta_color=color)
    st.caption("Foco principal: Deve ser positivo.")
with c3:
    st.metric("Ponto de Equilíbrio (Mês 1)", f"R$ {faturamento_equilibrio_mes1:,.2f}")
    st.caption(f"Ou vender {modulos_equilibrio_mes1:.1f} módulos no 1º mês.")

st.subheader("📋 Demonstrativo de Resultados (DRE)")
st.dataframe(df_dre.style.format("{:,.2f}"), use_container_width=True)

# Alertas de Viabilidade
if lucro_mês1 < 0:
    st.error(f"⚠️ **Atenção:** Com este preço, o Mês 1 apresenta prejuízo de R$ {abs(lucro_mês1):,.2f}. O franqueado precisará de fôlego financeiro para cobrir o início da operação.")
else:
    st.success(f"✅ **Campanha Saudável:** O primeiro mês já gera um lucro de R$ {lucro_mês1:,.2f}. O Ponto de Equilíbrio foi atingido!")

# Botão de Download
csv = df_dre.to_csv().encode('utf-8')
st.download_button("📥 Baixar Relatório Completo", data=csv, file_name='dre_campanha.csv', mime='text/csv')
