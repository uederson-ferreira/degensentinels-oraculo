#![no_std]

multiversx_sc::imports!();
multiversx_sc::derive_imports!();

use multiversx_sc::{derive_imports::*, imports::*};

pub mod seguro_parametrico_proxy;
#[allow(unused_imports)]

// -------------------------------------------------------
// Estrutura de dados que representa uma apólice de seguro
// -------------------------------------------------------
#[type_abi]
#[derive(TopEncode, TopDecode, NestedEncode, NestedDecode, Clone, PartialEq, Debug)]
pub struct Policy<M: ManagedTypeApi> {
    pub contratante: ManagedAddress<M>,      // Endereço do beneficiário
    pub local: ManagedBuffer<M>,             // Localização do seguro
    pub limite_chuva: u64,                   // Gatilho de chuva em mm
    pub duracao_dias: u64,                   // Intervalo mínimo entre acionamentos
    pub valor_indemnizacao: BigUint<M>,      // Valor de indenização em EGLD
    pub ativo: bool,                         // Status da apólice (ativa ou não)
    pub expiration: u64,                     // Data de expiração (timestamp)
    pub ultima_atualizacao: Option<u64>,     // Última data de acionamento (timestamp)
    pub limite_acionamentos: u32,            // Máximo de acionamentos permitidos (0 = ilimitado)
    pub acionamentos: u32,                   // Quantidade de vezes que a apólice foi acionada
}

// -------------------------------------------------------
// Contrato principal
// -------------------------------------------------------
#[multiversx_sc::contract]
pub trait SeguroParametrico {
    
    /// É executada apenas uma vez, no momento do deploy.
    #[init]
    fn init(&self) {
        // Obtém o endereço da conta que está realizando o deploy
        let caller = self.blockchain().get_caller();

        // Define esse endereço como o "dono" do contrato
        // Somente esse endereço poderá usar funções restritas como cancelar ou reativar apólices
        self.owner().set(&caller);
    }

    /// Mapeamento do dono do contrato
    #[storage_mapper("owner")]
    fn owner(&self) -> SingleValueMapper<ManagedAddress<Self::Api>>;

    // Armazenamento de apólices usando o ID como chave
    #[storage_mapper("policies")]
    fn policies(&self) -> MapMapper<BigUint<Self::Api>, Policy<Self::Api>>;

    // -------------------------------------------------------
    // REGISTRO DE NOVA APÓLICE
    // -------------------------------------------------------
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
        limite_acionamentos: u32, // Novo parâmetro
    ) {
        let policy = Policy {
            contratante,
            local,
            limite_chuva,
            duracao_dias,
            valor_indemnizacao,
            ativo: true,
            expiration,
            ultima_atualizacao: None,
            limite_acionamentos,
            acionamentos: 0,
        };

        self.policies().insert(policy_id, policy);
    }

    // -------------------------------------------------------
    // RECEBIMENTO DE FUNDOS (opcional)
    // -------------------------------------------------------
    #[payable("EGLD")]
    #[endpoint(receber_fundos)]
    fn receber_fundos(&self) {
        let payment = self.call_value().egld();
        let payment_value = payment.clone().into_big_int();
        require!(payment_value > 0, "Nenhum EGLD enviado");
    }

    // -------------------------------------------------------
    // ACIONAMENTO DO PAGAMENTO DO SEGURO
    // -------------------------------------------------------
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

        // Verifica se a apólice está ativa e dentro da validade
        require!(policy.ativo, "Policy is not active");
        require!(timestamp <= policy.expiration, "Policy has expired");

        // Verifica se a chuva acumulada supera o limite
        require!(
            chuva_acumulada > policy.limite_chuva,
            "Conditions for triggering the insurance are not met"
        );

        // Verifica se o número de acionamentos já atingiu o limite (se houver)
        if policy.limite_acionamentos != 0 {
            require!(
                policy.acionamentos < policy.limite_acionamentos,
                "Limite de acionamentos atingido"
            );
        }

        // Se já houve acionamento anterior, verifica se o intervalo mínimo foi respeitado
        if let Some(ultima) = policy.ultima_atualizacao {
            let intervalo_minimo = policy.duracao_dias * 86400; // dias → segundos
            require!(
                timestamp >= ultima + intervalo_minimo,
                "Aguardando intervalo mínimo entre acionamentos"
            );
        }

        // Faz o pagamento da indenização
        self.send().direct_egld(&policy.contratante, &policy.valor_indemnizacao);

        // Atualiza os dados da apólice
        policy.ultima_atualizacao = Some(timestamp);
        policy.acionamentos += 1;

        // Se atingiu o limite de acionamentos, desativa a apólice
        if policy.limite_acionamentos != 0 && policy.acionamentos >= policy.limite_acionamentos {
            policy.ativo = false;
        }

        self.policies().insert(policy_id, policy);
    }

    // -------------------------------------------------------
    // CANCELAMENTO MANUAL DA APÓLICE (apenas owner)
    // -------------------------------------------------------
    #[endpoint(cancelarApolice)]
    fn cancelar_apolice(&self, policy_id: BigUint<Self::Api>) {
        let caller = self.blockchain().get_caller();
        require!(caller == self.owner().get(), "Apenas o dono do contrato pode cancelar");

        let mut policy = self
            .policies()
            .get(&policy_id)
            .unwrap_or_else(|| sc_panic!("Apólice não encontrada"));

        require!(policy.ativo, "Apólice já está inativa");

        policy.ativo = false;
        policy.ultima_atualizacao = Some(self.blockchain().get_block_timestamp());
        self.policies().insert(policy_id, policy);
    }

    // -------------------------------------------------------
    // REATIVAÇÃO MANUAL DA APÓLICE (apenas owner)
    // -------------------------------------------------------
    #[endpoint(reativarApolice)]
    fn reativar_apolice(&self, policy_id: BigUint<Self::Api>) {
        let caller = self.blockchain().get_caller();
        require!(caller == self.owner().get(), "Apenas o dono do contrato pode reativar");

        let mut policy = self
            .policies()
            .get(&policy_id)
            .unwrap_or_else(|| sc_panic!("Apólice não encontrada"));

        require!(!policy.ativo, "Apólice já está ativa");

        policy.ativo = true;
        policy.ultima_atualizacao = Some(self.blockchain().get_block_timestamp());
        self.policies().insert(policy_id, policy);
    }

    // -------------------------------------------------------
    // CONSULTA ÚNICA DE APÓLICE
    // -------------------------------------------------------
    #[view(getPolicy)]
    fn get_policy(
        &self,
        policy_id: BigUint<Self::Api>
    ) -> Option<Policy<Self::Api>> {
        self.policies().get(&policy_id)
    }

    // Permite upgrades futuros do contrato
    #[upgrade]
    fn upgrade(&self) {}
}