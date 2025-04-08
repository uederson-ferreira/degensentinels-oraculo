use seguro_parametrico_sc::ContractBuilder;
use seguro_parametrico_sc::AbiProvider;

fn main() {
    ContractBuilder::builder() // Inicializa o ContractBuilder corretamente
        .with_contract::<AbiProvider>() // Adiciona o contrato
        .with_contract_dir("smart-contracts/seguro_parametrico_sc") // Define o diretório do contrato
        .build(); // Finaliza a construção (substituí `proxy()` por `build()`, que é mais comum)
}