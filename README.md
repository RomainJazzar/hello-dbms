# Hello DBMS+

Repository for the **Hello DBMS+** assignment:

- ✅ **Veille scientifique** (A → J) with metaphors + diagrams (Mermaid) + lexique
- ✅ **SQL Jobs 1 → 9** (one script per job in `/sql`)
- ✅ **Big Job**: Flask Carbon Footprint Calculator (**MySQL + Flask + HTML/CSS**)
- ✅ **Slides** in `/presentation`

---

## Quick start (Windows / MySQL)

### 1) Setup Python environment

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
2) Initialize MySQL databases + tables + imports
python scripts/init_mysql.py
3) Run the Flask app
python app/app.py
Open: http://127.0.0.1:5000

4) Run SQL jobs
Open each file in /sql/jobX.sql and execute in MySQL Workbench (or your SQL client).

Data sources
data/countries of the world.csv (countries + regions + indicators)

data/carbon-footprint-data.csv (energy mix by country)

External references used in the veille:

Statista – data volume (2010 → 2025 forecast): https://www.statista.com/statistics/871513/worldwide-data-created/

CO₂ absorbed per tree (order of magnitude): https://ecotree.green/combien-de-co2-absorbe-un-arbre

📚 Veille scientifique (A → J)
A) Qu’est-ce qu’une donnée ? Sous quelle forme ?
Définition simple : une donnée = un fait brut (chiffre, texte, signal) qui n’a pas de sens complet tant qu’on ne l’interprète pas.

Formes possibles :

Structurée : tables (CSV), base SQL (lignes/colonnes)

Semi-structurée : JSON, XML

Non structurée : texte libre, images, audio, vidéo

Temps réel / capteurs : logs, IoT, séries temporelles

Métaphore :

Données = ingrédients (farine, œufs)

Information = recette appliquée (gâteau)

Connaissance = savoir quand/pourquoi faire ce gâteau (anniversaire)

B) Critères de qualité des données
Exactitude : conforme à la réalité

Complétude : pas de champs clés manquants

Cohérence : pas de contradictions (âge négatif)

Unicité : pas de doublons indésirables

Actualité : données à jour

Validité : format respecté (date, email, etc.)

Traçabilité : source + date + méthode connues

Métaphore : ton GPS : si la carte est vieille ou fausse, tu peux avoir le meilleur moteur… tu vas te perdre.

C) Data Lake vs Data Warehouse vs Lakehouse (+ schéma)
Data Lake : stocke brut, multi-formats, “schema-on-read”

Data Warehouse : stocke propre, modélisé, BI/Reporting, “schema-on-write”

Lakehouse : hybride (lake + gouvernance + performance)

flowchart LR
  S[Sources: apps, IoT, fichiers, API] --> L[Data Lake (raw)]
  S --> W[Data Warehouse (curated)]
  L --> H[Lakehouse (raw + gouvernance)]
  W --> BI[BI / Reporting]
  H --> BI
  H --> ML[ML / Data Science]
Métaphore :

Lake = entrepôt brut

Warehouse = supermarché rangé

Lakehouse = entrepôt rangé + règles (contrôle, qualité)

D) SGBD / DBMS : définition + exemples
Un SGBD (DBMS) est le logiciel qui gère une base de données : stockage, requêtes, sécurité, transactions, utilisateurs.

SQL : MySQL, PostgreSQL, SQL Server

NoSQL : MongoDB, Redis, Neo4j

Métaphore : le bibliothécaire : tu ne cherches pas toi-même dans toutes les étagères, tu demandes au bibliothécaire.

E) Base relationnelle vs non relationnelle
Aspect	SQL (relationnel)	NoSQL (non relationnel)
Modèle	tables + relations	documents / key-value / graph
Schéma	rigide	flexible
Points forts	intégrité, joins, ACID	scalabilité, flexibilité
Exemples	MySQL, PostgreSQL	MongoDB, Cassandra
F) Clé primaire / clé étrangère
Clé primaire (PK) : identifiant unique d’une ligne (ex: country_id)

Clé étrangère (FK) : référence vers la PK d’une autre table (ex: department_id)

Métaphore :

PK = numéro de carte d’identité

FK = “je pointe vers la carte d’identité de quelqu’un d’autre”

G) Propriétés ACID
Atomicité : tout ou rien (si une étape échoue, on annule tout)

Cohérence : la base reste valide (contraintes respectées)

Isolation : transactions simultanées ne se perturbent pas

Durabilité : une fois validé, c’est sauvegardé (même après crash)

H) Merise et UML : utilité + mini schémas
H1) Merise (MCD / MLD / MPD)
Merise est une méthode (très utilisée en France) pour concevoir une base.

