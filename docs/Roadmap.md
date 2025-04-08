## 1. Roadmap do Projeto

### 1.1. Estrutura do Repositório

Crie uma organização clara para o projeto, algo como:

```
degensentinels-oraculo/
├── smart-contracts/   # Contratos inteligentes escritos em Rust para a MultiversX
├── oracle-backend/    # Serviço Off-chain para consulta das APIs e comunicação com a blockchain
├── frontend/          # (Opcional) Interface para cadastro, monitoramento e visualização de dados
└── docs/              # Documentação do projeto e fluxos de dados
```

### 1.2. Etapas de Desenvolvimento

1. **Smart Contract (On-chain):**
   - **Objetivo:** Registrar apólices, armazenar dados (local, limite de chuva, valor do seguro, status) e definir uma função para acionar o pagamento quando o gatilho (chuva abaixo do limiar) for atingido.
   - **Tecnologia:** Rust (usando as ferramentas e SDKs da MultiversX).

2. **Oracle Backend (Off-chain):**
   - **Objetivo:** Consultar periodicamente dados climáticos (por exemplo, com a API do OpenWeatherMap) e, se a condição de precipitação for identificada (chuva acumulada abaixo do limiar), enviar uma transação ao smart contract para acionamento do seguro.
   - **Tecnologia:** Pode ser desenvolvido em Node.js, Python ou outra linguagem de sua preferência.

3. **Frontend (Opcional):**
   - **Objetivo:** Permitir que os segurados cadastrem suas apólices, acompanhem o status do seguro, visualizem dados climáticos e históricos.
   - **Tecnologia:** React.js com TypeScript é uma boa opção para criar uma interface web interativa.

4. **Testes e Deploy:**
   - **Testnet:** Inicie os testes na testnet do MultiversX para validar todas as interações (on-chain e off-chain).
   - **Monitoramento:** Configure logs e alerts para acompanhar as consultas do oráculo e a execução dos contratos.

---

## 2. Desenvolvimento Inicial do Smart Contract

Abaixo, um exemplo simplificado de como pode ser implementado um contrato inteligente em Rust para gerenciar as apólices de seguro:

```rust
// smart-contracts/src/lib.rs
#![no_std]
elrond_wasm::imports!();

#[elrond_wasm::contract]
pub mod seguro_parametrico {
    #[storage]
    pub struct SeguroStorage<T: Storage> {
        policies: ManagedMap<BigUint, Policy<T>>,
    }

    #[derive(
        TopEncode, TopDecode, NestedEncode, NestedDecode, TypeAbi, Clone, PartialEq, Debug,
    )]
    pub struct Policy<T: Storage> {
        pub segurado: ManagedAddress,
        pub local: ManagedBuffer,          // Localização (exemplo: latitude, longitude ou nome da cidade)
        pub limite_chuva: u64,             // Limiar de precipitação (em mm acumulados)
        pub valor_indemnizacao: BigUint,   // Valor do seguro
        pub ativo: bool,                   // Status da apólice
        pub expiration: u64,               // Prazo da apólice (timestamp ou número de blocos)
        #[codec(optional)]
        pub ultima_atualizacao: Option<u64>,
    }

    #[init]
    fn init(&self) {}

    #[endpoint(registerPolicy)]
    pub fn register_policy(
        &self,
        policy_id: BigUint,
        segurado: ManagedAddress,
        local: ManagedBuffer,
        limite_chuva: u64,
        valor_indemnizacao: BigUint,
        expiration: u64
    ) {
        let policy = Policy {
            segurado: segurado.clone(),
            local,
            limite_chuva,
            valor_indemnizacao,
            ativo: true,
            expiration,
            ultima_atualizacao: None,
        };
        self.policies().insert(policy_id, policy);
    }

    #[endpoint(trigger)]
    pub fn trigger_payment(&self, policy_id: BigUint, chuva_acumulada: u64, timestamp: u64) {
        let mut policy = self.policies().get(&policy_id).expect("Policy not found");
        require!(policy.ativo, "Apólice não está ativa");
        require!(timestamp <= policy.expiration, "Apólice expirada");

        // Se a chuva acumulada for menor que o limite definido, aciona o pagamento
        require!(chuva_acumulada < policy.limite_chuva, "Condições para acionamento não atendidas");

        // Aqui você incluiria a lógica para realizar a transferência do valor da indenização para o segurado.
        // Por exemplo: self.send().direct(&policy.segurado, &policy.valor_indemnizacao, b"Pagamento de seguro");
        
        // Atualize o status da apólice
        policy.ativo = false;
        policy.ultima_atualizacao = Some(timestamp);
        self.policies().insert(policy_id, policy);
    }
}
```

