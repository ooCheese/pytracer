import numpy as np
from sceneObj import SceneObj
from utils import normalize

class Triangle(SceneObj):

    def __init__(self,point_a,point_b,point_c):
        super().__init__()
        self.point_a = point_a
        self.point_b = point_b
        self.point_c = point_c
        self.u = self.point_b - self.point_a
        self.v = self.point_c - self.point_a

    def __repr__(self):
        return 'Triangle(%s,%s,%s' %(
            repr(self.point_a),
            repr(self.point_b),
            repr(self.point_c))

    def intersection_parameter(self,ray):
        w = ray.origin - self.point_a
        dv = np.cross(ray.direction,self.v)
        dvu = dv.dot(self.u)
        if(dvu == 0.0):
            return None
        wu = np.cross(w,self.u)
        r = dv.dot(w) / dvu
        s = wu.dot(ray.direction) / dvu
        if 0 <=r and r <= 1 and 0 <= s and s<= 1 and r+s <= 1:
            return wu.dot(self.v) /dvu
        else:
            return None

    def normal_at(self,p):
        return normalize(np.cross(self.u,self.v))