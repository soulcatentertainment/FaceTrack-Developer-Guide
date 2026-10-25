# Rigging & Kinematics Implementation

Target rigs can receive tracking either through direct mesh morphs (Blendshapes / Shape Keys) or bone rotations.

## Head Rotation & Fallback Morphs

The raw rotation quaternion arrives in $[q_x, q_y, q_z, q_w]$ ordering.

- **Blender Conversion:** Reorder components to scalar-first: $(q_w, q_x, q_y, q_z)$.

- **Unity Conversion:** Negate $y$ and $z$ axes for left-handed coordinate systems: `new Quaternion(qx, -qy, -qz, qw)`.

When rigging characters without head bone hierarchies, calculate equivalent head morphs using Euler bounds:

- Range limits: $\text{Turn Up/Down} \in [-45^{\circ}, 45^{\circ}]$, $\text{Turn L/R} \in [-76.5^{\circ}, 76.5^{\circ}]$, $\text{Tilt L/R} \in [-35.1^{\circ}, 35.1^{\circ}]$.

- Linear remap formula:

$$\text{Value} = \left(\frac{\theta - \theta_{\min}}{\theta_{\max} - \theta_{\min}}\right) \cdot 3.0 - 1.5$$

## Eye Gaze Kinematics

Eye look channels (indices 12 to 19) can actuate bone rotations (Pitch and Yaw) using the differential weights between opposing directions:

$$\text{Pitch}_{\text{Left}} = (w_{18} - w_{12}) \cdot \theta_{\text{pitch\_max}} \cdot s_{\text{vert}}$$

$$\text{Yaw}_{\text{Left}} = (w_{14} - w_{16}) \cdot \theta_{\text{yaw\_max}} \cdot s_{\text{horiz}}$$

$$\text{Pitch}_{\text{Right}} = (w_{19} - w_{13}) \cdot \theta_{\text{pitch\_max}} \cdot s_{\text{vert}}$$

$$\text{Yaw}_{\text{Right}} = (w_{17} - w_{15}) \cdot \theta_{\text{yaw\_max}} \cdot s_{\text{horiz}}$$

- Default Angular Bounds: Pitch Range = $15.0^{\circ}$, Yaw Range = $25.0^{\circ}$ (or $45.0^{\circ}$ depending on rig sensitivity).

- Horizontal/Vertical sign scalars: $s_{\text{horiz}} = -1.0$ (when horizontal flip is enabled), $s_{\text{vert}} = 1.0$.
