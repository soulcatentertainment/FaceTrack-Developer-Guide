# FaceTrack Developer Guide

Welcome to the official developer integration guide for **FaceTrack** by SOUL CAT Entertainment Sdn Bhd.

This documentation provides the technical specifications, file schemas, network protocols, and rigging kinematics required to integrate third-party applications, game engines, and virtual avatar runtimes.

[Check out FaceTrack on Steam!](https://store.steampowered.com/app/3231540/FaceTrack/)

---

## System Overview & Architecture

FaceTrack uses NVIDIA RTX Maxine and Audio2Face deep-learning frameworks to extract high-fidelity facial performance metrics from webcam video, pre-recorded footage, or audio files.

The tracking system outputs a standardized 53-channel blendshape rig (based on the ARKit standard) paired with local head orientation quaternions. Facial tracking data is delivered through two distinct pipelines:

- **[File Export Pipeline:](pipelines/file-export.md)** Frame-by-frame baked data saved as either `.ftd` (a lightweight, sparse streaming log) or `.json` (human-readable structured data).
- **[Live Capture Pipeline:](pipelines/live-capture.md)** Low-latency real-time UDP socket streaming transmitting head orientation and 53 blendshape coefficients simultaneously.

---
