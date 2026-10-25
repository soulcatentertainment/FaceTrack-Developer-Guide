bl_info = {
    "name": "FaceTrack Importer (.ftd / .json)",
    "author": "SOUL CAT Entertainment Sdn Bhd",
    "version": (2, 1),
    "blender": (4, 1, 0),
    "location": "View3D > Sidebar > SCE",
    "description": "Imports FaceTrack Data (.ftd / .json) as Blendshapes and Joints animation.",
    "category": "Object"
}

import bpy
import os, math, json
from bpy.types import Panel, Operator, PropertyGroup
from bpy.props import StringProperty, PointerProperty, CollectionProperty, IntProperty, FloatProperty, BoolProperty
from mathutils import Quaternion, Euler

# Standard Maxine 53 Blendshape Mapping (Indices 0 to 52)
DEFAULT_MAPPING = {
    0: "browDownLeft", 1: "browDownRight", 2: "browInnerUpLeft", 3: "browInnerUpRight",
    4: "browOuterUpLeft", 5: "browOuterUpRight", 6: "cheekPuffLeft", 7: "cheekPuffRight",
    8: "cheekSquintLeft", 9: "cheekSquintRight", 10: "eyeBlinkLeft", 11: "eyeBlinkRight",
    12: "eyeLookDownLeft", 13: "eyeLookDownRight", 14: "eyeLookInLeft", 15: "eyeLookInRight",
    16: "eyeLookOutLeft", 17: "eyeLookOutRight", 18: "eyeLookUpLeft", 19: "eyeLookUpRight",
    20: "eyeSquintLeft", 21: "eyeSquintRight", 22: "eyeWideLeft", 23: "eyeWideRight",
    24: "jawForward", 25: "jawLeft", 26: "jawOpen", 27: "jawRight",
    28: "mouthClose", 29: "mouthDimpleLeft", 30: "mouthDimpleRight", 31: "mouthFrownLeft",
    32: "mouthFrownRight", 33: "mouthFunnel", 34: "mouthLeft", 35: "mouthLowerDownLeft",
    36: "mouthLowerDownRight", 37: "mouthPressLeft", 38: "mouthPressRight", 39: "mouthPucker",
    40: "mouthRight", 41: "mouthRollLower", 42: "mouthRollUpper", 43: "mouthShrugLower",
    44: "mouthShrugUpper", 45: "mouthSmileLeft", 46: "mouthSmileRight", 47: "mouthStretchLeft",
    48: "mouthStretchRight", 49: "mouthUpperUpLeft", 50: "mouthUpperUpRight",
    51: "noseSneerLeft", 52: "noseSneerRight"
}

EYE_NAME_TO_IDX = {
    "eyelookdownleft": 12,
    "eyelookdownright": 13,
    "eyelookinleft": 14,
    "eyelookinright": 15,
    "eyelookoutleft": 16,
    "eyelookoutright": 17,
    "eyelookupleft": 18,
    "eyelookupright": 19,
}

class FaceTrackMappingItem(PropertyGroup):
    ft_index: IntProperty()
    ft_name: StringProperty()
    target_shapekey: StringProperty(name="Target", description="Select Target Shape Key")

class FaceTrackSettings(PropertyGroup):
    head_joint: StringProperty(name="Head Joint", default="Ctrl_Head")
    left_eye_joint: StringProperty(name="Left Eye Joint", default="LeftEye")
    right_eye_joint: StringProperty(name="Right Eye Joint", default="RightEye")
    eye_x_rot: FloatProperty(name="Eye Pitch Range", default=15.0, description="Max vertical pitch rotation in degrees")
    eye_y_rot: FloatProperty(name="Eye Yaw Range", default=25.0, description="Max horizontal yaw rotation in degrees")
    flip_eye_horizontal: BoolProperty(name="Flip Horizontal (Yaw)", default=True, description="Invert left/right horizontal eye look direction")
    flip_eye_vertical: BoolProperty(name="Flip Vertical (Pitch)", default=False, description="Invert up/down vertical eye look direction")
    swap_eyes: BoolProperty(name="Swap L/R Eyes", default=False, description="Swap left and right eye tracking channels")
    
    # Set to True so eye look blendshapes are keyframed on the mesh
    animate_eye_shapekeys: BoolProperty(
        name="Animate Eye Look Blendshapes",
        default=True,
        description="Keyframe eyeLook shape keys directly onto mesh shape keys"
    )
    animate_eye_bones: BoolProperty(
        name="Animate Eye Bones",
        default=True,
        description="Rotate eye bones on the armature using eye tracking values"
    )
    mappings: CollectionProperty(type=FaceTrackMappingItem)

