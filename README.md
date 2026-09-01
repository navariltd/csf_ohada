# CSF OHADA

ERPNext personnalise et adapte ses fonctionnalités pour les entités de l’espace comptable OHADA. Cette implémentation enrichit les rapports standards fournis par ERPNext en y ajoutant les états financiers de l’OHADA.

## Etats financiers

### Rapports générés à l'aide du modèle des états financiers avancés

**Le modèle des États financiers avancés** (Financial Report Template Enhanced) est un générateur de modèles permettant de personnaliser la mise en page de n'importe quel rapport financier, sans aucune restriction. Une fois configuré, visualisez-le depuis **États financiers avancés** (Financial Statement Enhanced).

Voici quelques exemples de rapports configurés:

| Etats financiers                  | Description                                                                                                                                              |
| --------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Compte de résultat**            | Il récapitule les produits et les charges qui font apparaitre les résultats intermédiaires et, in fine, le bénéfice net ou la perte nette de l’exercice. |
| **Bilan**                         | Il décrit les éléments d’actif, les éléments du passif et les capitaux propres distinctement.                                                            |
| **Tableau de Flux de Trésorerie** | Il retrace les mouvements d’entrée et de sortie de liquidités de la période.                                                                             |

Vous pouvez également définir des instructions personnalisées au-delà de ces exemples. Les modèles sont configurés une fois et réutilisés, pas besoin de reconstruire les rapports dans Excel à chaque période.

## Modèle des Etats financiers avancés

Ce modèle d'États financiers avancés s'appuie sur la structure de base d'ERPNext. Sa flexibilité permet de générer n'importe quel rapport financier directement depuis le module **Financial Statement Enhanced**.

**Fonctionnalités**

- **Colonnes de valeur configurables** - nommez des colonnes de valeur (par exemple Valeur brute, Valeur nette, Amortissement) qui s'étendent sur chaque période comptable. Laissez les colonnes de valeur vides pour conserver le style d’ERPNext avec une seule colonne de valeur par période.
- **Règles par colonne** - reclassez la nature du solde par type de compte, appliquez des filtres de compte ou les formules pour des colonnes de valeur individuelles sans dupliquer les lignes.
- **Mise en page professionnelle** - en-têtes en gras, indentation, couleurs, masquage des valeurs nulles, filtrage par côté débit/crédit et prise en charge des graphiques..
- **Point d’exécution unique** - a génération des rapports est centralisée au sein du module Financial Statement Enhanced, d'où sont exécutés tous les modèles améliorés.

Standard ERPNext reports (Balance Sheet, Profit and Loss Statement, Cash Flow, Custom Financial Statement) continue to use ERPNext's original Financial Report Template and are not affected by Enhanced templates.

## Autres rapports

| Etats financiers                        | Provenance                   | Description                                                                                                                                    |
| --------------------------------------- | ---------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| **Registre des immobilisations avancé** | Registre des immobilisations | Montants des réévaluations, numéros du plan comptable (lorsqu'ils sont regroupés par catégorie d'actifs) et taux d'amortissement par catégorie |

Générer depuis **Accounting → Fixed Asset Register Enhanced** avancé (également disponible dans l’espace de travail **OHADA**)

## Documentation

Des guides de configuration étape par étape, la configuration des modèles, le référentiel des formules et les règles de validation sont disponibles dans la documentation complète:

**[docs.navari.co.ke](https://docs.navari.co.ke)**

## Installation

Installez cette application à l'aide de l'interface de ligne de commande (CLI) de [bench](https://github.com/frappe/bench):

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app $URL_OF_THIS_REPO --branch develop
bench install-app csf_ohada
```

## Contributing

Cette application utilise `pre-commit` pour le formatage et la validation du code. Veuillez installer [install pre-commit](https://pre-commit.com/#installation) et l'activer pour ce dépôt:

```bash
cd apps/csf_ohada
pre-commit install
```

Pre-commit est configuré pour utiliser les outils suivants:

- ruff
- eslint
- prettier
- pyupgrade

## CI

Cette application utilise GitHub Actions pour l'intégration continue (CI). Les workflows suivants sont configurés:

- **CI:** installe le projet et exécute les tests unitaires lors de chaque push vers la branche `develop`.
- **Linters:** exécute [Frappe Semgrep Rules](https://github.com/frappe/semgrep-rules) et [pip-audit](https://pypi.org/project/pip-audit/) lors de chaque pull request.

## License

AGPL-3.0
