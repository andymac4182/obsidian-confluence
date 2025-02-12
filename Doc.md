# Introduction

Le moteur de conception paramétrique pour EuroTempl sert de composant central pour la gestion des relations paramétriques, des données géométriques et facilite l'intégration transparente entre la couche de base de données et FreeCAD. Le moteur est conçu comme un monolithe modulaire, avec des limites claires pour une éventuelle extraction de microservices à l'avenir.

## Architecture du moteur central

Le moteur est structuré selon une approche de conception pilotée par le domaine (DDD), utilisant Python comme langue principale pour sa flexibilité et sa facilité d'utilisation, tout en incorporant C++ pour les opérations critiques en termes de performance. Cette architecture met l'accent sur une séparation claire des préoccupations, améliorant la maintenabilité et l'évolutivité. Le moteur central comprend les composants clés suivants :

### Paramètres

- Stocke les définitions de tous les paramètres utilisés dans le système.
- Inclut des métadonnées sur chaque paramètre, telles que son type (par exemple, entier, flottant, chaîne, spatial), les unités, les contraintes et les plages autorisées.
- Prend en charge des formules ou des expressions pour définir des relations paramétriques, permettant aux paramètres d'être influencés par d'autres paramètres ou des expressions mathématiques.
- Utilise des dictionnaires Python pour stocker les détails des paramètres et tire parti de la flexibilité des structures de données intégrées de Python.

### Relations de paramètres

- Maintient une structure de graphe de dépendance pour gérer comment les paramètres s'influencent mutuellement.
  - Met en œuvre des algorithmes pour traverser efficacement le graphe de dépendance lorsqu'un paramètre est modifié.
  - Assure une propagation appropriée des modifications aux paramètres dépendants et aux composants géométriques.
- La structure du graphe doit être explicite et facilement compréhensible.

### Valeurs de paramètres

- Enregistre à la fois les valeurs historiques et actuelles pour tous les paramètres.
  - Stocke un journal détaillé des modifications, y compris le moment de la modification et l'utilisateur qui a effectué le changement.
  - Prend en charge la version des conceptions paramétriques grâce à l'historique des paramètres, permettant ainsi une comparaison facile entre différentes itérations de conception.

### Données géométriques

- Stocke des informations spatiales en utilisant PostGIS.
  - Utilise une base de données spatiale pour gérer et interroger efficacement les données spatiales, prenant en charge des opérations comme l'indexation spatiale.
  - Inclut des fonctionnalités pour stocker à la fois la définition paramétrique et la représentation géométrique résultante des modèles CAO.
  - Stocke explicitement des attributs topologiques, permettant une reconstruction efficace des géométries CAO.
  - Met en œuvre des algorithmes de conversion entre les géométries CAO et les géométries GIS 3D, utilisant des polyèdres pour représenter les solides.
  - Stocke le modèle 3D de manière paramétrique en utilisant un JSON adapté pour permettre le stockage, la requête et la reconstruction des données CAO.
  - Inclut une bibliothèque paramétrique pour reconstruire des géométries solides CAO avec des polyèdres.

## Intégration avec FreeCAD

Le moteur s'intègre à FreeCAD via son API Python, reflétant l'approche de FreeCAD en matière de modélisation paramétrique. Les aspects clés de l'intégration comprennent :

- **Objets paramétriques** : Crée des objets FreeCAD correspondants pour chaque composant, assurant une synchronisation cohérente entre la base de données et le modèle CAO. Ces objets sont construits à l'aide de classes Python, définissant des propriétés et des comportements.
- **Modification de la géométrie** : Fournit des méthodes pour créer et modifier des caractéristiques géométriques en fonction des changements de paramètres. Cela implique une manipulation directe de la représentation géométrique interne de FreeCAD.
- **Gestion des contraintes** : Prend en charge la mise à jour des relations de contrainte dans le modèle CAO pour refléter les changements dans les dépendances paramétriques. Cela est crucial pour maintenir l'intégrité des conceptions.
- **Exportation au format standard** : Permet l'exportation de modèles CAO dans des formats standard tels que STEP et IGES pour l'interopérabilité avec d'autres systèmes.
- **Exportation de nomenclature** : Utilise l'outil de nomenclature intégré de FreeCAD pour générer une liste de matériaux synchronisée avec la base de données.
- **Outils personnalisés** : Prend en charge la personnalisation via des interfaces de programmation visuelle et des scripts Python pour développer des outils personnalisés et de l'automatisation.

## Optimisations de performance

Pour garantir des performances optimales, le moteur met en œuvre plusieurs optimisations :

- **Mise en cache** : Met en œuvre la mise en cache des valeurs de paramètres calculées et des données géométriques, ce qui réduit les recalculs inutiles.
- **Évaluation paresseuse** : Emploie l'évaluation paresseuse des mises à jour géométriques pour minimiser les calculs inutiles, améliorant ainsi la réactivité globale du système.
- **Traitement parallèle** : Utilise C++ pour permettre le traitement parallèle des mises à jour de paramètres indépendants, atténuant les limitations du GIL de Python.
- **Algorithmes efficaces** : Utilise des algorithmes optimisés pour la traversée de graphes, la résolution de dépendances et les calculs géométriques.

## Structure du code et meilleures pratiques

