# 📄 Documentação dos Endpoints
## Smart Contract: Seguro Paramétrico

---

## 🔧 `init`
### `fn init(&self)`
Inicializa o contrato e define o `owner` (quem fez o deploy).
> 🔒 Apenas executado no deploy.

---

## 📅 `registerPolicy`
### `fn register_policy(...)`
Registra uma nova apólice de seguro com parâmetros customizáveis.

#### Parâmetros:
- `policy_id: BigUint` – Identificador único da apólice
- `contratante: ManagedAddress` – Endereço do beneficiário
- `local: ManagedBuffer` – Local da propriedade segurada
- `limite_chuva: u64` – Chuva acumulada (em mm) para acionar
- `duracao_dias: u64` – Intervalo mínimo entre acionamentos (em dias)
- `valor_indemnizacao: BigUint` – Valor da indenização (em EGLD)
- `expiration: u64` – Data de expiração (timestamp)
- `limite_acionamentos: u32` – Máximo de ativações (0 = ilimitado)

#### Ações:
- Salva a apólice no storage.
- Marca como ativa.

---

## 💰 `receber_fundos`
### `fn receber_fundos(&self)`
Endpoint `payable("EGLD")` para envio de fundos ao contrato.
> Pode ser chamado várias vezes para abastecer o contrato com saldo suficiente.

---

## ⚙️ `triggerPayment`
### `fn trigger_payment(policy_id, chuva_acumulada, timestamp)`
Aciona a apólice e transfere o valor de indenização se todas as condições forem atendidas.

#### Parâmetros:
- `policy_id: BigUint`
- `chuva_acumulada: u64` – Valor de chuva da medição (mm)
- `timestamp: u64` – Timestamp da leitura

#### Regras de ativação:
- Apólice deve estar ativa
- Ainda válida (não expirada)
- Chuva superior ao limite
- Intervalo mínimo de tempo respeitado (se já houver uma ativação)
- Número de ativações abaixo do limite (se houver)

#### Resultado:
- Transfere valor para o contratante
- Atualiza `ultima_atualizacao` e `acionamentos`
- Desativa apólice se atingir limite

---

## ❌ `cancelarApolice`
### `fn cancelar_apolice(policy_id)`
Desativa manualmente uma apólice, impedindo novos acionamentos.

> 🔒 Apenas o `owner` pode executar.

---

## ♻️ `reativarApolice`
### `fn reativar_apolice(policy_id)`
Reativa manualmente uma apólice desativada anteriormente.

> 🔒 Apenas o `owner` pode executar.

---

## 👁️ `getPolicy`
### `fn get_policy(policy_id) -> Option<Policy>`
Consulta pública para obter os dados de uma apólice específica.

#### Retorno:
```rust
struct Policy {
    contratante: ManagedAddress,
    local: ManagedBuffer,
    limite_chuva: u64,
    duracao_dias: u64,
    valor_indemnizacao: BigUint,
    ativo: bool,
    expiration: u64,
    ultima_atualizacao: Option<u64>,
    acionamentos: u32,
    limite_acionamentos: u32
}
```

---

## 📦 Armazenamento

### `#[storage_mapper("policies")]`
- Mapeia `policy_id: BigUint` → `Policy`
- Todas as operações de consulta, edição e deleção usam este storage.

---

📅 Documentação gerada automaticamente com base na estrutura e comportamento do contrato Rust/MxSC