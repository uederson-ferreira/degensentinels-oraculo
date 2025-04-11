// Estamos importando algumas ferramentas que nos ajudam a brincar de blockchain.
use multiversx_sc_scenario::imports::*;
use seguro_parametrico::seguro_parametrico_proxy::{self, Policy};

const CODE_PATH: MxscPath = MxscPath::new("output/seguro_parametrico.mxsc.json");
const OWNER: TestAddress = TestAddress::new("owner");
const BENEFICIARIO: TestAddress = TestAddress::new("beneficiario");
const CONTRATO: TestSCAddress = TestSCAddress::new("seguro");

fn world() -> ScenarioWorld {
    let mut blockchain = ScenarioWorld::new();

    blockchain.set_current_dir_from_workspace("seguro_parametrico");
    blockchain.register_contract(CODE_PATH, seguro_parametrico::ContractBuilder);

    blockchain
}

fn seguro_parametrico_deploy() -> ScenarioWorld {
    let mut world = world();

    // Dono começa com saldo suficiente para cobrir as transações
    world.account(OWNER).nonce(0).balance(2_000_000_000u64);

    // Inicializa o contrato
    let contrato = world
        .tx()
        .from(OWNER)
        .typed(seguro_parametrico_proxy::SeguroParametricoProxy)
        .init()
        .code(CODE_PATH)
        .new_address(CONTRATO)
        .returns(ReturnsNewAddress)
        .run();

    assert_eq!(contrato, CONTRATO.to_address());

    world
}

// Teste: registro de apólice
#[test]
fn test_register_policy() {
    let mut world = seguro_parametrico_deploy();

    world.account(BENEFICIARIO).nonce(0).balance(0);

    let policy_id = BigUint::from(1u64);
    let limite_chuva = 50u64;
    let duracao_dias = 7u64;
    let indemnizacao = BigUint::from(1_000_000_000u64); // 1 EGLD
    let expiration = 123_456u64;
    let local = ManagedBuffer::from("Fazenda X");

    world
        .tx()
        .from(OWNER)
        .to(CONTRATO)
        .typed(seguro_parametrico_proxy::SeguroParametricoProxy)
        .register_policy(
            &policy_id,
            &BENEFICIARIO.to_address(),
            &local,
            limite_chuva,
            duracao_dias,
            &indemnizacao,
            expiration,
        )
        .run();

    world
        .query()
        .to(CONTRATO)
        .typed(seguro_parametrico_proxy::SeguroParametricoProxy)
        .get_policy(&policy_id)
        .returns(ExpectValue(Some(Policy {
            contratante: ManagedAddress::from(BENEFICIARIO.to_address()),
            local,
            limite_chuva,
            duracao_dias,
            valor_indemnizacao: indemnizacao,
            ativo: true,
            expiration,
            ultima_atualizacao: None,
        })))        
        .run();
}

#[test]
fn test_trigger_payment_success() {
    let mut world = seguro_parametrico_deploy();

    let policy_id = BigUint::from(1u64);
    let indemnizacao = BigUint::from(1_000_000_000u64); // 1 EGLD

    // Beneficiário começa com saldo 0
    world.account(BENEFICIARIO).nonce(0).balance(0);

    // Dono registra uma apólice
    world
        .tx()
        .from(OWNER)
        .to(CONTRATO)
        .typed(seguro_parametrico_proxy::SeguroParametricoProxy)
        .register_policy(
            &policy_id,
            &BENEFICIARIO.to_address(),
            &ManagedBuffer::from("Região Z"),
            100u64,
            10u64,
            indemnizacao.clone(),
            999_999u64,
        )
        .run();

    // Envia EGLD ao contrato
    world
    .tx()
    .from(OWNER)
    .to(CONTRATO)
    .egld(BigUint::from(1_000_000_000u64)) // Define o valor em EGLD
    .raw_call("receber_fundos") // Chama o método do contrato para receber fundos
    .run();

    // Avança o tempo do bloco
    world.current_block().block_timestamp(999_000u64);

    // Aciona pagamento com chuva menor que o limite
    world
        .tx()
        .from(OWNER)
        .to(CONTRATO)
        .typed(seguro_parametrico_proxy::SeguroParametricoProxy)
        .trigger_payment(&policy_id, 30u64, 999_000u64)
        .run();

    // Verifica se o beneficiário recebeu a indenização
    world.check_account(BENEFICIARIO).balance(1_000_000_000u64);
}

// Teste: acionar pagamento com erro (chuva alta)
#[test]
fn test_trigger_payment_fail_chuva_alta() {
    let mut world = seguro_parametrico_deploy();

    let policy_id = BigUint::from(2u64);

    world.account(BENEFICIARIO).nonce(0).balance(0);

    world
        .tx()
        .from(OWNER)
        .to(CONTRATO)
        .typed(seguro_parametrico_proxy::SeguroParametricoProxy)
        .register_policy(
            &policy_id,
            &BENEFICIARIO.to_address(),
            &ManagedBuffer::from("Região Y"),
            40u64,
            5u64,
            &BigUint::from(1_000_000_000u64),
            888_888u64,
        )
        .run();

    world.current_block().block_timestamp(888_000u64);

    // Aciona pagamento com chuva maior que o limite → esperamos erro
    world
        .tx()
        .from(OWNER)
        .to(CONTRATO)
        .typed(seguro_parametrico_proxy::SeguroParametricoProxy)
        .trigger_payment(&policy_id, 100u64, 888_000u64)
        .with_result(ExpectError(4, "Conditions for triggering the insurance are not met"))
        .run();
}
