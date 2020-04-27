#!/usr/bin/python3
"""Mainwindow for app

Copyright (c) 2020 lileilei <hustlei@sina.cn>
"""

import os

from PyQt5.QtCore import Qt, QModelIndex, QMetaEnum
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QFileDialog, QAbstractItemView, QItemDelegate, QInputDialog, QDialog, QLabel, QFormLayout, \
    QSpinBox, QDialogButtonBox, QGroupBox, QVBoxLayout, QHBoxLayout, QComboBox, QDoubleSpinBox

from core.graphicsView import GraphDigitGraphicsView
from .enums import OpMode
from .mainwinbase import MainWinBase
from .utils import nextName
from .widgets.custom import QLineComboBox


class MainWin(MainWinBase):
    def __init__(self):
        super(MainWin, self).__init__()
        # 图形控件
        self.view = GraphDigitGraphicsView()  # 创建视图窗口
        self.mainTabWidget.addTab(self.view, "main")

        # actions
        self.view.sigMouseMovePoint.connect(self.slotMouseMovePoint)
        self.setupActions()

    def slotMouseMovePoint(self, pt, ptscene):
        self.updatePixelCoordStatus(pt.x(), pt.y())
        self.updatePointCoordStatus(ptscene)

    # action funcs
    def new(self):
        """create new GraphDigitGrapicsView"""
        self.view = GraphDigitGraphicsView()

    def importimage(self, file=None):  # _参数用于接收action的event参数,bool类型
        if not file:
            file, _ = QFileDialog.getOpenFileName(
                self, self.tr("Import Image"), "",
                "Images (*.png *.jpg *.jpep *.gif);;Bitmap Image(*.bmp *.xpm *.xbm *.pbm *.pgm);;all(*.*)"
            )  # _是filefilter
        if os.path.exists(file):
            self.statusbar.showMessage(self.tr("importing image..."))
            ok = self.view.setGraphImage(file)
            if ok:
                self.statusbar.showMessage(self.tr("import successfully"))
            else:
                self.statusbar.showMessage(self.tr("import failed"))
        else:
            self.statusbar.showMessage(self.tr("image file not found."))

    def zoom(self, factor=1):
        self.view.scale(factor, factor)

    def changeMode(self, mode, checked):
        if not checked:
            self.view.mode = OpMode.default
        else:
            lastmode = self.view.mode
            self.view.mode = mode
            if lastmode != OpMode.default:
                self.actions[lastmode.name].setChecked(False)
        if self.view.mode == OpMode.default or self.view.mode == OpMode.select:
            self.view.setCursor(Qt.ArrowCursor)
            self.view.showAxes(False)
        else:
            self.view.setCursor(Qt.CrossCursor)
            if self.view.mode == OpMode.axesx or self.view.mode == OpMode.axesy:
                self.view.showAxes(True)
            else:
                self.view.showAxes(False)

    def tst(self):
        print("test")

    def setupActions(self):
        self.actions["import"].triggered.connect(self.importimage)
        self.actions["export"].triggered.connect(self.export)
        self.actions["close"].triggered.connect(self.new)

        self.actions["del"].triggered.connect(self.view.deleteSelectedPoint)

        self.actions["select"].triggered.connect(lambda x: self.changeMode(OpMode.select, x))
        self.actions["axesx"].triggered.connect(lambda x: (self.changeMode(OpMode.axesx, x)))
        self.actions["axesy"].triggered.connect(lambda x: (self.changeMode(OpMode.axesy, x)))
        self.actions["curve"].triggered.connect(lambda x: self.changeMode(OpMode.curve, x))
        self.actions["zoomin"].triggered.connect(lambda: self.zoom(1.1))
        self.actions["zoomout"].triggered.connect(lambda: self.zoom(0.9))
        self.actions["showgrid"].triggered.connect(self.view.showGrid)

        self.actions["undo"].setEnabled(False)
        self.actions["redo"].setEnabled(False)

        self.actions["scalegraph"].triggered.connect(self.scalegraph)
        self.actions["gridsetting"].triggered.connect(self.gridsetting)

        self.axesxTable.setModel(self.view.axesxModel)
        self.axesyTable.setModel(self.view.axesyModel)
        self.curveTable.setModel(self.view.curveModel)
        self.pointsTable.setModel(self.view.pointsModel)
        self.axesxTable.setColumnWidth(0, 120)
        self.axesxTable.setColumnWidth(1, 100)
        self.axesyTable.setColumnWidth(0, 120)
        self.axesyTable.setColumnWidth(1, 100)
        self.curveTable.setColumnWidth(0, 45)
        self.curveTable.setColumnWidth(1, 120)
        self.curveTable.setColumnWidth(2, 45)
        self.pointsTable.setColumnWidth(0, 45)
        self.pointsTable.setColumnWidth(1, 80)
        self.pointsTable.setColumnWidth(2, 80)

        class ReadOnlyDelegate(QItemDelegate):
            def __init__(self, parent):
                super().__init__(parent)

            def createEditor(self, QWidget, QStyleOptionViewItem, QModelIndex):
                return None

        self.axesxTable.setItemDelegateForColumn(0, ReadOnlyDelegate(self.axesxTable))
        self.axesyTable.setItemDelegateForColumn(0, ReadOnlyDelegate(self.axesyTable))
        self.curveTable.setItemDelegateForColumn(1, ReadOnlyDelegate(self.curveTable))
        self.axesxTable.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.axesxTable.setSelectionMode(QAbstractItemView.SingleSelection)
        self.axesyTable.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.axesyTable.setSelectionMode(QAbstractItemView.SingleSelection)
        self.curveTable.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.curveTable.setSelectionMode(QAbstractItemView.SingleSelection)

        def selectedCurve():
            name = None
            try:
                name = self.view.curveModel.item(self.curveTable.selectedIndexes()[0].row(), 1).text()
            except:
                pass
            return name

        self.actions["addcurve"].triggered.connect(lambda: self.view.addCurve(nextName(selectedCurve())))
        self.actions["renamecurve"].triggered.connect(lambda: self.view.renameCurve(name=selectedCurve()))

        def changecurve(index):
            if index.column() == 0:
                for i in range(self.view.curveModel.rowCount()):
                    if i == index.row():
                        self.view.curveModel.item(i, 0).switch(True)
                        self.view.changeCurrentCurve(self.view.curveModel.item(i, 1).text())
                    else:
                        self.view.curveModel.item(i, 0).switch(False)

        self.curveTable.doubleClicked.connect(changecurve)
        # self.pointsTable.mov

    def scalegraph(self):
        scale,ok = QInputDialog.getDouble(self, self.tr("scale the graph"),
                                           self.tr("set the scale value:"), 1, 0.01, 100, 2)
        if ok:
            self.view.resizeGraphImage(scale)

    def gridsetting(self):
        dialog=QDialog(self)
        layout=QVBoxLayout(dialog)

        xgroup=QGroupBox(self.tr("grid parameter for axis x"),self)
        form=QFormLayout(xgroup)
        spinboxxmin = QDoubleSpinBox(dialog)
        spinboxxmax = QDoubleSpinBox(dialog)
        spinboxxstep = QDoubleSpinBox(dialog)
        spinboxxmin.setValue(0)
        spinboxxmax.setValue(1)
        spinboxxstep.setValue(0.1)
        form.addRow(self.tr("minimum value:"), spinboxxmin)
        form.addRow(self.tr("maximum value:"), spinboxxmax)
        form.addRow(self.tr("step value:"), spinboxxstep)

        ygroup=QGroupBox(self.tr("grid parameter for axis y"),self)
        form=QFormLayout(ygroup)
        spinboxymin = QDoubleSpinBox(dialog)
        spinboxymax = QDoubleSpinBox(dialog)
        spinboxystep = QDoubleSpinBox(dialog)
        spinboxymin.setValue(0)
        spinboxymax.setValue(1)
        spinboxystep.setValue(0.1)
        form.addRow(self.tr("minimum value:"), spinboxymin)
        form.addRow(self.tr("maximum value:"), spinboxymax)
        form.addRow(self.tr("step value:"), spinboxystep)

        hbox1=QHBoxLayout()
        hbox1.addWidget(xgroup)
        hbox1.addWidget(ygroup)
        hbox2=QHBoxLayout()
        spinboxWidth = QSpinBox(dialog)
        spinboxWidth.setValue(1)
        lineCombo = QLineComboBox()
        lineCombo.addItem(self.tr("SolidLine"),Qt.SolidLine)
        lineCombo.addItem(self.tr("DashLine"),Qt.DashLine)
        lineCombo.addItem(self.tr("DotLine"),Qt.DotLine)
        lineCombo.addItem(self.tr("DashDotLine"),Qt.DashDotLine)
        lineCombo.addItem(self.tr("DashDotDotLine"),Qt.DashDotDotLine)
        lineCombo.setCurrentIndex(1)
        colorCombo = QComboBox()
        colorCombo.addItems(QColor.colorNames())
        colorCombo.setCurrentText("red")
        hbox2.addWidget(QLabel("GridWidth"))
        hbox2.addWidget(spinboxWidth)
        hbox2.addWidget(QLabel("LineType"))
        hbox2.addWidget(lineCombo)
        hbox2.addWidget(QLabel("LineColor"))
        hbox2.addWidget(colorCombo)

        buttonBox=QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, Qt.Horizontal, dialog)

        layout.addLayout(hbox1)
        layout.addLayout(hbox2)
        layout.addWidget(buttonBox)

        buttonBox.accepted.connect(dialog.accept)
        buttonBox.rejected.connect(dialog.reject)

        if dialog.exec() == QDialog.Accepted:
            self.view.datas.gridx=[spinboxxmin.value(),spinboxxmax.value(),spinboxxstep.value()]
            self.view.datas.gridy=[spinboxymin.value(),spinboxymax.value(),spinboxystep.value()]
            self.view.datas.gridLineWidth=spinboxWidth.value()
            self.view.datas.gridColor=QColor(colorCombo.currentText())
            self.view.datas.gridLineType=lineCombo.currentData()

    def export(self, file=None):
        if not file:
            file, _ = QFileDialog.getSaveFileName(self, self.tr("Export Curves"), "",
                                                  "CSV (*.csv);;all(*.*)")  # _是filefilter
        if file:
            with open(file, "w", encoding="utf8") as f:
                f.write(self.view.exportToCSVtext())
            self.statusbar.showMessage(self.tr("export successfully."))
        else:
            self.statusbar.showMessage(self.tr("export failure."))
