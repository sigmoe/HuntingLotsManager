# -*- coding: utf-8 -*-

"""
    ***************************************************************************
    * Plugin name:   SgmHunting
    * Plugin type:   QGIS 3 plugin
    * Module:        Main
    * Description:   Main class
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

from qgis.PyQt.QtCore import  QCoreApplication
from qgis.PyQt.QtWidgets import QAction, QMenu
from qgis.PyQt.QtGui import QIcon
from qgis.core import QgsProject
from qgis.utils import iface

import os.path

from .sgm_hunting_globalvars import *
from .sgm_hunting_prepaparclot import PrepaParcLot
from .sgm_hunting_crerapport import ExportXl
from .sgm_hunting_conf import Conf

# Imports resources (for icons)
from . import sgm_hunting_rc


class SgmHunting:
    
    # Initialization
    def __init__(self, iface):
        self.iface = iface
        self.canvas = self.iface.mapCanvas()
        self.project = QgsProject.instance()
        self.selectiae_window = None
        
        # Initializes plugin directory
        self.plugin_dir = os.path.dirname(__file__)


    def initGui(self):
        '''
            Initialization of menu and toolbar
        '''
        # Adds specific menu to QGIS menu
        self.sgm_menu = QMenu(QCoreApplication.translate("Hunting", mnu_title_txt))
        self.iface.mainWindow().menuBar().insertMenu(self.iface.firstRightStandardMenu().menuAction(), self.sgm_menu)
        
        # Adds specific toolbar
        self.sgm_tb = self.iface.addToolBar(mnu_title_txt)
        self.sgm_tb.setObjectName("HuntingToolBar")
        
        # Creates actions
        self.action_prepaparclot = QAction(
            QIcon(r":sgm_hunting_prepaparclot"), mnu_fnc1_txt, self.iface.mainWindow())
        self.action_crerapport = QAction(
            QIcon(r":sgm_hunting_crerapport"), mnu_fnc2_txt, self.iface.mainWindow())
        self.action_conf = QAction(
            QIcon(r":sgm_hunting_conf"), mnu_fnc3_txt, self.iface.mainWindow())

        # Adds actions to the toolbar
        self.sgm_tb.addActions([self.action_prepaparclot,
                                self.action_crerapport,
                                self.action_conf
                                ])
                                 
        # Adds actions to the menu
        self.sgm_menu.addActions([  self.action_prepaparclot,
                                    self.action_crerapport,
                                    self.action_conf
                                    ])
        
        # Manages signals
        self.action_prepaparclot.triggered.connect(self.hunting_prepaparclot)
        self.action_crerapport.triggered.connect(self.hunting_crerapport)
        self.action_conf.triggered.connect(self.hunting_conf)
        
        # Gets the config
        self.huntingconf = Conf(self.iface, self.canvas, self.project, self.plugin_dir)


    def unload(self):
        '''
            Removes the plugin menu item and icon from QGIS GUI
        '''
        if self.sgm_menu != None:
            self.iface.mainWindow().menuBar().removeAction(self.sgm_menu.menuAction())
            self.sgm_menu.deleteLater()
            self.iface.mainWindow().removeToolBar(self.sgm_tb)
        else:
            self.iface.removePluginMenu("&Hunting", self.sgm_menu.menuAction())
            self.sgm_menu.deleteLater()


    def hunting_prepaparclot(self):
        '''
            Creates new layers to manage hunting lots
        '''
        self.prepaparclot = PrepaParcLot(self.iface, self.canvas, self.project, self.plugin_dir, self.huntingconf.old_params)
        self.prepaparclot.launch()


    def hunting_crerapport(self):
        '''
            Creates new report (Excel export)
        '''
        self.export_xl_rapport = ExportXl(self.iface, self.canvas, self.project, self.plugin_dir, self.huntingconf.old_params)
        self.export_xl_rapport.launch()


    def hunting_conf(self):
        '''
            Configuration
        '''
        self.huntingconf.reconf()