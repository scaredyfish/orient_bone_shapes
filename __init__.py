__version__ = '1.0.1'

bl_info = {
    "name": "Orient Custom Shape",
    "author": "Gilles Pagia, Ron Tarrant, Michael B, Andrew Charlton",
    "version": (1, 0, 1),
    "blender": (2, 80, 0),
    "location": "Pose mode context menu",
    "description": "Rotates, scales and translates a custom bone shape to match rotation, scale and translation of its bone",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Rigging"
}

if 'bpy' in locals():
    import importlib

    if 'op_blender_rhubarb' in locals():
        importlib.reload(orient_custom_shape)
else:
    from . import orient_custom_shape

import bpy


def register():
    orient_custom_shape.register()
  
def unregister():
    orient_custom_shape.unregister()

if __name__ == "__main__":
    register()
