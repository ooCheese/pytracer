import numpy as np 
from triangle import Triangle
from sceneObj import Material

def read_obj_file(filepath,mat=None):
    
    file = open(filepath)
    header_lines = []
    points = []
    triangles = []
    point_sum = np.zeros((3,))
    for line in file:
        if line[0] != '#': #is no Comment
            line_elements = line.split()
            if(line_elements[0] == "v"): # is point
                p_x = float(line_elements[1])
                p_y = float(line_elements[2])
                p_z = float(line_elements[3])

                point = np.array([p_x,p_y,p_z])

                points.append(np.array(point))
                point_sum  += point
            elif(line_elements[0] == "f"):
                p0 = points[int(line_elements[1])-1]
                p1 = points[int(line_elements[2])-1]
                p2 = points[int(line_elements[3])-1]
                t = Triangle(p0,p1,p2)
                if mat:
                    t.material = mat
                triangles.append(t)
    print("center pos : ",point_sum  / len(points))
    return triangles
        




