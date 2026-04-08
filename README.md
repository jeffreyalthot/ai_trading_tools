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

## Roadmap d'amélioration (objectif : dépasser les standards actuels du trading algorithmique)

> 🎯 **Ambition assumée** : construire un système qui vise le **top décile des performances ajustées du risque** sur plusieurs régimes de marché, avec une exécution institutionnelle, une robustesse scientifique et une itération ultra-rapide.
>
> ⚠️ **Discipline non négociable** : aucune promesse de profit garanti. Toute hausse d'ambition doit s'accompagner d'un contrôle du risque plus strict que la concurrence.

### Phase 1 — Infrastructure de recherche “institution grade” (0-2 mois)

- **Lakehouse de données unifié** : OHLCV, carnet d'ordres L2/L3, funding, options flow, macro, sentiment, on-chain, flux news.
- **Qualité data automatisée** : validation de schéma, détection d'anomalies en streaming, correction des trous, traçabilité complète.
- **Feature store versionné + lineage** : chaque signal est reproductible, auditable et relié à son dataset source.
- **Framework d'évaluation anti-surapprentissage** : walk-forward, nested CV temporelle, tests de robustesse par sous-période.
- **Backtests “proches réel”** : microstructure, latence, slippage non linéaire, impact de marché, capacité (AUM stress tests).

### Phase 2 — IA multi-modèles à avantage adaptatif (2-4 mois)

- **Ensemble hétérogène** : transformers temporels, gradient boosting, modèles de volatilité, classifieurs de régimes.
- **Sorties probabilistes calibrées** : direction, amplitude attendue, horizon optimal, intervalle de confiance.
- **Meta-model de sélection dynamique** : pondération des modèles selon régime, liquidité, volatilité et drift détecté.
- **Détection de rupture de marché** : alertes précoces sur changements structurels + fallback défensif automatique.
- **Learning loop continue** : retraining piloté par drift, validation stricte et rollback rapide en cas de dégradation.

### Phase 3 — Moteur de décision “alpha + exécution” (4-6 mois)

- **Allocation dynamique du risque** : sizing par conviction, corrélation croisée, volatilité conditionnelle et budget VaR.
- **Portefeuille multi-stratégies / multi-actifs** : arbitrage des expositions avec contraintes hiérarchiques.
- **Overlay de risk management avancé** : kill-switch global, limites intraday, stress scénarios, protection anti-krach.
- **Execution intelligence** : routage adaptatif, timing d'entrée/sortie, réduction active du slippage.
- **Filtre d'edge net** : trade uniquement si alpha prévisionnel > coût total + prime d'incertitude.

### Phase 4 — Industrialisation et montée en puissance contrôlée (6-9 mois)

- **MLOps complet** : registry, CI/CD quant, tests de non-régression, déploiement canary, rollback automatique.
- **Shadow / paper / live progressif** : promotion en capital par paliers avec critères quantitatifs objectifs.
- **A/B/n testing continu** : comparaison simultanée de stratégies sur univers identiques.
- **Observabilité temps réel** : performance, risque, drift, latence, qualité d'exécution, incidents.
- **Boucle post-trade priorisée par impact** : analyse causale des gains/pertes et backlog piloté par ROI recherche.

### Phase 5 — Frontière R&D pour “surpasser le marché” (9-18 mois)

- **Research factory** : génération hebdomadaire d'hypothèses, auto-benchmarking, scoring recherche en continu.
- **Simulations massives** : stress tests multi-régimes sur 10k+ scénarios synthétiques et historiques.
- **Optimisation portefeuille globale** : intégration cross-exchange, cross-asset, contraintes de liquidité et capacité.
- **Architecture modulaire “plug-and-win”** : ajout rapide de nouveaux modèles sans réécriture stratégique.
- **Objectif de résilience extrême** : maintien de performance relative même en périodes de volatilité atypique.

### KPIs d'excellence (revue mensuelle + comité trimestriel)

- **Performance** : CAGR net, alpha vs benchmark, ratio gain/perte, espérance par trade.
- **Risque** : max drawdown, temps de récupération, volatilité, VaR/ES, ratio Calmar/Sortino.
- **Exécution** : slippage médian/p95, coût total de transaction, fill rate, latence ordre-à-exécution.
- **Robustesse** : stabilité par actif/régime, sensibilité hyperparamètres, score de drift, taux de rollback.
- **Scalabilité** : capacité nominale (AUM), dégradation de performance sous stress de taille, coût infra par alpha généré.

### Priorités techniques concrètes pour ce dépôt

- Étendre `signal_engine.py` vers un **moteur d'ensemble multi-modèles** avec pondération dynamique par régime.
- Enrichir `AITradingToolsStrategy.py` avec un **risk engine** (limits, kill-switch, sizing avancé, sorties adaptatives).
- Ajouter un dossier `research/` (notebooks + scripts) orienté **expérimentation reproductible** et benchmark.
- Ajouter des tests unitaires + tests de non-régression backtest avec **seuils de performance/risk gates**.
- Ajouter une configuration centralisée (`YAML`) pour séparer code, paramètres, environnements et profils de déploiement.
