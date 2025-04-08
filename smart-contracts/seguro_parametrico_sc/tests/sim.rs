use multiversx_sc::types::{BigUint, ManagedBuffer};
use multiversx_sc_scenario::*;
use seguro_parametrico_sc::generated::proxy::ProxySeguroParametrico;

#[test]
fn test_register_and_trigger_policy() {
    let mut world = ScenarioWorld::new();

    let owner = world.create_user_account(&BigUint::from(1_000_000_000_000_000_000u64));

    let contrato = world
        .deploy_contract("file:output/seguro_parametrico.wasm", &owner, &[], "init")
        .contract_proxy::<ProxySeguroParametrico>();

    let policy_id = BigUint::from(1u32);
    let local = ManagedBuffer::from("Cidade XYZ");
    let limite_chuva = 100u64;
    let duracao_dias = 3u64;
    let expiration = 999999999u64;
    let valor_indemnizacao = BigUint::from(10_000_000_000_000_000u64);

    contrato
        .register_policy(
            &policy_id,
            &owner.address,
            &local,
            &limite_chuva,
            &duracao_dias,
            &valor_indemnizacao,
            &expiration,
        )
        .assert_ok();

    contrato
        .trigger_payment(&policy_id, &80u64, &888888888u64)
        .assert_ok();

    let policy = contrato.get_policy(&policy_id).execute().unwrap();
    assert_eq!(policy.ativo, false);
    assert_eq!(policy.ultima_atualizacao, Some(888888888));
}
