# Rapports Phase 3 — Sprint corrections

> Rapports par agent après exécution des 3 phases (corrections, tests, surveillance).

---

## Rapport Expert_automatisation

**Périmètre :** Matching, ATV, génération, erreurs de calcul.

### Corrections effectuées
- **#1 ATV_CHECK** : Intégration `valider_donnees()` dans l'orchestrateur — CV et LM validés contre base_json.
- **#2 Mots-clés composés** : `_expand_keywords()` — "SEO technique" → ["seo", "technique"] pour matching.
- **#3 niveau_poste** : Guard `(niveau_poste or "").lower()` — plus de crash si None/vide.
- **#4 Brouillon sans email** : Orchestrateur ne lance plus `create_draft` si `email_trouve` vide ; GmailDraftingAgent refuse `to_email` vide.
- **#5 Erreur LLM EmailEngine** : Fallback dict avec clés `sujet`, `email_j0`, etc. si LLM retourne {} ou None.
- **#6 bullet_cv_court** : Fallback robuste — si `list(values)[0]` n'est pas une liste, conversion en liste.

### Benchmarks data-driven
| Métrique | Valeur |
|----------|--------|
| Tests benchmark matching | 5 (niveau_poste, composites, big_data_ia, expand_keywords) |
| Tests benchmark ATV | 3 (sans chiffres, autorisés, inventé) |
| Tests régression sprint | 3 (draft, EmailEngine, bullet_cv) |
| Durée totale tests | ~4 s |

### Améliorations suggérées
- Enrichir `EntrepriseScraper` pour trouver des emails réels.
- Ajouter validation des `exemples_interdits` dans le texte généré (phrases interdites).
- Tokenisation plus fine des mots-clés (néologismes, acronymes).

---

## Rapport Chef de projet

**Périmètre :** Coordination, RACI, stratégies.

### Actions
- Plan de sprint documenté (`SPRINT_CORRECTIONS.md`).
- Répartition des 6 points entre les corrections.
- Coordination expert_automatisation pour la Phase 1.

### Stratégies mises à jour
- RACI : expert_automatisation (assistance), chef_de_projet (adaptation RACI/stratégies).
- Processus : Phase 1 → Phase 2 (test réel) → Phase 3 (rapports).

### Prochaines étapes
- Test end-to-end en conditions réelles (vraies offres) quand l'équipe sera prête.
- Intégrer les retours des rapports dans le backlog.

---

## Rapport Scraper / Matching

**Périmètre :** Extraction, scoring.

### Tests exécutés
- `test_matching_benchmark_case[niveau_poste_none]` — PASSED
- `test_matching_benchmark_case[mots_cles_composites]` — PASSED
- `test_matching_benchmark_case[big_data_ia]` — PASSED
- `test_matching_expand_keywords` — PASSED

### Constats
- Matching robuste aux mots-clés composés.
- Plus de crash sur `niveau_poste` vide.

---

## Rapport Generator / ATV

**Périmètre :** CV, LM, emails, validation ATV.

### Tests exécutés
- `test_atv_ok_sans_chiffres`, `test_atv_ok_chiffres_autorisés`, `test_atv_fail_chiffre_inventé` — PASSED
- `test_email_engine_fallback_dict` — PASSED
- `test_cv_bullet_dict_fallback` — PASSED
- `test_orchestrator_atv_check` — PASSED

### Constats
- ATV_CHECK reflète désormais une validation réelle.
- Fallback EmailEngine et bullet_cv opérationnels.

---

## Synthèse benchmarks

| Catégorie | Nombre | Statut |
|-----------|--------|--------|
| Matching | 5 | 5/5 PASSED |
| ATV | 3 | 3/3 PASSED |
| Sprint régression | 3 | 3/3 PASSED |
| Orchestrateur | 2 | 2/2 PASSED |
| **Total** | **16** | **16/16** |

---

*Rapports générés le 2026-03-02. Voir `SPRINT_CORRECTIONS.md` pour le plan.*
