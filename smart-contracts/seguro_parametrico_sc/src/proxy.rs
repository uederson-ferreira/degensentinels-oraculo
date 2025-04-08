#![no_std]

multiversx_sc::imports!();

use seguro_parametrico::SeguroParametrico;

multiversx_sc::proxy! {
    pub trait ProxySeguroParametrico {
        fn register_policy(
            &self,
            policy_id: BigUint<Self::Api>,
            contratante: ManagedAddress<Self::Api>,
            local: ManagedBuffer<Self::Api>,
            limite_chuva: u64,
            duracao_dias: u64,
            valor_indemnizacao: BigUint<Self::Api>,
            expiration: u64
        );

        fn trigger_payment(&self, policy_id: BigUint<Self::Api>, chuva_acumulada: u64, timestamp: u64);

        #[view(getPolicy)]
        fn get_policy(&self, policy_id: BigUint<Self::Api>) -> Option<seguro_parametrico::Policy<Self::Api>>;
    }
}