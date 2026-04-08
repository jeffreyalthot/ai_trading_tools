# ai_trading_tools

Outil prêt à l'emploi pour brancher des signaux IA dans une stratégie **Freqtrade**.

Version actuelle du package: **56.9.1**.

## Fichiers inclus

- `strategies/AITradingToolsStrategy.py` : stratégie Freqtrade compatible avec des signaux IA externes + garde-fous risk engine.
- `ai_trading_tools/signal_engine.py` : moteur de chargement/fusion des prédictions IA (mono-modèle + ensemble multi-modèles pondéré).
- `tests/test_signal_engine.py` : tests unitaires sur la logique de chargement/fusion des signaux.

## Format attendu du fichier de signaux IA

Créer un fichier CSV : `user_data/data/ai_signals.csv`

### Mode simple (legacy)

```csv
date,prediction
2026-01-01T00:00:00Z,0.40
2026-01-01T00:15:00Z,0.32
2026-01-01T00:30:00Z,-0.10
```

### Mode ensemble (recommandé)

```csv
date,prediction_fast,prediction_slow,weight_fast,weight_slow,regime
2026-01-01T00:00:00Z,0.55,0.10,0.70,0.30,trend
2026-01-01T00:15:00Z,0.35,0.05,0.60,0.40,range
```

- `date` : timestamp UTC de la bougie
- `prediction` : score IA entre `-1` et `1` (mode simple)
- `prediction_*` : scores par modèle (mode ensemble)
- `weight_*` : poids par modèle (optionnel, mode ensemble)
- `regime` : étiquette de régime de marché (optionnel)

## Utilisation avec Freqtrade

1. Copier `AITradingToolsStrategy.py` dans votre dossier `user_data/strategies/` (ou ajuster le `--strategy-path`).
2. Vérifier que le module `ai_trading_tools/` est dans le PYTHONPATH du projet Freqtrade.
3. Lancer un backtest :

```bash
freqtrade backtesting --strategy AITradingToolsStrategy
```

## Comportement risk engine (intégré)

- Blocage des entrées en mode **risk_off** si volatilité court terme excessive (`atr_pct > 5%`) ou volume nul.
- Filtre de conviction IA minimal (`abs(ai_prediction) >= 0.18`).
- Sortie défensive renforcée si signal IA très négatif (`ai_prediction <= -0.60`).

## Personnalisation

Dans la stratégie, vous pouvez ajuster :

- `ai_buy_threshold` (défaut `0.25`)
- `ai_sell_threshold` (défaut `-0.25`)
- `minimal_roi`, `stoploss`, `timeframe`
- `max_atr_pct`, `min_ai_conviction`, `hard_exit_ai`

## Roadmap

- Voir `ROADMAP_TITAN_QUANTIQUE.md` pour la roadmap détaillée orientée exécution institutionnelle, résilience et scalabilité.
