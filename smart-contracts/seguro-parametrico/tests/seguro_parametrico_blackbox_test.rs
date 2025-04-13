// Estamos importando ferramentas de simulação do MultiversX
use multiversx_sc_scenario::imports::*;
use seguro_parametrico::seguro_parametrico_proxy::{self, Policy};

// Caminho para o bytecode e metadados do contrato
const CODE_PATH: MxscPath = MxscPath::new("output/seguro_parametrico.mxsc.json");

// Endereços fictícios usados nos testes
const OWNER: TestAddress = TestAddress::new("owner");
const BENEFICIARIO: TestAddress = TestAddress::new("beneficiario");
const CONTRATO: TestSCAddress = TestSCAddress::new("seguro");

// Criação do ambiente de simulação
fn world() -> ScenarioWorld {
    let mut blockchain = ScenarioWorld::new();
    blockchain.set_current_dir_from_workspace("seguro_parametrico");
    blockchain.register_contract(CODE_PATH, seguro_parametrico::ContractBuilder);
    blockchain
}

// Função de deploy padrão utilizada por todos os testes
fn seguro_parametrico_deploy() -> ScenarioWorld {
    let mut world = world();
    world.account(OWNER).nonce(0).balance(5_000_000_000u64); // Dono tem saldo inicial

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
            3u32,
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
            limite_acionamentos: 3,
            acionamentos: 0,
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
            3u32,
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
        .trigger_payment(&policy_id, 120u64, 999_000u64) // Chuva maior que o limite
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
            3u32,
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

    world.current_block().block_timestamp(888_000u64);

    // Aciona pagamento com chuva maior que o limite → esperamos erro
    world
        .tx()
        .from(OWNER)
        .to(CONTRATO)
        .typed(seguro_parametrico_proxy::SeguroParametricoProxy)
        // Se a policy tem limite 40:
        .trigger_payment(&policy_id, 40u64, 888_000u64) // ← isso não deve acionar
        .with_result(ExpectError(4, "Conditions for triggering the insurance are not met"))
        .run();
}

/// Teste com múltiplos acionamentos controlados por tempo e limite
#[test]
fn test_multiple_trigger_with_wait() {
    let mut world = seguro_parametrico_deploy();

    let policy_id = BigUint::from(3u64);
    let indemnizacao = BigUint::from(1_000_000_000u64);
    let duracao_dias = 10u64;
    let limite_acionamentos = 2u32;

    world.account(BENEFICIARIO).nonce(0).balance(0);

    world.tx().from(OWNER).to(CONTRATO).typed(seguro_parametrico_proxy::SeguroParametricoProxy).register_policy(
        &policy_id,
        &BENEFICIARIO.to_address(),
        &ManagedBuffer::from("Zona Rural"),
        70u64,
        duracao_dias,
        &indemnizacao,
        1_000_000u64,
        limite_acionamentos,
    ).run();

    world.tx().from(OWNER).to(CONTRATO).egld(&(&indemnizacao * 2u32)).raw_call("receber_fundos").run();

    // Primeiro acionamento - válido
    world.current_block().block_timestamp(100_000u64);
    world.tx().from(OWNER).to(CONTRATO).typed(seguro_parametrico_proxy::SeguroParametricoProxy).trigger_payment(&policy_id, 80u64, 100_000u64).run();

    // Segundo acionamento - muito cedo, erro esperado
    world.current_block().block_timestamp(100_100u64);
    world.tx().from(OWNER).to(CONTRATO).typed(seguro_parametrico_proxy::SeguroParametricoProxy).trigger_payment(&policy_id, 90u64, 100_100u64)
        .with_result(ExpectError(4, "Aguardando intervalo mínimo entre acionamentos")).run();

    // Aguarda intervalo válido (10 dias)
    world.current_block().block_timestamp(964_001u64);
    world.tx().from(OWNER).to(CONTRATO).typed(seguro_parametrico_proxy::SeguroParametricoProxy).trigger_payment(&policy_id, 95u64, 964_001u64).run();

    // Terceiro acionamento - excede o limite
    world.current_block().block_timestamp(1_828_002u64);
    world.tx().from(OWNER).to(CONTRATO).typed(seguro_parametrico_proxy::SeguroParametricoProxy).trigger_payment(&policy_id, 100u64, 1_828_002u64)
        .with_result(ExpectError(4, "Policy is not active")).run();

    world.check_account(BENEFICIARIO).balance(&(indemnizacao * 2u32));
}

