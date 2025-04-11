#![no_std]

multiversx_sc::imports!();
multiversx_sc::derive_imports!();
use multiversx_sc::{derive_imports::*, imports::*};
pub mod seguro_parametrico_proxy;
#[allow(unused_imports)]

#[type_abi]
#[derive(TopEncode, TopDecode, NestedEncode, NestedDecode, Clone, PartialEq, Debug)]
pub struct Policy<M: ManagedTypeApi> {
    pub contratante: ManagedAddress<M>,
    pub local: ManagedBuffer<M>,
    pub limite_chuva: u64,
    pub duracao_dias: u64,
    pub valor_indemnizacao: BigUint<M>,
    pub ativo: bool,
    pub expiration: u64,
    pub ultima_atualizacao: Option<u64>,
}
 
#[multiversx_sc::contract]
pub trait SeguroParametrico {
   /// Inicializa o contrato.
    #[init]
    fn init(&self) {
        // Se necessário, inicialize parâmetros ou registre dados padrão.
    }
    
    // -------------------------------------------------------
    // ARMAZENAMENTO
    // -------------------------------------------------------

    /// Mapeia um identificador (BigUint) para uma apólice.
    #[storage_mapper("policies")]
    fn policies(&self) -> MapMapper<BigUint<Self::Api>, Policy<Self::Api>>;

    // -------------------------------------------------------
    // REGISTRO DE APÓLICE
    // -------------------------------------------------------

    /// Registra uma nova apólice de seguro.
    ///
    /// Parâmetros:
    /// - `policy_id`: Identificador único da apólice.
    /// - `contratante`: Endereço da carteira do contratante (destinatário do pagamento).
    /// - `local`: Localização (nome ou coordenadas).
    /// - `limite_chuva`: Limite de precipitação (em mm) que define o gatilho.
    /// - `duracao_dias`: Período de observação (em dias).
    /// - `valor_indemnizacao`: Valor da indenização (em EGLD).
    /// - `expiration`: Momento de expiração da apólice (timestamp ou número de bloco).
    #[endpoint(registerPolicy)]
    fn register_policy(
        &self,
        policy_id: BigUint<Self::Api>,
        contratante: ManagedAddress<Self::Api>,
        local: ManagedBuffer<Self::Api>,
        limite_chuva: u64,
        duracao_dias: u64,
        valor_indemnizacao: BigUint<Self::Api>,
        expiration: u64,
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

    // #[payable("EGLD")]
    // #[endpoint(receberFundos)]
    // fn receber_fundos(&self) {
    //     // Não precisa fazer nada
    //     // Apenas para aceitar o valor enviado
    // }


    #[payable("EGLD")]
    #[endpoint(receber_fundos)]
    fn receber_fundos(&self) {
        let payment = self.call_value().egld(); // Obtém o valor enviado como EGLD
        let payment_value = payment.clone().into_big_int(); // ✅ Converte para BigUint de forma segura
        require!(payment_value > 0, "Nenhum EGLD enviado"); // Verifica se o valor é maior que zero

        // Aqui você pode armazenar, logar ou reagir ao valor recebido
        // Por exemplo:
        //self.blockchain().print(&payment_value); // Apenas para debug
}


    // -------------------------------------------------------
    // ACIONAMENTO DO SEGURO
    // -------------------------------------------------------

    /// Aciona o pagamento do seguro caso as condições definidas sejam atendidas.
    ///
    /// Parâmetros:
    /// - `policy_id`: Identificador da apólice.
    /// - `chuva_acumulada`: Valor acumulado de chuva (em mm) medido pelo oráculo.
    /// - `timestamp`: Momento da medição (usado para validar a expiração).
    ///
    /// Condições:
    /// - A apólice deve estar ativa.
    /// - O timestamp não pode ultrapassar a expiração.
    /// - A precipitação acumulada deve ser menor que o limite definido.
    ///
    /// Ação:
    /// - Transfere o valor da indenização em EGLD para o contratante.
    /// - Atualiza a apólice para inativa e registra o timestamp da atualização.
    #[endpoint(triggerPayment)]
    fn trigger_payment(
        &self,
        policy_id: BigUint<Self::Api>,
        chuva_acumulada: u64,
        timestamp: u64,
    ) {
        let mut policy = self
            .policies()
            .get(&policy_id)
            .expect("Policy not found");

        require!(policy.ativo, "Policy is not active");
        require!(timestamp <= policy.expiration, "Policy has expired");
        require!(
            chuva_acumulada > policy.limite_chuva,
            "Conditions for triggering the insurance are not met"
        );

        // Efetua a transferência da indenização (em EGLD) para o contratante.
        // A função `direct_egld` do SDK espera dois argumentos: o endereço e o valor.
        self.send().direct_egld(&policy.contratante, &policy.valor_indemnizacao);

        // Marca a apólice como inativa e registra o timestamp da atualização.
        policy.ativo = false;
        policy.ultima_atualizacao = Some(timestamp);
        self.policies().insert(policy_id, policy);
    }

    // -------------------------------------------------------
    // VIEW: Consulta de Apólice
    // -------------------------------------------------------

    /// Consulta os dados da apólice com o ID fornecido.
    #[view(getPolicy)]
    fn get_policy(
        &self,
        policy_id: BigUint<Self::Api>
    ) -> Option<Policy<Self::Api>> {
        self.policies().get(&policy_id)
    }

    #[upgrade]                  
    fn upgrade(&self) {}  
}
