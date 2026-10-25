import socket
import os
import time

UDP_IP = "127.0.0.1"
UDP_PORT = 9000

# Standard 53 ARKit/Maxine Blendshape Names
BLENDSHAPES = [
    "browDownLeft", "browDownRight", "browInnerUpLeft", "browInnerUpRight",
    "browOuterUpLeft", "browOuterUpRight", "cheekPuffLeft", "cheekPuffRight",
    "cheekSquintLeft", "cheekSquintRight", "eyeBlinkLeft", "eyeBlinkRight",
    "eyeLookDownLeft", "eyeLookDownRight", "eyeLookInLeft", "eyeLookInRight",
    "eyeLookOutLeft", "eyeLookOutRight", "eyeLookUpLeft", "eyeLookUpRight",
    "eyeSquintLeft", "eyeSquintRight", "eyeWideLeft", "eyeWideRight",
    "jawForward", "jawLeft", "jawOpen", "jawRight",
    "mouthClose", "mouthDimpleLeft", "mouthDimpleRight", "mouthFrownLeft",
    "mouthFrownRight", "mouthFunnel", "mouthLeft", "mouthLowerDownLeft",
    "mouthLowerDownRight", "mouthPressLeft", "mouthPressRight", "mouthPucker",
    "mouthRight", "mouthRollLower", "mouthRollUpper", "mouthShrugLower",
    "mouthShrugUpper", "mouthSmileLeft", "mouthSmileRight", "mouthStretchLeft",
    "mouthStretchRight", "mouthUpperUpLeft", "mouthUpperUpRight",
    "noseSneerLeft", "noseSneerRight"
]

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))
sock.setblocking(False) 

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

print(f"Listening for FaceTrack on {UDP_IP}:{UDP_PORT}...")
print("Press Ctrl+C to stop.")

last_ui_update = 0
UI_REFRESH_RATE = 0.1 

try:
    while True:
        try:
            data, addr = sock.recvfrom(4096) 
            message = data.decode('utf-8')
            
            current_time = time.time()
            if current_time - last_ui_update > UI_REFRESH_RATE:
                rot_str, bs_str = message.split('|')
                rot_data = [float(x) for x in rot_str.split(',')]
                bs_data = [float(x) for x in bs_str.split(',')]
                
                clear_screen()
                
                print(f"=== FACETRACK LIVE CAPTURE DATA | Source: {addr[0]}:{addr[1]} ===")
                print(f"Head Rotation:  X: {rot_data[0]: 5.3f} | Y: {rot_data[1]: 5.3f} | Z: {rot_data[2]: 5.3f} | W: {rot_data[3]: 5.3f}")
                print("=" * 110)
                
                print("Blendshape Values (0-52):")
                grid_output = ""
                for i, val in enumerate(bs_data):
                    # Graceful fallback if bs_data exceeds our label list
                    name = BLENDSHAPES[i] if i < len(BLENDSHAPES) else f"Unknown_{i}"
                    
                    # Truncate long names to 15 characters to keep the grid aligned
                    grid_output += f"[{i:02d}] {name[:15]:<15}: {val:5.3f}   "
                    
                    # Drop to a new line every 3 items for better readability with names
                    if (i + 1) % 3 == 0:
                        grid_output += "\n"
                        
                print(grid_output)
                print("\nPress Ctrl+C to stop.")
                
                last_ui_update = current_time
                
        except BlockingIOError:
            pass
        except ValueError:
            pass

except KeyboardInterrupt:
    print("\nListener stopped.")