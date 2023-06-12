from fnmatch import translate
from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import Qt, QPoint, QRect
from PyQt6.QtGui import (QPainter, QPainterPath, QBrush, QPolygon, QPixmap, QPen, QColor, QLinearGradient, QFont)
from geometry import distance2D, convertToVirtual, convertToReal
from math import atan2
from shapely.geometry import Polygon, LineString, Point
from shapely.affinity import affine_transform
from itertools import combinations
from windows import BoundaryAndLoadingDialog
import numpy as np
from itertools import cycle
# from time import sleep

class Canvas(QLabel):

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        width, height = parent.width()//1.2, parent.height()

        self.pixmap = QPixmap(width, height)
        self.pixmap.fill(Qt.GlobalColor.white)
        self.setPixmap(self.pixmap)

        self.mouse_track_label = QLabel()
        self.setMouseTracking(True)

        self.points = []
        self.lines = []
        self.polygons = []
        self.points_drawn = []
        self.lines_drawn = []
        self.point_count = 0
        self.line_count = 0

        self.boundaries_mesh = None
        self.loads_mesh = None
        self.mesh = None
        self.set_loads = []
        self.set_boundaries = []
        

        self.selection = None
        self.previous_selection = None
        

        self.drawing_tool = 'line'
        
        self.drawing = False
        self.drawing_line = False

        self.translate = (self.parent.width()//2, self.parent.height()//2)
        self.scale = 10000

        self.M = np.array([1, 0, 0, -1, -self.parent.width()//2, self.parent.height()//2])/self.scale



    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            mouse_pos = event.pos()
            if self.drawing_tool == 'line' and (not self.drawing_line):
                self.line_first_point = mouse_pos
                self.drawing_line = True
            elif self.drawing_tool == 'line' and self.drawing_line:
                self.line_second_point = mouse_pos
                self.drawOnCanvas()
                self.drawing_line = False           
            else:
                pass


            if self.drawing_tool == 'select' and self.selection == None:
                for line in self.lines_drawn+self.lines:
                    if Point(mouse_pos.x(), mouse_pos.y()).distance(line) < 2:
                        self.selection = {
                            'type': 'line',
                            'object': line
                        }
                        self.drawOnCanvas()
                        break

            elif self.drawing_tool == 'select' and self.selection != None:
                self.previous_selection = self.selection
                self.selection = None
                self.drawOnCanvas()
            else:
                pass



    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            # self.drawing = False
            pass

    def mouseMoveEvent(self, event):
        mouse_pos = event.pos()

        x, y = convertToReal(self.scale, self.translate, (mouse_pos.x(), mouse_pos.y()))

        coords_text = f'Coordinates: {x}, {y}'
        self.mouse_track_label.setVisible(True)
        self.mouse_track_label.setText(coords_text)

        self.parent.status_bar.addWidget(self.mouse_track_label)


                
                


        if(event.buttons() == Qt.MouseButton.LeftButton) and self.drawing:
            # self.drawOnCanvas(mouse_pos)
            pass

    def drawOnCanvas(self):

        if self.drawing_tool == 'line':
            painter = QPainter(self.pixmap)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            pen = QPen(QColor(Qt.GlobalColor.blue), 2)
            painter.setPen(pen)

            draw_first_point = True
            draw_second_point = True

            print('Boo')

            for point in self.points_drawn+self.points:
                print('iter')
                if distance2D(self.line_first_point, point) < 5:
                    print('found')
                    self.line_first_point = QPoint(point.x, point.y)
                    draw_first_point = False

                if distance2D(self.line_second_point, point) < 5:
                    print('found')
                    self.line_second_point = QPoint(point.x, point.y)
                    draw_second_point = False

            if Point(self.line_first_point.x(), self.line_first_point.y()) != Point(self.line_second_point.x(), self.line_second_point.y()):
                print('Line drawn i')

                self.lines.append(LineString([
                    (self.line_first_point.x(), self.line_first_point.y()),
                    (self.line_second_point.x(), self.line_second_point.y())
                ]))

                painter.drawLine(self.line_first_point, self.line_second_point)
                print('Line drawn f')

                pen = QPen(QColor(Qt.GlobalColor.blue), 5)
                painter.setPen(pen)

                if draw_first_point:
                    painter.drawPoint(self.line_first_point)
                    self.points.append(Point(self.line_first_point.x(), self.line_first_point.y()))
                if draw_second_point:
                    painter.drawPoint(self.line_second_point)
                    self.points.append(Point(self.line_second_point.x(), self.line_second_point.y()))

            #Check for self-intersecting polygon 
            # print(len(self.points), len(self.lines))

            if len(self.points) <= len(self.lines):

                #Sort points with lines

                points = []

                current_line = self.lines[0]

                while len(points) < len(self.lines):
                    adjacent_lines = [line for line in self.lines if (line.coords[0] == current_line.coords[0] or line.coords[1] == current_line.coords[0]) and not line.equals(current_line)]
                    
                    if adjacent_lines:
                        adjacent_line = adjacent_lines[0]
                        points.append(current_line.intersection(adjacent_line))
                        current_line = adjacent_line

                self.points = points



                intersections = [l1.intersection(l2) for l1, l2 in combinations(self.lines,2)]
                intersections = [intersection for intersection in intersections if str(type(intersection)).split('.')[-1].split('\'>')[0] == 'Point']

                P = Polygon(self.points)

                self_intersections = [point for point in intersections if point.within(P)]

                if self.parent.edit_scale.text():
                    self.scale = float(self.parent.edit_scale.text())
                    self.M = np.array([1, 0, 0, -1, -self.parent.width()//2, self.parent.height()//2])/self.scale
                else:
                    self.scale = 10000

                Pt = affine_transform(P, self.M)
                self.polygons.append(Pt)
                # print([(p.x, p.y) for p in self.points])
                # print(Pt.exterior.xy)

                if self_intersections:
                    print('Self intersecting')
                else:
                    print('Regular')
                self.points_drawn += self.points
                self.lines_drawn += self.lines
                self.points = []
                self.lines = []

            # print(self.points_drawn, self.points)




        if self.drawing_tool == 'select':
            painter = QPainter(self.pixmap)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)

            if self.selection != None:
                pen = QPen(QColor(Qt.GlobalColor.green), 2)
                painter.setPen(pen)            
                painter.drawLine(QPoint(*self.selection['object'].coords[0]), QPoint(*self.selection['object'].coords[1]))
                self.openBoundaryAndLoadingSetup()
            else:
                pen = QPen(QColor(Qt.GlobalColor.blue), 2)
                painter.setPen(pen) 
                painter.drawLine(QPoint(*self.previous_selection['object'].coords[0]), QPoint(*self.previous_selection['object'].coords[1])) 



        # print(self.lines)


        self.update()

    def selectDrawingTool(self, tool):
        self.drawing_tool = tool

    def drawMesh(self):
        painter = QPainter(self.pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        pen = QPen(QColor(Qt.GlobalColor.red), 1)
        painter.setPen(pen)
        
        for triangle in self.mesh.cells[1].data:
            p0 = QPoint(self.mesh.points.T[0][triangle[0]]*self.scale + self.parent.width()//2, -self.mesh.points.T[1][triangle[0]]*self.scale + self.parent.height()//2)
            p1 = QPoint(self.mesh.points.T[0][triangle[1]]*self.scale + self.parent.width()//2, -self.mesh.points.T[1][triangle[1]]*self.scale + self.parent.height()//2)
            p2 = QPoint(self.mesh.points.T[0][triangle[2]]*self.scale + self.parent.width()//2, -self.mesh.points.T[1][triangle[2]]*self.scale + self.parent.height()//2)

            tri = QPolygon([p0, p1, p2])

            painter.drawPolygon(tri)

        self.update()

    def drawBoundaryPoints(self):
        painter = QPainter(self.pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        pen = QPen(QColor(Qt.GlobalColor.yellow), 5)
        painter.setPen(pen)

        for p1, p2 in self.mesh.cells[0].data:
            painter.drawPoint(QPoint(self.mesh.points.T[0][p1]*self.scale + self.parent.width()//2, -self.mesh.points.T[1][p1]*self.scale + self.parent.height()//2))
            # sleep(3)

        self.update()

    def setBoundaryCondition(self, line, value):
        if self.boundaries_mesh is None:
            self.boundaries_mesh = np.zeros(self.mesh.points.shape)
            self.boundaries_mesh.T[0] = self.mesh.points.T[0]
            self.boundaries_mesh.T[1] = self.mesh.points.T[1]
        
        painter = QPainter(self.pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        pen = QPen(QColor(Qt.GlobalColor.yellow), 5)
        painter.setPen(pen)

        for point in self.boundaries_mesh:
            if Point(*convertToVirtual(self.scale, self.translate, point[:2])).distance(line) < 0.001:
                point[2] = value
                painter.drawPoint(QPoint(*convertToVirtual(self.scale, self.translate, point[:2])))

        boundaries = [boundary for boundary in self.set_boundaries if boundary['boundary'] == line]

        if boundaries:
            boundaries[0]['value'] = value
        else:
            self.set_boundaries.append({
                'boundary': line,
                'value': value
            })

        self.update()

    def setLoadingCondition(self, line, fx, fy): 
        if self.loads_mesh is None:
            self.loads_mesh = np.zeros((self.mesh.points.shape[0], self.mesh.points.shape[1]+1))
            self.loads_mesh.T[0] = self.mesh.points.T[0]
            self.loads_mesh.T[1] = self.mesh.points.T[1]      

        for point in self.loads_mesh:
            if Point(*convertToVirtual(self.scale, self.translate, point[:2])).distance(line) < 0.001:
                point[2] = fx
                point[3] = fy

        loads = [load for load in self.set_loads if load['boundary'] == line]

        if loads:
           loads[0]['fx'] = fx
           loads[0]['fy'] = fy
        else:
            self.set_loads.append({
                'boundary': line,
                'fx': fx,
                'fy': fy
            })

        self.update()

    def resetBoundariesandLoading(self):
        self.boundaries_mesh = None
        self.loads_mesh = None

        self.set_loads = []
        self.set_boundaries = []
        

    def eraseMesh(self):
        painter = QPainter(self.pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        pen = QPen(QColor(Qt.GlobalColor.white), 1)
        painter.setPen(pen)
        
        for triangle in self.mesh.cells[1].data:
            p0 = QPoint(self.mesh.points.T[0][triangle[0]]*self.scale + self.parent.width()//2, -self.mesh.points.T[1][triangle[0]]*self.scale + self.parent.height()//2)
            p1 = QPoint(self.mesh.points.T[0][triangle[1]]*self.scale + self.parent.width()//2, -self.mesh.points.T[1][triangle[1]]*self.scale + self.parent.height()//2)
            p2 = QPoint(self.mesh.points.T[0][triangle[2]]*self.scale + self.parent.width()//2, -self.mesh.points.T[1][triangle[2]]*self.scale + self.parent.height()//2)

            tri = QPolygon([p0, p1, p2])

            painter.drawPolygon(tri)

        self.update()


    def selectDrawingTool(self, tool):
        self.drawing_tool = tool


    def paintEvent(self, event):
        painter = QPainter(self)
        target_rect = event.rect()
        painter.drawPixmap(target_rect, self.pixmap, target_rect)

        painter.end()

    def openBoundaryAndLoadingSetup(self):

        set_boundary = [boundary for boundary in self.set_boundaries if boundary['boundary'] == self.selection['object']]
        set_load = [load for load in self.set_loads if load['boundary'] == self.selection['object']]


        self.bounday_window = BoundaryAndLoadingDialog(self, set_boundary, set_load)
        self.bounday_window.show()


        
