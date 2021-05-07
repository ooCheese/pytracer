import numpy as np
import math
import utils

class Material():
    
    def __init__(self,
        base_color,
        reflection = 0.1,
        deffuse = 0.2,
        ambient = 0.1,
        diffuse = 0.4,
        specular = 0.3,
        surface = 17):
        self.base_color = base_color
        self.ambient = ambient
        self.deffuse = deffuse
        self.reflection = reflection
        self.specular = specular
        self.surface = surface

    def color_at(self,point):
        return self.base_color

class SceneObj():
    
    def __init__(self,material=Material(np.array([0.0,0.0,0.0]))):
        self.material = material
        
    def color_at(self,point):
        return self.material.color_at(point)

import sphere
import plane

class UVTextureMaterial(Material):
    def __init__(self,
        img,obj,
        base_color=np.array([0,0,0]),
        ambient= 0.3,
        diffuse= 0.1,
        reflection= 0.5,
        checkSize=10,
        specular = 0.3,
        surface= 17
        ):

        super().__init__(base_color=base_color,ambient=ambient,diffuse=diffuse,reflection=reflection,specular=specular,surface=surface)
        self.img = img
        self.obj = obj

        self.aspectratio = img.shape[0]/img.shape[1]

    def __color_on_sphere(self,point):
        d =  self.obj.center - point
        d = utils.normalize(d)

        dx = d[0]
        dy = d[1]
        dz = d[2]
            
        u = (0.5 + (math.atan(2)*math.atan(dz)*math.atan(dx)/(2*math.pi))) * self.img.shape[0]
        v = (0.5 + math.asin(dy)/math.pi) * self.img.shape[1]

        return self.img[int(u)][int(v)]

    def __color_on_plane(self,point):
        normale = self.obj.normal_at(point)
        d = point - normale
        d = utils.normalize(d)
        d = d[(d != 0)] # remove 0

        u = abs(d[0]) * self.img.shape[0]
        
        if len(d) ==  1:
            v = 0
        else:
            v = abs(d[1]) * self.img.shape[1]

        return self.img[int(u)][int(v)]


    def color_at(self,point):
        if isinstance(self.obj,sphere.Sphere): # UV for Sphere
            return self.__color_on_sphere(point)
        elif isinstance(self.obj,plane.Plane):
            return self.__color_on_plane(point)
        return self.base_color


class CheckerboardMaterial(Material):
    def __init__(self,
        base_color=np.array([0,0,0]),
        other_color=np.array([0.5,0.5,0.5]),
        ambient= 0.3,
        diffuse= 0.1,
        reflection= 0.5,
        checkSize=10,
        specular = 0.3,
        surface= 17,
        ):

        super().__init__(base_color=base_color,ambient=ambient,diffuse=diffuse,reflection=reflection,specular=specular,surface=surface)
        self.other_color = other_color
        self.checkSize =  1
    
    def color_at(self,point):
        v = point * (1.0 / self.checkSize)
        if (int(abs(v[0])+0.5)+int(abs(v[1]+0.5)+int(abs(v[2] + 0.5))))%2:
            return self.other_color
        return self.base_color