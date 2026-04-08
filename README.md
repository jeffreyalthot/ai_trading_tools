# ai_trading_tools

Outil prêt à l'emploi pour brancher des signaux IA dans une stratégie **Freqtrade**.

## Fichiers inclus

- `strategies/AITradingToolsStrategy.py` : stratégie Freqtrade compatible avec des signaux IA externes.
- `ai_trading_tools/signal_engine.py` : moteur de chargement et fusion des prédictions IA.

## Format attendu du fichier de signaux IA

Créer un fichier CSV : `user_data/data/ai_signals.csv`

```csv
date,prediction
2026-01-01T00:00:00Z,0.40
2026-01-01T00:15:00Z,0.32
2026-01-01T00:30:00Z,-0.10
```

- `date` : timestamp UTC de la bougie
- `prediction` : score IA entre `-1` et `1`

## Utilisation avec Freqtrade

1. Copier `AITradingToolsStrategy.py` dans votre dossier `user_data/strategies/` (ou ajuster le `--strategy-path`).
2. Vérifier que le module `ai_trading_tools/` est dans le PYTHONPATH du projet Freqtrade.
3. Lancer un backtest :

```bash
freqtrade backtesting --strategy AITradingToolsStrategy
```

## Personnalisation

Dans la stratégie, vous pouvez ajuster :

- `ai_buy_threshold` (défaut `0.25`)
- `ai_sell_threshold` (défaut `-0.25`)
- `minimal_roi`, `stoploss`, `timeframe`
