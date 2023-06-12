from PyQt6.QtWidgets import (QLabel, QDialog, QVBoxLayout,QHBoxLayout, QCheckBox, QLineEdit,
                                QWidget, QDialogButtonBox, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem)

from PyQt6.QtCore import Qt, QPropertyAnimation, QPointF, QObject, pyqtProperty
from PyQt6.QtGui import QPixmap
from geometry import convertToVirtual
import numpy as np

from matplotlib.backends.qt_compat import QtWidgets
from matplotlib.backends.backend_qtagg import (
    FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure
import time

class MaterialProperties(QDialog):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.setModal(True)
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Material properties')
        self.setMinimumSize(400, 200)
        self.setUpMainWindow()

    def setUpMainWindow(self):
        self.layout = QVBoxLayout()
        
        layout_E = QHBoxLayout()
        label_E = QLabel('E')
        self.edit_E = QLineEdit()

        layout_E.addWidget(label_E)
        layout_E.addWidget(self.edit_E)

        layout_Nu = QHBoxLayout()
        label_Nu = QLabel("Poisson's ratio")
        self.edit_Nu = QLineEdit()

        layout_Nu.addWidget(label_Nu)
        layout_Nu.addWidget(self.edit_Nu)

        layout_sig_f = QHBoxLayout()
        label_sig_f = QLabel('Failure strength')
        self.edit_sig_f = QLineEdit()

        layout_sig_f.addWidget(label_sig_f)
        layout_sig_f.addWidget(self.edit_sig_f)

        layout_density = QHBoxLayout()
        label_density = QLabel('Density')
        self.edit_density = QLineEdit()

        layout_density.addWidget(label_density)
        layout_density.addWidget(self.edit_density)

        layout_c = QHBoxLayout()
        label_c = QLabel('c')
        self.edit_c = QLineEdit()

        layout_c.addWidget(label_c)
        layout_c.addWidget(self.edit_c)

        # layout_dt = QHBoxLayout()
        # label_dt = QLabel('Time step')
        # self.edit_dt = QLineEdit()

        # layout_dt.addWidget(label_dt)
        # layout_dt.addWidget(self.edit_dt)



        # layout_Tt = QHBoxLayout()
        # label_Tt = QLabel('Total time')
        # self.edit_Tt = QLineEdit()

        # layout_Tt.addWidget(label_Tt)
        # layout_Tt.addWidget(self.edit_Tt)

        if self.parent.material_properties:
            self.edit_E.setText(str(self.parent.material_properties['E']))
            self.edit_Nu.setText(str(self.parent.material_properties['Nu']))
            self.edit_density.setText(str(self.parent.material_properties['density']))
            self.edit_sig_f.setText(str(self.parent.material_properties['sig_f']))
            self.edit_c.setText(str(self.parent.material_properties['c']))

        self.buttonbox = QDialogButtonBox(QDialogButtonBox.StandardButton.Apply | QDialogButtonBox.StandardButton.Cancel)
        apply_button = self.buttonbox.button(QDialogButtonBox.StandardButton.Apply)
        apply_button.clicked.connect(self.apply)
        self.buttonbox.rejected.connect(self.reject)

        self.layout.addLayout(layout_E)
        self.layout.addLayout(layout_Nu)
        self.layout.addLayout(layout_sig_f)
        self.layout.addLayout(layout_density)
        self.layout.addLayout(layout_c)
        self.layout.addWidget(self.buttonbox)
        self.setLayout(self.layout)

    def apply(self):
        self.parent.material_properties = {
            'E': float(self.edit_E.text()),
            'Nu': float(self.edit_Nu.text()),
            'density': float(self.edit_density.text()),
            'sig_f': float(self.edit_sig_f.text()),
            'c': float(self.edit_c.text())
        }

        self.hide()

    def reject(self):
        self.hide()
    



class BoundaryAndLoadingDialog(QDialog):

    def __init__(self, parent, set_bounday, set_load):
        super().__init__()
        self.parent = parent
        self.set_boundary, self.set_load = set_bounday, set_load
        self.setModal(True)
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Boundary & Loading')
        self.setMinimumSize(400, 200)
        self.setUpMainWindow()

    def setUpMainWindow(self):

        self.layout = QVBoxLayout()

        boundary_title = QLabel('Boundary')

        self.rigid_boundary_cb = QCheckBox('Set as rigid boundary')
        self.rigid_boundary_cb.toggled.connect(self.setUpLoadEdits)

        loading_title = QLabel('Loading')
        mag_x_layout = QHBoxLayout()
        mag_x_label = QLabel('Fx (N) :')
        self.mag_x_edit = QLineEdit()

        mag_x_layout.addWidget(mag_x_label)
        mag_x_layout.addWidget(self.mag_x_edit)

        mag_y_layout = QHBoxLayout()
        mag_y_label = QLabel('Fy (N) :')
        self.mag_y_edit = QLineEdit()

        mag_y_layout.addWidget(mag_y_label)
        mag_y_layout.addWidget(self.mag_y_edit)

        if self.set_boundary and self.set_boundary[0]['value'] == 1:
            self.rigid_boundary_cb.toggle()

        if self.set_load:
            self.mag_x_edit.setText(str(self.set_load[0]['fx']))
            self.mag_y_edit.setText(str(self.set_load[0]['fy']))
        else:
            self.mag_x_edit.setText('0')
            self.mag_y_edit.setText('0')

        self.buttonbox = QDialogButtonBox(QDialogButtonBox.StandardButton.Apply | QDialogButtonBox.StandardButton.Cancel)
        apply_button = self.buttonbox.button(QDialogButtonBox.StandardButton.Apply)
        apply_button.clicked.connect(self.apply)
        self.buttonbox.rejected.connect(self.reject)

        self.layout.addWidget(boundary_title)
        self.layout.addWidget(self.rigid_boundary_cb)

        self.layout.addWidget(loading_title)
        self.layout.addLayout(mag_x_layout)
        self.layout.addLayout(mag_y_layout)
        self.layout.addWidget(self.buttonbox)
        self.setLayout(self.layout)

    def setUpLoadEdits(self, checked):
        if checked:
            self.mag_x_edit.setEnabled(False)
            self.mag_y_edit.setEnabled(False)
        else:
            self.mag_x_edit.setEnabled(True)
            self.mag_y_edit.setEnabled(True)          

    def apply(self):
        if self.rigid_boundary_cb.checkState() == Qt.CheckState.Checked:
            self.parent.setBoundaryCondition(self.parent.selection['object'], 1)
            self.parent.setLoadingCondition(self.parent.selection['object'], 0, 0)
        else:
            self.parent.setBoundaryCondition(self.parent.selection['object'], 0)
            self.parent.setLoadingCondition(
                self.parent.selection['object'], 
                float(self.mag_x_edit.text()), 
                float(self.mag_y_edit.text())
            )

        self.hide()

        

    def reject(self):
        self.hide()



class AnimationWindow(QtWidgets.QMainWindow):

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.initUI()

    def initUI(self):
        self.setMaximumSize(1000, 1000)
        self.setWindowTitle('Simulation')
        self.setUpMainWindow()
        self.show()
        self.activateWindow()

    def setUpMainWindow(self):
        self._main = QtWidgets.QWidget()
        self.setCentralWidget(self._main)
        layout = QtWidgets.QVBoxLayout(self._main)

        dynamic_canvas = FigureCanvas(Figure(figsize=(5, 3)))
        layout.addWidget(dynamic_canvas)
        layout.addWidget(NavigationToolbar(dynamic_canvas, self))


        self._dynamic_ax = dynamic_canvas.figure.subplots()
        self.frame_number = 0

        self._scatter = self._dynamic_ax.scatter(self.parent.canvas.mesh.points.T[0], self.parent.canvas.mesh.points.T[1], s=2)
        self._timer = dynamic_canvas.new_timer(100)
        self._timer.add_callback(self._update_canvas)
        self._timer.start()

    def _update_canvas(self):
        print(self.frame_number)
        self.frame_number += 1
        if self.parent.edit_frame_interval.text():
            fi = int(self.parent.edit_frame_interval.text())
        else:
            fi = 20

        try:
            self._scatter.set_offsets(self.parent.Positions[self.frame_number*fi])
        except:
            self._timer.stop()

        self._scatter.figure.canvas.draw()

    def closeEvent(self, event):
        self._timer.stop()



class AnimationWindowCrack(QtWidgets.QMainWindow):

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.initUI()

    def initUI(self):
        self.setMaximumSize(1000, 1000)
        self.setWindowTitle('Simulation Crack')
        self.setUpMainWindow()
        self.show()
        self.activateWindow()

    def setUpMainWindow(self):
        self._main = QtWidgets.QWidget()
        self.setCentralWidget(self._main)
        layout = QtWidgets.QVBoxLayout(self._main)

        dynamic_canvas = FigureCanvas(Figure(figsize=(5, 3)))
        layout.addWidget(dynamic_canvas)
        layout.addWidget(NavigationToolbar(dynamic_canvas, self)) 
        
        self._dynamic_ax = dynamic_canvas.figure.subplots()
        self.frame_number = 0

        self.facecolors = np.ones(self.parent.canvas.mesh.cells[1].data.shape[0])

        
        self._tripcolor = self._dynamic_ax.tripcolor(
            self.parent.canvas.mesh.points.T[0], 
            self.parent.canvas.mesh.points.T[1],
            self.parent.canvas.mesh.cells[1].data,
            facecolors=self.facecolors,
            edgecolor='k'
        )
        self.xmin = self.parent.canvas.mesh.points.T[0].min()
        self.xmax = self.parent.canvas.mesh.points.T[0].max()

        self.ymin = self.parent.canvas.mesh.points.T[1].min()
        self.ymax = self.parent.canvas.mesh.points.T[1].max()
        
        self._timer = dynamic_canvas.new_timer(100)
        self._timer.add_callback(self._update_canvas)
        self._timer.start()

    def calculate_sed(self, tn):

        y = self.parent.Positions[tn, self.parent.canvas.mesh.cells[1].data, :].reshape(1, self.parent.Ne, 3, 2)
        y1 = np.roll(y, 1, 2)
        y2 = np.roll(y, 2, 2)

        D_y1_y = y1 - y
        D_y2_y = y2 - y
        D_y2_y_inv = np.roll(D_y2_y, 1, 3)
        prods = D_y1_y*D_y2_y_inv

        Denoms = prods[:, :, :, 0] - prods[:, :, :, 1]

        #derivatives of shape functions

        dNa_dx = -D_y1_y[:, :, 2, 1]/Denoms[:, :, 2]
        dNa_dy = D_y1_y[:, :, 2, 0]/Denoms[:, :, 2]

        dNb_dx = -D_y1_y[:, :, 0, 1]/Denoms[:, :, 0]
        dNb_dy = D_y1_y[:, :, 0, 0]/Denoms[:, :, 0]

        dNc_dx = -D_y1_y[:, :, 1, 1]/Denoms[:, :, 1]
        dNc_dy = D_y1_y[:, :, 1, 0]/Denoms[:, :, 1]

        # del Denoms, prods, D_y1_y, D_y2_y, D_y2_y_inv, y1, y2, y

        dNa_dx = dNa_dx.reshape(1, self.parent.Ne, 1)
        dNa_dy = dNa_dy.reshape(1, self.parent.Ne, 1)
        dNb_dx = dNb_dx.reshape(1, self.parent.Ne, 1)
        dNb_dy = dNb_dy.reshape(1, self.parent.Ne, 1)
        dNc_dx = dNc_dx.reshape(1, self.parent.Ne, 1)
        dNc_dy = dNc_dy.reshape(1, self.parent.Ne, 1)

        z = np.zeros(dNa_dx.shape)

        B = np.concatenate((
            dNa_dx, z, dNb_dx, z, dNc_dx, z,
            z, dNa_dy, z, dNb_dy, z, dNc_dy,
            dNa_dy, dNa_dx, dNb_dy, dNb_dx, dNc_dy, dNc_dx
        ), 2)
        B = B.reshape(1, self.parent.Ne, 3, 6)

        # del dNa_dx, dNa_dy, dNb_dx, dNb_dy, dNc_dx, dNc_dy, z

        epsilon = B[0].reshape(self.parent.Ne*3, 6)@self.parent.u[tn, self.parent.canvas.mesh.cells[1].data, :].reshape(self.parent.Ne, 6).T

        rows = np.arange(0, epsilon.shape[0]).reshape(epsilon.shape[0]//3, 3)
        columns = np.arange(0, epsilon.shape[1])
        columns = np.repeat(columns, 3, axis=0).reshape(epsilon.shape[1], 3)
        epsilon = epsilon[rows, columns].T

        sig = self.parent.D@epsilon

        U = np.diag(0.5*epsilon.T@sig)

        self.facecolors[U>=self.parent.Uc] = 0.4


    def _update_canvas(self):
        print(self.frame_number)
        if self.parent.edit_frame_interval.text():
            fi = int(self.parent.edit_frame_interval.text())
        else:
            fi = 20
        tn = self.frame_number*fi
        # self._dynamic_ax.set_xlim(self.xmin, self.xmax)
        # self._dynamic_ax.set_ylim(self.ymin, self.ymax)
        self.frame_number += 1

        try:
            self.calculate_sed(tn)
            self._dynamic_ax.tripcolor(
                self.parent.Positions[tn].T[0], 
                self.parent.Positions[tn].T[1],
                self.parent.canvas.mesh.cells[1].data,
                facecolors=self.facecolors,
                edgecolor='k'
            )
            self._dynamic_ax.figure.canvas.draw()
            self._dynamic_ax.cla()
        except:
            self._timer.stop()
            
    def closeEvent(self, event):
        self._timer.stop()

        

       

    

        





# class Object(QObject):

#     def __init__(self, image):
#         super().__init__()
#         # point_image = QImage(5, 5 ,QImage.Format.Format_RGBX64)
#         # point_image.fill(Qt.GlobalColor.black)
#         item_pixmap = QPixmap.fromImage(image)
#         self.item = QGraphicsPixmapItem(item_pixmap)

#     def _set_position(self, position):
#         self.item.setPos(position)

#     position = pyqtProperty(QPointF, fset=_set_position)

# class AnimationScene(QGraphicsView):

#     def __init__(self, parent, point_image):
#         super().__init__()
#         self.parent = parent
#         self.point_image = point_image
#         self.initView()

#     def initView(self):
#         self.setMaximumSize(800, 800)
#         self.setWindowTitle('Simulation')

#         self.createObjects()
#         self.createScene()
#         self.show()

    # def setPositions(self, point_anim, positions_xy):
    #     self.points_anim.setDuration(5000)
    #     p = convertToVirtual(self.parent.canvas.scale, self.parent.canvas.translate, self.parent.canvas.mesh.points[i][:2])

    #     self.points_anim[i].setStartValue(QPointF(*p))

    #     for step, positions in enumerate(self.parent.Positions):
    #         p = convertToVirtual(self.parent.canvas.scale, self.parent.canvas.translate, positions[i][:2])
    #         self.points_anim[i].setKeyValueAt(step*self.parent.dt, QPointF(*p))

    #     p = convertToVirtual(self.parent.canvas.scale, self.parent.canvas.translate, self.parent.Positions[-1][i][:2])
    #     self.points_anim[i].setEndValue(QPointF(*p))


    # def createObjects(self):


    #     self.points = np.array([Object(self.point_image) for i in range(self.parent.Np)])
    #     self.points_anim = np.array([QPropertyAnimation(point, b'position') for point in self.points])

    #     for i in range(self.parent.Np):
    #         print(i)
    #         self.points_anim[i].setDuration(5000)
    #         p = convertToVirtual(self.parent.canvas.scale, self.parent.canvas.translate, self.parent.canvas.mesh.points[i][:2])

    #         self.points_anim[i].setStartValue(QPointF(*p))

    #         for step, positions in enumerate(self.parent.Positions):
    #             p = convertToVirtual(self.parent.canvas.scale, self.parent.canvas.translate, positions[i][:2])
    #             self.points_anim[i].setKeyValueAt(step*self.parent.dt, QPointF(*p))

    #         p = convertToVirtual(self.parent.canvas.scale, self.parent.canvas.translate, self.parent.Positions[-1][i][:2])
    #         self.points_anim[i].setEndValue(QPointF(*p))

    #     for point_anim in self.points_anim:
    #         point_anim.setLoopCount(-1)
    #         point_anim.start()

    # def createScene(self):
    #     self.scene = QGraphicsScene(self)
    #     self.scene.setSceneRect(0, 0 , 800, 800)

    #     for point in self.points:
    #         self.scene.addItem(point.item)
    #     self.setScene(self.scene)
    

        
