# Live Capture Pipeline

FaceTrack includes a native UDP streaming server designed for low-latency facial tracking integration into external software.

To enable this feature, go to **Settings > Live Capture > Enable Streaming**.

## Network Protocol (UDP)

### Socket Configuration

- **Default Protocol:** UDP (User Datagram Protocol)

- **Default Host / IP:** `127.0.0.1`

- **Default Target Port:** `9000`

- **Transmit State:** Broadcasts only when the FaceTrack application is in **Avatar Preview** mode. A small chain icon can be seen when the Live Capture mode is active.

To make it discoverable through local network, set the IP to `0.0.0.0` and set the IP address on the Reciever to the IP of the machine that runs FaceTrack.

Make sure the Firewall doesn't block the connection. Administrator access is required to make changes to the rules.

## Datagram Payload Format

Each UDP packet is encoded as a raw UTF-8 string consisting of two sections separated by a vertical bar pipe (`|`):

```text
<qx>,<qy>,<qz>,<qw>|<val_0>,<val_1>,<val_2>,...,<val_52>
```

| Field Segment       | Data Type                 | Description                                                                          |
| ------------------- | ------------------------- | ------------------------------------------------------------------------------------ |
| `qx,qy,qz,qw`       | 4 Comma-Separated Floats  | Head rotation quaternion in local space.                                             |
| <code>&#124;</code> | ASCII Character (`0x7C`)  | Delimiter separating head orientation from facial weights.                           |
| `val_0,...,val_52`  | 53 Comma-Separated Floats | Continuous array of all 53 facial blendshape weights, indexed strictly from 0 to 52. |

### Example Packet Payload

```text
0.029712,-0.002083,0.025074,0.999241|0.6347,0.6399,0.0219,0.0284,0.0023,0.0017,0.0,0.0,0.1614,...
```
