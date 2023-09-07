# -*- coding: utf-8 -*-

"""
    ***************************************************************************
    * Plugin name:   SgmHunting
    * Plugin type:   QGIS 3 plugin
    * Module:        Global Functions
    * Description:   Global functions
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


from qgis.PyQt.QtCore import QDate, QDateTime
from qgis.PyQt.QtGui import QColor
from qgis.core import (QgsFields, QgsGradientStop, QgsCategorizedSymbolRenderer, QgsSymbol, QgsRendererCategory, 
                        QgsGradientColorRamp, QgsExpression, QgsExpressionContext, QgsExpressionContextScope, QgsMessageLog)

import os
import subprocess
import sys
import json
import codecs
import locale


def read_jsparams(plugin_dir, json_name, json_key ):
    '''
        Reads paramaters from json file of paramaters (located in plugin dir)
        json_name = the name of the json file without extension
        json_key = the first key to find the desired parameters
        Returns a tuple with the dict of params and the path of the json file
    '''
    try:
        params_path = os.path.join(plugin_dir, json_name + ".json")
    except IOError as error:
        raise error
    with codecs.open(params_path, encoding='utf-8', mode='r') as json_file:
        json_params = json.load(json_file)
        return (json_params[json_key], params_path)


def save_jsparams(plugin_dir, json_name, json_params):
    '''
        Saves paramaters to json file of paramaters
        json_name = the name of the json file without extension
        json_params = the whole dict of paramaters to save in the json file
    '''
    try:
        params_path = os.path.join(plugin_dir, json_name + ".json")
    except IOError as error:
        raise error
    with codecs.open(params_path, encoding='utf-8', mode='w') as json_file:
            json_file.write(json.dumps(json_params, indent=4, separators=(',', ': '), ensure_ascii=False))



def set_txt_qobj(qobj, val_txt):
    '''
        Fills the qobject (qobj) with the val_txt value
        The 3 last characters of the qobj_name determine the type of qobject:
        cmb -> Combobox
        led -> LineEdit
        pte -> PlainTextEdit
        dte -> DateTimeEdit
        spb -> SpinBox
    '''
    # Case of ComboBox
    qobj_name = qobj.objectName()
    if qobj_name[-3:] == 'cmb':
        cur_idx = qobj.findText(val_txt)
        qobj.setCurrentIndex(cur_idx)
    # Case of LineEdit
    elif qobj_name[-3:] == 'led':
        if not_empty_val(val_txt):
            qobj.setText(unicode(val_txt))
        else:
            qobj.setText('')
    # Case of PlainTextEdit
    elif qobj_name[-3:] == 'pte':
        if not_empty_val(val_txt):
            qobj.setPlainText(unicode(val_txt))
        else:
            qobj.setPlainText('')
    # Case of DateTimeEdit
    elif qobj_name[-3:] == 'dte':
        if not_empty_val(val_txt.toString()):
            if isinstance(val_txt, QDate):
                nw_val_txt = QDateTime()
                nw_val_txt.setDate(val_txt)
            else:
                nw_val_txt = val_txt
            qobj.setDateTime(nw_val_txt)
        else:
            qobj.clear()
    # Case of TimeEdit
    elif qobj_name[-3:] == 'tim':
        if not_empty_val(val_txt.toString()):
            qobj.setTime(val_txt)
        else:
            qobj.clear()
    # Case of SpinBox
    elif qobj_name[-3:] == 'spb':
        if not_empty_val(val_txt):
            qobj.setValue(val_txt)
        else:
            qobj.setValue(0)


def get_txt_qobj(qobj):
    '''
        Retrieves the value of a qobject (qobj) 
        Returns a list of 2 values:
        val1: the text value
        val2: a boolean that is True is the text is not empty
        The 3 last characters of the qobj_name determine the type of qobject:
        cmb -> Combobox
        led -> LineEdit
        pte -> PlainTextEdit
        dte -> DateTimeEdit
        spb -> SpinBox
    '''
    qobj_name = qobj.objectName()
    # Case of ComboBox
    if qobj_name[-3:] == 'cmb':
        return [unicode(qobj.currentText()), True]
    # Case of LineEdit
    elif qobj_name[-3:] == 'led':
        val_txt = qobj.text()
        if not_empty_val(val_txt):
            return [unicode(val_txt), True]
        else:
            return ['', False]
    # Case of PlainTextEdit
    elif qobj_name[-3:] == 'pte':
        val_txt = qobj.toPlainText()
        if not_empty_val(val_txt):
            return [unicode(val_txt), True]
        else:
            return ['', False]
    # Case of DateTimeEdit
    elif qobj_name[-3:] == 'dte':
        val_txt = qobj.dateTime()
        if not_empty_val(val_txt):
            return [val_txt, True]
        else:
            return ['', False]
    # Case of TimeEdit
    elif qobj_name[-3:] == 'tim':
        val_txt = qobj.time()
        if not_empty_val(val_txt):
            return [val_txt, True]
        else:
            return ['', False]
    # Case of SpinBox
    elif qobj_name[-3:] == 'spb':
        val_txt = qobj.value()
        if not_empty_val(val_txt):
            return [val_txt, True]
        else:
            return [0, False]


def not_empty_val(val_2_check):
    '''
        Checks if a value is not empty (NULL or 'NULL' or '')
    '''
    if val_2_check and val_2_check !='' and val_2_check != 'NULL':
        return True
    else:
        return False


def merge_fields(*args):
    '''
        Merges several QgsFields
    '''
    nw_flds = QgsFields()
    for flds in args:
        for fld in flds:
            nw_flds.append(fld)
    return nw_flds


def update_attval(lyr, obj, att_name, nw_val):
    '''
        Updates attribute value of an obj in lyr
    '''
    id_att = obj.fieldNameIndex(att_name)
    id_obj = obj.id()
    lyr.changeAttributeValue(id_obj, id_att, nw_val)


def get_lst_lyr_fld_values(lyr):
    '''
        Returns a dictionnary containing, for each field of a specific layer, 
        a list of all the distinct values
    '''
    att_val_dic = {}
    atts = get_layer_fields(lyr)
    for obj in lyr.getFeatures():
        for att in atts:
            if att in att_val_dic:
                # val_lst = att_val_dic[att].split(lst_sep)
                if str(obj[att]) not in att_val_dic[att]:
                    att_val_dic[att].append(str(obj[att]))
                    att_val_dic[att].sort(key=locale.strxfrm)
            else:
                att_val_dic[att] = []
                att_val_dic[att].append(str(obj[att]))
    return att_val_dic


def add_cat_symb(lyr, att_name, ramp_colors, label):
    '''
        Adds a categarized symbology
        lyr: layer to symbologize
        att_name: name of attribute to use for categorization
        ramp_colors: list of colors ('#hexa' colors) for the ramp
        label: string using {0:s} to determine categories labels
    '''
    val_lst = get_lst_lyr_fld_values(lyr)[att_name]
    nb_cat = len(val_lst)
    nb_stop = len(ramp_colors)
    sp_stops = []
    for i in range(1, nb_stop):
        nw_stop = QgsGradientStop(i * 1 / (nb_stop -1), QColor(ramp_colors[i]))
        sp_stops.append(nw_stop)
    sp_ramp = QgsGradientColorRamp(QColor(ramp_colors[0]), QColor(ramp_colors[-1]), False, sp_stops)
    nw_rend = QgsCategorizedSymbolRenderer(att_name)
    for cat_id, val in enumerate(val_lst):
        symb = QgsSymbol.defaultSymbol(lyr.geometryType())
        rd_color = sp_ramp.color(cat_id / (nb_cat - 1))
        symb.setColor(rd_color)
        cat = QgsRendererCategory(val, symb, label.format(val))
        nw_rend.addCategory(cat)
    lyr.setRenderer(nw_rend)


def move_lyr_to_top(project, lyr):
    '''
        Moves layer to the top of legend list
    '''
    lt_root = project.layerTreeRoot()
    lt_lyr = lt_root.findLayer(lyr)
    lt_root.insertChildNode(0, lt_lyr.clone())
    lt_lyr.parent().removeChildNode(lt_lyr)


def get_fldval_sorted(lyr, att_name):
    '''
        Returns sorted list of values of a field
    '''
    val_lst = []
    for obj in lyr.getFeatures():
        val_lst.append(obj[att_name])
    return sorted(val_lst, key=locale.strxfrm)


def transfo_m_to_ha(surf_m2):
    '''
        Transforms a surface in m² into a surface in ha a ca
    '''
    hectare = int(surf_m2 // 10000)
    surf_m2 -= hectare * 10000
    are = int(surf_m2 // 100)
    centiare = int(surf_m2 % 100)
    return f"{hectare}ha {are}a {centiare}ca"


def open_file(filename):
    '''
    Opens a file with default system app
    '''
    if sys.platform == "win32":
        os.startfile(filename)
    else:
        opener ="open" if sys.platform == "darwin" else "xdg-open"
        subprocess.call([opener, filename]) 


def get_val_by_expr(expr_val, lyr, obj):
    '''
        Returns the value calculated with an expression
        expr_val: expression to use (text)
        lyr: layer in which apply the expression
        obj: object to use to calculate
    '''
    nw_val = None
    expr = QgsExpression(expr_val)
    ctx = QgsExpressionContext()
    scp = QgsExpressionContextScope()
    scp.setFields(lyr.fields())
    ctx.appendScope(scp)
    ctx.setFeature(obj)
    nw_val = expr.evaluate(ctx)
    return nw_val


def getmulti_fields_values_from_one_value(lyr, find_val, in_att, cond_val, cond_fld):
    '''
        Returns a list of dictionnaries containing all the attribute values of a specific feature
        The specific feature is given by the value (find_val) of one attribute (in_att)
        respecting the condition cond_fld = cond_val
        If cond_fld == '', no condition (all the values of the field)
        The list contains the different features found respecting those rules
    '''
    obj_lst = []
    for obj in lyr.getFeatures():
        att_val_dic = {}
        if cond_fld != '':
            if obj[in_att] == find_val and obj[cond_fld] == cond_val:
                atts = get_layer_fields(lyr)
                for att in atts:
                    att_val_dic[att] = obj[att]
                obj_lst.append(att_val_dic)
        else:
            if obj[in_att] == find_val:
                atts = get_layer_fields(lyr)
                for att in atts:
                    att_val_dic[att] = obj[att]
                obj_lst.append(att_val_dic)
    return obj_lst


def get_layer_fields(layer):
    '''
        Return sorted list of fields of a layer instance
    '''
    fld_lst = []
    for field in layer.fields():
        fld_lst.append(field.name())
    return sorted(fld_lst, key=locale.strxfrm)


def as_text(value):
    '''
        Transforms a value in a string
    '''
    if value is None:
        return ""
    return str(value)


def create_alias(lyr, alias_map):
    '''
        Create aliases on lyr (if field att_name exists)
        alias_map: list of [att_name, att_alias]
    '''
    for fld in alias_map:
        fld_idx = lyr.fields().indexFromName(fld[0])
        if fld_idx != -1 and fld[1] != '':
            lyr.setFieldAlias(fld_idx, fld[1])


def get_layer_fields_alias(lyr):
    '''
        For a layer (lyr), returns a list of [field_name, alias]
    '''
    fld_lst = []
    for field in lyr.fields():
        fld_lst.append([field.name(), field.alias()])
    return fld_lst


def debug_msg(debug_on_off, msg_str, msg_list_var):
    '''
        Shows the debug messages
        Usage: 
        debug_msg('DEBUG', "var1: %s, - var2: %s" , (str(var1), str(var2)))
    '''
    if debug_on_off == 'DEBUG':
        msg = msg_str % msg_list_var
        QgsMessageLog.logMessage(msg, 'Sgm debug')