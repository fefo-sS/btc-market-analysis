# BTC Analysis (Python)

Projeto de estudo para análise técnica do BTC com base em metodologias reais.

## Status do Projeto

### Checkpoint CP-02 (atual)

- Coleta de OHLCV via ccxt (Binance)
- Limpeza e padronização dos dados (Fase 1.5)
    - timestamp convertido e como índice
    - ordenação temporal
    - tipos numéricos garantidos
    - remoção de duplicatas
    - remoção do candle em formação
- Price Action (início)
    - detecção de Swing High e Swing Low
- Indicadores
    - cálculo de EMA 9 / 21 / 50
- Execução no `main.py` para:
    - BTC 1D
    - BTC 4H

## Como rodar

1. Criar ambiente virtual
2. Instalar dependências:
    - `pip install -r requirements.txt`
3. Executar:
    - `python main.py`

## Próximos passos (planejado)

- Estrutura de mercado (HH/HL/LH/LL)
- Tendência (uptrend/downtrend/range)
- Painel visual (web) com gráficos