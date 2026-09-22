import streamlit as st
import pandas as pd
from pricing_engine import calcular_preco_ideal
from market_api import buscar_preco_concorrente
from tratar_df import tratamento
import json
def main():
    st.set_page_config(page_title="Pricing Engine V0", layout="wide")
    
    st.title("Pricing Engine - V0 (Determinístico)")
    st.markdown("Interface para cálculo de preço considerando custos, concorrência e posicionamento.")
    
    # ==========================
    # BARRA LATERAL (SIDEBAR)
    # ==========================
    st.sidebar.header("Custos e Parâmetros")
    
    custo_base = st.sidebar.number_input("Custo Base (R$)", min_value=0.0, value=50.0, step=1.0)
    frete_fixo = st.sidebar.number_input("Frete Fixo (R$)", min_value=0.0, value=15.0, step=1.0)
    
    comissao_pct = st.sidebar.number_input("Comissão (%)", min_value=0.0, max_value=100.0, value=15.0, step=0.5)
    margem_pct = st.sidebar.number_input("Margem Alvo (%)", min_value=0.0, max_value=100.0, value=10.0, step=0.5)
    
    st.sidebar.header("Estratégia (EVE)")
    # Slider estritamente limitado entre -10% e +10%
    fator_eve_pct = st.sidebar.slider(
        "Fator de Posicionamento EVE (%)", 
        min_value=-10, 
        max_value=10, 
        value=0, 
        step=1,
        help="Ajuste estratégico em relação ao concorrente (-10% a +10%)"
    )
    
    # ==========================
    # PAINEL PRINCIPAL
    # ==========================
    st.subheader("Consulta de Produto")
    nome_produto = st.text_input("Nome do Produto (Busca na API)", placeholder="Ex: smartphone, perfume, laptop")
    
    if st.button("Calcular Preço", type="primary"):
        if not nome_produto.strip():
            st.warning("Por favor, digite o nome de um produto.")
            return
            
        with st.spinner("Consultando preço do mercado..."):
            with open("exemplo.json", "r") as f:
                data = json.load(f)
            produtos = data['shopping']
            df_bruto = pd.DataFrame(produtos)
            # df_bruto = buscar_preco_concorrente(nome_produto.strip())

            
        if df_bruto is None or df_bruto.empty:
            st.error("Não foi possível encontrar concorrentes fora da blacklist.")
        else:
            st.session_state['df_bruto'] = df_bruto
            
    if 'df_bruto' in st.session_state:
        df_bruto = st.session_state['df_bruto']
        
        df_limpo = tratamento(df_bruto)
        if df_limpo.empty:
            st.error("Falha ao higienizar os preços retornados.")
            return
            
        st.success("Análise de mercado concluída!")
        
        # Pega a melhor opção (mais relevante do Google) como base matemática
        conc_escolhido = st.selectbox(
            "Selecione um concorrente principal",
            df_limpo['source'].unique(),
        )
        melhor_opcao = df_limpo[df_limpo['source'] == conc_escolhido].iloc[0]
        preco_concorrente = float(melhor_opcao["price_limpo"])
        
        # Cria colunas para organizar a exibição visual do concorrente principal
        col1, col2 = st.columns([1, 3])
        
        with col1:
            if 'imageUrl' in melhor_opcao and pd.notna(melhor_opcao["imageUrl"]):
                st.image(melhor_opcao["imageUrl"], width=150)
                
        with col2:
            st.markdown(f"**Principal Concorrente Base:** {melhor_opcao.get('title', 'N/A')}")
            st.markdown(f"**Loja:** {melhor_opcao.get('source', 'N/A')}")
            st.markdown(f"**Preço Base:** R$ {preco_concorrente:.2f}")
            if 'link' in melhor_opcao and pd.notna(melhor_opcao['link']):
                st.markdown(f"[Ver oferta no Google]({melhor_opcao['link']})")
        
        st.divider()
        
        st.subheader("Análise do Mercado")
        
        col_med1, col_med2 = st.columns(2)
        preco_medio = df_limpo["price_limpo"].mean()
        preco_mediano = df_limpo["price_limpo"].median()
        
        col_med1.metric("Média de Preços (S/ Gigantes)", f"R$ {preco_medio:.2f}")
        col_med2.metric("Mediana de Preços", f"R$ {preco_mediano:.2f}")
        
        st.write("Ofertas de Concorrentes (Preço por Loja)")
        # Agrupa preços por loja para exibir no gráfico
        df_grafico = df_limpo.groupby('source')['price_limpo'].mean().sort_values()
        st.bar_chart(df_grafico)
        
        st.divider()
        
        # Conversão de percentual para decimal (ex: 15% -> 0.15)
        taxa_comissao = comissao_pct / 100.0
        margem_alvo = margem_pct / 100.0
        fator_eve = fator_eve_pct / 100.0
        
        # Chamada para o motor determinístico
        resultado = calcular_preco_ideal(
            custo_base=custo_base,
            frete_fixo=frete_fixo,
            taxa_comissao=taxa_comissao,
            margem_alvo=margem_alvo,
            preco_concorrente=preco_concorrente,
            fator_posicionamento_eve=fator_eve
        )
        
        # Armazena o resultado no session_state (único estado permitido)
        if 'historico' not in st.session_state:
            st.session_state['historico'] = []
            
        st.session_state['historico'].append({
            "produto": nome_produto,
            "resultado": resultado
        })
        
        # Exibição do JSON formatado
        st.subheader("Resposta do Pricing Engine")
        st.json(resultado)

if __name__ == "__main__":
    main()
