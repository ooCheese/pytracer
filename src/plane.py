import numpy as np
import utils
from sceneObj import SceneObj

class Plane(SceneObj):
    def __init__(self,point,normal):
        super().__init__()
        self.point = point
        self.normal = utils.normalize(normal)

    def __repr__(self):
        return 'Plane(%s,%s)' %(repr(self.point),repr(self.normal))

    def intersection_parameter(self,ray):
        op = ray.origin - self.point
        a = op.dot(self.normal)
        b = ray.direction.dot(self.normal)
        if b < 0:
            return -a/b
        else:
            return None

    def normal_at(self,p):
        return self.normal