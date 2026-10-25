# Live Capture Pipeline

The **Live Capture Pipeline** enables real-time, low-latency streaming of facial performance capture and head pose kinematics directly over a local network. Built for interactive use cases—including virtual production in Unreal Engine or Unity, live VTubing, and real-time avatar puppeteering—it delivers frame-by-frame tracking data synchronously without the overhead of heavy transport protocols.

By broadcasting lightweight UDP datagrams, FaceTrack allows any external software or custom runtime client to ingest facial animation coefficients with minimal latency and zero handshaking overhead.

### Key Capabilities

- **Minimal Transport Latency:** Uses connectionless UDP sockets to avoid head-of-line blocking and eliminate packet retransmission lag.
- **Unified State Transmission:** Delivers normalized 6-DOF head orientation and all 53 facial blendshape channels synchronized in a single packet.
- **Flexible Deployment:** Supports single-machine loopback pipelines (`127.0.0.1`) as well as dedicated multi-machine LAN broadcast configurations.
- **Engine-Agnostic Ingestion:** Compatible with any programming environment supporting standard socket programming (C#, C++, Python, Rust).

---

## Configuration & Activation

To start streaming tracking data from FaceTrack:

1. Navigate to **Settings** > **Live Capture**.
2. Toggle **Enable Streaming** on.
3. Switch FaceTrack to **Avatar Preview** mode.

> **Status Indicator:** Data is transmitted only while in **Avatar Preview** mode. A **chain icon** appears in the interface to indicate an active broadcast state.

---

## Network Protocol Configuration

### Default Socket Parameters

| Parameter               | Default Value                  | Notes                                    |
| :---------------------- | :----------------------------- | :--------------------------------------- |
| **Protocol**            | `UDP` (User Datagram Protocol) | Fast, connectionless transport.          |
| **Default Host / IP**   | `127.0.0.1`                    | Local loopback (same-machine streaming). |
| **Default Target Port** | `9000`                         | Configurable receiving port.             |

### Local Network (LAN) Setup

To stream data from FaceTrack to another computer across a local network:

1. In FaceTrack settings, set the bind address / IP to `0.0.0.0` (listens on all available network interfaces).
2. On the receiving machine (e.g., a secondary workstation running Unreal Engine), configure the client listener to target the local IPv4 address of the host machine running FaceTrack (e.g., `192.168.1.X`).
3. **Firewall Requirements:** Ensure inbound UDP traffic on port `9000` is permitted on the host machine. You may need administrative privileges to create an inbound firewall rule in Windows Defender or corporate firewall tools.

---

## Datagram Payload Format

Each packet is serialized as a raw, human-readable UTF-8 string divided into two distinct sections by a vertical bar delimiter (`|`):

```text
<qx>,<qy>,<qz>,<qw>|<val_0>,<val_1>,<val_2>,...,<val_52>
```
