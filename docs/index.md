# FaceTrack Developer Guide

Welcome to the official developer integration guide for **FaceTrack** by SOUL CAT Entertainment Sdn Bhd. This documentation provides the technical specifications, file schemas, and network protocols required to build third-party integrations, game engine plugins, and virtual avatar runtimes.

FaceTrack exports facial performance data via offline files (`.ftd` and `.json`) or real-time UDP network streaming. The system tracks a standardized 53-channel blendshape rig (based on ARKit/Maxine) alongside head orientation quaternions.

## Documentation Directory

- **[Data Formats & Schemas](formats/file-formats.md)**: Specifications for parsing `.ftd` and `.json` offline exports.
- **[Live Capture UDP Protocol](integrations/live-capture-udp.md)**: Network packet structures for real-time streaming.
- **[Unity Avatar Integration](integrations/unity-avatar.md)**: Reference math and logic for applying tracking data to 3D meshes and bones.

# FaceTrack Developer Guide

This documentation defines the specifications, data structures, network protocols, and rigging kinematics required to integrate third-party applications, virtual avatar runtimes, and game engines with FaceTrack.

---

## System Overview & Architecture

FaceTrack uses NVIDIA RTX Maxine and Audio2Face deep-learning frameworks to extract high-fidelity facial performance metrics from webcam video, pre-recorded footage, or audio files. The software outputs facial tracking data across two delivery pipelines:

- **File Export Pipeline:** Frame-by-frame baked data saved either as `.ftd` (compact streaming log) or `.json` (human-readable structured data).

- **Live Capture Pipeline:** Real-time UDP socket streaming transmitting head orientation and 53 blendshape coefficients simultaneously.
