import numpy as np

class Light():

    def __init__(self,position,color=np.array([0.0,0.0,0.0])):
        self.position = position
        self.color =color