MCD (conceptuel) : entités + relations (sans détails techniques SQL).

MLD/MPD : traduction vers le relationnel puis vers le SQL.

✅ Mini schéma Merise : MCD (SomeCompany)
Exemple basé sur Job 8 (Employees / Departments / Projects).

erDiagram
  DEPARTMENT ||--o{ EMPLOYEE : "emploie"
  DEPARTMENT ||--o{ PROJECT : "porte"

  DEPARTMENT {
    int department_id
    string department_name
    int department_head
    string location
  }

  EMPLOYEE {
    int employee_id
    string first_name
    string last_name
    date birthdate
    string position
    int department_id
  }

  PROJECT {
    int project_id
    string project_name
    date start_date
    date end_date
    int department_id
  }
Lecture simple :

1 département emploie plusieurs employés

1 département porte plusieurs projets

Métaphore :

Département = une “équipe”

Employé = un “membre”

Projet = une “mission” gérée par l’équipe

H2) UML (modélisation applicative)
UML sert à modéliser un système logiciel (classes, interactions, scénarios).

✅ UML Class Diagram (simple)
classDiagram
  class Department {
    +int department_id
    +string department_name
    +string location
  }
  class Employee {
    +int employee_id
    +string first_name
    +string last_name
    +string position
  }
  class Project {
    +int project_id
    +string project_name
  }

  Department "1" --> "0..*" Employee : employs
  Department "1" --> "0..*" Project : manages
✅ UML Sequence Diagram (Big Job Flask)
sequenceDiagram
  participant U as Utilisateur
  participant B as Navigateur
  participant F as Flask App
  participant DB as MySQL (carbonfootprint)

  U->>B: Choisit Pays/Continent + kW
  B->>F: POST /
  F->>DB: SELECT mix énergétique
  DB-->>F: % Coal/Gas/Oil/Hydro/Renewable/Nuclear
  F->>F: Calcule intensité + annuel + arbres
  F-->>B: HTML rendu (table + KPI)
  B-->>U: Affichage des résultats
I) SQL : définition + commandes + jointures
SQL = langage pour interroger / modifier une base.

DML : SELECT, INSERT, UPDATE, DELETE

DDL : CREATE, ALTER, DROP

DCL : GRANT, REVOKE

TCL : COMMIT, ROLLBACK

Jointures :

INNER JOIN : seulement les correspondances

LEFT JOIN : tout de la table gauche + matches

RIGHT JOIN : tout de la table droite + matches

FULL OUTER JOIN : MySQL ne le supporte pas directement → on le simule via LEFT JOIN ... UNION ... RIGHT JOIN.

J) Expliquer simplement (public non initié)
Règle appliquée partout :

à quoi ça sert

comment ça marche (en 1 phrase)

métaphore du quotidien

🌱 Big Job — Calculateur d’Empreinte Carbone (Flask)
Objectif
Calculer l’empreinte carbone de la production électrique en fonction :

du mix énergétique (%)

des facteurs d’émissions IPCC 2014 (médianes)

d’une puissance consommée kW (entrée utilisateur)

Formules (résumé)
Contribution(source) = (%/100) × facteur(gCO₂/kWh)

Intensité totale = somme des contributions (gCO₂/kWh)

Conversion : g → kg : /1000

Émissions annuelles = (kgCO₂/kWh) × (kW × 24 × 365)

Arbres = kgCO₂/an ÷ 25

Observations (Step 3 – demandé par l’énoncé)
Exemples d’observations issues des résultats :

Plus la part de charbon est grande, plus l’intensité carbone explose (facteur médian très élevé).

Hydro et nucléaire donnent des contributions faibles (facteurs médians bas).

Une région “Unknown” peut apparaître si certains pays ne se mappent pas proprement à un continent (données manquantes / noms non alignés).

Les résultats varient fortement selon le mix : deux pays avec la même consommation (kW) peuvent avoir des émissions annuelles très différentes.

Le gaz est souvent un “intermédiaire” : moins que charbon, mais bien supérieur au nucléaire/hydro.

Lexique (version simple)
Table : feuille Excel (lignes/colonnes)

Index : sommaire qui accélère la recherche

ETL : Extract / Transform / Load (collecter, nettoyer, charger)

Transaction : ensemble d’actions “tout ou rien”

Schéma : structure de la base (tables + relations)

Sources / Base de connaissances (énoncé)
Statista – Volume of data created worldwide (2010–2025)

SQL.sh – Apprendre le SQL

Practice SQL

SQL Cheatsheet

Article NoSQL – bases non relationnelles

MySQL Basics (tutorial)

7 Database Paradigms

EcoTree – CO₂ absorbé par un arbre (~25 kg/an)
```
