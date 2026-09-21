import streamlit as st
from pricing_engine import calcular_preco_ideal
from market_api import buscar_preco_concorrente

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
            dados_concorrente = buscar_preco_concorrente(nome_produto.strip())
            
        if dados_concorrente is None:
            st.error("Não foi possível encontrar o preço do produto na API (Falha ou não encontrado).")
            return
            
        preco_concorrente = dados_concorrente["preco"]
        
        st.success("Concorrente encontrado com sucesso!")
        
        # Cria colunas para organizar a exibição visual
        col1, col2 = st.columns([1, 3])
        
        with col1:
            if dados_concorrente.get("imageUrl"):
                st.image(dados_concorrente["imageUrl"], width=150)
                
        with col2:
            st.markdown(f"**Produto Base:** {dados_concorrente.get('title', 'N/A')}")
            st.markdown(f"**Loja:** {dados_concorrente.get('source', 'N/A')}")
            st.markdown(f"**Preço:** R$ {preco_concorrente:.2f}")
            if dados_concorrente.get('link'):
                st.markdown(f"[Ver oferta no Google]({dados_concorrente['link']})")
        
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
