# FaceTrack Developer Guide

This repository contains the source documentation and build configuration for the official **FaceTrack Developer Guide** by SOUL CAT Entertainment Sdn Bhd, built with [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/) and hosted on GitHub Pages.

The documentation provides technical specifications, file schemas, coordinate transforms, and network protocols required to integrate FaceTrack with third-party software, DCC tools, and game engines.

---

## Documentation Structure

The documentation source files are located in the `docs/` directory:

```text
├── mkdocs.yml                            # MkDocs configuration and navigation hierarchy
├── .github/workflows/deploy.yml          # Automated GitHub Pages deployment workflow
└── docs/
    ├── index.md                          # Guide overview, architecture, and pipeline summary
    ├── specifications/
    │   └── blendshapes.md                # 53 ARKit-standard facial blendshape channel index
    │   └── kinematics.md                 # Head orientation, Euler bounds, and eye gaze math
    ├── pipelines/
    │   ├── file-export.md                # Specifications for .ftd and .json offline formats
    │   └── live-capture.md               # UDP streaming protocol, and payload format
    └── integrations/
        └── live-capture-integration.md   # Code samples to connect Live Capture streams

```

---

## Core Topics Covered

- **System Overview & Architecture:** High-fidelity performance extraction leveraging NVIDIA RTX Maxine and Audio2Face deep-learning frameworks.
- **Facial Blendshape Channels:** Complete mapping of all 53 standard blendshape channels (0–52), noting unsupported channels (`cheekPuffLeft`/`Right` and tongue targets).
- **Kinematics & Coordinate Conversions:** Formulae for converting Maxine right-handed coordinates to Unity left-handed space and Blender scalar-first formats, eye gaze bone differential actuation, and Euler remap bounds.
- **File Formats:** Plaintext frame-delimited streaming files (`.ftd`) and structured frame arrays (`.json`).
- **Live Capture UDP Streaming:** Datagram payload structures over UDP (default port `9000`) for low-latency live streaming.
- **Sample Integrations:** Minimal receiver scripts in Python and multi-threaded C# scripts for Unity.
