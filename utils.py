from PyQt6.QtCore import  QThread
# from windows import AnimationScene

import ctypes
from numpy.ctypeslib import ndpointer
import math

from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation 

class ModelWorker(QThread):

    def __ini__(self):
        super().__init__()
        
    def setArguments(self, *args):
        self.args = args

    def stopRunning(self):
        self.terminate()
        self.wait()

    def run(self):
        functions = ctypes.CDLL('./model2D.so')
        getParticlePositions = functions.particlePositions
        getParticlePositions.restype = None
        getParticlePositions.argtypes = [
            ctypes.c_int,
            ctypes.c_int,
            ndpointer(ctypes.c_float, flags="C_CONTIGUOUS"),
            ndpointer(ctypes.c_float, flags="C_CONTIGUOUS"),
            ndpointer(ctypes.c_int, flags="C_CONTIGUOUS"),
            ndpointer(ctypes.c_float, flags="C_CONTIGUOUS"),
            ndpointer(ctypes.c_float, flags="C_CONTIGUOUS"),
            ctypes.c_float,
            ctypes.c_float,
            ctypes.c_float,
            ctypes.c_float,
            ctypes.c_float,
            ctypes.c_float,
            ctypes.c_float,
            ndpointer(ctypes.c_float, flags="C_CONTIGUOUS") 
        ]

        getParticlePositions(*self.args)


class AnimationWorker(QThread):

    def __init__(self, mesh):
        super().__init__()
        self.mesh = mesh

    def stopRunning(self):
        self.terminate()
        self.wait()

    def run(self):
        # self.parent.scene = AnimationScene(self.parent, self.image)
        xmin = min(self.mesh.points.T[0])
        xmax = max(self.mesh.points.T[0])

        ymin = min(self.mesh.points.T[1])
        ymax = max(self.mesh.points.T[1])

        fig = plt.figure(figsize=(7,7))
        ax = plt.axes(xlim=(xmin, xmax),ylim=(ymin, ymax))

        self.scatter = ax.scatter(self.mesh.points.T[0], self.mesh.points.T[1], s=0.5)
        self.anim = FuncAnimation(fig, self.updatePlot, interval=10)
        plt.show()

    def updatePlot(self, frame_number):
        self.scatter.set_offsets(self.mesh.points[:,:2]+0.1)

    


    




    

    




def calculateParticlePostions(*args):
    functions = ctypes.CDLL('./model2D.so')
    getParticlePositions = functions.particlePositions
    getParticlePositions.restype = None
    getParticlePositions.argtypes = [
        ctypes.c_int,
        ctypes.c_int,
        ndpointer(ctypes.c_float, flags="C_CONTIGUOUS"),
        ndpointer(ctypes.c_float, flags="C_CONTIGUOUS"),
        ndpointer(ctypes.c_int, flags="C_CONTIGUOUS"),
        ndpointer(ctypes.c_float, flags="C_CONTIGUOUS"),
        ndpointer(ctypes.c_float, flags="C_CONTIGUOUS"),
        ctypes.c_float,
        ctypes.c_float,
        ctypes.c_float,
        ctypes.c_float,
        ctypes.c_float,
        ctypes.c_float,
        ndpointer(ctypes.c_float, flags="C_CONTIGUOUS")    
    ]

    getParticlePositions(*args)
    return args[-1]
        