import requests
import os
import re
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()

def buscar_preco_concorrente(nome_produto: str) -> Optional[Dict[str, Any]]:
    """
    Busca o preço e os dados do produto utilizando a API do Serper (Google Shopping).
    
    Parâmetros:
        nome_produto: O nome do produto para pesquisa.
        
    Retorna:
        Um dicionário contendo o preço limpo (float) e os metadados do concorrente.
        Retorna None em caso de falha ou erro.
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
            
        primeiro_produto = produtos[0]
        preco_bruto = primeiro_produto.get("price")
        
        if not preco_bruto:
            return None
            
        # Tratamento matemático da string
        if isinstance(preco_bruto, str):
            apenas_numeros = re.sub(r'[^\d.,]', '', preco_bruto)
            preco_limpo = apenas_numeros.replace('.', '').replace(',', '.')
            preco = float(preco_limpo)
        else:
            preco = float(preco_bruto)
            
        # Agora retornamos um dicionário rico com todas as informações vitais!
        return {
            "preco": preco,
            "title": primeiro_produto.get("title", "Título não informado"),
            "source": primeiro_produto.get("source", "Loja Desconhecida"),
            "link": primeiro_produto.get("link", ""),
            "imageUrl": primeiro_produto.get("imageUrl", "")
        }

    except (requests.exceptions.RequestException, ValueError, KeyError, TypeError) as e:
        print(f"Erro ao consultar mercado: {e}")
        return None

# Bloco para testar no terminal
if __name__ == "__main__":
    prod = input("Digite seu produto: ")
    resultado = buscar_preco_concorrente(prod)
    if resultado:
        print(f"\n✅ CONCORRENTE ENCONTRADO!")
        print(f"Produto: {resultado['title']}")
        print(f"Loja: {resultado['source']}")
        print(f"Preço Limpo: R$ {resultado['preco']:.2f}")
    else:
        print("\n❌ Produto não encontrado ou falha na API.")
