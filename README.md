# FFF - BTC Market Analyzer (estudo)

## Status atual (CP-03)

- ✅ Coleta OHLCV via ccxt (Binance)
- ✅ Limpeza de dados (Fase 1.5)
- ✅ Price Action: Swing High / Swing Low
- ✅ EMAs (9/21/50)
- ✅ Market Structure (HH/HL/LH/LL)
- ✅ Positioning (bias 1D + zona 4H + invalidação)
- ✅ Backtest base em 15m (TP = 2R, 1 posição por vez)
- ✅ Log de trades em `logs/trades.csv`

## Como rodar

1. Criar venv e instalar dependências:
    - `pip install -r requirements.txt`
2. Executar:
    - `python main.py`

## Próximos passos (roadmap curto)

### Fase 2.8 — Modo COLLECT vs Modo TRADE

- [ ] Adicionar `MODE` no main (`collect` / `trade`)
- [ ] Implementar policy: max trades/dia, cooldown após loss, filtro de metade da zona

### Fase 2.9 — Signals log (dataset para IA)

- [ ] Gerar `logs/signals.csv` com oportunidades (in_zone/trigger/accepted)

### Fase 3.0 — Walk-forward backtest (sem lookahead)

- [ ] Recalcular bias/zona ao longo do tempo, evitando usar “zona do futuro” no passado

### Fase 3.1 — Métricas melhores

- [ ] Profit factor, expectancy, drawdown, distribuição de R
- [ ] Fee/slippage

### Fase 4 — Painel Web (candles + EMAs + swings + zonas)

- [ ] Dashboard com plot interativo
- [ ] Marcação de swings e estrutura no gráfico