import cv2
import numpy as np
import math
import time
import json
import sys
import re

from sphere import Sphere
from triangle import Triangle
from plane import Plane
from light import Light
from camera import Camera
import sceneObj as so
import objFileReader

def load_img(filepath):
    img=cv2.imread(filepath)
    return cv2.normalize(img, None, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_32F)

def simple_geom(texture_path=None):
    s1 = Sphere(np.array([0,1,10]),radius=1)
    s2 = Sphere(np.array([-1.2,-1,10]),1)
    s3 = Sphere(np.array([1.2,-1,10]),1)
    t = Triangle(np.array([0,2,20]),np.array([2.5,-2,20]),np.array([-2.5,-2,20]))
    p = Plane(np.array([0,-2.3,4.5]),np.array([0,200,-0.1]))

    s1.material = so.Material(np.array([1,0.5,0.5]),reflection=0.5,deffuse=0.5,ambient=0.1,specular=0.5,surface=100)
    s2.material = so.Material(np.array([0.5,1.0,0.5]),reflection=0.5,deffuse=0.5,ambient=0.1,specular=0.5,surface=100)
    s3.material = so.Material(np.array([1.0,0.5,1.0]),reflection=0.5,deffuse=0.5,ambient=0.1,specular=0.5,surface=100)
    t.material = so.Material(np.array([1.0,1.0,0.5]),reflection=0.5,deffuse=0.5,ambient=0.1,specular=0.0,surface=100)
    p.material = so.CheckerboardMaterial(base_color=np.array([0.0,0.0,0.0]),other_color=np.array([1.0,1.0,1.0]),
            reflection=0.1,ambient=0.0,diffuse=0.5,specular=0.5,surface=10)
    
    if texture_path is not None:

        p.material = so.UVTextureMaterial(img=load_img(texture_path),obj=p,
            reflection=0.3,ambient=0.0,diffuse=0.5,specular=0.5,surface=20)

        s3.material = so.UVTextureMaterial(img=load_img(texture_path),obj=s3,
            reflection=0.3,ambient=0.0,diffuse=0.5,specular=0.5,surface=20)

    return [s1,s2,s3,t,p]


def complex_geom():
    return objFileReader.read_obj_file("../resource/squirrel_aligned_lowres.obj",so.Material(base_color=np.array([0.0,0.0,0.8])))

def main():

    obj_lst = None

    #default raytracing options
    allow_reflection=True
    allow_direct_light= True
    allow_ambient_color= True
    allow_multi = True
    allow_shadows = True

    #default camera_pos
    camera_pos = np.array([0.0,0.0,0])
    camera_focus = np.array([0.0,0.0,50])

    if len(sys.argv) > 1:
        for param in sys.argv[1:]:
            if param=="squirrelripper":
                obj_lst = complex_geom()
                camera_pos = np.array([3.0,0.0,3.0])
                camera_focus = np.array([-0.00264657,1.45722065,-0.07497032])

                allow_reflection=False
                allow_direct_light= True
                allow_ambient_color= False
                allow_shadows = False
                allow_multi = True
            elif param == "texsphere":
                obj_lst = simple_geom(texture_path="resource/cheese.jpg")
            elif re.match(".*\.obj",param):
                obj_lst = objFileReader.read_obj_file(param)

    if obj_lst is None:
        obj_lst = simple_geom()

    main_camera = Camera(
        camera_pos=camera_pos,
        focus_point=camera_focus,
        up_vector=np.array([0.0,-1.0,0.0]),
        obj_lst=obj_lst,
        aspectratio=1/1,
        resolution=[400,400],
        field_of_view= math.pi/4,
        light=Light(np.array([5,5,-2])),
        number_of_prozesses=4,
        bg_color=np.array([1.0,0.76,0.5]),
        shadow_color=np.array([0.0,0.0,0.0]),
        ambient_color= np.array([0.0,0.5,0.0]),
        allow_reflection=allow_reflection,
        allow_direct_light= allow_direct_light,
        brightness= 2,
        allow_ambient_color= allow_ambient_color,
        allow_multi = allow_multi,
        allow_shadows = allow_shadows
    )

    print(len(obj_lst))

    t = time.time()
    img = main_camera.calc_image()
    print(time.time() - t)

    cv2.imwrite("out/test.jpg",img)
    cv2.namedWindow('test',cv2.WINDOW_NORMAL)
    cv2.resizeWindow('test',img.shape[0],img.shape[1])
    cv2.imshow("test",img)

    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()