import math
import pathlib
import sys
from collections import defaultdict
import pandas as pd 

# Dictionnaire des rayons de Van der Waals pour différents atomes
VanderWallR = {
    'H': 1.20, 'HE': 1.40, 'LI': 1.82, 'BE': 1.53, 'B': 1.92,
    'C': 1.7, 'N': 1.55, 'O': 1.52, 'F': 1.47, 'NE': 1.54,
    'NA': 2.27, 'MG': 1.73, 'AL': 1.84, 'SI': 2.10, 'P': 1.80,
    'S': 1.80, 'CL': 1.75, 'AR': 1.88, 'K': 2.75, 'CA': 2.31,
    'SC': 2.11, 'TI': 2.11, 'V': 2.07, 'CR': 2.06, 'MN': 2.05,
    'FE': 2.04, 'CO': 2.00, 'NI': 1.63, 'CU': 1.40, 'ZN': 1.39,
    'GA': 1.87, 'GE': 2.11, 'AS': 1.85, 'SE': 1.90, 'BR': 1.85,
    'KR': 2.02, 'RB': 3.03, 'SR': 2.49, 'Y': 2.27, 'ZR': 2.20,
    'NB': 2.07, 'MO': 2.09, 'TC': 2.09, 'RU': 2.07, 'RH': 2.04,
    'PD': 1.63, 'AG': 1.72, 'CD': 1.58, 'IN': 1.93, 'SN': 2.17,
    'SB': 2.06, 'TE': 2.06, 'I': 1.98, 'XE': 2.16, 'CS': 3.43,
    'BA': 2.68, 'PT': 1.75, 'AU': 1.66, 'HG': 1.55, 'TL': 1.96,
    'PB': 2.02, 'BI': 2.07, 'PO': 1.97, 'AT': 2.02, 'RN': 2.20,
    'FR': 3.48, 'RA': 2.83, 'U': 1.86
}

rayon_solvant = VanderWallR['O']


## Fonctions utilitaires 
# Sauvegarde des points 
def sauvegarde_points(points, nom_fichier):
    with open(nom_fichier, 'w') as f:
        for p in points:
            f.write(f'{p[0]},{p[1]},{p[2]}\n')

# Sauvegarde des atomes 
def sauvegarde_atomes(atomes, nom_fichier):
    with open(nom_fichier, 'w') as f:
        for atome in atomes:
            f.write(f'{atome["nom"]},{atome["nom_residu"]},{atome["position"][0]},{atome["position"][1]},{atome["position"][2]},{atome["rayon_w"]}\n')


# Lecture du fichier pdb pour extraire les coordonnées des atomes 
def lire_pdb(nom_fichier, points_sphere_unite):
    atomes = []
    with open(nom_fichier, "r") as f:
        for ligne in f:
            if ligne.startswith('ATOM'):
                atome = {
                    'nom': ligne[12:14].strip(),
                    'nom_residu': ligne[17:20] + ligne[22:26].strip(),
                    'position': tuple(map(float, [ligne[30:38], ligne[38:46], ligne[46:54]])),
                    'rayon_w': VanderWallR.get(ligne[12:14].strip(), 2),
                }
                atome['surface'] = calculer_surface(atome['rayon_w'])
                atome['sphere_atome'] = mise_a_echelle_points(points_sphere_unite, atome['rayon_w'], atome['position'])
                atome['sphere_atome_plus_solvant'] = mise_a_echelle_points(points_sphere_unite, atome['rayon_w'] + rayon_solvant, atome['position'])
                atome['points_accessibles'] = [True] * len(atome['sphere_atome_plus_solvant'])
                atome['nombre_points_accessibles'] = 0
                atome['surface_accessible'] = 0
                atomes.append(atome)

# Grouper les atomes par nom de résidu
    atomes_par_residu = defaultdict(list)
    for atome in atomes:
        atomes_par_residu[atome['nom_residu']].append(atome)
    
    return atomes_par_residu

## Fonction mathématiques 
# Calcul de la surface d'une sphère 
def calculer_surface(rayon):
    return 4 * math.pi * (rayon ** 2)

# Calcul de la distance entre deux points
def calculer_distance(point1, point2):
    return math.sqrt(sum((p1 - p2) ** 2 for p1, p2 in zip(point1, point2)))

# Génération de points sur une sphère unitaire 
"""Génère des points uniformément distribués sur une sphère unitaire en utilisant l'algorithme de Saff et Kuijlaars."""
def sphere_unite(nombre_points_sphere):
    points = []
    s = 3.6 / math.sqrt(nombre_points_sphere)
    dz = 2.0 / nombre_points_sphere
    longitude = 0
    z = 1 - dz / 2
    
    for k in range(nombre_points_sphere):
        r = math.sqrt(1 - z * z)
        points.append((math.cos(longitude) * r, math.sin(longitude) * r, z))
        z -= dz
        longitude += s / r

    sauvegarde_points(points, './points_sphere_unite.csv')
    return points

# Mise à l'échelle et translation des points
"""Mettre à l'échelle et translater les points de la sphère unitaire pour correspondre au rayon et à la position de l'atome."""
def mise_a_echelle_points(points, rayon, centre):
    return [(p[0] * rayon + centre[0], p[1] * rayon + centre[1], p[2] * rayon + centre[2]) for p in points]

## Calcul de l'accessibilité des atomes et résidus 

