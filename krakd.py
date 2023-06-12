from PyQt6.QtWidgets import QApplication, QMainWindow, QToolBar, QDockWidget, QStatusBar, QLineEdit, QLabel, QMessageBox
from PyQt6.QtGui import QAction, QImage
from PyQt6.QtCore import Qt, QSize
from canvas import Canvas
import pygmsh, sys, math
from utils import calculateParticlePostions, ModelWorker, AnimationWorker
from windows import AnimationWindow, AnimationWindowCrack, MaterialProperties
import numpy as np



class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.material_properties = None
        self.initUI()
    def initUI(self):
        self.setMinimumSize(1200, 600)

        self.setWindowTitle('krakd')
        self.setUpMainWindow()
        self.createActions()
        self.createMenu()
        self.creatToolBar()
        self.createObjectDockWidget()
        self.show()

    def createActions(self):

        #file

        self.new_act = QAction('New')
        self.new_act.setShortcut('Ctrl+N')

        self.open_act = QAction('Open')
        self.open_act.setShortcut('Ctrl+O')

        self.save_act = QAction('Save')
        self.save_act.setShortcut('Ctrl+S')

        self.quit_act = QAction('Quit')
        self.quit_act.setShortcut('Ctrl+Q')

        #edit
        self.undo_act = QAction('Undo')
        self.undo_act.setShortcut('Ctrl+Z')       

        self.redo_act = QAction('Redo')
        self.redo_act.setShortcut('Ctrl+Shift+Z')

        self.cut_act = QAction('Cut')
        self.cut_act.setShortcut('Ctrl+X')

        self.copy_act = QAction('Copy')
        self.copy_act.setShortcut('Ctrl+C')

        self.paste_act = QAction('Paste')
        self.paste_act.setShortcut('Ctrl+V')

        #view

        # self.grid_act = QAction('Grid')

        #draw
        self.select_act = QAction('Select')
        self.select_act.triggered.connect(lambda: self.canvas.selectDrawingTool('select'))

        self.point_act = QAction('Point')  

        self.line_act = QAction('Line')
        self.line_act.triggered.connect(lambda: self.canvas.selectDrawingTool('line'))

        self.circle_act = QAction('Circle')
        self.rect_act = QAction('Rectangle')
        self.polygon_act = QAction('Polygon')

        #model

        self.mesh_act = QAction('Mesh')
        self.mesh_act.triggered.connect(self.mesh)

        self.material_properties_dialog_act = QAction('Material')
        self.material_properties_dialog_act.triggered.connect(self.open_material_properties_dialog)

        #simulation
        self.run_act = QAction('Run')
        self.run_act.triggered.connect(self.evaluatePositions)

        self.sim_playParticleSim_act = QAction('Play--Particles')
        self.sim_playParticleSim_act.triggered.connect(self.playSimulation_particle)

        self.sim_playCrackSim_act = QAction('Play--Crack')
        self.sim_playCrackSim_act.triggered.connect(self.playSimulation_crack)

    def createMenu(self):
        self.menuBar().setNativeMenuBar(False)
        file_menu = self.menuBar().addMenu('File')
        file_menu.addAction(self.new_act)
        file_menu.addAction(self.open_act)
        file_menu.addAction(self.save_act)
        file_menu.addAction(self.quit_act)

        edit_menu = self.menuBar().addMenu('Edit')
        edit_menu.addAction(self.undo_act)
        edit_menu.addAction(self.redo_act)
        edit_menu.addAction(self.cut_act)
        edit_menu.addAction(self.copy_act)
        edit_menu.addAction(self.paste_act)

        view_menu = self.menuBar().addMenu('View')

        draw_menu = self.menuBar().addMenu('Draw')
        draw_menu.addAction(self.select_act)
        draw_menu.addAction(self.point_act)
        draw_menu.addAction(self.line_act)
        draw_menu.addAction(self.circle_act)
        draw_menu.addAction(self.rect_act)
        draw_menu.addAction(self.polygon_act)

        model_menu = self.menuBar().addMenu('Model')
        model_menu.addAction(self.mesh_act)
        model_menu.addAction(self.material_properties_dialog_act)

        sim_menu = self.menuBar().addMenu('Simulation') 
        sim_menu.addAction(self.run_act)
        sim_menu.addAction(self.sim_playParticleSim_act)
        sim_menu.addAction(self.sim_playCrackSim_act)


    def creatToolBar(self):

        tool_bar = QToolBar('Tools')
        tool_bar.setIconSize(QSize(24, 24))

        self.edit_dt = QLineEdit()
        self.edit_dt.setMaximumWidth(75)

        label_dt = QLabel('Time step : ')

        tool_bar.addWidget(label_dt)
        tool_bar.addWidget(self.edit_dt)

        label_total_time = QLabel('Total time : ')
        self.edit_total_time = QLineEdit()
        self.edit_total_time.setMaximumWidth(75)

        tool_bar.addWidget(label_total_time)
        tool_bar.addWidget(self.edit_total_time)

        label_frame_interval = QLabel('Frame interval : ')
        self.edit_frame_interval = QLineEdit()
        self.edit_frame_interval.setMaximumWidth(75)

        tool_bar.addWidget(label_frame_interval)
        tool_bar.addWidget(self.edit_frame_interval)

        label_mesh_size = QLabel('Mesh size : ')
        self.edit_mesh_size = QLineEdit()
        self.edit_mesh_size.setMaximumWidth(75)

        tool_bar.addWidget(label_mesh_size)
        tool_bar.addWidget(self.edit_mesh_size)

        label_scale = QLabel('Scale : ')
        self.edit_scale = QLineEdit()
        self.edit_scale.setMaximumWidth(75)

        tool_bar.addWidget(label_scale)
        tool_bar.addWidget(self.edit_scale)

        self.sim_label = QLabel('')

        tool_bar.addWidget(self.sim_label)


        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, tool_bar)

    def createObjectDockWidget(self):
        g_objects = QDockWidget()
        g_objects.setWindowTitle('Geometrical objects')
        g_objects.setMinimumSize(int(self.width()*0.2/1.2), self.height())
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, g_objects)

    def mesh(self):
        if(self.canvas.mesh != None):
            self.canvas.eraseMesh()

        self.canvas.polygons.sort(key=lambda P: P.area, reverse=True)
        if self.edit_mesh_size.text():
            self.mesh_size = float(self.edit_mesh_size.text())
        else:
            self.mesh_size = 0.1


        # points = [[(point[0] - self.width()//2)/self.canvas.scale, (-point[1] + self.height()//2)/self.canvas.scale] for point in list(zip(*self.canvas.polygons[0].exterior.xy))[:-1]]
        # print(points)
        # print(list(zip(*self.canvas.polygons[0].exterior.xy)))

        
        with pygmsh.occ.Geometry() as geom:
            outer_boundary = geom.add_polygon(list(zip(*self.canvas.polygons[0].exterior.xy))[:-1], mesh_size=self.mesh_size)
            if len(self.canvas.polygons)==1:
                pass
            elif len(self.canvas.polygons)==2:
                inner_boundary = geom.add_polygon(list(zip(*self.canvas.polygons[1].exterior.xy))[:-1], mesh_size=self.mesh_size)
                plate = geom.boolean_difference(outer_boundary, inner_boundary)
            else:
                inner_boundaries = []
                for P in self.canvas.polygons[1:]:
                    print(inner_boundaries, P)
                    print(list(zip(*P.exterior.xy)))
                    inner_boundaries.append(geom.add_polygon(list(zip(*P.exterior.xy))[:-1], mesh_size=self.mesh_size))
                print(inner_boundaries)
                # P = geom.add_polygon([
                #     [0.0, 0.0],
                #     [1.0, 0.0],
                #     [1.0, 1.0],
                #     [0.0, 1.0]
                # ], mesh_size=self.mesh_size)
                plate = geom.boolean_difference(outer_boundary, geom.boolean_union(inner_boundaries))
            self.canvas.mesh = geom.generate_mesh()
            self.canvas.drawing_tool = 'select'
            

        print(self.canvas.mesh)
        print(self.canvas.mesh.points)

        self.canvas.drawMesh()
        self.canvas.resetBoundariesandLoading()
        # self.canvas.drawBoundaryPoints()

    def evaluatePositions(self):
        if not self.canvas.set_loads or not self.canvas.set_boundaries:
            QMessageBox.warning(
                self, 
                'Missing variables', 
                '<p>Please set loading & boundary conditions</p>',
                QMessageBox.StandardButton.Ok
            )
            return False
        self.sim_label.setText('Running...')
        self.Np = len(self.canvas.mesh.points)
        self.Ne = len(self.canvas.mesh.cells[1].data)

        X = self.canvas.mesh.points.T[0].astype('float32')
        Y = self.canvas.mesh.points.T[1].astype('float32')

        cells = self.canvas.mesh.cells[1].data.astype('int32')

        LC = self.canvas.loads_mesh.astype('float32')
        BC = self.canvas.boundaries_mesh.astype('float32')

        if self.material_properties:
            self.sig_f = self.material_properties['sig_f']
            self.density = self.material_properties['density']
            self.c = self.material_properties['c']
            self.E = self.material_properties['E']
            self.Nu = self.material_properties['Nu']
        else:
            self.sig_f = 8e6
            self.density = 1830
            self.c = 1
            self.E = 5e6
            self.Nu = 0.3

        if self.edit_dt.text():
            self.dt = float(self.edit_dt.text())
        else:
            self.dt = 0.0001

        if self.edit_total_time.text():
            self.Tt = float(self.edit_total_time.text())
        else:
            self.Tt = 1

        self.Positions = np.zeros((math.ceil(self.Tt/self.dt), self.Np, 2), dtype='float32')
        # self.Elements = np.ones((math.ceil(self.Tt/self.dt), self.Ne), dtype='int32')


        self.Uc = self.sig_f**2/(2*self.E)
        self.Tn = self.Positions.shape[0]

        self.modelWorker = ModelWorker()
        self.modelWorker.setArguments(self.Np, self.Ne, X, Y, cells, LC, BC, self.dt, self.density, self.c, self.Tt, self.E, self.Nu, self.sig_f, self.Positions)
        self.modelWorker.finished.connect(self.modelWorkerFinished)
        self.modelWorker.start()

        



        # calculated_positions = calculateParticlePostions(Np, Ne, X, Y, cells, LC, BC, dt, density, c, Tt, E, Nu, Positions)
        # print(calculated_positions)
    def playSimulation_particle(self):
        self.animation  = AnimationWindow(self)

    def playSimulation_crack(self):
        self.animation  = AnimationWindowCrack(self)

    def open_material_properties_dialog(self):
        self.material_properties_dialog = MaterialProperties(self)
        self.material_properties_dialog.show()


    def modelWorkerFinished(self):
        self.sim_label.setText('Completed')
        print(self.Positions)
        # print(self.Elements[self.Elements==0])
        self.modelWorker.deleteLater()

        #varaibles
        self.u = np.diff(self.Positions, axis=0)
        self.D = np.array([
                    [1, self.Nu, 0],
                    [self.Nu, 1, 0],
                    [0, 0, (1-self.Nu)/2]
                ])*self.E/(1-self.Nu**2)

    def setUpMainWindow(self):
        self.canvas = Canvas(self)
        self.setCentralWidget(self.canvas)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)


app = QApplication(sys.argv)
window = MainWindow()
sys.exit(app.exec())


