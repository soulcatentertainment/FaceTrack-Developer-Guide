# FaceTrack Developer Guide

Welcome to the official developer integration guide for **FaceTrack** by SOUL CAT Entertainment Sdn Bhd.

This documentation provides the technical specifications, file schemas, network protocols, and rigging kinematics required to integrate third-party applications, game engines, and virtual avatar runtimes.

[Check out FaceTrack on Steam!](https://store.steampowered.com/app/3231540/FaceTrack/)

---

## System Overview & Architecture

FaceTrack uses NVIDIA RTX Maxine and Audio2Face deep-learning frameworks to extract high-fidelity facial performance metrics from webcam video, pre-recorded footage, or audio files.

The tracking system outputs a standardized 53-channel blendshape rig (based on the ARKit standard) paired with local head orientation quaternions. Facial tracking data is delivered through two distinct pipelines:

- **[File Export Pipeline:](pipelines/file-export.md)** Frame-by-frame baked data saved as either `.ftd` (a lightweight, sparse streaming log) or `.json` (human-readable structured data).
- **[Live Capture UDP Protocol:](pipelines/live-capture.md)** Low-latency real-time UDP socket streaming transmitting head orientation and 53 blendshape coefficients simultaneously.

---

## Documentation Directory & Use Cases

Explore the dedicated documentation modules below based on your development and pipeline requirements:

### Specifications

- **[53 Facial Blendshape Channels](specifications/blendshapes.md)**
  - **Contents:** Complete index mapping (channels 0 to 52) across ARKit-compatible facial expressions, along with known channel constraints (e.g., zeroed `cheekPuff` targets and omitted tongue tracking).
  - **Use Cases:** Standardizing custom character blendshape names, creating facial morph targets in DCC software (Blender, Maya, ZBrush), and setting up animation retargeting profiles.

- **[Rigging & Kinematics Implementation](specifications/kinematics.md)**
  - **Contents:** Mathematical coordinate conversions (scalar-first ordering for Blender vs. axis-negation for Unity), linear Euler remapping formulas for rigs lacking head bones, and differential eye gaze kinematics for pitch/yaw bone rotation.
  - **Use Cases:** Translating raw quaternion tracking data to skeletal transforms, automating procedural look-at eye bones, and creating headless avatar morph setups.

---

### Delivery Pipelines & File Formats

- **[File Export Pipeline](pipelines/file-export.md)**
  - **Contents:** Format structures and specifications for `.ftd` (sparse line-delimited key-value pairs omitting weights $\le 0.0001$) and `.json` (timestamped frame arrays).
  - **Use Cases:** Non-realtime animation workflows, recorded mocap cleanup, custom DCC importer plugin development, and offline performance archival.

- **[Live Capture UDP Protocol](pipelines/live-capture.md)**
  - **Contents:** UDP socket configuration, network broadcast settings (`0.0.0.0`), port bindings, firewall setup, and raw string datagram payload definitions separated by pipe characters (`|`).
  - **Use Cases:** Low-latency real-time tracking, live VTuber runtime applications, broadcast studio networking, and game engine integration.

---

### Integration Reference Implementations

Located within the **[Live Capture Integration Samples](integrations/live-capture-integration.md)**, complete runtime implementations are provided for reference:

- **Python UDP Receiver:** Lightweight socket listener for data logging, real-time metrics parsing, and terminal inspection.
  - **Use Cases:** Custom analytical dashboards, standalone robotics control, AI pipelines, and headless tracking verification.
- **C# / Unity Receiver:** Multi-threaded, thread-safe runtime component featuring right-to-left-handed coordinate transforms, dynamic `SkinnedMeshRenderer` weight updates, and `preventDoubleJaw` transform filtering.
  - **Use Cases:** Direct avatar actuation in Unity, live streaming apps, interactive game mechanics, and virtual production runtimes.
