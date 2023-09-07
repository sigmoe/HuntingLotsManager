# -*- coding: utf-8 -*-

"""
    ***************************************************************************
    * Plugin name:   SgmHunting
    * Plugin type:   QGIS 3 plugin
    * Module:        Global Vars
    * Description:   Global variables
    * Specific lib:  None
    * First release: 2023-09-01
    * Last release:  2023-09-07
    * Copyright:     (C)2023 SIGMOE
    * Email:         em at sigmoe.fr
    * License:       GPL
    ***************************************************************************

    ***************************************************************************
    * This program is free software: you can redistribute it and/or modify
    * it under the terms of the GNU General Public License as published by
    * the Free Software Foundation, either version 3 of the License, or
    * (at your option) any later version.
    ***************************************************************************
"""

from qgis.PyQt.QtCore import QVariant


# Interface and dialog messages
mnu_title_txt = "Gestion Lots de Chasse"
mnu_fnc1_txt = "Création des nouvelles couches de gestion des lots"
mnu_fnc2_txt = "Export Excel de la liste des parcelles par lot"
mnu_fnc3_txt = "Configuration"

dlg_msg_titles = [  "Création des nouvelles couches de gestion de chasse",
                    "Export Excel Liste des parcelles par lot de chasse"
                    ]
dlg_msg_buts = [    "Créer les couches  >>",
                    "Exporter fichier Excel >>"
                    ]
crelyr_msg_txt = [  "Ré-ajustement des Lots sur Parcelles",
                    "Création de la nouvelle couche <font color=\"firebrick\">{0:s}</font>",
                    "Création des nouveaux objets",
                    "Calcul des 2 nouveaux champs surface chasse",
                    "Applique la symbologie catégorisée",
                    "Calcul des totaux par lot",
                    "Création de la couche lots calculés",
                    "Ajout du total",
                    "Applique la symbologie catégorisée",
                    "Création des nouvelles couches terminée ! "
                    ]
exportxl_msg_txt = [    "Création du fichier Excel",
                        "Création de la feuille <font color=\"firebrick\">{0:s}</font>",
                        "Export du fichier Excel des parcelles par lot de chasse terminé !"
                        ]
alert_lyr_msg_txt = [   "Problème couche non valide",
                        "L'une des couches <font color=\"firebrick\">{0:s}</font> et <font color=\"firebrick\">{1:s}</font> n'est pas valide<br>Veuillez vérifier que ces 2 couches sont bien présentes dans votre projet et qu'elles sont valides !"
                        ]
alert_cre_msg_txt = ["Erreur création couches", "Une erreur est apparue lors de la céation des nouvelles couches Chasse:<br><font color=\"firebrick\">{0:s}</font><br><br><b>Veuillez vérifer les couches utilisées (Parcelles, ...) et la configuration (Nom de la couche zonage des Lots, Nom du champ contenant le nom des lots, ...), corriger le problème, puis relancer l'opération !</b>"]
alert_fic_msg_txt = ["Erreur fichier Excel", "Une erreur est apparue lors de la céation du fichier Excel:<br><font color=\"firebrick\">{0:s}</font><br><br><b>Veuillez corriger le problème (fermer le fichier s'il existe déjà et qu'il est ouvert, vérifier que le répertoire choisi existe, ...) et relancer l'opération !</b>"]
fnd_dir_txt = "Choix du répertoire"

# Default file, directories and layer names used for the process
gpkg_fname = "gestion chasse"
parc_lyrname = 'Parcelles'
surfgeo_fldname = 'surface_geo'
contparc_fldname = 'contenance'

# Spectral color ramp
ramp_c = ['#d7191c', '#fdae61', '#ffffbf', '#abdda4', '#2b83ba']

# New layers configuration
add_fldnames = ["surface_geo_chasse", "contenance_chasse"]
add_fldqtypes = [QVariant.Double, QVariant.Double]
add_fldalias = ["Surface chasse", "Contenance chasse"]

tot_fldname = "total_surface_chasse"
tot_fldqtype = QVariant.Double
tot_fldalias = "Total Surface chasse"

cat_label = "Lot {0:s}"

# Excel export configuration
col_delta_w = 5
tot_label = "Total surface chasse Lot {0:s}"