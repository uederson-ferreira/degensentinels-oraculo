# DegenSentinels Oráculo - Documentação Oficial

## Visão Geral

O projeto **DegenSentinels Oráculo** é um sistema de seguro paramétrico baseado em blockchain, desenvolvido na **MultiversX Devnet**, com backend em Python, smart contracts em Rust, e integração a oráculos de dados climáticos simulados. Ele permite o registro de apólices que são acionadas automaticamente com base na acumulação de chuvas.

## 🔐 Variáveis de Ambiente

Antes de executar o projeto, crie um arquivo .env na raiz do repositório com o seguinte conteúdo:

```bash
# 🔑 Chave da API do OpenWeather (opcional, se usar API real)

OPENWEATHER_API_KEY=your_openweather_api_key

# 📄 Caminho do arquivo PEM com chave privada do remetente
PEM_PATH=smart-contracts/carteiras/carteira1/erd1xxxxx.pem

# 🏷️ Endereço do contrato inteligente
CONTRACT_ADDRESS=erd1qqqqqqqqqqqqqpgqa6...

# 📬 Endereço da conta remetente
SENDER_ADDRESS=erd1xxxxx...

# 🔗 ID da rede (ex: D para Devnet)
CHAIN_ID=D

# 🌐 Proxy da rede MultiversX
PROXY=https://devnet-api.multiversx.com

```

## Tecnologias Utilizadas

- **MultiversX Devnet**: infraestrutura blockchain
- **Python 3.11**: backend do oráculo
- **Flask**: API de simulação climática
- **Rust**: smart contract compilado para WASM
- **Rich**: para logs e saídas visuais no terminal

---

## Estrutura do Projeto

```bash

├── oracle-backend/
│   ├── main.py                      # Oráculo de monitoramento das apólices
│   ├── register_policy.py          # Cadastro de novas apólices
│   ├── blockchain.py               # Envio de transações ao contrato
│   ├── weather.py                  # Obtenção de dados climáticos
│   ├── mock_api.py                 # API simulada de chuva
│   ├── apolices/                   # Armazena arquivos JSON das apólices
│   ├── listar_apolices.py         # Listagem de apólices cadastradas
│   ├── config.py                   # Configurações do projeto e .env
├── smart-contracts/               # Contrato inteligente em Rust
├── .gitignore                     # Ignora carteiras, apólices e ambientes locais

```

---

## Fluxo de Trabalho

### 1. Cadastro de Apólice

O arquivo `register_policy.py` permite cadastrar uma nova apólice, salvando:

- ID automático
- Local de cobertura
- Limite de chuva acumulada
- Duração em dias
- Valor da indenização (em wei)
- Data de expiração

Isso gera:

- Um arquivo JSON com os dados da apólice em `apolices/`
- Atualiza a lista `apolices_monitoradas.json`
- Envia uma transação para o contrato inteligente

### 2. Monitoramento

O `main.py` executa em loop:

- Lê a lista de apólices ativas
- Consulta dados de chuva da `mock_api.py`
- Compara o acumulado com o limite de cada apólice
- Aciona o contrato caso o limite seja ultrapassado

### 3. Acionamento

O `blockchain.py` envia uma transação `triggerPayment` para o contrato
com os dados da apólice, usando:

- ID da apólice
- Total de chuva (x10)
- Timestamp atual

---

## Simulação Climática

O `mock_api.py` permite simular chuva acumulada por 10 dias.

- Endpoint: `GET /onecall` retorna os dados simulados
- Endpoint: `POST /set?value=XX` define a chuva diária

---

## Considerações de Segurança

- O arquivo `.pem` e dados sensíveis estão protegidos via `.gitignore`
- A pasta `smart-contracts/carteiras/` foi removida do histórico
- As transações são assinadas com chaves locais e seguras

---

## Comandos úteis

```bash
# Ativar ambiente virtual
source oraculo-venv/bin/activate

# Executar API de chuva simulada
python mock_api.py

# Cadastrar nova apólice
python register_policy.py

# Rodar o oráculo principal
python main.py

# Listar apólices cadastradas
python listar_apolices.py
```

---

## Futuras Implementações

- Integração com OpenWeatherMap real
- Painel web com Streamlit ou Next.js
- Cadastro de múltiplas contas
- Validação descentralizada do oráculo

---

## Autor

- Uederson Ferreira (@uederson-ferreira)
- [GitHub](https://github.com/uederson-ferreira/degensentinels-oraculo.git)
- Desenvolvido durante o desafio [DOJO da NearX School](https://twitter.com/nearxschool)
