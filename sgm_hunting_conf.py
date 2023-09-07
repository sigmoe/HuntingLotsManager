# -*- coding: utf-8 -*-

"""
     ***************************************************************************
    * Plugin name:   SgmHunting
    * Plugin type:   QGIS 3 plugin
    * Module:        Configuration
    * Description:   Configuration
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


from qgis.PyQt import uic
from qgis.PyQt.QtCore import Qt, QFileInfo, pyqtSignal
from qgis.PyQt.QtWidgets import QDialog, QFileDialog
from qgis.core import QgsProject

from functools import partial

import os.path

from .sgm_hunting_globalvars import *
from .sgm_hunting_globalfnc import *

gui_dlg_conf, _ = uic.loadUiType(
        os.path.join(os.path.dirname(__file__), r"gui/dlg_hunting_conf.ui"))


class Conf:
    
    def __init__(self, iface, canvas, project, plugin_dir):

        self.iface = iface
        self.canvas = canvas
        self.project = project
        self.plugin_dir = plugin_dir
        
        self.old_params = {}
        
        # Loads the original parameters
        self.pop_oldparams_fromjson()
        self.pop_params()


    def reconf(self) :
        # Reloads the last params
        self.pop_oldparams_fromjson()
        # Prepares the parameters window
        self.param_conf = ParamConf(self.project, self.plugin_dir, self.old_params, self.params_path)
        # Captures the dic of parameters when closing the dlg window
        self.param_conf.send_nw_params.connect(self.ok_param) 
        # Modal window
        self.param_conf.setWindowModality(Qt.ApplicationModal)
        # Shows the parameters window
        self.param_conf.show()


    def ok_param(self, dic_param):
        self.old_params = dic_param
        self.pop_params()


    def pop_params(self):
        for k, v in self.old_params.items():
            self.__dict__[k] = v
            
            
    def pop_oldparams_fromjson(self):
        self.old_params, self.params_path = read_jsparams(self.plugin_dir, "sgm_hunting_conf", "params" )



class ParamConf(QDialog, gui_dlg_conf):
    '''
        Manages the window of parameters
    '''

    send_nw_params = pyqtSignal(dict)
    
    def __init__(self, project, plugin_dir, old_params, params_path, parent=None):
        super(ParamConf, self).__init__(parent)
        self.setupUi(self)
        self.project = project
        self.plugin_dir = plugin_dir
        self.old_params = old_params
        self.params_path = params_path
        # Initialization of the closing method (False = quit by red cross)
        self.quit_valid = False

        self.params = {}

        # Connections
        self.export_rep_but.clicked.connect(partial(self.dir_choose, "export_rep_led"))
        self.valid_btn.accepted.connect(self.butt_ok)
        self.valid_btn.rejected.connect(self.butt_cancel)
        # Fill values
        for k, v in self.old_params.items():
            set_txt_qobj(self.__dict__[k], v)
        # Delete Widget on close event
        self.setAttribute(Qt.WA_DeleteOnClose)


    
    def dir_choose(self, dir_type):
        '''
            To select a directory
        '''
        # Determines a path to use by default:
        # Chooses the inirep if exists
        # Otherwise, chooses the project path
        cur_dir = self.old_params[dir_type]
        docs_dir_fi = QFileInfo(cur_dir)
        if docs_dir_fi.exists():
            prjpath = cur_dir
        else:
            # Case of using the project path
            prjfi = QFileInfo(QgsProject.instance().fileName())
            prj_filepath = prjfi.absolutePath()
            prjpath = os.path.dirname(prj_filepath)
        # Opens the dlg to choose a directory
        nw_dir = QFileDialog.getExistingDirectory(self, fnd_dir_txt, prjpath)
        if nw_dir is not None and nw_dir != '':
            set_txt_qobj(self.__dict__[dir_type], nw_dir)
        else:
            set_txt_qobj(self.__dict__[dir_type], prjpath)


    def butt_ok(self):
        '''
            Closes the window when clicking on the OK button
        '''
        self.quit_valid = True
        self.close()


    def butt_cancel(self):
        '''
            Closes the window when clicking on the Cancel button
        '''
        self.quit_valid = False
        self.close()


    def closeEvent(self, event):
        '''
            Sends the parameters when the windows is quit
        '''
        if self.quit_valid:
            # Saves the different parameters
            for k, v in self.old_params.items():
                self.params[k] = get_txt_qobj(self.__dict__[k])[0]
            # Updates the new parameters in the json file
            json_params = {}
            json_params["params"] = self.params
            save_jsparams(self.plugin_dir, "sgm_hunting_conf", json_params)
            # Sends the parameters
            self.send_nw_params.emit(self.params)
        # Hides the window
        self.hide()
