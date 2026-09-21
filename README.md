# Pricing Engine - V0 (Determinístico)

Um motor de precificação construído em Python e Streamlit. Este sistema calcula a viabilidade e o preço sugerido de um produto comparando regras determinísticas de margem e custo com os preços praticados no mercado (coletados em tempo real via Google Shopping / Serper API).

## 🏗️ Arquitetura do Projeto

O projeto foi construído seguindo uma arquitetura modularizada em 3 arquivos principais (sem persistência de banco de dados na V0):

- **`pricing_engine.py`**: O coração matemático. Contém regras determinísticas (sem Machine Learning). Calcula o **Piso** (Break-even), o **Teto** (Estratégia de posicionamento vs. Concorrente) e define se a operação é viável.
- **`market_api.py`**: O coletor de dados de mercado. Conecta-se à API do Serper.dev para fazer a busca das ofertas do Google Shopping Brasil. Contém tratamento de erros de conexão, higienização rigorosa de moedas e uso do Fuzzy Matching nativo do Google.
- **`app.py`**: A interface de usuário (Frontend). Construída com Streamlit, permite imputar custos fixos, comissões e consultar a viabilidade de venda do produto em tempo real na tela.

## 🚀 Como Executar Localmente

### 1. Pré-requisitos
- Python instalado na máquina.
- Conta na [Serper.dev](https://serper.dev/) para gerar a chave da API (Google Shopping).

### 2. Configuração do Ambiente Virtual (VENV)
Ative o seu ambiente virtual para evitar conflitos de pacotes globais:
```bash
# Ativar no Windows (Powershell / CMD)
.\venv\Scripts\activate

# Ativar no Mac/Linux (Terminal)
source venv/bin/activate
```

### 3. Instalação das Dependências
Com o ambiente ativado (aparecerá `(venv)` no seu terminal), instale as bibliotecas necessárias:
```bash
pip install -r requirements.txt
```

### 4. Configuração da Variável de Ambiente
Crie um arquivo chamado exatamente `.env` na raiz do projeto e insira a sua chave de API:
```env
SERPAPI_KEY=sua_chave_secreta_aqui
```
*(Dica de segurança: O arquivo `.env` já está ignorado pelo `.gitignore`, então sua chave nunca subirá publicamente no repositório).*

### 5. Iniciando a Aplicação
Rode o sistema usando o comando do Streamlit:
```bash
python -m streamlit run app.py
```
O aplicativo abrirá automaticamente no seu navegador padrão no endereço `localhost:8501`.

## 🧮 Regras da Lógica de Negócio

A V0 utiliza as seguintes fórmulas:
- **Piso Mínimo:** `(Custo Base + Frete Fixo) / (1 - Taxa de Comissão)`
  *Garante que o preço de venda cobre todos os custos variáveis sem gerar prejuízo.*
- **Teto de Mercado:** `Preço do Concorrente * (1 + Fator EVE)`
  *Baseia-se na percepção de valor (Economic Value Estimation) ajustável entre -10% e +10%.*
- **Viabilidade:** Se o **Piso > Teto**, a venda é barrada, pois o custo para vender é mais caro do que o mercado aceita pagar.
