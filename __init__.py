# -*- coding: utf-8 -*-

"""
    ***************************************************************************
    * Plugin name:   SgmHunting
    * Plugin type:   QGIS 3 plugin
    * Module:        Initialization
    * Description:   Specific plugin for French rental of communal hunts
    *                (only for Alsace/Moselle cities in France)
    * Specific lib:  openpyxl
    * First release: 2023-09-01
    * Last release:  2023-09-07
    * Copyright:     (C)2023 SIGMOE
    * Email:         em at sigmoe.fr
    * License:       GPL v3
    ***************************************************************************
 
    ***************************************************************************
    * This program is free software: you can redistribute it and/or modify
    * it under the terms of the GNU General Public License as published by
    * the Free Software Foundation, either version 3 of the License, or
    * (at your option) any later version.
    *
    * This program is distributed in the hope that it will be useful,
    * but WITHOUT ANY WARRANTY; without even the implied warranty of
    * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    * GNU General Public License for more details.
    *
    * You should have received a copy of the GNU General Public License
    * along with this program. If not, see <http://www.gnu.org/licenses/>.
    *************************************************************************** 
    
    This script initializes the plugin, making it known to QGIS.
"""

import os
import sys

# Loads specific lib
plugin_libs_path = os.path.join(os.path.dirname(__file__), 'libs')
for file in os.listdir(plugin_libs_path):
    if file.endswith('.whl'):
        sys.path.append(os.path.join(plugin_libs_path, file))


def classFactory(iface):
    # Loads SgmHunting class from file sgm_hunting
    from .sgm_hunting import SgmHunting
    return SgmHunting(iface)
