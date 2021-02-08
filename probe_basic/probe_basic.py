#!/usr/bin/env python

import os

from qtpy.QtCore import Slot, QRegExp
from qtpy.QtGui import QFontDatabase, QRegExpValidator
from qtpy.QtWidgets import QAbstractButton

from qtpyvcp import actions, plugins
from qtpyvcp.utilities import logger
from qtpyvcp.widgets.form_widgets.main_window import VCPMainWindow

import probe_basic_rc

import run_from_line as rfl

import linuxcnc

LOG = logger.getLogger('QtPyVCP.' + __name__)
VCP_DIR = os.path.abspath(os.path.dirname(__file__))
STATUS = plugins.status.Status()
TOOLTABLE = plugins.tool_table.ToolTable()
COMMAND = linuxcnc.command()
STAT = linuxcnc.stat()

# Add custom fonts
QFontDatabase.addApplicationFont(os.path.join(VCP_DIR, 'fonts/BebasKai.ttf'))

class ProbeBasic(VCPMainWindow):
    """Main window class for the ProbeBasic VCP."""
    def __init__(self, *args, **kwargs):
        super(ProbeBasic, self).__init__(*args, **kwargs)
        self.run_from_line_Num.setValidator(QRegExpValidator(QRegExp("[0-9]*")))

    @Slot(QAbstractButton)
    def on_probetabGroup_buttonClicked(self, button):
        self.probe_tab_widget.setCurrentIndex(button.property('page'))

    @Slot(QAbstractButton)
    def on_guiaxisdisplayGroup_buttonClicked(self, button):
        self.gui_axis_display_widget.setCurrentIndex(button.property('page'))


    # Fwd/Back buttons off the stacked widget
    def on_probe_help_next_released(self):
        lastPage = 7
        currentIndex = self.probe_help_widget.currentIndex()
        if currentIndex == lastPage:
            self.probe_help_widget.setCurrentIndex(0)
        else:
            self.probe_help_widget.setCurrentIndex(currentIndex + 1)

    def on_probe_help_prev_released(self):
        lastPage = 7
        currentIndex = self.probe_help_widget.currentIndex()
        if currentIndex == 0:
            self.probe_help_widget.setCurrentIndex(lastPage)
        else:
            self.probe_help_widget.setCurrentIndex(currentIndex - 1)

    @Slot(QAbstractButton)
    def on_probemodeGroup_buttonClicked(self, button):
        if button.isChecked():
            self.probe_mode.setText(button.property('checkedAction'))

    def on_set_wco_offset_Btn_clicked(self):
        if self.set_wco_offset_Btn.isChecked():
            self.wco_rotation.setText('1')
        else:
            self.wco_rotation.setText('0')

    def on_tool_diameter_probe_Btn_clicked(self):
        if self.tool_diameter_probe_Btn.isChecked():
            self.tool_diameter_probe_mode.setText('1')
        else:
            self.tool_diameter_probe_mode.setText('0')

    def on_tool_diameter_offset_Btn_clicked(self):
        if self.tool_diameter_offset_Btn.isChecked():
            self.tool_diameter_offset_mode.setText('1')
        else:
            self.tool_diameter_offset_mode.setText('0')

    @Slot(QAbstractButton)
    def on_xycalbtnGroup_buttonClicked(self, button):
        if button.isChecked():
            self.sq_cal_axis.setText(button.property('checkedAction'))

    @Slot(QAbstractButton)
    def on_fileviewerbtnGroup_buttonClicked(self, button):
        self.file_viewer_widget.setCurrentIndex(button.property('page'))

    @Slot(QAbstractButton)
    def on_guiaxisdisplayGroup_buttonClicked(self, button):
        self.gui_axis_display_widget.setCurrentIndex(button.property('page'))

    def on_run_from_line_Btn_clicked(self):
        curFile = STATUS.file()
        curTools = TOOLTABLE.tool_table_file
        #curINI = 
        #curVars = 
        
        if curFile == "No file loaded":
            return False

        try:
            lineNum = int(self.run_from_line_Num.text())
        except:
            return False
        
        pos = rfl.getEndPos(curFile, curTools, lineNum-1)
        STAT.poll()
        
        if STAT.interp_state == linuxcnc.INTERP_IDLE:
            COMMAND.mode(linuxcnc.MODE_MDI)
            COMMAND.wait_complete(1)
            COMMAND.mdi("G0 X{0}Y{1}Z{2}A{3}B{4}".format(*pos))
            COMMAND.wait_complete(30)

        actions.program_actions.run(lineNum)

