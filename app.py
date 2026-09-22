import streamlit as st
import pandas as pd
from pricing_engine import calcular_preco_ideal
from market_api import buscar_preco_concorrente
from tratar_df import tratamento
import json
def main():
    st.set_page_config(page_title="LuLu Tech | Pricing Engine", layout="wide", page_icon="🛍️")
    
    # ==========================
    # BRANDING: LULU TECH (CSS)
    # ==========================
    st.markdown("""
        <style>
        /* Header Customizado com Gradiente Azul e Rosa */
        .lulu-header {
            background: linear-gradient(90deg, #1E3A8A 0%, #E83E8C 100%);
            padding: 25px;
            border-radius: 10px;
            color: white;
            text-align: center;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin-bottom: 30px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.15);
        }
        .lulu-title {
            margin: 0;
            font-size: 2.8rem;
            font-weight: 900;
            letter-spacing: 1.5px;
            text-transform: uppercase;
        }
        .lulu-subtitle {
            margin: 5px 0 0 0;
            font-size: 1.2rem;
            font-weight: 400;
            opacity: 0.95;
        }
        
        /* Customizando a cor do botão primário para o Azul da empresa */
        .stButton>button[kind="primary"] {
            background-color: #1E3A8A !important;
            color: white !important;
            border: none !important;
            border-radius: 6px !important;
            transition: all 0.3s ease;
        }
        /* Hover do botão primário vai para o Rosa da empresa */
        .stButton>button[kind="primary"]:hover {
            background-color: #E83E8C !important;
            box-shadow: 0 4px 8px rgba(232, 62, 140, 0.4) !important;
        }
        
        /* Estilo do Rodapé */
        .lulu-footer {
            margin-top: 60px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            text-align: center;
            color: #555;
            font-size: 0.95rem;
            font-family: 'Segoe UI', sans-serif;
        }
        .lulu-footer .brand {
            color: #E83E8C;
            font-weight: bold;
        }
        .lulu-footer .tech {
            color: #1E3A8A;
            font-weight: bold;
        }
        </style>
        
        <div class="lulu-header">
            <h1 class="lulu-title">LULU TECH</h1>
            <p class="lulu-subtitle">Pricing Engine Intelligence 🎯</p>
        </div>
    """, unsafe_allow_html=True)
    
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
    
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        nome_produto = st.text_input("Nome do Produto (Busca na API)", placeholder="Ex: smartphone, perfume, laptop")
    with col_b2:
        loja_cliente = st.text_input("Nome da sua Loja (Para ignorar na busca)", placeholder="Ex: Pichau, Kabum, etc", help="Seus próprios preços serão excluídos da análise (blacklist).")
    
    if st.button("Calcular Preço", type="primary"):
        if not nome_produto.strip():
            st.warning("Por favor, digite o nome de um produto.")
            return
            
        with st.spinner("Consultando preço do mercado na API..."):
            # Chamada Oficial para a API do Google Shopping (Serper)
            df_bruto = buscar_preco_concorrente(nome_produto.strip())            
            
        if df_bruto is None or df_bruto.empty:
            st.error("Não foi possível encontrar concorrentes fora da blacklist.")
        else:
            st.session_state['df_bruto'] = df_bruto
            st.session_state['loja_cliente'] = loja_cliente
            
    if 'df_bruto' in st.session_state:
        df_bruto = st.session_state['df_bruto']
        loja_cliente = st.session_state.get('loja_cliente', '')
        
        df_limpo = tratamento(df_bruto, loja_cliente)
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
        
        # Exibição Visual do Preço Sugerido (Substituindo o JSON bruto)
        st.subheader("💡 Recomendação do Pricing Engine")
        
        # Define a cor/alerta baseado no status da operação
        status_op = resultado.get("status", "INFO")
        if status_op == "ÓTIMO":
            st.success(f"**{status_op}**: {resultado.get('mensagem', '')}")
            delta_color = "normal"
            delta_text = "Margem Alvo Atingida!"
        elif status_op == "COMPETITIVO/SUB-ÓTIMO":
            st.warning(f"**{status_op}**: {resultado.get('mensagem', '')}")
            delta_color = "off"
            delta_text = "Abaixo da Margem"
        else:
            st.error(f"**{status_op}**: {resultado.get('mensagem', '')}")
            delta_color = "inverse"
            delta_text = "Sobrevivência/Prejuízo"
            
        # KPI Principal em Destaque
        st.metric(
            label="Preço de Venda Sugerido", 
            value=f"R$ {resultado['preco_sugerido']:.2f}" if resultado.get('preco_sugerido') is not None else "N/A",
            delta=delta_text,
            delta_color=delta_color
        )
        
        # Limites (Piso e Teto) formatados menores abaixo
        c_piso, c_teto = st.columns(2)
        c_piso.markdown(f"**📉 Piso (Break-even):** R$ {resultado['piso']:.2f}")
        
        teto_val = resultado.get('teto')
        teto_str = f"R$ {teto_val:.2f}" if teto_val is not None else "Voo Cego (Sem Teto)"
        c_teto.markdown(f"**📈 Teto (Concorrente + EVE):** {teto_str}")

    # ==========================
    # RODAPÉ (FOOTER)
    # ==========================
    st.markdown("""
        <div class="lulu-footer">
            Desenvolvido com 💙 e 💗 pela equipe de Engenharia de Dados da <span class="brand">LuLu</span> <span class="tech">Tech</span>.<br>
            <small>© 2024 LuLu Tech. Todos os direitos reservados.</small>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
