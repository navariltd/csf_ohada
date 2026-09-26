# CSF OHADA

[![en](https://img.shields.io/badge/lang-en-red.svg)](./README.en.md)

ERPNext personnalise et adapte ses fonctionnalités pour les entités de l’espace comptable OHADA (Organisation pour l’Harmonisation en Afrique du Droit des Affaires). Cette implémentation fournit le plan comptable du SYSCOHADA (Système Comptable OHADA) et enrichit les rapports standards fournis par ERPNext en y ajoutant les états financiers de l’OHADA.

## Etats membres de l’OHADA

OHADA compte 17 États membres parmi lesquels :

| Pays                             | Code |
| -------------------------------- | ---- |
| Benin                            | BJ   |
| Burkina Faso                     | BF   |
| Cameroon                         | CM   |
| Central African Republic         | CF   |
| Chad                             | TD   |
| Comoros                          | KM   |
| Côte d'Ivoire                    | CI   |
| Democratic Republic of the Congo | CD   |
| Equatorial Guinea                | GQ   |
| Gabon                            | GA   |
| Guinea                           | GN   |
| Guinea-Bissau                    | GW   |
| Mali                             | ML   |
| Niger                            | NE   |
| Republic of the Congo            | CG   |
| Senegal                          | SN   |
| Togo                             | TG   |

## Plan comptable

La configuration du plan comptable des entités des Etats membres susmentionnés est celui du SYSCOHADA, par préférence, en plus des plans standards d’ERPNext.
Les plans suivants sont disponibles :

| Plan                                     | Description                                                                                                                                    |
| ---------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| **Syscohada - Plan Comptable**           | La longueur de base des comptes de 1 à 4 chiffres dans la nomenclature officielle du SYSCOHADA (par exemple 1011-Capital souscrit, non appelé) |
| **Syscohada - Plan Comptable avec code** | Le même plan avec des comptes de 6 chiffres pour les besoins de comptabilité analytique ou auxiliaire des entités.                             |

Les plans ERPNext **Standard** et **Standard avec Numéros** restent disponibles. Les modèles régionaux pour les pays hors de l’espace OHADA sont également inclus. La configuration trouve toujours ce plan lorsque cette application est installée.

## Rapports

### Rapports optimisés par le modèle de rapport financier

**Financial Report Template Enhanced** est un générateur de modèles permettant de définir n'importe quelle présentation de rapport financier, sans se limiter à un ensemble fixe d'états.

Les rapports courants configurés en utilisant cette application comprennent :

| Rapport                           | Description                                                                                                                                              |
| --------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Compte De Résultat**            | Il récapitule les produits et les charges qui font apparaitre les résultats intermédiaires et, in fine, le bénéfice net ou la perte nette de l’exercice. |
| **Bilan**                         | Il décrit les éléments d’actif, les éléments du passif et les capitaux propres distinctement.                                                            |
| **Tableau de Flux de Trésorerie** | Il retrace les mouvements d’entrée et de sortie de liquidités de la période.                                                                             |

Vous pouvez adapter ces modèles ou définir d’autres instructions personnalisées. Les modèles sont configurés une fois et réutilisés. Il n’est pas nécessaire de reconstruire des rapports dans Excel à chaque période.

## Etats Financiers avancés

Le modèle de rapport financier amélioré s'appuie sur le modèle de rapport financier d'ERPNext. Il s'agit d'un plan flexible pour tout état financier que vous devez produire en fonction du **Profit and Loss Statement**, du **Balance Sheet**, des **Cash Flow** ou **Custom Financial Statement**.

**Objectifs**

- **Colonnes de valeur configurables** - définir des colonnes de valeurs nommées (par exemple, Valeur brute, Valeur nette, Amortissement) qui s’étendent sur chaque période de rapport. Laissez les colonnes de valeurs vides pour conserver le comportement de style ERPNext avec une seule colonne de valeur par période.
- **Règles par colonne** - définir le type de solde, les filtres de compte ou les formules pour des colonnes de valeurs individuelles sans dupliquer les lignes.
- **Présentation professionnelle** - titres en gras, indentation, couleur, masquer-zéro, filtrage débit/crédit et prise en charge des comptes.

## Autres rapports

| Etats financiers                        | Provenance                   | Description                                                                                                                                    |
| --------------------------------------- | ---------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| **Registre des immobilisations avancé** | Registre des immobilisations | Montants des réévaluations, numéros du plan comptable (lorsqu'ils sont regroupés par catégorie d'actifs) et taux d'amortissement par catégorie |

## Documentation

Des guides de configuration étape par étape, la configuration des modèles, le référentiel des formules et les règles de validation sont disponibles dans la documentation complète:

**[docs.navari.co.ke/ohada-fr](https://docs.navari.co.ke/ohada-fr)**

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