# Marquage des points accessibles sur la sphère
"""Déterminer si chaque point de la sphère est accessible en vérifiant les distances avec les autres atomes."""
def marquer_points_accessibles(atome, tous_atomes, nombre_atomes_proches):
    voisins = sorted(tous_atomes, key=lambda a: calculer_distance(atome['position'], a['position']))[:nombre_atomes_proches] if nombre_atomes_proches > 0 else tous_atomes

    for i, point in enumerate(atome['sphere_atome_plus_solvant']):
        if not atome['points_accessibles'][i]:
            continue

        for voisin in voisins:
            if atome == voisin:
                continue

            if any(calculer_distance(point, point_voisin) < rayon_solvant for point_voisin in voisin['sphere_atome']):
                atome['points_accessibles'][i] = False
                break


# Calcul de la surface accessible d'un atome
def calculer_surface_accessible(atome):
    atome['nombre_points_accessibles'] = sum(atome['points_accessibles'])
    atome['surface_accessible'] = atome['surface'] * (atome['nombre_points_accessibles'] / len(atome['points_accessibles']))

# Calcul de l'accessibilité pour un atome
def calculer_accessibilite(atome, tous_atomes, nombre_atomes_proches):
    marquer_points_accessibles(atome, tous_atomes, nombre_atomes_proches)
    calculer_surface_accessible(atome)

# Calcul de l'accessibilité pour un résidu
def calculer_accessibilite_residu(atomes_residu):
    surface_totale = sum(atome['surface'] for atome in atomes_residu)
    surface_accessible_totale = sum(atome['surface_accessible'] for atome in atomes_residu)
    pourcentage_accessibilite_totale = (surface_accessible_totale / surface_totale) * 100 if surface_totale > 0 else 0
    return surface_totale, surface_accessible_totale, pourcentage_accessibilite_totale


# Programme principal
def main():
    if len(sys.argv) != 4:
        print("Usage: python script.py <nombre_points_sphere> <nombre_atomes_proches> <fichier_pdb>")
        return

    try:
        nombre_points_sphere = int(sys.argv[1])
        nombre_atomes_proches = int(sys.argv[2])
        fichier_pdb = sys.argv[3]
    except ValueError:
        print("Erreur : Les deux premiers arguments doivent être des entiers.")
        return

    if not pathlib.Path(fichier_pdb).is_file():
        print(f"Erreur : Le fichier '{fichier_pdb}' n'existe pas.")
        return

    print('\n-DÉBUT Chargement des atomes...')
    points_sphere_unite = sphere_unite(nombre_points_sphere)
    atomes_par_residu = lire_pdb(fichier_pdb, points_sphere_unite)
    atomes = [atome for residu_atomes in atomes_par_residu.values() for atome in residu_atomes]
    sauvegarde_atomes(atomes, './atomes.csv')
    print(f'-FIN Chargé {len(atomes)} atomes')

    print('\n-DÉBUT Calcul des surfaces accessibles...')
    for atome in atomes:
        calculer_accessibilite(atome, atomes, nombre_atomes_proches)
    print('-FIN Calcul des surfaces accessibles')

    print('\n-DÉBUT Sauvegarde des résultats...')
    nom_proteine = pathlib.Path(fichier_pdb).stem
    fichier_resultats_excel = f'Surface_accessible_au_solvant_de_la_proteine_{nom_proteine}.xlsx'

    """préparation des données pour sauvegarde dans Excel"""
    donnees_residu = defaultdict(lambda: {"surface_totale": 0, "surface_accessible_totale": 0})

    for nom_residu, atomes_residu in atomes_par_residu.items():
        surface_totale, surface_accessible_totale, _ = calculer_accessibilite_residu(atomes_residu)
        donnees_residu[nom_residu]["surface_totale"] = surface_totale
        donnees_residu[nom_residu]["surface_accessible_totale"] = surface_accessible_totale

    """conversion en DataFrame pandas pour faciliter la sauvegarde dans Excel"""
    df_residus = pd.DataFrame.from_dict(donnees_residu, orient='index')
    df_residus.reset_index(inplace=True)
    df_residus.rename(columns={'index': 'residu'}, inplace=True)

    """calcul du pourcentage d'accessibilité et ajouter aux données"""
    df_residus['accessibilite'] = (df_residus['surface_accessible_totale'] / df_residus['surface_totale']) * 100

    """ caclul de la surface totale et surface accessible totale pour toute la protéine """
    surface_totale = df_residus['surface_totale'].sum()
    surface_accessible_totale = df_residus['surface_accessible_totale'].sum()
    accessibilite_totale = (surface_accessible_totale / surface_totale) * 100 if surface_totale > 0 else 0

    
    df_totaux = pd.DataFrame({'residu': ['Totaux'], 'surface_totale': [surface_totale],
                              'surface_accessible_totale': [surface_accessible_totale],
                              'accessibilite': [accessibilite_totale]})

    """concaténation des données des résidus et les totaux"""
    df_final = pd.concat([df_residus, df_totaux])
    df_final.to_excel(fichier_resultats_excel, index=False, sheet_name='Résultats')

    """sauvegarde dans un fichier Excel"""
    print(f'\nRésultats sauvegardés dans : {fichier_resultats_excel}')

    print(f'\nRésultats:')
    print(f'Surface totale : {surface_totale:.1f}Å²')
    print(f'Surface accessible totale : {surface_accessible_totale:.1f}Å²')
    print(f'Pourcentage d\'accessibilité au solvant : {accessibilite_totale:.1f}%')
    print('\n-FIN Sauvegarde des résultats')

if __name__ == '__main__':
    main()