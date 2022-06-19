# GD4H MVP

Minimum viable product pour la plateforme du catalogue Green Data For Health

## Fonctionnalités

### Site Web publique:
- Affichage du catalogue (jeux de données, organismes, référentiels et normes, commentaires)
- Moteur de recherche plein texte pour les jeux de données multilingue: module d'indexation avec ElasticSearch
- Filtres contextuels pour les jeux de donnée et les organismes
- Site web multilingue(Français/Anglais): module de traduction automatique Français Anglais des métadonnées et des données du catalogue

### Site web accès producteur:
- Gestion des données catalogue: ajout (API + formulaire) édition des données du catalogue (API)
- Fonctionnalités collaboratives: commentaires sur la plateforme, sur un jeu de données, sur une section du jeu de données et sur un champs de métadonnées: `fonctionnalités désactivées prévue pour V2`
 
### Site web accès administrateur:
> Pas d'interface web pour le moment mais paramétrage via des fichiers CSV et des points API dédiés
- Paramétrages des fonctionnalités  de la plateforme:
  - affichage
  - validation des données
  - moteur de recherche et filtres
  - traduction  
  - export
Cf [CONFIG.md](CONFIG.md)

- Gestion administrative des données du  catalogue: 
  - ajout édition supression des données du catalogue via API: unitaire (via API) et multiples (import )
  - export des données du catalogue  
Cf []()
- Gestion administrative des métadonnées du catalogue:
  - modelisation: ajout édition suppression des métadonnées descriptives du modèle: jeux de données, organismes, ...
  - réferentiels: ajout édition suppression des métadonnées controlées par des référentiels
Cf []()

## Architecture

Le projet est composé de plusieurs briques fonctionnelles et ordonné de la manière suivante:

#### `generateur`

  - initialisation d'une base de données (MongoDB)
  - initialisation du moteur d'indexation et de recherche (Elastic Search)
  - création des modèles de données et de leur validation
  - traduction automatique des données et métadonnées
  - import des données d'initialisation (cf. [data](####data))

#### `back` 
  
  - Une API (FastAPI) qui gère les interaction avec la base de données et le moteur de recherche
  > elle est créée adhoc par le générateur, celui ci étant désormais stocké dans le dossier back avec les données d'initialisation 

#### `front`
  

#### `init_data`

Les données qui permettent la création et l'initialisation de la base de données, l'indexation mais aussi toutes les règles d'affichage de filtrage et de requetage.

init_data est le dossier qui contient toutes les données et paramétrages de départ: 
elles sont toutes au format csv puis insérée dans la base de données à l'initialisation
une fois insérées le système permet l'administration  via l'API
##### données de paramétrages

- rules.csv
- references/

Les données méta décrivent l'ensemble des champs qui définissent un modèle, toutes les règles qui s'attachent aux champs définitoires d'un modèle. C'est le point d'entrée du création de la plateforme.
En effet le fichier `rules.csv` liste tous les champs de données pour tous les modèles présents dans la BDD et dicte la manière d':

- insérer/modifier/supprimer les données dans la base
- indexer les données dans ElasticSearch
- valider les données
- afficher les données 
- afficher les filtres

##### données descriptives `/references/`

Ces données correspondent aux nomenclatures à respecter pour ajouter une valeur à un champ descriptif d'un jeu de données ou d'une organisation.
Pour décrire un jeu de données on utilse plusieurs champs tel que le nom l'url et le sujet, les règles de ce que peut contenir le champ "sujet" est défini grace aux références qui détaille les valeurs acceptées pour le champ sujet.

  - une liste de tous les champs dans les valeurs sont controlées appelée `références`:

    > Exemple: un dataset possède un champ descriptif "Nature et Usage", celui ci accepte seulement les valeurs :Biodiversité, Indicateurs géographiques et socio-démographiques, Agents Physiques, Pesticides
    
Le fichier csv puis la table `references` liste toutes les champs dont les valeurs sont controlées par un référentiel.

table `references`
  | field_slug   | table_name|field_label_fr  | field_label_en|
  |------------|-----------|----------------|---------------|
  |nature      | ref_nature| Nature et Usage| Use and Nature|



  - pour chaque référence controlée on trouve la liste des valeurs acceptées en anglais et en francais aggrémenté d'une uri si référentiel sémantique appelée `ref_<nom_du_champ>`:

    > Exemple : Le champ Nature et Usage
    
stocké dans la table `ref_nature`


|field_label_fr  | field_label_en| uri                 |
|----------------|---------------|---------------------|
|Biodiversité    | Biodiversity  |                     |
|Agents Physiques| Physical Agents  |                     |
|Indicateurs géographiques et socio-démographiques|Géographical and socio-demographical indicators||
| Pesticides     | Pesticides ||


##### données du catalogue:
  
  - fichier issu d'un premier recensement des données du catalogue GD4H (datasets) en Français `/datasets_fr.csv` 
    > correspond à la table `datasets` accessible dans l'API via le endpoint `/datasets`
  - fichier issu d'un premier recensement des données du catalogue GD4H (organizations) en Français `/organizations_fr.csv` 
    > correspond à la table  `organizations` accessible dans l'API via le endpoint `/organizations`
  

## Installation

La procédure d'installation des sources a été supprimée pour laisser place à une installation via docker. Une archive de la procédure d'installation des sources est disponible (ici)[./OLD_INSTALL.md]

Pour installer via docker se référer à la (documentation d'installation docker)[INSTALL.md]

## Deploiement

Pour déployer le système se référer à la (documentation de déploiement docker)[DEPLOY.md]

