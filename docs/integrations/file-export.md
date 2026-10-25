# File Export Pipeline

## File Formats Specification

### FaceTrack Data File (`.FTD`)

The `.ftd` format is a lightweight plaintext data format optimized for continuous capture storage without timestamp overhead.

#### Frame Structure

1. **Head Orientation Line:** 4 comma-separated floating-point values representing quaternion axes: `qx,qy,qz,qw`.

2. **Blendshape Channel Lines:** Sparse key-value pairs formatted as `<channel_index> <weight>`.

- Channels with values $\le 0.0001$ are omitted to reduce file size.

- Weights are normalized floats between `0.0` and `1.0`.

3. **Frame Delimiter:** A single right-angle bracket `>` on its own line signals the end of the current frame.

#### Example File Snippet

```text
0.0297122,-0.00208396,0.02507434,0.9992418
0 0.6347082
1 0.6399387
2 0.02196054
3 0.02843724
4 0.0023322
5 0.00170354
8 0.1614697
9 0.1289135
10 0.5920473
11 0.7764561
12 0.707012
13 0.707012
14 0.4345896
15 0.2536998
16 0.2536998
17 0.4345896
18 0.0004983902
19 0.0004983902
20 0.003017151
21 0.002904928
24 0.5769335
25 0.0005057824
26 0.008271621
27 0.07415253
28 0.00434836
29 0.1851757
30 0.1615853
31 0.00148939
32 0.001405794
33 0.03623935
34 0.002614718
35 0.2573872
36 0.3607733
37 0.01283595
38 0.007983878
39 0.003223931
40 0.1278339
41 0.003926528
42 0.01328478
43 0.01517543
44 0.01376856
45 0.02780233
46 0.03149441
47 0.06066087
48 0.02799019
49 0.03341239
50 0.07254299
51 0.1725106
52 0.4385237
>
... next frame ...
```

> **Note on FPS:** `.ftd` files do not store a target frame rate header due to real-time capture fluctuations; importers default to the project framerate or 60 FPS.

### FaceTrack JSON File (`.JSON`)

The `.json` file contains structured, pretty-printed frames intended for non-realtime DCC authoring and manual animation cleanup.

#### Frame Structure

The root JSON object encapsulates global capture metadata and an array of sequential frame data:

1. **Global Properties:**
* `targetFPS`: An integer designating the capture and authoring framerate (e.g., `30`, `60`).
* `frames`: An array containing sequential frame objects in chronological capture order.

2. **Frame Object Properties (`frames[]`):**
**`headRotation` Object:** Local-space rotation quaternion defined across four floating-point properties:
* `x`: Float representing the $q_x$ axis component.
* `y`: Float representing the $q_y$ axis component.
* `z`: Float representing the $q_z$ axis component.
* `w`: Float representing the $q_w$ scalar component.

**`blendshapes` Array:** An ordered list of expression objects defining facial weights:
* `name`: String identifier corresponding to the FaceTrack 53-channel blendshape standard (e.g., `"browDownLeft"`).
* `value`: Normalized floating-point weight between `0.0` and `1.0`.

