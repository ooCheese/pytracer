import numpy as np
from utils import normalize
from sceneObj import SceneObj
import math

class Sphere(SceneObj):

    def __init__(self,center,radius):
        super().__init__()
        self.center = center
        self.radius = radius

    def __repr__(self):
        return 'Sphere(%s,%s)' %(repr(self.center),repr(self.radius))

    def intersection_parameter(self,ray):
        co = self.center - ray.origin
        v = np.dot(co,ray.direction)
        discriminant = v**2 - np.dot(co,co) + self.radius**2
        if discriminant < 0:
            return None
        else:
            return v - math.sqrt(discriminant)

    def normal_at(self,p):
        return normalize(p - self.center)