*Observação:*  
- Esse código é um exemplo simplificado. Na prática, você precisará incluir validações adicionais, lidar com possíveis erros e integrar com as funções nativas dos SDKs da MultiversX.

---

## 3. Desenvolvimento do Oracle Backend

Utilize um serviço que consulte a API do OpenWeatherMap e chame o endpoint do smart contract quando necessário. Veja um exemplo básico em Node.js:

```javascript
// oracle-backend/index.js
const axios = require('axios');
const { MultiversXSDK } = require('multiversx-sdk'); // Exemplo: adapte conforme o SDK específico que estiver utilizando

const API_KEY = 'SUA_API_KEY_OPENWEATHERMAP';
const LAT = -23.5505, LON = -46.6333;  // Exemplo: São Paulo
const POLICY_ID = '1'; // Identificador da apólice (pode ser um BigUint em uma implementação real)

async function getPrecipitationData(lat, lon) {
    const url = `https://api.openweathermap.org/data/2.5/weather?lat=${lat}&lon=${lon}&appid=${API_KEY}`;
    
    try {
        const response = await axios.get(url);
        // Exemplo: dados de chuva da última hora
        const precipitation = response.data.rain ? response.data.rain['1h'] || 0 : 0;
        return precipitation;
    } catch (err) {
        console.error('Erro ao buscar dados climáticos:', err);
        return 0;
    }
}

async function checkAndTrigger() {
    const chuva = await getPrecipitationData(LAT, LON);
    console.log('Chuva acumulada:', chuva);

    // Aqui você define a lógica: se a chuva acumulada for menor que o limiar, chama o smart contract
    // Utilize o SDK do MultiversX para enviar a transação que chama o endpoint 'trigger'
    
    // Exemplo pseudocódigo:
    // const sdk = new MultiversXSDK({ ...config });
    // const tx = sdk.createTransaction({
    //   receiver: 'ENDEREÇO_DO_CONTRATO',
    //   data: [ 'trigger', POLICY_ID, chuva, Date.now() ],
    //   ...
    // });
    // await sdk.sendTransaction(tx);

    // Implemente a lógica real com base no SDK e nas credenciais configuradas.
}

setInterval(checkAndTrigger, 60 * 60 * 1000); // Verifica a cada hora (ajuste conforme necessário)
```

*Observação:*  
- Você deve substituir as variáveis, configurar corretamente o SDK da MultiversX e realizar o tratamento de chaves/assinaturas de forma segura.
- Esse código roda periodicamente (por exemplo, a cada hora) e verifica se a condição para o acionamento do seguro é atendida.

---

## 4. Próximos Passos

1. **Configuração e Testes Locais:**
   - Prepare o ambiente de desenvolvimento para Rust e Node.js.
   - Execute testes unitários no smart contract utilizando frameworks de teste da MultiversX.
   - Simule chamadas ao backend e valide a integração com dados reais da API.

2. **Deploy na Testnet:**
   - Faça o deploy do contrato inteligente na testnet do MultiversX.
   - Configure o serviço oráculo para apontar para a testnet e valide o fluxo completo (cadastro, verificação de clima e acionamento).

3. **Documentação e Monitoramento:**
   - Documente o processo, os endpoints e os fluxos de dados.
   - Implemente logs e alertas para monitorar chamadas à API e transações on-chain.

4. **Iterações e Feedback:**
   - Após o MVP estar funcionando, colete feedback dos usuários e ajuste os parâmetros (por exemplo, limiares de chuva, intervalos de verificação, etc.).
   - Explore a adição de funcionalidades opcionais, como uma interface mais completa ou integração com outras fontes de dados.

---

## 5. Próximos Passos Concretos

Agora, como próximo passo, você pode:

- Configurar o ambiente e estrutura do repositório conforme descrito.
- Implantar o contrato inteligente básico e realizar testes unitários.
- Configurar o serviço oráculo localmente para testar a comunicação com a API e a blockchain na testnet.