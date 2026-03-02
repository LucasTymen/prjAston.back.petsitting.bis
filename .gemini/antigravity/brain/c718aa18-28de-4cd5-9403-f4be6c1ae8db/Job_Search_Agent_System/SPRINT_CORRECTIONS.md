# Sprint collectif — Corrections audit expert_automatisation

> Plan de sprint pour corriger les points identifiés par l'audit (erreurs de calcul matching, hallucinations, bugs). Coordination : chef de projet + expert_automatisation.

---

## Contexte

L'agent **expert_automatisation** a parcouru le projet, les données et l'intelligence métier. Il a identifié des erreurs et risques (voir rapport d'audit dans l'historique des échanges ou résumé ci-dessous). Ce sprint vise à les corriger de façon collective, puis à valider en conditions réelles.

---

## Phase 1 — Corrections (un par un)

Chaque point est corrigé **un par un** lors du sprint collectif.

### Coordination
- **Chef de projet** : répartition des tâches, priorisation, suivi.
- **Expert_automatisation** : assistance technique, vérification cohérence avec logique métier et `base_real.json`, revue des patches.

### Points à corriger (priorité)

| # | Gravité | Point | Fichier(s) | Statut |
|---|---------|-------|------------|--------|
| 1 | Critique | ATV_CHECK fictif — aucune vérification réelle des sorties CV/LM/emails vs base_json | `core/orchestrator.py` | [x] |
| 2 | Critique | Mots-clés composés non matchés (ex. "SEO technique" vs "SEO"/"technique") — faux négatifs | `agents/matching.py` | [x] |
| 3 | Haute | Crash si `niveau_poste` est None | `agents/matching.py` | [x] |
| 4 | Haute | Brouillon Gmail créé avec `email_trouve=None` (EntrepriseScraper stub) | `core/orchestrator.py`, `agents/drafting.py` | [x] |
| 5 | Moyenne | Erreur LLM non gérée proprement → sortie CV/LM dégradée | `agents/generator.py` | [x] |
| 6 | Moyenne | Fallback `bullet_cv_court` fragile (structure dict) | `agents/generator.py` | [x] |

Chaque intervenant corrige son périmètre. L'expert_automatisation assiste pour éviter régressions et incohérences.

---

## Phase 2 — Test en conditions réelles

Une fois toutes les corrections effectuées :

- **Test end-to-end** en conditions réelles (vraies offres, pipeline complet).
- Flux : découverte → scraping → matching → génération CV/LM/emails → brouillon (si applicable).
- Objectif : valider que le système fonctionne sans crash et sans hallucination détectable.

---

## Phase 3 — Surveillance et rapports par agent

Chaque agent, à son niveau :

1. **Surveille le process** pendant et après le test.
2. **Exécute ses tests** (unitaires, d'intégration).
3. **Rédige un rapport** avec :
   - améliorations possibles ;
   - erreurs ou anomalies détectées ;
   - corrections supplémentaires à envisager.

Ces rapports alimentent la prochaine itération et le registre décisions/erreurs.

---

## Rôles RACI (rappel)

- **Expert_automatisation** : assistance technique, audit, prévention erreurs de calcul et hallucinations.
- **Chef de projet** : coordination, répartition des tâches, adaptation RACI et stratégies.
- **Agents intervenants** : exécution des corrections, tests, rapports.

---

## Benchmarks data-driven (Phase 2)

- **Tests :** `tests/test_benchmark_matching.py`, `tests/test_benchmark_atv.py`, `tests/test_benchmark_sprint.py`
- **Données :** `tests/benchmark_data/matching_cases.json`
- **Exécution :** `python -m pytest tests/test_benchmark_*.py tests/test_matching.py tests/test_orchestrator.py -v -o addopts=`
- **Rapports :** `SPRINT_RAPPORTS.md`

---

*Dernière mise à jour : 2026-03-02. Voir `HISTORIQUE.md` et `ARCHITECTURE_AGENTIQUE.md`.*
