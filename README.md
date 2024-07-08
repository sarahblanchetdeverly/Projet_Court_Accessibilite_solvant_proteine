# Projet_Court_Accessibilite_solvant_proteine
Ce projet implémente un programme en Python pour calculer la surface accessible au solvant des protéines à partir des coordonnées fournies dans un fichier PDB. L'algorithme utilisé est basé sur l'algorithme de Shrake-Rupley.

## Description
La surface accessible au solvant des acides aminés des protéines est un paramètre essentiel pour comprendre leur structure et leurs interactions. Ce programme utilise un maillage de points autour de chaque atome pour déterminer quels points sont accessibles au solvant.

## Langage 
- Python 3

## Bibliothéque et Module 
@ Bibliothèque : 
- pandas

@ Modules : 
- math
- pathlib
- sys 
- collections

## Installation 
Créer un environnement virtuel sur conda 
```bash
$ conda create projet_court
$ conda activate projet_court
```
Et installer les dépendances nécessaires : 
```bash
$ conda install pandas
```

Clonage du répertoire : 
```bash
$ git clone https://github.com/sarahblanchetdeverly/Projet_Court_Accessibilite_solvant_proteine.git
```

## Data 
Code éxécuté sur le fichier 3i40.pdb

## Nom du script
projet_court_proteine.py

## Exécution du code dans le terminal 
```bash
$ python3 script.py  <nombre_points_sphere> <nombre_atomes_proches> <fichier_pdb>
```
Exemple :
```bash
$ python3 projet_court_proteine.py 100 5 3i40.pdb
```