#### Example File Snippet
```json
{
    "targetFPS": 30,
    "frames": [
        {
            "headRotation": {
                "x": 0.02971220202744007,
                "y": -0.002083959523588419,
                "z": 0.025074340403079988,
                "w": 0.9992417693138123
            },
            "blendshapes": [
                {
                    "name": "browDownLeft",
                    "value": 0.6347081661224365
                },
                {
                    "name": "browDownRight",
                    "value": 0.6399387121200562
                },
                {
                    "name": "browInnerUpLeft",
                    "value": 0.021960539743304254
                },
                {
                    "name": "browInnerUpRight",
                    "value": 0.028437241911888124
                },
                {
                    "name": "browOuterUpLeft",
                    "value": 0.00233220006339252
                },
                {
                    "name": "browOuterUpRight",
                    "value": 0.0017035402124747635
                },
                {
                    "name": "cheekSquintLeft",
                    "value": 0.16146966814994813
                },
                {
                    "name": "cheekSquintRight",
                    "value": 0.1289135068655014
                },
                {
                    "name": "eyeBlinkLeft",
                    "value": 0.5920473337173462
                },
                {
                    "name": "eyeBlinkRight",
                    "value": 0.7764560580253601
                },
                {
                    "name": "eyeLookDownLeft",
                    "value": 0.7070119976997376
                },
                {
                    "name": "eyeLookDownRight",
                    "value": 0.7070119976997376
                },
                {
                    "name": "eyeLookInLeft",
                    "value": 0.43458956480026247
                },
                {
                    "name": "eyeLookInRight",
                    "value": 0.25369977951049807
                },
                {
                    "name": "eyeLookOutLeft",
                    "value": 0.25369977951049807
                },
                {
                    "name": "eyeLookOutRight",
                    "value": 0.43458956480026247
                },
                {
                    "name": "eyeLookUpLeft",
                    "value": 0.0004983901744708419
                },
                {
                    "name": "eyeLookUpRight",
                    "value": 0.0004983901744708419
                },
                {
                    "name": "eyeSquintLeft",
                    "value": 0.0030171512626111509
                },
                {
                    "name": "eyeSquintRight",
                    "value": 0.0029049282893538477
                },
                {
                    "name": "jawForward",
                    "value": 0.5769335031509399
                },
                {
                    "name": "jawLeft",
                    "value": 0.0005057823727838695
                },
                {
                    "name": "jawOpen",
                    "value": 0.008271620608866215
                },
                {
                    "name": "jawRight",
                    "value": 0.07415252923965454
                },
                {
                    "name": "mouthClose",
                    "value": 0.004348359536379576
                },
                {
                    "name": "mouthDimpleLeft",
                    "value": 0.18517567217350007
                },
                {
                    "name": "mouthDimpleRight",
                    "value": 0.16158531606197358
                },
                {
                    "name": "mouthFrownLeft",
                    "value": 0.0014893901534378529
                },
                {
                    "name": "mouthFrownRight",
                    "value": 0.001405794289894402
                },
                {
                    "name": "mouthFunnel",
                    "value": 0.036239348351955417
                },
                {
                    "name": "mouthLeft",
                    "value": 0.0026147179305553438
                },
                {
                    "name": "mouthLowerDownLeft",
                    "value": 0.2573871910572052
                },
                {
                    "name": "mouthLowerDownRight",
                    "value": 0.3607732653617859
                },
                {
                    "name": "mouthPressLeft",
                    "value": 0.012835945934057236
                },
                {
                    "name": "mouthPressRight",
                    "value": 0.007983878254890442
                },
                {
                    "name": "mouthPucker",
                    "value": 0.0032239307183772327
                },
                {
                    "name": "mouthRight",
                    "value": 0.12783388793468476
                },
                {
                    "name": "mouthRollLower",
                    "value": 0.003926527686417103
                },
                {
                    "name": "mouthRollUpper",
                    "value": 0.013284778222441674
                },
                {
                    "name": "mouthShrugLower",
                    "value": 0.015175433829426766
                },
                {
                    "name": "mouthShrugUpper",
                    "value": 0.013768556527793408
                },
                {
                    "name": "mouthSmileLeft",
                    "value": 0.027802327647805215
                },
                {
                    "name": "mouthSmileRight",
                    "value": 0.03149441257119179
                },
                {
                    "name": "mouthStretchLeft",
                    "value": 0.060660865157842639
                },
                {
                    "name": "mouthStretchRight",
                    "value": 0.02799018658697605
                },
                {
                    "name": "mouthUpperUpLeft",
                    "value": 0.0334123857319355
                },
                {
                    "name": "mouthUpperUpRight",
                    "value": 0.07254298776388169
                },
                {
                    "name": "noseSneerLeft",
                    "value": 0.17251059412956239
                },
                {
                    "name": "noseSneerRight",
                    "value": 0.43852365016937258
                },
            ]
        },
        { ... next frame ... }
    ]
}
```