/// Teste com apólice ilimitada que permite múltiplos acionamentos
#[test]
fn test_unlimited_trigger() {
    let mut world = seguro_parametrico_deploy();

    let policy_id = BigUint::from(4u64);
    let indemnizacao = BigUint::from(1_000_000_000u64); // 1 EGLD
    let duracao_dias = 5u64;
    let limite_acionamentos = 0u32;

    world.account(BENEFICIARIO).nonce(0).balance(0);

    // 1. Registro da apólice com acionamentos ilimitados
    world.tx()
        .from(OWNER)
        .to(CONTRATO)
        .typed(seguro_parametrico_proxy::SeguroParametricoProxy)
        .register_policy(
            &policy_id,
            &BENEFICIARIO.to_address(),
            &ManagedBuffer::from("Área Ilimitada"),
            60u64,
            duracao_dias,
            &indemnizacao,
            2_000_000u64,
            limite_acionamentos,
        )
        .run();

    // 2. Envia 1 EGLD 3 vezes (total = 3 EGLD)
    for i in 1..=3 {
        world
            .tx()
            .from(OWNER)
            .to(CONTRATO)
            .egld(&indemnizacao)
            .raw_call("receber_fundos")
            .run();
        println!("✅ Fundos enviados: {i} EGLD");
    }

    // 3. Verifica saldo no contrato = 3 EGLD
    world.check_account(CONTRATO).balance(&(indemnizacao.clone() * 3u32));

    // 4. Acionamento 1
    world.current_block().block_timestamp(200_000u64);
    world.tx()
        .from(OWNER)
        .to(CONTRATO)
        .typed(seguro_parametrico_proxy::SeguroParametricoProxy)
        .trigger_payment(&policy_id, 70u64, 200_000u64)
        .run();

    // 5. Acionamento 2 (após 5 dias)
    world.current_block().block_timestamp(632_001u64);
    world.tx()
        .from(OWNER)
        .to(CONTRATO)
        .typed(seguro_parametrico_proxy::SeguroParametricoProxy)
        .trigger_payment(&policy_id, 80u64, 632_001u64)
        .run();

    // 6. Acionamento 3 (após mais 5 dias)
    world.current_block().block_timestamp(1_064_002u64);
    world.tx()
        .from(OWNER)
        .to(CONTRATO)
        .typed(seguro_parametrico_proxy::SeguroParametricoProxy)
        .trigger_payment(&policy_id, 90u64, 1_064_002u64)
        .run();

    // 7. Verifica saldo final do beneficiário: 3x indenização
    world.check_account(BENEFICIARIO).balance(&(indemnizacao * 3u32));
}

/// Teste: não deve permitir acionamento após expiração da apólice
#[test]
fn test_trigger_after_expiration() {
    let mut world = seguro_parametrico_deploy();

    let policy_id = BigUint::from(5u64);
    let indemnizacao = BigUint::from(1_000_000_000u64);

    world.account(BENEFICIARIO).nonce(0).balance(0);

    // Apólice já expirada (expiração em 500_000)
    world.tx().from(OWNER).to(CONTRATO).typed(seguro_parametrico_proxy::SeguroParametricoProxy).register_policy(
        &policy_id,
        &BENEFICIARIO.to_address(),
        &ManagedBuffer::from("Expirada"),
        30u64,
        5u64,
        &indemnizacao,
        500_000u64,
        1u32,
    ).run();

    world.tx().from(OWNER).to(CONTRATO).egld(&indemnizacao).raw_call("receber_fundos").run();

    world.current_block().block_timestamp(600_000u64);
    world.tx().from(OWNER).to(CONTRATO).typed(seguro_parametrico_proxy::SeguroParametricoProxy)
        .trigger_payment(&policy_id, 50u64, 600_000u64)
        .with_result(ExpectError(4, "Policy has expired"))
        .run();
}

