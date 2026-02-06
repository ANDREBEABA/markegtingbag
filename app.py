import streamlit as st
import pandas as pd

st.set_page_config(page_title="Simulador de Campanhas Profissional", layout="wide")

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

st.title("📊 Simulador de Viabilidade Financeira")
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

# --- LÓGICA DE SUGESTÃO DE PREÇO TOTAL ---
# Preço necessário para o Mês 1 ser positivo
custos_mes_1 = custo_prod + C_FRETE + C_ROY + C_MEI + C_GAS + C_OUT
# Preço MENSAL sugerido
p_mensal_sugerido = (custos_mes_1 / mod_max) / (1 - ((margem_alvo + comissao_percent) / 100))
# Preço TOTAL sugerido (Conforme solicitado: multiplicado por 1, 3 ou 6)
p_total_sugerido = p_mensal_sugerido * duracao

# Input do preço praticado (Valor Total)
st.sidebar.info(f"Sugestão de Valor Total: R$ {p_total_sugerido:,.2f}")
v_total_praticado = st.sidebar.number_input(f"Valor Total do Contrato por Módulo (R$)", min_value=0.0, value=float(p_total_sugerido))
p_venda_mensal = v_total_praticado / duracao

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

for i in range(1, duracao + 1):
    receita_mes = mod_max * p_venda_mensal
    comis_mes = receita_mes * (comissao_percent / 100)
    p_prod_mes = custo_prod if i == 1 else 0.0
    p_frete_mes = C_FRETE if i == 1 else 0.0
    
    lucro_mes = receita_mes - p_prod_mes - p_frete_mes - C_ROY - C_MEI - C_GAS - C_OUT - comis_mes
    
    dre_data["Faturamento (Receita)"].append(receita_mes)
    dre_data["(-) Produção"].append(p_prod_mes)
    dre_data["(-) Frete"].append(p_frete_mes)
    dre_data["(-) Royalties"].append(C_ROY)
    dre_data["(-) MEI"].append(C_MEI)
    dre_data["(-) Gasolina"].append(C_GAS)
    dre_data["(-) Outros Custos"].append(C_OUT)
    dre_data["(-) Comissão Representante"].append(comis_mes)
    dre_data["LUCRO LÍQUIDO"].append(lucro_mes)

# DataFrame e Transposição
df_dre = pd.DataFrame(dre_data, index=[f"Mês {i}" for i in range(1, duracao + 1)]).T
df_dre["TOTAL ACUMULADO"] = df_dre.sum(axis=1)

# --- FUNÇÃO DE ESTILIZAÇÃO PARA AS CORES ---
def style_lucro(row):
    if row.name == 'LUCRO LÍQUIDO':
        return ['background-color: #90EE90' if v >= 0 else 'background-color: #FFB6C1' for v in row]
    return ['' for _ in row]

# --- EXIBIÇÃO DE MÉTRICAS ---
lucro_mes_1 = df_dre.loc["LUCRO LÍQUIDO", "Mês 1"]
custo_total_campanha = (custo_prod + C_FRETE) + ( (C_ROY + C_MEI + C_GAS + C_OUT) * duracao )
faturamento_total_campanha = mod_max * v_total_praticado

c1, c2, c3 = st.columns(3)
with c1:
    st.metric("Sugestão de Valor Total", f"R$ {p_total_sugerido:,.2f}")
    st.caption(f"Valor por módulo para os {duracao} meses")
with c2:
    st.metric("Lucro Líquido (Mês 1)", f"R$ {lucro_mes_1:,.2f}")
    st.caption("Visão crítica de início de operação")
with c3:
    pe_financeiro = (custos_mes_1 / (1 - (comissao_percent/100))) / p_venda_mensal if p_venda_mensal > 0 else 0
    st.metric("Ponto Equilíbrio (Mês 1)", f"{pe_financeiro:.1f} Mód.")
    st.caption("Vendas necessárias no 1º mês")

st.subheader("📋 Demonstrativo de Resultados (DRE)")
# Aplicando estilo e exibindo
st.dataframe(df_dre.style.apply(style_lucro, axis=1).format("{:,.2f}"), use_container_width=True)

# Alertas
if lucro_mes_1 >= 0:
    st.success(f"✅ Campanha Viável! O Mês 1 já apresenta lucro positivo de R$ {lucro_mes_1:,.2f}.")
else:
    st.error(f"⚠️ Alerta de Caixa: O Mês 1 terá um déficit de R$ {abs(lucro_mes_1):,.2f}. O retorno total virá nos meses seguintes.")

# Download
csv = df_dre.to_csv().encode('utf-8')
st.download_button("📥 Baixar Relatório CSV", data=csv, file_name='dre_campanha.csv', mime='text/csv')
