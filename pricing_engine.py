from typing import Dict, Any

def calcular_preco_ideal(
    custo_base: float,
    frete_fixo: float,
    taxa_comissao: float,
    margem_alvo: float,
    preco_concorrente: float,
    fator_posicionamento_eve: float
) -> Dict[str, Any]:
    """
    Função orquestradora para o cálculo do preço de venda determinístico.
    
    Parâmetros:
        custo_base: Custo de aquisição do produto.
        frete_fixo: Custo fixo do frete.
        taxa_comissao: Percentual cobrado pelo marketplace/plataforma (ex: 0.15 para 15%).
        margem_alvo: Percentual de margem de lucro desejada (ex: 0.10 para 10%).
        preco_concorrente: Preço praticado pelo principal concorrente.
        fator_posicionamento_eve: Percentual premium/desconto do Economic Value Estimation (ex: 0.05 para +5%).
        
    Fórmulas utilizadas:
    1) Piso (Break-even): (custo_base + frete_fixo) / (1 - taxa_comissao)
    2) Teto (Posicionamento Estratégico): preco_concorrente * (1 + fator_posicionamento_eve)
    
    Retorna:
        Dicionário com os indicadores de preço e a viabilidade (Piso <= Teto).
    """
    
    # 1) Calcular o piso (Break-even point)
    # O piso garante que ao descontar a comissão, o valor cobre exatamente custo + frete.
    try:
        piso = (custo_base + frete_fixo) / (1.0 - taxa_comissao)
    except ZeroDivisionError:
        piso = float('inf')
        
    # Calculando preço considerando a margem alvo apenas para referência adicional
    try:
        preco_com_margem = (custo_base + frete_fixo) / (1.0 - taxa_comissao - margem_alvo)
    except ZeroDivisionError:
        preco_com_margem = float('inf')

    # 2) Calcular o teto
    # O teto é balizado pelo concorrente ajustado pelo nosso EVE (Economic Value Estimation)
    teto = preco_concorrente * (1.0 + fator_posicionamento_eve)
    
    # 3) Verificar viabilidade
    # Se o piso (custo sem prejuízo) for maior que o teto aceito pelo mercado, a venda é inviável
    is_viavel = piso <= teto
    
    # Preço sugerido: Teto (maximização de receita dentro da estratégia de posicionamento)
    # Poderíamos também utilizar outras estratégias, mas o teto é seguro se for viável.
    preco_sugerido = teto if is_viavel else None
    
    # 4) Retornar o dicionário de resposta
    return {
        "viavel": is_viavel,
        "piso": round(piso, 2),
        "teto": round(teto, 2),
        "preco_sugerido": round(preco_sugerido, 2) if preco_sugerido is not None else None,
        "preco_com_margem_alvo": round(preco_com_margem, 2) if preco_com_margem != float('inf') else None,
        "mensagem": "Viável" if is_viavel else "Inviável: Piso > Teto"
    }
