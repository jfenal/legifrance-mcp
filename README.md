# legifrance-mcp

Serveur MCP [Model Context Protocol](https://modelcontextprotocol.io/introduction) expérimental permettant d'interroger les bases juridiques françaises via l'API Legifrance dans des LLMs compatibles comme Claude.

## Description

Ce projet implémente un serveur MCP qui permet d'accéder aux ressources juridiques françaises (textes légaux, codes, jurisprudence) directement depuis un Large Language Model. Il facilite les recherches juridiques en rendant les données de Legifrance accessibles via des outils interactifs.

Il fait suite à la création du package [pylegifrance](https://github.com/pylegifrance/pylegifrance). 

### Origine

Ce dépôt est issu d'un fork du projet [pylegifrance/mcp-server-legifrance](https://github.com/pylegifrance/mcp-server-legifrance),
créé par Raphaël d'Assignies ([dassignies.law](https://dassignies.law)), qui
authentifiait via son proxy tiers. Le fork a depuis divergé significativement
(authentification directe auprès de PISTE, dépendance sur
[un fork de pylegifrance](https://github.com/jfenal/pylegifrance), nouveaux
outils Judilibre et `get_text_history`, recherche par proximité, etc.) et a
été détaché de son dépôt d'origine pour devenir ce projet autonome.

### Qu'est-ce que le MCP ?

Le Model Context Protocol (MCP) est un protocole standardisé développé par Anthropic qui permet aux modèles de langage comme Claude d'interagir de manière structurée avec des outils et services externes. Il s'agit d'une avancée intéressante dans l'interopérabilité des LLMs car il établit un cadre commun pour l'échange de données et l'exécution de fonctions entre les modèles et les API tierces. Jusqu'à maintenant, il fallait développer, pour chaque service, des appels de fonctions spécifiques. 

### L'interopérabilité via MCP

L'importance du MCP réside dans sa capacité à créer une interface standardisée entre les LLMs et les systèmes externes. Cette standardisation présente plusieurs avantages :

1. **Architecture modulaire** : Les développeurs peuvent créer des outils spécialisés qui sont facilement intégrables à différents LLMs compatibles avec le protocole.

2. **Sécurité accrue** : Le MCP limite l'accès des modèles aux seules fonctionnalités explicitement définies, réduisant ainsi les risques de sécurité.

3. **Maintenance simplifiée** : Les mises à jour des outils externes peuvent être faites indépendamment du modèle, facilitant l'évolution des systèmes.

4. **Extension des capacités** : Les LLMs peuvent accéder à des données en temps réel et exécuter des opérations complexes qu'ils ne pourraient pas réaliser seuls.

### legifrance-mcp ?

L’idée est d’exploiter la puissance des modèles de langage comme Claude pour effectuer des traitements sur des contenus juridiques officiels via Légifrance, et à terme, d’autres bases de données publiques comme le RNE, le BODACC, etc. Les premiers résultats sont très prometteurs et permettent de pallier certaines limites de la recherche statistique classique proposée par Légifrance. Le service est en amélioration continue, mais vous pouvez déjà consulter quelques exemples de recherches ci-dessous.

Le serveur prend en charge les fonctionnalités suivantes:
- Recherche dans les textes légaux (lois, ordonnances, décrets, arrêtés)
- Consultation des articles de codes juridiques français
- Recherche dans la jurisprudence judiciaire

Les autres fonds Legifrance seront bientôt implémentés. 

Ce projet authentifie directement auprès de PISTE (le portail officiel DILA)
via la bibliothèque [pylegifrance](https://github.com/pylegifrance/pylegifrance),
plutôt que via un proxy tiers.

Il utilise actuellement [le fork jfenal/pylegifrance](https://github.com/jfenal/pylegifrance/tree/direct-piste-integration),
qui ajoute le support direct de PISTE et de Judilibre et corrige plusieurs
bugs (validation des identifiants CID/NOR, gestion de l'expiration des
jetons, recherche par proximité, etc. — voir [la pull request correspondante](https://github.com/pylegifrance/pylegifrance/pull/79))
tant que ces correctifs ne sont pas fusionnés dans le dépôt officiel.

## Prérequis

- Python 3.12+
- Un compte [PISTE](https://piste.gouv.fr/registration) avec une application
  souscrite aux API **Légifrance** et **Judilibre** (CGU acceptées pour les
  deux, en sandbox comme en production)
- Un modèle compatible avec le protocole MCP (comme Claude desktop)

## Installation

1. Clonez ce dépôt et [le fork jfenal/pylegifrance](https://github.com/jfenal/pylegifrance)
   (branche `direct-piste-integration`) en répertoire frère — ce projet
   dépend de pylegifrance via un chemin local (voir `pyproject.toml`), et
   nécessite les correctifs de ce fork tant qu'ils ne sont pas fusionnés
   dans le dépôt officiel ([pylegifrance/pylegifrance#79](https://github.com/pylegifrance/pylegifrance/pull/79)):
```bash
git clone https://github.com/jfenal/legifrance-mcp.git
git clone -b direct-piste-integration https://github.com/jfenal/pylegifrance.git
```

2. Installez les dépendances:
```bash
cd legifrance-mcp
uv sync
```

3. Créez un fichier `.env` à la racine du projet avec vos identifiants PISTE:
```
LEGIFRANCE_CLIENT_ID=votre_client_id
LEGIFRANCE_CLIENT_SECRET=votre_client_secret
PISTE_ENV=sandbox  # ou "production" ; "sandbox" par défaut si omis
JUDILIBRE_KEY_ID=votre_key_id  # requis pour le tool rechercher_jurisprudence_judilibre
```

Ces identifiants s'obtiennent sur [piste.gouv.fr](https://piste.gouv.fr/registration) —
voir la FAQ officielle de l'[API Légifrance](https://www.legifrance.gouv.fr/contenu/pied-de-page/foire-aux-questions-api)
pour la procédure complète (création de compte, consentement aux CGU par API,
puis souscription de l'application).

## Utilisation


### Intégration avec Claude Desktop

1. Ouvrez la configuration de Claude Desktop (Paramètres > Développeur >
   Modifier la configuration, un fichier `.json`) et ajoutez cette entrée,
   en remplaçant `<CHEMIN_VERS_VOTRE_REP>` par le chemin absolu où vous avez
   cloné ce dépôt. `uv run` se charge de l'environnement virtuel — inutile
   de pointer vers un interpréteur Python spécifique.

```json
{
  "mcpServers": {
    "legifrance": {
      "command": "uv",
      "args": [
        "run",
        "--directory", "<CHEMIN_VERS_VOTRE_REP>/legifrance-mcp",
        "python", "src/server.py"
      ]
    }
  }
}
```

2. Redémarrez Claude Desktop. L'icône d'outils (🔨) dans la zone de saisie
   doit lister les cinq outils ci-dessous :
![Icônes d'outils dans Claude Desktop](image.png)

3. Essayez par exemple : *« Recherche les conditions de validité du PACS
   dans le Code civil »*. Claude appelle `rechercher_code` et répond en
   citant l'article trouvé, avec son URL Légifrance :

```
> Recherche les conditions de validité du PACS dans le Code civil

[appel de l'outil rechercher_code: search="pacte civil de solidarité", code_name="Code civil"]

## Code civil — art. 515-1
**État**: VIGUEUR
**URL**: https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000006428463

Un pacte civil de solidarité est un contrat conclu par deux personnes
physiques majeures, de sexe différent ou de même sexe, pour organiser
leur vie commune.
[...]
```

## Outils disponibles

Ces cinq outils appellent directement l'API Légifrance (`fonds.code`,
`fonds.loda`, `fonds.juri`) ou l'API Judilibre de
[pylegifrance (fork jfenal)](https://github.com/jfenal/pylegifrance/tree/direct-piste-integration) —
voir sa documentation technique pour le détail des paramètres sous-jacents.

### 1. rechercher_dans_texte_legal

Recherche des articles dans les textes légaux (lois, ordonnances, décrets, arrêtés).

**Paramètres:**
- **text_id**: Identifiant du texte (ex: "78-17" pour la loi informatique et libertés)
- **search**: Mots-clés ou numéro d'article
- **champ**: Zone de recherche ("ALL", "TITLE", "TABLE", "NUM_ARTICLE", "ARTICLE")
- **type_recherche**: Mode de recherche ("TOUS_LES_MOTS_DANS_UN_CHAMP", "EXPRESSION_EXACTE", "AU_MOINS_UN_MOT")
- **page_size**: Nombre de résultats (max 100)

**Exemple:**
Pour rechercher l'article 7 de la loi 78-17:
```
{
  "text_id": "78-17",
  "search": "7",
  "champ": "NUM_ARTICLE"
}
```

### 2. rechercher_code

Recherche des articles dans les codes juridiques français.

Par ex. *"Rédige-moi une synthèse sur le régime juridique du PACS"* — voir la
démonstration dans la section [Intégration avec Claude Desktop](#intégration-avec-claude-desktop)
ci-dessus pour un exemple complet d'appel et de réponse.

**Paramètres:**
- **search**: Termes de recherche
- **code_name**: Nom du code (ex: "Code civil", "Code du travail")
- **champ**: Zone de recherche
- **sort**: Tri des résultats
- **type_recherche**: Mode de recherche
- **page_size**: Nombre de résultats
- **fetch_all**: Si tous les résultats doivent être récupérés

**Exemple:**
Pour rechercher des informations sur le PACS dans le Code civil, le modèle de langage va envoyer la requête suivante : 
```
{
  "search": "pacte civil de solidarité",
  "code_name": "Code civil"
}
```

### 3. rechercher_jurisprudence_judiciaire

Recherche dans la base de jurisprudence judiciaire. On peut utiliser la
puissance des modèles de langage pour faire des recherches de
jurisprudence directement dans Légifrance, par exemple :

- *« Trouve les dernières décisions sur la rupture brutale des relations
  commerciales établies et fais-moi un tableau de synthèse »* — Claude
  appelle `rechercher_jurisprudence_judiciaire` avec
  `search="rupture brutale des relations commerciales établies"`,
  `sort="DATE_DESC"`, puis construit le tableau à partir des décisions
  renvoyées (chacune avec son URL Légifrance).
- Analyse pas à pas d'une décision connue (numéro de pourvoi) : Claude la
  retrouve, en extrait la fiche d'arrêt et les articles visés, puis peut
  rechercher ces mêmes articles via `rechercher_code`/`rechercher_dans_texte_legal`
  et des décisions comparables via un second appel à cet outil.

**Paramètres:**
- **search**: Termes ou numéro d'affaire
- **publication_bulletin**: Si publiée au bulletin ["T"] ou non ["F"]
- **sort**: Tri des résultats
- **champ**: Zone de recherche
- **type_recherche**: Mode de recherche
- **page_size**: Nombre de résultats
- **fetch_all**: Si tous les résultats doivent être récupérés
- **juri_keys**: Champs de réponse à extraire 
- **juridiction_judiciaire**: Liste des juridictions

### 4. rechercher_jurisprudence_judilibre

Recherche de décisions de justice via l'API Judilibre (Cour de cassation et
juridictions du fond), en complément de `rechercher_jurisprudence_judiciaire`.
Nécessite la variable d'environnement `JUDILIBRE_KEY_ID`.

**Paramètres:**
- **search**: Termes de recherche
- **jurisdiction**: Juridiction(s) à filtrer
- **chamber**: Chambre(s) à filtrer
- **date_start** / **date_end**: Plage de dates (YYYY-MM-DD)
- **page_size**: Nombre de résultats (max 100)

**Exemple:**
```
{
  "search": "licenciement sans cause réelle et sérieuse"
}
```

### 5. get_text_history

Retourne l'historique des modifications (créations, modifications,
abrogations d'articles) apportées par un texte légal.

**Paramètres:**
- **text_id**: Identifiant du texte (ex: "78-17")

**Exemple:**
```
{
  "text_id": "78-17"
}
```

## Prompts prédéfinis

Le serveur peut inclure des prompts prédéfinis pour faciliter l'utilisation. 
Pour le moment, seul un prompt a été implémenté à titre d'exemple. Il est possible de mettre en place des prompts beaucoup plus 
détaillés notamment pour effectuer des opérations de type *deepsearch* ou des extractions dans plusieurs documents ... 

### agent_juridique_expert

Crée un agent juridique expert qui:
- Cite systématiquement ses sources
- Utilise les outils pertinents pour rechercher des informations
- Fournit des analyses étape par étape
- Inclut les liens officiels vers les textes juridiques

**Usage:**
```python
# Exemple d'utilisation du prompt prédéfini
response = client.messages.create(
    model="claude-3-opus-20240229",
    max_tokens=1000,
    tools=tools,
    messages=[
        {
            "role": "user", 
            "content": [
                {
                    "type": "tool_use",
                    "id": "prompt_use_1",
                    "name": "legifrance.get_prompt",
                    "input": {
                        "prompt_name": "agent_juridique_expert",
                        "inputs": {
                            "question": "Quelles sont les conditions de validité d'un contrat de mariage?"
                        }
                    }
                }
            ]
        }
    ]
)
```

## Limitations

- Les requêtes sont limitées à 5 par seconde par défaut (`rate_limit` dans
  `src/server.py`) — PISTE applique son propre quota par application, non
  publié publiquement; consultez le vôtre sur piste.gouv.fr (Applications >
  Actions > Consulter les quotas) et ajustez cette valeur en conséquence.
- Une connexion internet est nécessaire pour accéder aux bases juridiques
- Le serveur ne met pas en cache les résultats, chaque requête interroge l'API

## Contribution

Les contributions sont les bienvenues! Veuillez ouvrir une issue ou soumettre une pull request pour toute amélioration ou correction.

## Licence

[MIT License](LICENSE)
