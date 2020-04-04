bl_info = {
    "name": "Edit Mode Copy & Paste",
    "author": "Jonas Olesen",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "Edit Mode search menu, custom bind in addon preferences",
    "description" : "Uses Blender's inbuilt copy & paste functionality to enable copying and pasting from and into edit mode. Copying from object mode into edit mode and vice versa also works",
}  

import bpy
from bpy.props import *
from bpy.utils import register_class
from bpy.utils import unregister_class

def copy_func(context):
    
    old_selection = bpy.context.selected_objects
    
    bpy.ops.object.editmode_toggle() #enter object mode
    bpy.ops.object.duplicate_move()
    bpy.ops.object.join()
    merged_obj = bpy.context.active_object
    bpy.ops.object.editmode_toggle() #re-enter edit mode
    
    #seprate and copy the selection
    bpy.ops.mesh.separate(type='SELECTED')
    
    bpy.data.objects.remove(merged_obj, do_unlink=True, do_id_user=True)
    
    copy_obj = bpy.context.selected_objects[0]
    copy_obj.name = "COPIED_OBJECT"
    
    bpy.ops.view3d.copybuffer()
    
    #remove the copied object and restore previous state
    bpy.data.objects.remove(copy_obj, do_unlink=True, do_id_user=True)

    bpy.ops.object.select_all(action="DESELECT")
    for obj in old_selection:
        obj.select_set(True)
    
    bpy.context.view_layer.objects.active = old_selection[0]
    bpy.ops.object.editmode_toggle()

    

def paste_func(context):
    
    #old selection and active object
    old_selection = bpy.context.selected_objects
    bpy.ops.object.editmode_toggle()
    active = bpy.context.active_object
    
    bpy.ops.object.select_all(action="DESELECT")
    bpy.ops.view3d.pastebuffer()
    active.select_set(True)
    bpy.context.view_layer.objects.active = active
    
    #join copied object
    bpy.ops.object.join()
    
    #restore previous state
    for obj in old_selection:
        obj.select_set(True)
    bpy.ops.object.editmode_toggle()
    


class EDIT_OT_copy_selection(bpy.types.Operator):
    """Save current Selection"""
    bl_idname = "edit.copy_selection"
    bl_label = "Copy Edit Mode Selection"

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj and obj.type == 'MESH' and obj.mode == 'EDIT'

    def execute(self, context):
        copy_func(context)
        return {'FINISHED'}
    
class EDIT_OT_paste_selection(bpy.types.Operator):
    """Save current Selection"""
    bl_idname = "edit.paste_selection"
    bl_label = "Paste Edit Mode Selection"

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj and obj.type == 'MESH' and obj.mode == 'EDIT'

    def execute(self, context):
        paste_func(context)
        return {'FINISHED'}
         
class AddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__
                                    
    def draw(self, context):
        
        wm = bpy.context.window_manager 
        km_items = wm.keyconfigs.user.keymaps['3D View'].keymap_items
        
        km_item = km_items[EDIT_OT_copy_selection.bl_idname]
        row = self.layout.row()
        row.label(text=km_item.name)
        row.prop(km_item, 'type', text='', full_event=True)

        km_item = km_items[EDIT_OT_paste_selection.bl_idname]
        row = self.layout.row()
        row.label(text=km_item.name)
        row.prop(km_item, 'type', text='', full_event=True)

addon_keymaps = []

classes = (
    EDIT_OT_copy_selection,
    EDIT_OT_paste_selection,
    AddonPreferences
)

def register():

    for cls in classes:
        register_class(cls)
    
    # add keymap entry
    kcfg = bpy.context.window_manager.keyconfigs.addon
    if kcfg:
        km = kcfg.keymaps.new(name='3D View', space_type='VIEW_3D')
        kmi = km.keymap_items.new(EDIT_OT_copy_selection.bl_idname, 'C', 'PRESS', ctrl=True, shift=True)
        addon_keymaps.append((km, kmi))
        kmi = km.keymap_items.new(EDIT_OT_paste_selection.bl_idname, 'V', 'PRESS', ctrl=True, shift=True)
        addon_keymaps.append((km, kmi))


def unregister():

    for cls in classes:
        unregister_class(cls)

    #unregister keymap
    wm = bpy.context.window_manager
    kcfg = wm.keyconfigs.addon
    km = kcfg.keymaps["3D View"]
    
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()
    
if __name__ == "__main__":
    register()
