// Define o armazenamento do contrato com um mapeamento das apólices.
#[storage]
pub trait SeguroStorage {
    /// Mapeia uma apólice (identificada por um BigUint) para os dados da apólice.
    #[view(getPolicy)]
    #[storage_mapper("policies")]
    fn policies(&self) -> StorageMap<BigUint, Policy<Self::Api>>;
}

/// Estrutura que representa uma apólice de seguro.
/// Os campos incluem:
/// - `contratante`: endereço da carteira do contratante (destinatário do pagamento em EGLD).
/// - `local`: localização (nome da cidade ou coordenadas geográficas).
/// - `limite_chuva`: valor limite de chuva (em mm) que serve como gatilho para o seguro.
/// - `duracao_dias`: número de dias consecutivos para a medição.
/// - `valor_indemnizacao`: valor da indenização em caso de acionamento.
/// - `ativo`: status da apólice (ativa ou inativa).
/// - `expiration`: tempo de expiração da apólice (timestamp ou número de bloco).
/// - `ultima_atualizacao`: timestamp da última atualização, opcional.
#[derive(TopEncode, TopDecode, NestedEncode, NestedDecode, TypeAbi, Clone, PartialEq, Debug)]
pub struct Policy<T: ManagedTypeApi> {
    pub contratante: ManagedAddress,
    pub local: ManagedBuffer,
    pub limite_chuva: u64,
    pub duracao_dias: u64,
    pub valor_indemnizacao: BigUint,
    pub ativo: bool,
    pub expiration: u64,
    #[codec(optional)]
    pub ultima_atualizacao: Option<u64>,
}

#[init]
fn init(&self) {
    // Inicialização do contrato (caso seja necessário configurar algum parâmetro inicial).
}

/// Registra uma nova apólice de seguro.
///
/// Parâmetros:
/// - `policy_id`: Identificador único da apólice.
/// - `contratante`: Endereço da carteira do contratante (destino do pagamento).
/// - `local`: Localização (nome da cidade ou coordenadas).
/// - `limite_chuva`: Limite de precipitação em mm (gatilho para o acionamento).
/// - `duracao_dias`: Número de dias consecutivos para avaliar a precipitação.
/// - `valor_indemnizacao`: Valor da indenização (em EGLD).
/// - `expiration`: Prazo de validade da apólice (timestamp ou número de bloco).
#[endpoint(registerPolicy)]
pub fn register_policy(
    &self,
    policy_id: BigUint,
    contratante: ManagedAddress,
    local: ManagedBuffer,
    limite_chuva: u64,
    duracao_dias: u64,
    valor_indemnizacao: BigUint,
    expiration: u64
) {
    let policy = Policy {
        contratante: contratante.clone(),
        local,
        limite_chuva,
        duracao_dias,
        valor_indemnizacao,
        ativo: true,
        expiration,
        ultima_atualizacao: None,
    };
    self.policies().insert(policy_id, policy);
}

/// Aciona o pagamento do seguro caso as condições definidas sejam atendidas.
///
/// Parâmetros:
/// - `policy_id`: Identificador da apólice.
/// - `chuva_acumulada`: Valor acumulado de chuva (em mm) medido pelo oráculo off-chain durante o período de `duracao_dias`.
/// - `timestamp`: Data/hora da medição (usado para validar a expiração).
#[endpoint(trigger)]
pub fn trigger_payment(&self, policy_id: BigUint, chuva_acumulada: u64, timestamp: u64) {
    // Recupera a apólice com base no ID.
    let mut policy = self
        .policies()
        .get(&policy_id)
        .expect("Policy not found");

    // Verifica se a apólice ainda está ativa.
    require!(policy.ativo, "Policy is not active");
    // Garante que a medição está dentro do prazo da apólice.
    require!(timestamp <= policy.expiration, "Policy has expired");
    // Verifica se a chuva acumulada é menor que o limite definido.
    require!(
        chuva_acumulada < policy.limite_chuva,
        "Conditions for triggering the insurance are not met"
    );

    // Lógica de pagamento: transfere o valor da indenização para o endereço do contratante.
    self.send().direct(
        &policy.contratante,
        &policy.valor_indemnizacao,
        b"Insurance payout"
    );

    // Atualiza o status da apólice para inativa e registra o timestamp da última atualização.
    policy.ativo = false;
    policy.ultima_atualizacao = Some(timestamp);
    self.policies().insert(policy_id, policy);
}