# --- CORE FUNCTIONS ---

def get_armature_and_meshes(context_obj):
    armature = None
    meshes = set()

    if not context_obj:
        return None, []

    if context_obj.type == 'ARMATURE':
        armature = context_obj
    elif context_obj.type == 'MESH':
        meshes.add(context_obj)
        for mod in context_obj.modifiers:
            if mod.type == 'ARMATURE' and mod.object:
                armature = mod.object
                break

    if armature:
        for obj in bpy.data.objects:
            if obj.type == 'MESH':
                if obj.parent == armature:
                    meshes.add(obj)
                else:
                    for mod in obj.modifiers:
                        if mod.type == 'ARMATURE' and mod.object == armature:
                            meshes.add(obj)
                            break

    return armature, list(meshes)

def apply_head_rotation(armature, quat_values, frame_index, head_joint):
    head_bone = armature.pose.bones.get(head_joint)
    if not head_bone: return
    blender_quat = (quat_values[3], quat_values[0], quat_values[1], quat_values[2])
    head_bone.rotation_mode = 'QUATERNION'
    head_bone.rotation_quaternion = blender_quat
    head_bone.keyframe_insert(data_path="rotation_quaternion", frame=frame_index)

def apply_eye_rotations(armature, frame_index, left_bone_name, right_bone_name, eye_values, eye_pitch_max, eye_yaw_max, flip_h=True, flip_v=False, swap_lr=False):
    if swap_lr:
        down_l = eye_values.get(13, 0.0)
        down_r = eye_values.get(12, 0.0)
        in_l   = eye_values.get(15, 0.0)
        in_r   = eye_values.get(14, 0.0)
        out_l  = eye_values.get(17, 0.0)
        out_r  = eye_values.get(16, 0.0)
        up_l   = eye_values.get(19, 0.0)
        up_r   = eye_values.get(18, 0.0)
    else:
        down_l = eye_values.get(12, 0.0)
        down_r = eye_values.get(13, 0.0)
        in_l   = eye_values.get(14, 0.0)
        in_r   = eye_values.get(15, 0.0)
        out_l  = eye_values.get(16, 0.0)
        out_r  = eye_values.get(17, 0.0)
        up_l   = eye_values.get(18, 0.0)
        up_r   = eye_values.get(19, 0.0)

    h_mult = -1.0 if flip_h else 1.0
    v_mult = -1.0 if flip_v else 1.0

    left_pitch = (up_l - down_l) * eye_pitch_max * v_mult
    left_yaw   = (in_l - out_l) * eye_yaw_max * h_mult

    right_pitch = (up_r - down_r) * eye_pitch_max * v_mult
    right_yaw   = (out_r - in_r) * eye_yaw_max * h_mult

    left_bone = armature.pose.bones.get(left_bone_name)
    if left_bone:
        left_bone.rotation_mode = 'XYZ'
        left_bone.rotation_euler = Euler((math.radians(left_pitch), 0.0, math.radians(left_yaw)), 'XYZ')
        left_bone.keyframe_insert(data_path="rotation_euler", frame=frame_index)

    right_bone = armature.pose.bones.get(right_bone_name)
    if right_bone:
        right_bone.rotation_mode = 'XYZ'
        right_bone.rotation_euler = Euler((math.radians(right_pitch), 0.0, math.radians(right_yaw)), 'XYZ')
        right_bone.keyframe_insert(data_path="rotation_euler", frame=frame_index)

