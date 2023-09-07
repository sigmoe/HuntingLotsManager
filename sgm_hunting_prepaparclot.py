# -*- coding: utf-8 -*-

"""
    ***************************************************************************
    * Plugin name:   SgmHunting
    * Plugin type:   QGIS 3 plugin
    * Module:        PrepaParcLot class
    * Description:   Class to do the job for creating new layers to manage 
    *                hunting lots
    * Specific lib:  none
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
from qgis.PyQt.QtCore import Qt, pyqtSignal
from qgis.PyQt.QtWidgets import qApp, QMessageBox, QWidget
from qgis.PyQt.QtGui import QTextCursor
from qgis.core import QgsProcessing, QgsFields, QgsField

import processing
import os

from .sgm_hunting_globalvars import *
from .sgm_hunting_globalfnc import *

gui_dlg_hunting_msg, _ = uic.loadUiType(
        os.path.join(os.path.dirname(__file__), r"gui/dlg_hunting_msg.ui"))


class PrepaParcLot:
    
    def __init__(self, iface, canvas, project, plugin_dir, conf):

        self.iface = iface
        self.canvas = canvas
        self.project = project
        self.plugin_dir = plugin_dir
        self.conf = conf
        for k, v in self.conf.items():
            self.__dict__[k[:-4]] = v


    def launch(self) :
        # Prepares the msg window
        self.feedback = MsgWnd()
        # Captures the signal to launch the process
        self.feedback.send_ok.connect(self.ok_param) 
        # Modal window
        self.feedback.setWindowModality(Qt.ApplicationModal)
        # Shows the parameters window
        self.feedback.show()


    def ok_param(self):
        '''
            Launch the process once the msg window is validated
        '''
        # Initializes progressbar
        self.feedback.pg_bar.setMaximum(8)
        self.pgb_val = 0
        
        # Initialization
        parc_lyr = self.project.mapLayersByName(parc_lyrname)[0]
        lot_lyr = self.project.mapLayersByName(self.lot_lyrname)[0]
        parclyr_al = get_layer_fields_alias(parc_lyr)
        lot_lyr_al = get_layer_fields_alias(lot_lyr)
        if not parc_lyr.isValid() or not lot_lyr.isValid():
            QMessageBox.warning(
                                    self.feedback, 
                                    alert_lyr_msg_txt[0], 
                                    alert_lyr_msg_txt[1].format(parc_lyrname, self.lot_lyrname)
                                    )
        else:
            try:
                # If necessary, creates new snapping Lots on Parcelles layer
                self.send_msg(crelyr_msg_txt[0])
                if self.dist_max > 0:
                    alg_params = {  'INPUT': lot_lyr,
                                    'REFERENCE_LAYER': parc_lyr,
                                    'TOLERANCE': self.dist_max,
                                    'BEHAVIOR': 1,
                                    'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
                                    }
                    lotaccr_lyr = processing.run("native:snapgeometries", alg_params)['OUTPUT']
                else:
                    lotaccr_lyr = lot_lyr
                    
                # Creates new parclot intersection layer
                self.send_msg(crelyr_msg_txt[1].format(self.parclot_lyrname))
                # Builts the new complete filename for the new layer (GPKG)
                prj_dir = self.project.absolutePath()
                nw_filename = gpkg_fname + ".gpkg"
                nw_filepath = os.path.join(prj_dir, nw_filename)
                # Removes existing files before creating new file
                if os.path.exists(nw_filepath):
                    os.remove(nw_filepath)
                # Uses intersection processing algorithm
                self.send_msg(crelyr_msg_txt[2])
                output_uri = 'ogr:dbname=\'' + nw_filepath + '\' table="' + self.parclot_lyrname + '" (geom)'
                alg_params = {
                                'INPUT': parc_lyr,
                                'OVERLAY': lotaccr_lyr,
                                'INPUT_FIELDS': [],
                                'OVERLAY_FIELDS': [self.lot_attname],
                                'OVERLAY_FIELDS_PREFIX': '',
                                'OUTPUT': output_uri,
                                'GRID_SIZE': None
                                }
                parclot_uri = processing.run("native:intersection", alg_params)['OUTPUT']
                parclot_lyr = self.iface.addVectorLayer(parclot_uri, self.parclot_lyrname, 'ogr')
                
                # Adds 2 surface fields
                self.send_msg(crelyr_msg_txt[3])
                add_flds = QgsFields()
                for i, n in enumerate(add_fldnames):
                    add_flds.append(QgsField(n, add_fldqtypes[i]))
                parclot_lyr.dataProvider().addAttributes(add_flds)
                parclot_lyr.updateFields()
                
                # Calculates 2 new fields
                if not parclot_lyr.isEditable():
                    parclot_lyr.startEditing()
                for obj in parclot_lyr.getFeatures():
                    parclot_psurf = obj[surfgeo_fldname]
                    parclot_pcont = obj[contparc_fldname]
                    parclot_surf = round(obj.geometry().area())
                    parclot_cont = parclot_pcont
                    if parclot_psurf != 0 :
                        if parclot_surf < parclot_psurf:
                            parclot_cont = round(parclot_surf / parclot_psurf * parclot_pcont)
                        else:
                            parclot_surf = parclot_psurf
                    update_attval(parclot_lyr, obj, add_fldnames[0], parclot_surf)
                    update_attval(parclot_lyr, obj, add_fldnames[1], parclot_cont)
                parclot_lyr.commitChanges()
                
                # Creates alias
                al_map = parclyr_al + lot_lyr_al + [[fdn, add_fldalias[i]] for i, fdn in enumerate(add_fldnames)] + [[tot_fldname, tot_fldalias]]
                print(f"al_map: {al_map}")
                create_alias(parclot_lyr, al_map)
                
                # Moves layer to the top (layer order)
                move_lyr_to_top(self.project, parclot_lyr)
                
                # Adds categorized symbology
                self.send_msg(crelyr_msg_txt[4])
                add_cat_symb(parclot_lyr, self.lot_attname, ramp_c, cat_label)
                
                parclot_lyr.triggerRepaint()

                # Creates new stat by category for total surface by lot calculation
                self.send_msg(crelyr_msg_txt[5])
                alg_params = {  'INPUT': parclot_lyr,
                                'VALUES_FIELD_NAME': add_fldnames[1],
                                'CATEGORIES_FIELD_NAME':[self.lot_attname],
                                'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
                                }
                stat_lyr = processing.run("qgis:statisticsbycategories", alg_params)['OUTPUT']
                # Creates dic of total contenance by lot
                cont_lot_dic = {}
                for obj in stat_lyr.getFeatures():
                    cont_lot_dic[obj[self.lot_attname]] = obj['sum']
                
                # Creates new calculated lots layer
                output_uri = 'ogr:dbname=\'' + nw_filepath + '\' table="' + self.nwlots_lyrname + '" (geom)'
                self.send_msg(crelyr_msg_txt[6])
                alg_params = {  'INPUT': parclot_lyr,
                                'FIELD': [self.lot_attname],
                                'SEPARATE_DISJOINT': False,
                                'OUTPUT': output_uri
                                }
                nwlots_uri = processing.run("native:dissolve", alg_params)['OUTPUT']
                nwlots_lyr = self.iface.addVectorLayer(nwlots_uri, self.nwlots_lyrname, 'ogr')
                
                # Moves layer to the top (layer order)
                move_lyr_to_top(self.project, nwlots_lyr)
                
                # Deletes useless fields and add the contenance total field
                self.send_msg(crelyr_msg_txt[7])
                del_flds = []
                for fld in nwlots_lyr.fields():
                    fld_name = fld.name()
                    if fld_name not in ['fid', self.lot_attname]:
                        del_flds.append(nwlots_lyr.fields().indexFromName(fld_name))
                nwlots_lyr.dataProvider().deleteAttributes(del_flds)
                nwlots_lyr.updateFields()
                add_flds = QgsFields()
                add_flds.append(QgsField(tot_fldname, tot_fldqtype))
                nwlots_lyr.dataProvider().addAttributes(add_flds)
                nwlots_lyr.updateFields()
                if not nwlots_lyr.isEditable():
                    nwlots_lyr.startEditing()
                for obj in nwlots_lyr.getFeatures():
                    update_attval(nwlots_lyr, obj, tot_fldname, cont_lot_dic[obj[self.lot_attname]])
                nwlots_lyr.commitChanges()
                
                create_alias(nwlots_lyr, al_map)

                # Add categorized symbology
                self.send_msg(crelyr_msg_txt[8])
                add_cat_symb(nwlots_lyr, self.lot_attname, ramp_c, cat_label)
                
                nwlots_lyr.triggerRepaint()
                
                # End message
                self.send_msg(crelyr_msg_txt[9])
                QMessageBox.information(
                                        self.feedback, 
                                        mnu_fnc1_txt, 
                                        crelyr_msg_txt[9]
                                        )

            except Exception as e:
                self.send_msg(alert_cre_msg_txt[1].format(str(e)))
                QMessageBox.warning(
                                        self.feedback, 
                                        alert_cre_msg_txt[0], 
                                        alert_cre_msg_txt[1].format(str(e))
                                        )
        self.feedback.close()


    def send_msg(self, msg):
        '''
            Send message to the dlg
        '''
        self.feedback.pg_bar.setValue(self.pgb_val)
        self.feedback.update_log(msg)
        self.pgb_val += 1


class MsgWnd(QWidget, gui_dlg_hunting_msg):
    '''
        Manages the message window
    '''

    send_ok = pyqtSignal()

    def __init__(self, parent=None):
        super(MsgWnd, self).__init__(parent)
        self.setupUi(self)
        # Fills title and button text
        self.setWindowTitle(dlg_msg_titles[0])
        self.valid_bt.setText(dlg_msg_buts[0])
        # Initialization of the closing method (False = quit by red cross)
        self.quit_valid = False
        # Deletes Widget on close event
        self.setAttribute(Qt.WA_DeleteOnClose)
        # Connections
        self.valid_bt.clicked.connect(self.butt_ok)


    def butt_ok(self):
        '''
            Closes the window when clicking on the launch button
        '''
        self.quit_valid = True
        self.close()


    def closeEvent(self, event):
        '''
            Sends signal when the window is quit
        '''
        if self.quit_valid:
            self.send_ok.emit()
        else:
            # Hides the window
            self.hide()


    def update_log(self, msg):
        """
            Updates the message zone
        """
        t = self.msg_ted
        t.ensureCursorVisible()
        prefix = '<span style="font-weight:normal;">'
        suffix = '</span>'
        t.append('%s %s %s' % (prefix, msg, suffix))
        c = t.textCursor()
        c.movePosition(QTextCursor.End, QTextCursor.MoveAnchor)
        t.setTextCursor(c)
        qApp.processEvents()
        