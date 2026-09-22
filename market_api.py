import requests
import os
import pandas as pd
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

def buscar_preco_concorrente(nome_produto: str) -> Optional[pd.DataFrame]:
    """
    Busca os dados do produto utilizando a API do Serper (Google Shopping).
    
    Parâmetros:
        nome_produto: O nome do produto para pesquisa.
        
    Retorna:
        Um DataFrame Pandas com os produtos encontrados, filtrando as lojas da blacklist,
        ou None em caso de falha ou ausência de dados.
    """
    api_key = os.getenv("SERPAPI_KEY")
    url = "https://google.serper.dev/shopping"
    
    parametros = {
        "q": nome_produto,
        "hl": "pt-br",
        "gl": "br",   
        "num": 10,
        "apiKey": api_key
    }

    try:
        response = requests.get(url, params=parametros, timeout=10)
        response.raise_for_status()
        
        dados = response.json()
        produtos = dados.get("shopping", [])
        
        if not produtos:
            return None
            
        df = pd.DataFrame(produtos)
        
        # O DataFrame precisa ter no mínimo as colunas essenciais
        colunas_esperadas = ["title", "source", "link", "price"]
        for col in colunas_esperadas:
            if col not in df.columns:
                df[col] = None
        
        # Lista de lojas a serem ignoradas (Blacklist) - minúsculas
        blacklist = [
            "amazon", "amazon.com.br", "magazine luiza", "magalu", 
            "mercadolivre", "mercado livre", "shopee", "americanas", 
            "casas bahia", "ponto", "pontofrio", "extra", 
            "submarino", "shoptime"
        ]
        
        # Se certifica que a coluna source seja tratada como string para filtro
        df["source"] = df["source"].astype(str)
        
        # Filtra removendo as lojas que contêm itens da blacklist
        filtro_regex = '|'.join(blacklist)
        df_filtrado = df[~df["source"].str.lower().str.contains(filtro_regex, na=False)].copy()
        
        if df_filtrado.empty:
            return None
            
        # Reseta o index para manter o 0 como o mais relevante do Google
        df_filtrado = df_filtrado.reset_index(drop=True)
            
        return df_filtrado

    except (requests.exceptions.RequestException, ValueError, KeyError, TypeError) as e:
        print(f"Erro ao consultar mercado: {e}")
        return None
