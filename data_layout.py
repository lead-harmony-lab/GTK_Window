from pyassimp import *

scene = load('models/char_01_triangulated.obj')
character = scene.meshes[0]

print(character)
print(len(character.vertices))
print(len(character.normals))
print(len(character.texturecoords[0]))
print(len(character.faces))