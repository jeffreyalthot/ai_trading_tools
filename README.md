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

## Roadmap d'amélioration (objectif : robustesse et performance durable)

> ⚠️ **Important** : viser des “gros gains” impose aussi de maîtriser le risque. Cette roadmap privilégie des performances **ajustées du risque** et une amélioration durable, plutôt qu'une promesse de profits garantis.

### Phase 1 — Fondations data & recherche (0-2 mois)

- **Pipeline de données multi-sources** (OHLCV, orderbook, funding, sentiment, macro, on-chain selon actifs).
- **Contrôle qualité data** : déduplication, alignement temporel, gestion des trous, détection d'anomalies.
- **Feature store versionné** pour reproduire exactement chaque expérience.
- **Cadre d'évaluation strict** : walk-forward, splits temporels, métriques PnL + Sharpe/Sortino + drawdown.
- **Backtests réalistes** : frais, slippage, latence, liquidité, tailles de position et contraintes d'exécution.

### Phase 2 — IA prédictive plus robuste (2-4 mois)

- **Ensemble de modèles** : modèles de séries temporelles (TFT/transformers), gradient boosting, signaux de régime.
- **Prédictions probabilistes** (direction + confiance) au lieu d'un score unique brut.
- **Détection de régime de marché** (trend/range/volatilité extrême) pour activer des sous-stratégies adaptées.
- **Calibration des signaux** (Platt/Isotonic) pour convertir la sortie IA en probabilité exploitable.
- **Monitoring de dérive** (data drift / concept drift) avec alertes et retraining piloté.

### Phase 3 — Moteur de décision trading (4-6 mois)

- **Position sizing dynamique** basé sur volatilité, corrélation et niveau de confiance du modèle.
- **Portefeuille multi-actifs** avec limites d'exposition par secteur/asset et budget de risque global.
- **Gestion active du risque** : circuit breakers, daily loss limits, max drawdown guard, kill-switch.
- **Sorties intelligentes** : prise de profit partielle, trailing adaptatif, time stop, invalidation de signal.
- **Filtre de coût d'exécution** : n'entrer que si l'edge estimé dépasse frais + slippage + marge de sécurité.

### Phase 4 — Optimisation continue & production (6-9 mois)

- **MLOps complet** : registry de modèles, CI/CD, tests de non-régression stratégie, déploiement progressif.
- **Paper trading -> capital progressif** avec seuils de validation avant montée en taille.
- **A/B testing de stratégies** en parallèle sur périodes identiques.
- **Tableau de bord live** (performance, risque, stabilité des features, latence exécution).
- **Post-trade analytics** pour identifier les patterns de gains/pertes et prioriser les itérations.

### KPIs cibles à suivre (et réviser mensuellement)

- **Performance** : CAGR, rendement net, ratio gain/perte, hit rate.
- **Risque** : max drawdown, volatilité, VaR/ES, temps de récupération après drawdown.
- **Qualité d'exécution** : slippage moyen, taux d'ordres non exécutés, coût total de transaction.
- **Robustesse** : stabilité des résultats par marché/période, sensibilité aux paramètres, drift score.

### Priorités techniques concrètes pour ce dépôt

- Étendre `signal_engine.py` pour supporter plusieurs modèles et la pondération dynamique.
- Enrichir `AITradingToolsStrategy.py` avec un module de risk management avancé.
- Ajouter un dossier `research/` (notebooks + scripts) pour les expériences reproductibles.
- Ajouter des tests unitaires et des tests de backtest de non-régression.
- Ajouter une configuration centralisée (`YAML`) pour séparer code, paramètres et environnement.
