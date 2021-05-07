import numpy as np
import threading
import multiprocessing as mp
import cv2
import math

from sphere import Sphere
from triangle import Triangle
from plane import Plane
from light import Light
from queue import Queue
from utils import normalize

class Ray():

    def __init__(self,origin,direction):
        self.origin = origin
        self.direction = normalize(direction)

    def __repr__(self):
        return 'Ray(%s,%s)' %(repr(self.origin), repr(self.direction))

    def point_at_parameter(self,t):
        return self.origin + (self.direction * t)

class HitPointData():

    def __init__(self,hit_dist,hit_point,scene_obj,ray):
        self.hit_dist = hit_dist
        self.hit_point = hit_point
        self.scene_obj = scene_obj
        self.ray = ray

class Camera():

    def __init__(self,
        camera_pos,focus_point,
        obj_lst,
        aspectratio = 1/1,
        field_of_view = math.pi/4,
        resolution=[200,200],
        up_vector=np.array([0,1,0]),
        bg_color=np.array([1.0,1.0,1.0]),
        light=Light(np.array([30,30,10])),
        brightness=2,
        number_of_prozesses=4,
        ray_tracing_deep=3,
        ambient_color = np.array([0.0,0.5,0.0]),
        shadow_color = np.array([0.0,0.0,0.5]),
        allow_direct_light = True,
        allow_reflection = True,
        allow_ambient_color = True,
        fast_tracing = False,
        allow_multi = True,
        allow_shadows = True
        ):

        self.camera_pos = camera_pos

        self.aspectratio = aspectratio
        self.field_of_view = field_of_view
        self.aplha = field_of_view / 2
        self.resolution = resolution

        self.height = 2 * math.tan(self.aplha)
        self.width = aspectratio * self.height
        self.pix_width = self.width / (resolution[0]-1)
        self.pix_height = self.height/ (resolution[1]-1)
        self.allow_shadows = allow_shadows

        self.number_of_prozesses = number_of_prozesses

        self.field_of_view = field_of_view
        self.up_vector = up_vector
        self.focus_point = focus_point
        self.ray_tracing_deep = ray_tracing_deep
        self.ambient_color = ambient_color
        self.shadow_color = shadow_color

        self.allow_direct_light = allow_direct_light
        self.allow_reflection = allow_reflection
        self.allow_ambient_color = allow_ambient_color

        self.allow_multi = allow_multi

        sc_cp = focus_point - camera_pos
        self.view_direction = normalize(sc_cp)
        fup_cross = np.cross(self.view_direction,self.up_vector)
        self.s = normalize(fup_cross)
        self.u = np.cross(self.s,self.view_direction)

        self.fast_tracing = fast_tracing
        self.brightness = brightness

        self.bg_color = bg_color
        self.obj_lst = obj_lst
        self.obj_array = np.array(obj_lst)
        self.light = light

    def calc_image(self,img_dtype=np.uint8):
        #self.perpare_secne_obj()
        img = np.zeros((self.resolution[1],self.resolution[0],3),float)# value range [0,1]

        if self.allow_multi:
            img = self.__multi_raycasting(img) #single process
        else:
            img = self.__single_start_raycasting(img)# multi processes
        
        dtype_info =np.iinfo(img_dtype)
        img = img * dtype_info.max
        return img.astype(img_dtype)# new value range [0,dtype.max]

    def perpare_secne_obj(self):
        #perpare for faster intersection
        triangles = []
        spheres = []
        planes = []

        for obj in self.obj_lst:
            d = [obj.position,obj]
            if obj is Triangle:
                triangles.append(d)
            elif obj is Sphere:
                spheres.append(d)
            elif obj is Plane:
                planes.append(d)
        
        self.triangles = np.array(triangles)
        self.spheres = np.array(spheres)
        self.planes = np.array(planes)
        
    def __single_start_raycasting(self,img):
        return self.__start_raycasting(img,img.shape)

    def __calc_ray(self,x,y):

        xcomp = self.s * (y*self.pix_width - self.width/2)
        ycomp = self.u * (x*self.pix_height - self.height/2)

        return Ray(self.camera_pos,self.view_direction + xcomp + ycomp)

    def __start_raycasting(self,img,size,img_range=None):
        if img_range is None:
            img_range = ((0,size[0]),(0,size[1]))

        for x in range(size[0]):
            #print("Raycast: ",x/size[0]*100,"%")
            for y in range (size[1]):
                self.__cast_ray(img,x,y,img_range)
        
        return img

    def points_on_rays_at_parameter(self,rays,t):
        return self.postions + rays[1] * t
    
    def __multi_raycasting(self,img):
        self.x_segment_size = img.shape[0] // self.number_of_prozesses
        self.y_segment_size = img.shape[1]

        with mp.Pool(processes=self.number_of_prozesses) as pool:
            img_segments = pool.map(self.start_ray_cast_worker,range(self.number_of_prozesses))

        return np.vstack(img_segments)
    
    def start_ray_cast_worker(self,i):
        img = np.zeros((self.x_segment_size,self.y_segment_size,3),float)
        x_offset = (self.x_segment_size * (i),self.x_segment_size * (i+1))
        y_offset = (0,img.shape[1])

        return self.__start_raycasting(img,img.shape,(x_offset,y_offset))

    #Slow Version
    def __cast_ray(self,img,x,y,img_range):
        ray = self.__calc_ray(x+img_range[0][0],y+img_range[1][0])
        img[x][y]= self.__trace_ray(0,ray)

    def __trace_ray(self,lvl,ray):
        hit_point_data = self.__intersect(lvl,ray,self.ray_tracing_deep)
        if hit_point_data:
            return self.__shade(lvl,ray,hit_point_data)
        return self.bg_color

    def __intersect(self,lvl,ray,maxlvl):

        if lvl > maxlvl:
            return None

        maxdist = float('inf')
        hit_point_data = None

        for obj in self.obj_lst:
            hitdist = obj.intersection_parameter(ray)
            if hitdist is not None:
                if hitdist > 0 and hitdist < maxdist:
                    maxdist = hitdist
                    hit_point_data = HitPointData(hitdist,ray.point_at_parameter(hitdist),obj,ray)
        return hit_point_data

    def __shade(self,lvl,ray, hit_point_data):
        color = np.array([0.0,0.0,0.0])

        if self.allow_ambient_color:
            color += self.ambient_color * hit_point_data.scene_obj.material.ambient

        if self.allow_direct_light:
            #deffuse = hit_point_data.scene_obj.material.deffuse
            color += self.__compute_direct_light(hit_point_data)# * deffuse #direct Color
        else:
            color += hit_point_data.scene_obj.material.base_color
        
        if self.allow_reflection:
            refected_ray = self.__compute_refected_ray(hit_point_data)
            refected_color = self.__trace_ray(lvl + 1, refected_ray)
            reflection = hit_point_data.scene_obj.material.reflection 
            color += refected_color * reflection

        return np.clip(color,0,1)

    def __compute_direct_light(self,hit_point_data):
        l = self.light.position - hit_point_data.hit_point # vector between ligth and hitpoint
        scene_obj = hit_point_data.scene_obj

        n = scene_obj.normal_at(hit_point_data.hit_point)

        l = normalize(l)
        n = normalize(n)

        lr = l - 2 * np.dot(hit_point_data.hit_point,l) * n

        base_color = hit_point_data.scene_obj.color_at(hit_point_data.hit_point)
        surface = scene_obj.material.reflection

        #normieren
        lr = normalize(lr)
        
        color = base_color * scene_obj.material.deffuse * np.maximum(np.dot(l,n),0)
        color += base_color * scene_obj.material.specular * np.maximum(np.dot(lr,-hit_point_data.ray.direction), 0) ** scene_obj.material.surface

        if self.allow_shadows == True:
            ray_to_light =Ray(hit_point_data.hit_point,l)

            if self.__intersect(0,ray_to_light,self.ray_tracing_deep):
                color += self.shadow_color
            else:
                color *= self.brightness

        return color

    def __compute_refected_ray(self,hit_point_data):
        n = hit_point_data.scene_obj.normal_at(hit_point_data.hit_point)
        d = hit_point_data.hit_point - self.camera_pos
        d_ref = d - 2* np.dot(n,d) * n
        return Ray(hit_point_data.hit_point,d_ref)


