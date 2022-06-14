# CONFIG

## Paramétrer la plateforme du catalogage

En l'abscence d'interface web d'administration (V3), le paramétrage **initial** de la plateforme se fait par l'édition d'un fichier csv appelé `rules.csv`.
Celui ci est disponible dans le dossier `back/init_data/rules.csv`.

Une fois la plateforme installée, il est possible de changer les paramétres via l'API depuis le point d'accès `/rules` qui sera rendu disponible uniquement à l'administrateur de la plateforme (V2) et accessible depuis une interface web simplifiée (V3) pour une gestion au long cours.


Le catalogue est composé de plusieurs modèles de données qui peuvent entretenir des relations entre eux.

Par `modèle de données` on entend: 
- la définition des caractéristiques d'un modèle `schéma des métadonnées`. 
> Ce schéma décrit les caractéristiques du modèle en spécifiant le type, le format attendu, les valeurs possibles et/ou acceptées et par voie de conséquence le controle et la validation des données à l'insertion/édition. Il définit aussi les relations entre les différents modèles.
- les valeurs qui lui sont associées soit les `données`. 
> Elles sont stockées dans une base de données.
 
### Définir un modèle de données pour le catalogue

#### Principe de définition d'un modèle

Le fichier de paramétrage initial et donc de création des différents modèles du catalogue est au format CSV où chaque ligne correspond à une caractéristique/une propriété dont l'identifiant unique est `slug`. 

> Pour lister toutes les caractéristiques d'un modele, il suffit de selectionner dans la colonne `model` le modèle qui nous intéresse et consulter ainsi toutes les caractéristiques/propriétés/métadonnées d'un modèle. 

> On peut aussi consulter la définition du modèle de données via l'API `/rules/<model>` 

> Ce système permet à la plateforme d'être agnostique, c'est à dire de s'adapter à n'importe quel modèle de données définit par ces caractéristiques. 

Chaque ligne du fichier correspond donc à une **caractéristique** du modèle de données, identifié par la colonne `slug`, slug est l'idenfiant unique de la caractéristique et correspond au nom du champ tel que stocké dans la base de données et tel qu'il sera exporté dans différents formats. 
- `slug` est donc l'identifiant unique de la caractéristique
- `datatype` indique le type de données tel que stocké dans la base de données.

> Les type de données acceptés sont : 
- string (chaine de caractère ou texte, les cas spécifiques sont définis dans `format` : email, url, ...)
- boolean (booléen True/False) 
- integer (entier relatifs: 1, 2, -1) 
- date (representation textuelle d'une date dont le format est défini dans `format`: YYYY, YYYY/MM/DD) 
- object (dictionnaire relié à un autre modèle défini dans `external_model` dont les clés sont définis dans `external_model_display_keys`)

- `multiple` indique si cette caractéristique accepte un ou plusieurs élements 
- `mandatory` si cette caractéristique est obligatoire et donc si elle peut etre vide.

> La cardinalité d'une caractéristique est donc définie par multiple et mandatory

- `constraint` renseigne les contraintes propre à cette caractérique: on peut y indiquer que la valeur doit appartenir à une liste de valeurs possible `one of`, ou que la valeur doit être unique et donc ne pas préexister dans la base de données `unique`

On peut renseigner les relations de cette propriété avec d'autre modèle via `external_model` dans lequel on renseigne le nom du modele (le même que dans `model`)
et on ajoute les clés étrangères de ce modele (les caractéristiques permettant de relier les deux modèles) dans `external_model_display_keys` une liste de clés qui sont séparées par un `|`

On peut aussi indiquer si la propriété repose sur un référentiel externe contrôlé autrement dit une liste de choix possible pour cette valeur dans `reference_table`

