from typing import Dict, Any, Optional

def calcular_preco_ideal(
    custo_base: float,
    frete_fixo: float,
    taxa_comissao: float,
    margem_alvo: float,
    preco_concorrente: Optional[float],  # Agora aceita explicitamente None
    fator_posicionamento_eve: float
) -> Dict[str, Any]:
    
    # 1) Calcular Limites Internos
    try:
        piso = (custo_base + frete_fixo) / (1.0 - taxa_comissao)
        preco_com_margem = (custo_base + frete_fixo) / (1.0 - taxa_comissao - margem_alvo)
    except ZeroDivisionError:
        return {"mensagem": "Erro: Taxas somam 100% ou mais. Inviável matematicamente."}

    # 2) Rota de Voo Cego (Falha de Mercado / Sem âncora)
    if preco_concorrente is None or preco_concorrente <= 0:
        return {
            "viavel": True, # Presumimos viável pois garantimos a margem matemática
            "piso": round(piso, 2),
            "teto": None,
            "preco_sugerido": round(preco_com_margem, 2),
            "preco_com_margem_alvo": round(preco_com_margem, 2),
            "mensagem": "Voo Cego ativado: Preço ancorado apenas na Margem Alvo interna."
        }
        
# 3) Rota Normal (EVE e Posicionamento)
    teto = preco_concorrente * (1.0 + fator_posicionamento_eve)
    
    # Nova árvore de decisão
    if teto < piso:
        status = "INVIÁVEL"
        preco_sugerido = piso  # Redução de danos
        msg = "Alerta: Teto (EVE) não cobre os custos. Preço forçado para o Piso."
        
    elif teto < preco_com_margem:
        status = "COMPETITIVO/SUB-ÓTIMO"
        preco_sugerido = teto  # Maximiza dentro do possível
        msg = f"Aviso: Operação saudável, mas não atinge a margem alvo. Faltam R$ {preco_com_margem - teto:.2f}."
        
    else:
        status = "ÓTIMO"
        preco_sugerido = teto  # Captura todo o valor possível da mesa
        msg = "Sucesso: Teto supera a margem alvo interna. Captura máxima de valor."
    
    # 4) Retornar o dicionário de resposta consolidado
    is_viavel = teto >= piso
    return {
        "viavel": is_viavel,
        "piso": round(piso, 2),
        "teto": round(teto, 2),
        "preco_sugerido": round(preco_sugerido, 2),
        "preco_com_margem_alvo": round(preco_com_margem, 2),
        "mensagem": msg,
        "status": status
    }