def apply_head_blendshapes(target_meshes, quat_values, frame_index):
    blender_quat = Quaternion((quat_values[3], quat_values[0], quat_values[1], quat_values[2]))
    euler_angles = blender_quat.to_euler()
    
    blendshape_range = {
        'Head_Turn_UpDown': (-45, 45),
        'Head_Turn_LR': (-76.49, 76.49),
        'Head_Tilt_LR': (-35.1, 35.1)
    }
    
    head_turn_up_down = math.degrees(euler_angles.x)
    head_turn_left_right = math.degrees(euler_angles.y)
    head_tilt_left_right = math.degrees(euler_angles.z)
    
    def map_value(value, min_range, max_range):
        return (value - min_range) / (max_range - min_range) * 3.0 - 1.5
    
    head_turn_up_down = map_value(head_turn_up_down, *blendshape_range['Head_Turn_UpDown'])
    head_turn_left_right = map_value(head_turn_left_right, *blendshape_range['Head_Turn_LR'])
    head_tilt_left_right = map_value(head_tilt_left_right, *blendshape_range['Head_Tilt_LR'])
    
    def set_blendshape(name, value):
        for m in target_meshes:
            key_blocks = m.data.shape_keys.key_blocks if m.data.shape_keys else None
            if key_blocks and name in key_blocks:
                key_blocks[name].value = value
                key_blocks[name].keyframe_insert(data_path="value", frame=frame_index)
    
    set_blendshape('Head_Turn_Up', head_turn_up_down)
    set_blendshape('Head_Turn_Down', -head_turn_up_down)
    set_blendshape('Head_Turn_L', head_turn_left_right)
    set_blendshape('Head_Turn_R', -head_turn_left_right)
    set_blendshape('Head_Tilt_L', head_tilt_left_right)
    set_blendshape('Head_Tilt_R', -head_tilt_left_right)

# --- OPERATORS ---

class OBJECT_OT_InitializeMapping(Operator):
    bl_label = "Initialize Shape Key Mappings"
    bl_idname = "object.ft_init_mapping"

    def execute(self, context):
        settings = context.scene.face_track_settings
        settings.mappings.clear()
        
        for idx, name in DEFAULT_MAPPING.items():
            item = settings.mappings.add()
            item.ft_index = idx
            item.ft_name = name
            item.target_shapekey = name
        return {'FINISHED'}

class OBJECT_OT_SaveMapping(Operator):
    bl_label = "Save Mapping"
    bl_idname = "object.ft_save_mapping"
    filepath: StringProperty(subtype="FILE_PATH")

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        settings = context.scene.face_track_settings
        data = {item.ft_name: item.target_shapekey for item in settings.mappings}
        data["_JOINT_HEAD_"] = settings.head_joint
        data["_JOINT_LEFT_EYE_"] = settings.left_eye_joint
        data["_JOINT_RIGHT_EYE_"] = settings.right_eye_joint
        data["_EYE_PITCH_"] = settings.eye_x_rot
        data["_EYE_YAW_"] = settings.eye_y_rot
        data["_FLIP_EYE_H_"] = settings.flip_eye_horizontal
        data["_FLIP_EYE_V_"] = settings.flip_eye_vertical
        data["_SWAP_EYES_"] = settings.swap_eyes
        data["_ANIM_EYE_SHAPES_"] = settings.animate_eye_shapekeys
        data["_ANIM_EYE_BONES_"] = settings.animate_eye_bones
        
        if not self.filepath.endswith(".json"):
            self.filepath += ".json"
            
        with open(self.filepath, 'w') as f:
            json.dump(data, f, indent=4)
        self.report({'INFO'}, f"Saved mapping to {self.filepath}")
        return {'FINISHED'}

