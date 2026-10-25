# Blendshapes Implementation

FaceTrack outputs 53 facial blendshape channels (indexed **0 to 52**) based on the ARKit standard for easy integration with existing DCC applications.

## 53 Facial Blendshape Channels

Here are the 53 blendshapes channels, with both `browInnerUp` and `cheekPuff` split into bilateral (Left/Right) targets:

| Index | Blendshape Name       | Category |
| :---: | :-------------------- | :------- |
|   0   | `browDownLeft`        | Eyebrows |
|   1   | `browDownRight`       | Eyebrows |
|   2   | `browInnerUpLeft`     | Eyebrows |
|   3   | `browInnerUpRight`    | Eyebrows |
|   4   | `browOuterUpLeft`     | Eyebrows |
|   5   | `browOuterUpRight`    | Eyebrows |
|   6   | `cheekPuffLeft`       | Cheeks   |
|   7   | `cheekPuffRight`      | Cheeks   |
|   8   | `cheekSquintLeft`     | Cheeks   |
|   9   | `cheekSquintRight`    | Cheeks   |
|  10   | `eyeBlinkLeft`        | Eyes     |
|  11   | `eyeBlinkRight`       | Eyes     |
|  12   | `eyeLookDownLeft`     | Eyes     |
|  13   | `eyeLookDownRight`    | Eyes     |
|  14   | `eyeLookInLeft`       | Eyes     |
|  15   | `eyeLookInRight`      | Eyes     |
|  16   | `eyeLookOutLeft`      | Eyes     |
|  17   | `eyeLookOutRight`     | Eyes     |
|  18   | `eyeLookUpLeft`       | Eyes     |
|  19   | `eyeLookUpRight`      | Eyes     |
|  20   | `eyeSquintLeft`       | Eyes     |
|  21   | `eyeSquintRight`      | Eyes     |
|  22   | `eyeWideLeft`         | Eyes     |
|  23   | `eyeWideRight`        | Eyes     |
|  24   | `jawForward`          | Jaw      |
|  25   | `jawLeft`             | Jaw      |
|  26   | `jawOpen`             | Jaw      |
|  27   | `jawRight`            | Jaw      |
|  28   | `mouthClose`          | Mouth    |
|  29   | `mouthDimpleLeft`     | Mouth    |
|  30   | `mouthDimpleRight`    | Mouth    |
|  31   | `mouthFrownLeft`      | Mouth    |
|  32   | `mouthFrownRight`     | Mouth    |
|  33   | `mouthFunnel`         | Mouth    |
|  34   | `mouthLeft`           | Mouth    |
|  35   | `mouthLowerDownLeft`  | Mouth    |
|  36   | `mouthLowerDownRight` | Mouth    |
|  37   | `mouthPressLeft`      | Mouth    |
|  38   | `mouthPressRight`     | Mouth    |
|  39   | `mouthPucker`         | Mouth    |
|  40   | `mouthRight`          | Mouth    |
|  41   | `mouthRollLower`      | Mouth    |
|  42   | `mouthRollUpper`      | Mouth    |
|  43   | `mouthShrugLower`     | Mouth    |
|  44   | `mouthShrugUpper`     | Mouth    |
|  45   | `mouthSmileLeft`      | Mouth    |
|  46   | `mouthSmileRight`     | Mouth    |
|  47   | `mouthStretchLeft`    | Mouth    |
|  48   | `mouthStretchRight`   | Mouth    |
|  49   | `mouthUpperUpLeft`    | Mouth    |
|  50   | `mouthUpperUpRight`   | Mouth    |
|  51   | `noseSneerLeft`       | Nose     |
|  52   | `noseSneerRight`      | Nose     |

## Known Limitations

Keep in mind that `cheekPuffLeft`, `cheekPuffRight` are always set to zero as they are currently not supported. Tongue blendshapes are also omitted due to technical limitation.