- **Modularité** : Le code est organisé en modules en fonction de la fonctionnalité.
- **Architecture en couches** : Le code est structuré en couches : couche d'accès aux données, couche domaine (logique métier) et couche de présentation (interface utilisateur).
- **Programmation orientée objet (POO)** : Les classes Python sont utilisées pour définir des objets paramétriques et leur comportement. Les données sont encapsulées avec des méthodes qui y accèdent et les modifient.
- **Structures de données** : Utilise les structures de données intégrées de Python telles que les dictionnaires et les listes pour une manipulation efficace des données.
- **Bibliothèques Python** : Tire parti de l'énorme bibliothèque standard de Python et d'autres modules spécialisés pour étendre les capacités de FreeCAD.
- **Framework Django** : Utilise le framework Django pour gérer les données et créer une API REST.
- **Contrôle de version** : Utilise Git pour un contrôle de version robuste tant du code que du schéma de base de données.
- **Documentation** : Utilise la documentation en source pour expliquer le code et documente le processus de conception de manière approfondie.
- **Conventions de nommage** : Des conventions de nommage cohérentes sont utilisées pour le code, les objets de base de données et les paramètres.
- **Conception itérative** : Met en œuvre un processus de conception itératif avec une exploration, une génération, une réflexion et une modification fréquentes.
- **Gestion des erreurs** : Inclut une gestion robuste des erreurs et une validation des données pour garantir l'intégrité des données et un fonctionnement fluide.

## Considérations mathématiques et algorithmiques

- **Pensée algorithmique** : Le moteur incorpore une pensée algorithmique, utilisant des règles explicites pour générer des formes et des conceptions.
- **Schéma paramétrique** : Met en œuvre un schéma paramétrique qui agit comme un modèle mathématique pour la génération de formes algorithmiques.
- **Relations associatives** : Se concentre sur l'exploration des relations entre des concepts géométriques, créant des formes adaptables réactives aux changements de paramètres.
- **Conception basée sur des règles** : Utilise des méthodes de conception basées sur des règles pour les variations au sein d'un module standard.
- **Transformations géométriques** : Met en œuvre des opérations mathématiques pour des transformations telles que la translation, la rotation, le redimensionnement, le miroir et les conversions de forme.

## Considérations Métier

- **Assemblage modulaire** : Met l'accent sur des méthodes d'assemblage modulaire pour une construction rapide et efficace.
- **Simplicité cognitive** : Priorise la simplicité cognitive et un design minimaliste pour garantir la facilité d'utilisation.
- **Conception de fabrication de matériaux (MFD)** : Prend en compte l'ordre tectonique de la fabrication des matériaux dans le processus de conception.
- **Traçabilité** : Maintient la traçabilité des exigences à la conception, garantissant que toutes les exigences sont satisfaites.
- **Interopérabilité** : Utilise des formats de fichiers standard tels que STEP ou IGES pour échanger des données entre les systèmes CAO et CAE.
- **Normes ouvertes** : Adhère aux normes ouvertes dans la mesure du possible pour une adaptabilité et une évolutivité maximales.

## Structure

### parameters/
Contient des modules liés à la gestion des paramètres.

- `parameter.py` : Définit la classe de base et les fonctionnalités communes pour tous les paramètres, leurs propriétés et comportements.
- `numeric_parameter.py` : Étend la classe de base pour les paramètres numériques avec une validation spécifique.
- `spatial_parameter.py` : Classe de paramètres spécifique pour les données spatiales, interagissant avec PostGIS.
- `parameter_relationships.py` : Gère le graphe de dépendance des paramètres avec des méthodes pour la traversée et la propagation des changements.
- `parameter_values.py` : Gère le stockage des valeurs de paramètres actuelles et historiques et enregistre les changements.

### geometry/
Inclut des modules pour la gestion des données géométriques et des conversions.

- `cad_model.py` : Gère les objets FreeCAD avec des méthodes de modification basées sur des changements paramétriques.
- `spatial_data.py` : Gère le stockage et les requêtes de données spatiales en utilisant PostGIS, y compris des fonctions pour convertir des données en d'autres types de données.
- `conversion_algorithms.py` : Implémente des algorithmes de conversion entre différentes représentations géométriques (CAO et SIG 3D).
- `parametric_library.py` : Implémente une bibliothèque paramétrique pour reconstruire des géométries solides CAO avec des polyèdres.

### cad_engine/
Gère l'intégration entre le moteur et FreeCAD.

- `parametric_objects.py` : Crée et gère les objets FreeCAD correspondants pour chaque composant, maintenant les modèles CAO et les données synchronisés avec la base de données.
- `constraint_management.py` : Soutient la mise à jour des relations de contraintes au sein des modèles FreeCAD en fonction des dépendances paramétriques.
- `standard_export.py` : Implémente des méthodes pour exporter des modèles dans des formats standards comme STEP et IGES.
- `bom_export.py` : Utilise l'outil de nomenclature intégré de FreeCAD pour générer une liste de matériaux.
- `custom_tools.py` : Soutient les outils personnalisés et l'automatisation via des scripts Python.

### core_logic/
Contient des implémentations des algorithmes clés.

- `graph_traversal.py` : Inclut des algorithmes pour traverser le graphe de dépendance des paramètres.
- `dependency_resolution.py` : Gère les algorithmes pour résoudre les dépendances des paramètres.
- `geometric_computations.py` : Implémente des algorithmes optimisés pour divers calculs géométriques.

### core/
Modèles de base et interfaces

- `models/` : Définit des modèles de base de données utilisant Django ORM.
- `database_operations.py` : Implémente toutes les opérations de base de données pour les fonctionnalités CRUD.

### utils/
Inclut des modules utilitaires utilisés dans tout le moteur.

- `caching.py` : Implémente des mécanismes de mise en cache pour les valeurs de paramètres et les données géométriques.
- `lazy_evaluation.py` : Implémente une évaluation paresseuse pour les mises à jour géométriques.