/// Teste: cancelamento impede acionamento posterior
#[test]
fn test_cancel_then_trigger() {
    let mut world = seguro_parametrico_deploy();

    let policy_id = BigUint::from(6u64);
    let indemnizacao = BigUint::from(1_000_000_000u64);

    world.account(BENEFICIARIO).nonce(0).balance(0);

    // Criação da apólice
    world.tx().from(OWNER).to(CONTRATO).typed(seguro_parametrico_proxy::SeguroParametricoProxy).register_policy(
        &policy_id,
        &BENEFICIARIO.to_address(),
        &ManagedBuffer::from("Cancelada"),
        30u64,
        5u64,
        &indemnizacao,
        900_000u64,
        1u32,
    ).run();

    world.tx().from(OWNER).to(CONTRATO).egld(&indemnizacao).raw_call("receber_fundos").run();

    // Cancela apólice
    world.tx().from(OWNER).to(CONTRATO).typed(seguro_parametrico_proxy::SeguroParametricoProxy)
        .cancelar_apolice(&policy_id).run();

    // Tenta acionar depois do cancelamento
    world.current_block().block_timestamp(800_000u64);
    world.tx().from(OWNER).to(CONTRATO).typed(seguro_parametrico_proxy::SeguroParametricoProxy)
        .trigger_payment(&policy_id, 60u64, 800_000u64)
        .with_result(ExpectError(4, "Policy is not active"))
        .run();
}

/// Teste: reativação permite novo acionamento após cancelamento
#[test]
fn test_cancel_reactivate_trigger() {
    let mut world = seguro_parametrico_deploy();

    let policy_id = BigUint::from(7u64);
    let indemnizacao = BigUint::from(1_000_000_000u64);

    world.account(BENEFICIARIO).nonce(0).balance(0);

    world.tx().from(OWNER).to(CONTRATO).typed(seguro_parametrico_proxy::SeguroParametricoProxy).register_policy(
        &policy_id,
        &BENEFICIARIO.to_address(),
        &ManagedBuffer::from("Reativada"),
        20u64,
        3u64,
        &indemnizacao,
        1_500_000u64,
        1u32,
    ).run();

    world.tx().from(OWNER).to(CONTRATO).egld(&indemnizacao).raw_call("receber_fundos").run();

    world.tx().from(OWNER).to(CONTRATO).typed(seguro_parametrico_proxy::SeguroParametricoProxy)
        .cancelar_apolice(&policy_id).run();

    world.tx().from(OWNER).to(CONTRATO).typed(seguro_parametrico_proxy::SeguroParametricoProxy)
        .reativar_apolice(&policy_id).run();

    world.current_block().block_timestamp(700_000u64);
    world.tx().from(OWNER).to(CONTRATO).typed(seguro_parametrico_proxy::SeguroParametricoProxy)
        .trigger_payment(&policy_id, 25u64, 700_000u64).run();

    world.check_account(BENEFICIARIO).balance(&indemnizacao);
}

/// Teste: endereço não autorizado tentando cancelar apólice
#[test]
fn test_unauthorized_cancel() {
    let mut world = seguro_parametrico_deploy();

    let policy_id = BigUint::from(8u64);
    let indemnizacao = BigUint::from(1_000_000_000u64);

    world.tx().from(OWNER).to(CONTRATO).typed(seguro_parametrico_proxy::SeguroParametricoProxy).register_policy(
        &policy_id,
        &BENEFICIARIO.to_address(),
        &ManagedBuffer::from("Protegida"),
        25u64,
        2u64,
        &indemnizacao,
        1_200_000u64,
        1u32,
    ).run();

    world.account(BENEFICIARIO).nonce(0).balance(0);

    // Tenta cancelar com endereço não autorizado (BENEFICIARIO)
    world.tx().from(BENEFICIARIO).to(CONTRATO).typed(seguro_parametrico_proxy::SeguroParametricoProxy)
        .cancelar_apolice(&policy_id)
        .with_result(ExpectError(4, "Apenas o dono do contrato pode cancelar"))
        .run();
} 
