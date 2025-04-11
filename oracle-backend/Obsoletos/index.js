// oracle-backend/index.js

// Carrega as variáveis de ambiente a partir de um arquivo .env
require('dotenv').config();

import { get } from 'axios';
// Supondo que exista um SDK da MultiversX; ajuste conforme a biblioteca oficial
import { MultiversxSDK, Transaction } from 'multiversx-sdk'; // pseudocódigo

// Configurações através de variáveis de ambiente
const OPENWEATHER_API_KEY = process.env.OPENWEATHER_API_KEY; // Sua chave da API do OpenWeatherMap
const CONTRACT_ADDRESS = process.env.CONTRACT_ADDRESS;       // Endereço do smart contract
const POLICY_ID = process.env.POLICY_ID || '1';                // ID da apólice (pode ser definido dinamicamente)
const NETWORK_RPC = process.env.NETWORK_RPC;                 // URL do provider (ex.: testnet)

// Configurações geográficas
const LATITUDE = parseFloat(process.env.LATITUDE || '-23.5505');    // Exemplo: São Paulo
const LONGITUDE = parseFloat(process.env.LONGITUDE || '-46.6333');    // Exemplo: São Paulo

// Parâmetros do seguro
const ACCUMULATION_PERIOD_DAYS = parseInt(process.env.ACCUMULATION_PERIOD_DAYS || '10'); // Período de acumulação (em dias)
const PRECIPITATION_THRESHOLD = parseFloat(process.env.PRECIPITATION_THRESHOLD || '80');   // Limiar em mm para acionamento

// Inicialização do SDK da MultiversX (pseudocódigo; ajuste para seu ambiente)
const sdk = new MultiversxSDK({
    provider: NETWORK_RPC,
    // Inclua outros parâmetros de configuração conforme a documentação
});

// Array global para armazenar as leituras de precipitação (em memória)
let precipitationRecords = [];

/**
 * Remove as leituras armazenadas que são mais antigas que o período de acumulação.
 */
function pruneOldRecords() {
    const now = Date.now() / 1000; // timestamp atual em segundos
    const periodSeconds = ACCUMULATION_PERIOD_DAYS * 24 * 3600;
    precipitationRecords = precipitationRecords.filter(record => (now - record.timestamp) <= periodSeconds);
}

/**
 * Calcula a precipitação acumulada a partir dos registros atuais.
 * @returns {number} Valor total acumulado (em mm)
 */
function getTotalAccumulatedPrecipitation() {
    return precipitationRecords.reduce((total, record) => total + record.precipitation, 0);
}

/**
 * Consulta os dados de precipitação na API do OpenWeatherMap para a latitude e longitude informadas.
 * @param {number} lat - Latitude
 * @param {number} lon - Longitude
 * @returns {Promise<number|null>} Retorna a precipitação (em mm) ou null se ocorrer erro.
 */
async function getPrecipitationData(lat, lon) {
    const url = `https://api.openweathermap.org/data/2.5/weather?lat=${lat}&lon=${lon}&appid=${OPENWEATHER_API_KEY}&units=metric`;
    try {
        const response = await get(url);
        // Considera a precipitação dos últimos 1h; adapte se necessário.
        const precipitation = response.data.rain ? response.data.rain['1h'] || 0 : 0;
        return precipitation;
    } catch (err) {
        console.error('Erro ao buscar dados climáticos:', err);
        return null;
    }
}

/**
 * Aciona o pagamento do seguro chamando o endpoint "trigger" do smart contract.
 * @param {string} policyId - Identificador da apólice
 * @param {number} accumulatedPrecipitation - Precipitação acumulada (em mm)
 * @param {number} timestamp - Timestamp atual (em segundos)
 */
async function triggerInsurance(policyId, accumulatedPrecipitation, timestamp) {
    const functionName = 'trigger';
    const txData = [policyId, accumulatedPrecipitation, timestamp];

    try {
        // Cria a transação para chamar o endpoint 'trigger' no contrato.
        // Os detalhes como nonce, gasPrice, gasLimit devem ser definidos conforme o SDK e as regras da rede.
        const transaction = await sdk.createTransaction({
            receiver: CONTRACT_ADDRESS,
            function: functionName,
            data: txData,
            // Outros parâmetros podem ser adicionados aqui.
        });
        // Envia a transação para a blockchain.
        const txResult = await sdk.sendTransaction(transaction);
        console.log('Transação enviada com sucesso:', txResult);
    } catch (error) {
        console.error('Erro ao enviar a transação:', error);
    }
}

/**
 * Função que consolida o fluxo:
 * 1. Obtém dados de precipitação.
 * 2. Armazena e acumula os dados durante o período definido.
 * 3. Verifica se a precipitação acumulada está abaixo do limiar.
 * 4. Se sim, aciona o seguro via smart contract.
 */
async function checkPolicy() {
    console.log('Verificação iniciada em', new Date());
    
    // Obtém a leitura atual de precipitação.
    const currentPrecipitation = await getPrecipitationData(LATITUDE, LONGITUDE);
    if (currentPrecipitation === null) {
        console.log("Falha ao obter dados climáticos; a verificação será reprogramada para o próximo ciclo.");
        return;
    }

    const currentTimestamp = Math.floor(Date.now() / 1000); // Timestamp atual (segundos)
    console.log(`Precipitação atual: ${currentPrecipitation} mm`);

    // Armazena a leitura atual.
    precipitationRecords.push({ timestamp: currentTimestamp, precipitation: currentPrecipitation });
    
    // Remove registros antigos, mantendo apenas os últimos N dias.
    pruneOldRecords();

    // Calcula a precipitação acumulada durante o período configurado.
    const totalAccumulated = getTotalAccumulatedPrecipitation();
    console.log(`Precipitação acumulada dos últimos ${ACCUMULATION_PERIOD_DAYS} dias: ${totalAccumulated.toFixed(2)} mm`);

    // Se o acumulado for menor que o limiar, aciona o seguro.
    if (totalAccumulated < PRECIPITATION_THRESHOLD) {
        console.log('Condições atingidas, acionando o seguro...');
        await triggerInsurance(POLICY_ID, totalAccumulated, currentTimestamp);
    } else {
        console.log('Condições não atendidas. Nenhum acionamento realizado.');
    }
}

// Programa a execução da verificação a cada hora (3600000 milissegundos)
setInterval(checkPolicy, 60 * 60 * 1000);

// Execução imediata na inicialização (opcional)
checkPolicy();