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

## Integrations Reference

### Python UDP Streaming Receiver

This sample code binds to port 9000, receives live tracking packets, and parses the orientation quaternion and 53 blendshape channels:

```python
import socket

UDP_IP = "127.0.0.1"
UDP_PORT = 9000

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

print(f"FaceTrack UDP Receiver active on {UDP_IP}:{UDP_PORT}")

while True:
    data, addr = sock.recvfrom(2048)
    packet_str = data.decode("utf-8").strip()

    if "|" not in packet_str:
        continue

    rot_part, weights_part = packet_str.split("|", 1)

    # Parse Head Rotation Quaternion (qx, qy, qz, qw)
    qx, qy, qz, qw = [float(v) for v in rot_part.split(",")]

    # Parse 53 Blendshape Float Weights
    blendshapes = [float(w) for w in weights_part.split(",")]

    # Access expressions by channel index
    jaw_open = blendshapes[26]
    blink_left = blendshapes[10]
    blink_right = blendshapes[11]

    print(f"JawOpen: {jaw_open:.2f} | Blinks: ({blink_left:.2f}, {blink_right:.2f})")

```

## C# / Unity Reciever (Thread-Safe Runtime)

```csharp
using UnityEngine;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using System.Globalization;

public class FaceTrackLiveReceiver : MonoBehaviour
{
    [Header("Network")]
    public int listenPort = 9000;

    [Header("Target Bindings")]
    public Transform headBone;
    public SkinnedMeshRenderer faceMesh;
    public bool preventDoubleJaw = true;

    private Thread receiveThread;
    private UdpClient udpClient;
    private bool isRunning = false;

    private readonly object lockObject = new object();
    private Quaternion incomingRotation;
    private float[] incomingBlendshapes = new float[53];
    private bool hasNewFrame = false;

    void Start()
    {
        isRunning = true;
        receiveThread = new Thread(ReceiveThreadLoop) { IsBackground = true };
        receiveThread.Start();
    }

    private void ReceiveThreadLoop()
    {
        try
        {
            udpClient = new UdpClient(listenPort);
            IPEndPoint endPoint = new IPEndPoint(IPAddress.Any, listenPort);

            while (isRunning)
            {
                byte[] bytes = udpClient.Receive(ref endPoint);
                string message = Encoding.UTF8.GetString(bytes);

                int splitIndex = message.IndexOf('|');
                if (splitIndex < 0) continue;

                string rotPart = message.Substring(0, splitIndex);
                string weightsPart = message.Substring(splitIndex + 1);

                string[] rotValues = rotPart.Split(',');
                string[] bsValues = weightsPart.Split(',');

                if (rotValues.Length == 4 && bsValues.Length == 53)
                {
                    // Convert Right-Handed (Maxine) to Unity Left-Handed space
                    float qx = float.Parse(rotValues[0], CultureInfo.InvariantCulture);
                    float qy = -float.Parse(rotValues[1], CultureInfo.InvariantCulture);
                    float qz = -float.Parse(rotValues[2], CultureInfo.InvariantCulture);
                    float qw = float.Parse(rotValues[3], CultureInfo.InvariantCulture);

                    lock (lockObject)
                    {
                        incomingRotation = new Quaternion(qx, qy, qz, qw);
                        for (int i = 0; i < 53; i++)
                        {
                            incomingBlendshapes[i] = float.Parse(bsValues[i], CultureInfo.InvariantCulture);
                        }
                        hasNewFrame = true;
                    }
                }
            }
        }
        catch (SocketException ex)
        {
            if (isRunning) Debug.LogWarning($"[FaceTrack] Socket exception: {ex.Message}");
        }
    }

    void Update()
    {
        Quaternion targetRot;
        float[] targetWeights = new float[53];

        lock (lockObject)
        {
            if (!hasNewFrame) return;
            targetRot = incomingRotation;
            System.Array.Copy(incomingBlendshapes, targetWeights, 53);
            hasNewFrame = false;
        }

        // Apply Head Bone Rotation
        if (headBone != null)
        {
            headBone.localRotation = targetRot;
        }

        // Apply Blendshape Weights
        if (faceMesh != null)
        {
            for (int i = 0; i < 53; i++)
            {
                if (preventDoubleJaw && i == 26 && headBone != null) continue;

                // Unity Blendshape weights range from 0 to 100
                if (i < faceMesh.sharedMesh.blendShapeCount)
                {
                    faceMesh.SetBlendShapeWeight(i, targetWeights[i] * 100.0f);
                }
            }
        }
    }

    void OnDestroy()
    {
        isRunning = false;
        udpClient?.Close();
        receiveThread?.Abort();
    }
}
```
