import json
import codecs
from sceneObj import Material

def load_from_file(jsonfilepath):
    attributs = json.load(jsonfilepath)

    mat = Material(
        base_color=attributs["base_color"],
        ambient= attributs["ambient"],
        reflection= attributs["reflection"]
    )
    
def save_mat(filepath,mat):
    data = {
        "base_color" : mat.base_color,
        "ambient" : mat.ambient,
        "reflection" : mat.reflection
    }
    data = data.tolist()
    json.dump(data,codecs.open(filepath, 'w', encoding='utf-8'), separators=(',', ':'), sort_keys=True, indent=4)