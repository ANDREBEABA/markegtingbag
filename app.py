import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Simulador Profissional", layout="wide")

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

st.title("🚀 Simulador de Precificação e DRE")
st.markdown("---")

# --- SIDEBAR: CONFIGURAÇÕES ---
st.sidebar.header("⚙️ Configurações Base")
tamanho = st.sidebar.selectbox("Tamanho do Saquinho", list(dados_custos.keys()))
tiragem = st.sidebar.selectbox("Tiragem (unidades)", list(dados_custos[tamanho]["precos"].keys()))
duracao = st.sidebar.selectbox("Duração da Campanha", [1, 3, 6], format_func=lambda x: f"{x} meses")

st.sidebar.markdown("---")
st.sidebar.header("💰 Precificação")
margem_alvo = st.sidebar.slider("Margem de Lucro Alvo (%)", 10, 80, 40)
comissao_percent = st.sidebar.slider("Comissão Representante (%)", 0, 30, 10)

# --- CUSTOS FIXOS ---
C_ROY, C_MEI, C_GAS, C_OUT, C_FRETE = 399.00, 81.00, 500.00, 200.00, 600.00
mod_base = dados_custos[tamanho]["modulos"]
custo_prod_base = dados_custos[tamanho]["precos"][tiragem]

# --- LÓGICA DE SUGESTÃO DE PREÇO ---
# Cálculo: O preço que cobre o custo total diluído pelos meses e módulos, aplicando a margem
custo_total_estimado_sem_comissao = custo_prod_base + C_FRETE + ((C_ROY + C_MEI + C_GAS + C_OUT) * duracao)
# Preço sugerido considerando a margem e a comissão (Markup)
preco_sugerido_calculado = (custo_total_estimado_sem_comissao / (duracao * mod_base)) / (1 - ((margem_alvo + comissao_percent) / 100))

# Input do preço final (preenchido com a sugestão)
preco_venda_mensal = st.sidebar.number_input("Preço de Venda Praticado (R$)", min_value=0.0, value=float(preco_sugerido_calculado))

# --- PROCESSAMENTO DO DRE ---
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

faturamento_total = 0
custo_total = 0

for i in range(1, duracao + 1):
    receita_mes = mod_base * preco_venda_mensal
    comissao_mes = receita_mes * (comissao_percent / 100)
    p_prod = custo_prod_base if i == 1 else 0.0
    p_frete = C_FRETE if i == 1 else 0.0
    
    despesas_mes = p_prod + p_frete + C_ROY + C_MEI + C_GAS + C_OUT + comissao_mes
    lucro_mes = receita_mes - despesas_mes
    
    dre_data["Faturamento (Receita)"].append(receita_mes)
    dre_data["(-) Produção"].append(p_prod)
    dre_data["(-) Frete"].append(p_frete)
    dre_data["(-) Royalties"].append(C_ROY)
    dre_data["(-) MEI"].append(C_MEI)
    dre_data["(-) Gasolina"].append(C_GAS)
    dre_data["(-) Outros Custos"].append(C_OUT)
    dre_data["(-) Comissão Representante"].append(comissao_mes)
    dre_data["LUCRO LÍQUIDO"].append(lucro_mes)
    
    faturamento_total += receita_mes
    custo_total += despesas_mes

# Criar DataFrame e Transpor
df_dre = pd.DataFrame(dre_data, index=[f"Mês {i}" for i in range(1, duracao + 1)]).T
df_dre["TOTAL"] = df_dre.sum(axis=1)

# --- CÁLCULO PONTO EQUILÍBRIO (BASEADO NO 1º MÊS) ---
# PE = Custo Total da Campanha / Faturamento Mensal por Módulo
pe_modulos = custo_total / preco_venda_mensal if preco_venda_mensal > 0 else 0

# --- EXIBIÇÃO ---
c1, c2, c3 = st.columns(3)
with c1:
    st.metric("Sugestão de Preço", f"R$ {preco_sugerido_calculado:,.2f}", help=f"Preço para garantir {margem_alvo}% de margem")
with c2:
    st.metric("Ponto de Equilíbrio", f"{pe_modulos:.1f} Módulos", help="Módulos necessários para pagar a campanha toda com 1 mês de faturamento")
with c3:
    margem_real = (df_dre.loc["LUCRO LÍQUIDO", "TOTAL"] / faturamento_total * 100) if faturamento_total > 0 else 0
    st.metric("Lucro Total Estimado", f"R$ {df_dre.loc['LUCRO LÍQUIDO', 'TOTAL']:,.2f}", f"{margem_real:.1f}% Margem Real")

st.subheader("📋 Demonstrativo Financeiro")
st.dataframe(df_dre.style.format("{:,.2f}"), use_container_width=True)

# BOTÃO DE DOWNLOAD
csv = df_dre.to_csv().encode('utf-8')
st.download_button(
    label="📥 Baixar DRE em CSV",
    data=csv,
    file_name=f'dre_campanha_{tamanho}_{tiragem}.csv',
    mime='text/csv',
)

st.warning(f"📌 **Meta de Vendas:** O franqueado deve focar em vender pelo menos **{pe_modulos:.1f} módulos**. Como o saquinho tem capacidade para {mod_base}, ele tem uma margem de segurança de {mod_base - pe_modulos:.1f} módulos.")