class OBJECT_OT_LoadMapping(Operator):
    bl_label = "Load Mapping"
    bl_idname = "object.ft_load_mapping"
    filepath: StringProperty(subtype="FILE_PATH")

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        settings = context.scene.face_track_settings
        if not os.path.exists(self.filepath):
            self.report({'ERROR'}, "File not found")
            return {'CANCELLED'}
            
        if len(settings.mappings) == 0:
            bpy.ops.object.ft_init_mapping()
            
        try:
            if self.filepath.endswith(".json"):
                with open(self.filepath, 'r') as f:
                    data = json.load(f)
                    
                for item in settings.mappings:
                    if item.ft_name in data:
                        item.target_shapekey = data[item.ft_name]
                        
                settings.head_joint = data.get("_JOINT_HEAD_", settings.head_joint)
                settings.left_eye_joint = data.get("_JOINT_LEFT_EYE_", settings.left_eye_joint)
                settings.right_eye_joint = data.get("_JOINT_RIGHT_EYE_", settings.right_eye_joint)
                settings.eye_x_rot = data.get("_EYE_PITCH_", settings.eye_x_rot)
                settings.eye_y_rot = data.get("_EYE_YAW_", settings.eye_y_rot)
                settings.flip_eye_horizontal = data.get("_FLIP_EYE_H_", settings.flip_eye_horizontal)
                settings.flip_eye_vertical = data.get("_FLIP_EYE_V_", settings.flip_eye_vertical)
                settings.swap_eyes = data.get("_SWAP_EYES_", settings.swap_eyes)
                settings.animate_eye_shapekeys = data.get("_ANIM_EYE_SHAPES_", settings.animate_eye_shapekeys)
                settings.animate_eye_bones = data.get("_ANIM_EYE_BONES_", settings.animate_eye_bones)
            else:
                with open(self.filepath, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if not line: continue
                        parts = line.split(' ', 1)
                        if len(parts) == 2:
                            index = int(parts[0])
                            target_name = parts[1].replace('"', '') 
                            for item in settings.mappings:
                                if item.ft_index == index:
                                    item.target_shapekey = target_name
                                    break
            self.report({'INFO'}, f"Loaded mapping from {self.filepath}")
        except Exception as e:
            self.report({'ERROR'}, f"Failed to load mapping: {str(e)}")
            return {'CANCELLED'}
            
        return {'FINISHED'}

class OBJECT_OT_AutoMapShapeKeys(Operator):
    bl_label = "Auto-Detect Mappings"
    bl_idname = "object.ft_auto_map"

    def execute(self, context):
        armature, meshes = get_armature_and_meshes(context.object)
        
        if not meshes:
            self.report({'WARNING'}, "Select an Armature or Mesh with Shape Keys.")
            return {'CANCELLED'}

        settings = context.scene.face_track_settings
        if len(settings.mappings) == 0:
            bpy.ops.object.ft_init_mapping()

        mesh_shape_keys = set()
        for m in meshes:
            if m.data.shape_keys:
                mesh_shape_keys.update(m.data.shape_keys.key_blocks.keys())

        def normalize(name):
            n = name.lower().replace('_', '').replace('.', '').replace('-', '').replace(' ', '')
            if n.endswith('left'): n = n[:-4] + 'l'
            if n.endswith('right'): n = n[:-5] + 'r'
            return n

        aliases = {
            "browdown": ["browdrop"],
            "browinnerup": ["browraiseinner"],
            "browouterup": ["browraiseouter"],
            "mouthfunnel": ["mouthfunnelup", "mouthfunnel"],
            "mouthpucker": ["mouthpuckerup", "mouthpucker"],
            "cheeksquint": ["cheekraise"],
            "eye_look": ["eyelook"] 
        }

        normalized_mesh_keys = {normalize(k): k for k in mesh_shape_keys}
        
        for k in mesh_shape_keys:
            if "Eye_L_Look" in k or "Eye_R_Look" in k:
                special_norm = k.lower().replace('_', '').replace('eyellook', 'eyelookl').replace('eyerlook', 'eyelookr')
                normalized_mesh_keys[special_norm] = k

        matches_found = 0

        for item in settings.mappings:
            target_norm = normalize(item.ft_name)
            
            if target_norm in normalized_mesh_keys:
                item.target_shapekey = normalized_mesh_keys[target_norm]
                matches_found += 1
                continue
                
            matched = False
            for standard_base, alias_list in aliases.items():
                if standard_base in target_norm:
                    for alias in alias_list:
                        test_norm = target_norm.replace(standard_base, alias)
                        if test_norm in normalized_mesh_keys:
                            item.target_shapekey = normalized_mesh_keys[test_norm]
                            matches_found += 1
                            matched = True
                            break
                if matched: break

        self.report({'INFO'}, f"Auto-mapped {matches_found} shape keys!")
        return {'FINISHED'}

class OBJECT_OT_OpenFileDialogue(Operator):
    bl_label = "Import FaceTrack Data"
    bl_idname = "object.open_file_dialogue"
    filepath: StringProperty(subtype="FILE_PATH")
    filter_glob: StringProperty(default="*.ftd;*.json", options={'HIDDEN'})
    
    _timer = None
    _is_json = False
    _lines = []
    _json_frames = []
    _current_line = 0
    _current_json_frame = 0
    _frame_index = 0
    _eye_values = {}
    _json_target_map = {}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        bpy.ops.ed.undo_push(message="Before applying FaceTrack data")
        
        self.armature, meshes = get_armature_and_meshes(context.object)
        self.target_meshes = [m for m in meshes if m.data.shape_keys]
        
        if not self.armature and not self.target_meshes:
            self.report({'ERROR'}, "Select an Armature or a Mesh with Shape Keys")
            return {'CANCELLED'}
            
        self.settings = context.scene.face_track_settings
        self.mapping_dict = {item.ft_index: item.target_shapekey for item in self.settings.mappings if item.target_shapekey}

        # Build name lookup dictionary for JSON blendshapes
        self._json_target_map = {}
        for item in self.settings.mappings:
            if item.target_shapekey:
                k = item.ft_name.lower()
                self._json_target_map.setdefault(k, []).append(item.target_shapekey)

        # Backward compatibility bridges
        if "browinnerup" not in self._json_target_map:
            combined = []
            if "browinnerupleft" in self._json_target_map: combined.extend(self._json_target_map["browinnerupleft"])
            if "browinnerupright" in self._json_target_map: combined.extend(self._json_target_map["browinnerupright"])
            if combined: self._json_target_map["browinnerup"] = combined

        if "cheekpuff" not in self._json_target_map:
            combined = []
            if "cheekpuffleft" in self._json_target_map: combined.extend(self._json_target_map["cheekpuffleft"])
            if "cheekpuffright" in self._json_target_map: combined.extend(self._json_target_map["cheekpuffright"])
            if combined: self._json_target_map["cheekpuff"] = combined

        self._frame_index = 0
        self._current_line = 0
        self._current_json_frame = 0
        self._eye_values = {}
        self._is_json = self.filepath.lower().endswith(".json")

        if self._is_json:
            try:
                with open(self.filepath, 'r') as file:
                    data = json.load(file)
                self._json_frames = data.get("frames", [])
                fps = data.get("targetFPS")
                if fps and isinstance(fps, (int, float)) and fps > 0:
                    context.scene.render.fps = int(fps)
                total_progress = len(self._json_frames)
            except Exception as e:
                self.report({'ERROR'}, f"Failed to parse JSON file: {e}")
                return {'CANCELLED'}
        else:
            with open(self.filepath, 'r') as file:
                self._lines = file.readlines()
            total_progress = len(self._lines)
        
        wm = context.window_manager
        wm.progress_begin(0, total_progress)
        self._timer = wm.event_timer_add(0.01, window=context.window)
        wm.modal_handler_add(self)
        
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        if event.type == 'TIMER':
            anim_eye_shapes = self.settings.animate_eye_shapekeys
            anim_eye_bones = self.settings.animate_eye_bones and bool(self.armature)

            # --- JSON IMPORTER BRANCH ---
            if self._is_json:
                frames_per_tick = 20
                for _ in range(frames_per_tick):
                    if self._current_json_frame >= len(self._json_frames):
                        context.window_manager.progress_end()
                        context.window_manager.event_timer_remove(self._timer)
                        bpy.data.scenes["Scene"].frame_end = max(1, self._frame_index - 1)
                        self.report({'INFO'}, "FaceTrack JSON Import Complete!")
                        return {'FINISHED'}

                    frame_data = self._json_frames[self._current_json_frame]
                    self._current_json_frame += 1

                    # 1. Apply Head Rotation
                    hr = frame_data.get("headRotation")
                    if hr and self.armature:
                        quat = [hr.get("x", 0.0), hr.get("y", 0.0), hr.get("z", 0.0), hr.get("w", 1.0)]
                        apply_head_rotation(self.armature, quat, self._frame_index, self.settings.head_joint)
                        apply_head_blendshapes(self.target_meshes, quat, self._frame_index)

                    # 2. Extract Blendshapes & Eye Buffers
                    eye_values = {}
                    for bs in frame_data.get("blendshapes", []):
                        name = bs.get("name", "")
                        val = float(bs.get("value", 0.0))
                        name_lower = name.lower()

                        is_eye_look = name_lower in EYE_NAME_TO_IDX
                        if is_eye_look:
                            eye_values[EYE_NAME_TO_IDX[name_lower]] = val
                            if not anim_eye_shapes:
                                continue  # Skip mesh keyframing if user turned it off

                        target_sks = self._json_target_map.get(name_lower, [])
                        for target_sk in target_sks:
                            for m in self.target_meshes:
                                kb = m.data.shape_keys.key_blocks
                                if target_sk in kb:
                                    kb[target_sk].value = val
                                    kb[target_sk].keyframe_insert(data_path="value", frame=self._frame_index)

                    # 3. Apply Eye Rotations to Bones
                    if anim_eye_bones and eye_values:
                        apply_eye_rotations(
                            self.armature,
                            self._frame_index,
                            self.settings.left_eye_joint,
                            self.settings.right_eye_joint,
                            eye_values,
                            self.settings.eye_x_rot,
                            self.settings.eye_y_rot,
                            flip_h=self.settings.flip_eye_horizontal,
                            flip_v=self.settings.flip_eye_vertical,
                            swap_lr=self.settings.swap_eyes
                        )

                    self._frame_index += 1

                context.window_manager.progress_update(self._current_json_frame)
                return {'PASS_THROUGH'}

            # --- FTD IMPORTER BRANCH ---
            else:
                lines_to_process_per_tick = 800
                
                for _ in range(lines_to_process_per_tick):
                    if self._current_line >= len(self._lines):
                        if anim_eye_bones and self._eye_values:
                            apply_eye_rotations(
                                self.armature, 
                                self._frame_index, 
                                self.settings.left_eye_joint, 
                                self.settings.right_eye_joint, 
                                self._eye_values,
                                self.settings.eye_x_rot,
                                self.settings.eye_y_rot,
                                flip_h=self.settings.flip_eye_horizontal,
                                flip_v=self.settings.flip_eye_vertical,
                                swap_lr=self.settings.swap_eyes
                            )
                        context.window_manager.progress_end()
                        context.window_manager.event_timer_remove(self._timer)
                        bpy.data.scenes["Scene"].frame_end = self._frame_index
                        self.report({'INFO'}, "FaceTrack FTD Import Complete!")
                        return {'FINISHED'}

                    line = self._lines[self._current_line].strip()
                    self._current_line += 1
                    
                    if '>' in line:
                        if anim_eye_bones and self._eye_values:
                            apply_eye_rotations(
                                self.armature, 
                                self._frame_index, 
                                self.settings.left_eye_joint, 
                                self.settings.right_eye_joint, 
                                self._eye_values,
                                self.settings.eye_x_rot,
                                self.settings.eye_y_rot,
                                flip_h=self.settings.flip_eye_horizontal,
                                flip_v=self.settings.flip_eye_vertical,
                                swap_lr=self.settings.swap_eyes
                            )
                        self._eye_values = {}
                        self._frame_index += 1
                        continue

                    if ',' in line:
                        quat_values = [float(q) for q in line.split(',')]
                        if len(quat_values) == 4 and self.armature:
                            apply_head_rotation(self.armature, quat_values, self._frame_index, self.settings.head_joint)
                            apply_head_blendshapes(self.target_meshes, quat_values, self._frame_index)
                        continue

                    try:
                        index_str, value_str = line.split(' ')
                        index = int(index_str)
                        value = float(value_str)
                    except ValueError:
                        continue

                    is_eye_look = (12 <= index <= 19)
                    if is_eye_look:
                        self._eye_values[index] = value
                        if not anim_eye_shapes:
                            continue  # Skip mesh keyframing if user turned it off

                    target_sk = self.mapping_dict.get(index)
                    if target_sk:
                        for m in self.target_meshes:
                            kb = m.data.shape_keys.key_blocks
                            if target_sk in kb:
                                kb[target_sk].value = value
                                kb[target_sk].keyframe_insert(data_path="value", frame=self._frame_index)

                context.window_manager.progress_update(self._current_line)
                return {'PASS_THROUGH'}
                
        return {'PASS_THROUGH'}

# --- UI PANEL ---

class OBJECT_PT_BlendshapePanel(Panel):
    bl_label = "FaceTrack Importer"
    bl_idname = "OBJECT_PT_blendshape_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "SCE"

    def draw(self, context):
        layout = self.layout
        settings = context.scene.face_track_settings
        armature_obj, meshes = get_armature_and_meshes(context.object)

        ui_mesh = None
        max_keys = 0
        for m in meshes:
            if m.data.shape_keys:
                count = len(m.data.shape_keys.key_blocks)
                if count > max_keys:
                    max_keys = count
                    ui_mesh = m

        # Joint Assignments
        box = layout.box()
        box.label(text="Assign Joints:", icon='BONE_DATA')
        
        if armature_obj and armature_obj.data and hasattr(armature_obj.data, 'bones'):
            box.prop_search(settings, "head_joint", armature_obj.data, "bones", text="Head")
            box.prop_search(settings, "left_eye_joint", armature_obj.data, "bones", text="Left Eye")
            box.prop_search(settings, "right_eye_joint", armature_obj.data, "bones", text="Right Eye")
        else:
            box.label(text="Select an Armature to assign bones.", icon='INFO')
            box.prop(settings, "head_joint", text="Head")
            box.prop(settings, "left_eye_joint", text="Left Eye")
            box.prop(settings, "right_eye_joint", text="Right Eye")

        # Eye Controls
        col = box.column(align=True)
        col.prop(settings, "eye_x_rot", text="Eye Pitch (deg)")
        col.prop(settings, "eye_y_rot", text="Eye Yaw (deg)")
        
        row_mirror = box.row(align=True)
        row_mirror.prop(settings, "flip_eye_horizontal", text="Flip Horiz", toggle=True)
        row_mirror.prop(settings, "flip_eye_vertical", text="Flip Vert", toggle=True)
        row_mirror.prop(settings, "swap_eyes", text="Swap L/R", toggle=True)

        row_targets = box.row(align=True)
        row_targets.prop(settings, "animate_eye_shapekeys", text="Eye Shape Keys", toggle=True, icon='SHAPEKEY_DATA')
        row_targets.prop(settings, "animate_eye_bones", text="Eye Bones", toggle=True, icon='BONE_DATA')

        # Blendshape Mapping UI
        box = layout.box()
        box.label(text="Shape Key Mapping:", icon='SHAPEKEY_DATA')
        
        row = box.row()
        row.operator("object.ft_save_mapping", text="Save", icon='FILE_TICK')
        row.operator("object.ft_load_mapping", text="Load", icon='FILE_FOLDER')
        
        box.operator("object.ft_auto_map", text="Auto-Detect Mappings", icon='VIEWZOOM')

        if len(settings.mappings) == 0:
            box.operator("object.ft_init_mapping", text="Initialize Mappings", icon='FILE_REFRESH')
        else:
            if ui_mesh:
                col = box.column(align=True)
                for item in settings.mappings:
                    row = col.row()
                    row.label(text=item.ft_name)
                    row.prop_search(item, "target_shapekey", ui_mesh.data.shape_keys, "key_blocks", text="")
            else:
                box.label(text="No meshes with Shape Keys found.", icon='ERROR')

        layout.separator()
        layout.operator("object.open_file_dialogue", text="Import FTD / JSON", icon='IMPORT')

# --- REGISTRATION ---

classes = (
    FaceTrackMappingItem,
    FaceTrackSettings,
    OBJECT_OT_InitializeMapping,
    OBJECT_OT_SaveMapping,
    OBJECT_OT_LoadMapping,
    OBJECT_OT_AutoMapShapeKeys,
    OBJECT_OT_OpenFileDialogue,
    OBJECT_PT_BlendshapePanel
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.face_track_settings = PointerProperty(type=FaceTrackSettings)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.face_track_settings

if __name__ == "__main__":
    register()