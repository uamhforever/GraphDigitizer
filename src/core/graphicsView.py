import os

from PyQt5.QtCore import pyqtSignal, QRectF, QPoint, QPointF, Qt
from PyQt5.QtGui import QCursor, QPainterPath
from PyQt5.QtWidgets import (QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsPixmapItem, QGraphicsItem,
                             QGraphicsEllipseItem, QGraphicsPathItem)
from core.enums import OpMode, PointType
from core.graphicsItems import QGraphicsPointItem
from core.project import Datas
from core.dialogs.pick import Axesdialog


class GraphDigitGraphicsView(QGraphicsView):
    sigMouseMovePoint = pyqtSignal(QPoint, QPointF)

    # 自定义信号sigMouseMovePoint，当鼠标移动时，在mouseMoveEvent事件中，将当前的鼠标位置发送出去
    # QPoint--传递的是view坐标
    def __init__(self, parent=None):
        super(GraphDigitGraphicsView, self).__init__(parent)
        self.initView()
        self.mode = OpMode.default
        # data manage
        self.datas = Datas()
        # item objects storage
        self.axesPts = []
        self.gridLines = {}
        self.curveObjs = {}
        self.curvepts = {}

    def initView(self):
        # scene
        rect = QRectF(0, 0, 800, 600)
        self.scene = QGraphicsScene(rect)  # 创建场景 参数：场景区域
        self.setScene(self.scene)  # 给视图窗口设置场景
        # image
        self.graphicsPixmapItem = QGraphicsPixmapItem()  # chart image
        self.scene.addItem(self.graphicsPixmapItem)

        # test

        # for pos,color in zip([rect.left(),0,rect.right()],[Qt.red,Qt.yellow,Qt.blue]):
        #     item=QGraphicsEllipseItem(-50,-50,100,100)  #创建椭圆--场景坐标
        #     #参数1 参数2  矩形左上角坐标
        #     #参数3 参数4 矩形的宽和高
        #     item.setPos(pos,0)  #给图元设置在场景中的坐标(移动图元)--图元中心坐标
        #     item.setBrush(color)  #设置画刷
        #     item.setFlags(QGraphicsItem.ItemIsSelectable|QGraphicsItem.ItemIsFocusable|QGraphicsItem.ItemIsMovable)
        #     self.scene.addItem(item)

    def setGraphImage(self, imgfile):
        if os.path.exists(imgfile):
            self.datas.setImgpath(imgfile)
            self.graphicsPixmapItem.setPixmap(self.datas.img)
            self.scene.clearSelection()  # 【清除选择】
            return True
        else:
            return False

    def mouseMoveEvent(self, evt):
        pt = evt.pos()  # 获取鼠标坐标--view坐标
        self.sigMouseMovePoint.emit(pt, self.mapToScene(pt))  # 发送鼠标位置
        QGraphicsView.mouseMoveEvent(self, evt)
        # self.setDragMode(QGraphicsView.NoDrag) #(RubberBandDrag) #ScrollHandDrag) #NoDrag)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self.__pressPt = event.pos()

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        ptscene = self.mapToScene(event.pos())
        # item = self.scene.itemAt(ptscene, self.transform())
        clicked = True if event.pos() == self.__pressPt else False
        if self.mode is OpMode.select:
            pass
            # super().mousePressEvent(event)
        elif self.mode is OpMode.axes:
            item = QGraphicsPointItem()
            item.pointType = PointType.plus
            item.linewidth = 2
            item.setPos(ptscene)
            self.scene.addItem(item)
            item.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsFocusable | QGraphicsItem.ItemIsMovable)

            (x, y) = Axesdialog.getCoord()
            if x or y:
                if x:
                    self.datas.axisx[ptscene.x()] = x
                if y:
                    self.datas.axisy[ptscene.y()] = y
                self.axesPts.append(item)
                item.setFocus(True)
            else:
                self.scene.removeItem(item)
        elif self.mode is OpMode.curve and clicked:
            ptitem = QGraphicsPointItem()
            ptitem.pointColor = Qt.blue
            ptitem.linewidth = 1
            ptitem.setPos(ptscene)
            ptitem.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsFocusable | QGraphicsItem.ItemIsMovable)
            self.scene.addItem(ptitem)

            if self.datas.currentCurve not in self.curvepts:
                self.curvepts[self.datas.currentCurve] = []
            self.curvepts[self.datas.currentCurve].append(ptitem)
            self.datas.curves[self.datas.currentCurve].points.append(QPointF(ptscene))
            self.updateCurve(self.datas.currentCurve)
            self.sigMouseMovePoint.emit(event.pos(), ptscene)

        # item1=QGraphicsRectItem(rect)  #创建矩形---以场景为坐标
        # item1.setFlags(QGraphicsItem.ItemIsSelectable|QGraphicsItem.ItemIsFocusable|QGraphicsItem.ItemIsMovable)  #给图元设置标志
        # QGraphicsItem.ItemIsSelectable---可选择
        # QGraphicsItem.ItemIsFocusable---可设置焦点
        # QGraphicsItem.ItemIsMovable---可移动
        # QGraphicsItem.ItemIsPanel---
        # self.scene.addItem(item1)  #给场景添加图元

    def updateCurve(self, name):
        if name in self.curveObjs:
            item = self.curveObjs[name]
        else:
            item = QGraphicsPathItem()
            self.scene.addItem(item)
        path = QPainterPath()
        curve = self.datas.curves[name]
        if len(curve.points) > 0:
            path.moveTo(curve.points[0])
        for pt in curve.points[1:]:
            path.lineTo(pt)
        item.setPath(path)
