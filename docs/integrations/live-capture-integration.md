# Live Capture Integration Samples

Here provide reference implementations for ingesting, parsing, and applying FaceTrack's real-time UDP stream across external toolsets and game engines. Whether you are building real-time telemetry visualizers in Python or driving digital human rigs inside Unity or Unreal Engine, these examples demonstrate reliable patterns for zero-latency socket handling and thread-safe data synchronization.

### Integration Architecture & Best Practices

- **Thread Isolation:** In game engines and UI frameworks, socket listening runs on a dedicated background thread to prevent UI freezing and avoid dropping UDP datagrams during heavy frame renders.
- **Range Normalization:** FaceTrack outputs facial blendshape coefficients in a normalized `0.0` to `1.0` range. Runtimes requiring percentage-based inputs (such as Unity's `SkinnedMeshRenderer`, which expects `0` to `100`) must scale the values accordingly.
- **Culture-Invariant Parsing:** Floating-point numbers are transmitted with standard decimal points (`.`). Always parse using invariant culture (`CultureInfo.InvariantCulture` in C# or standard `float()` in Python) to prevent parse errors on systems configured with comma-based decimal locales.

---

## Python UDP Streaming Receiver

This lightweight script binds to port `9000`, receives incoming datagrams, splits the orientation and blendshape segments, and extracts individual channel weights by index.

```python
import socket

UDP_IP = "127.0.0.1"
UDP_PORT = 9000

# Initialize UDP socket
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

    # Parse 53 Blendshape Float Weights (0.0 to 1.0)
    blendshapes = [float(w) for w in weights_part.split(",")]

    # Access expressions by channel index
    jaw_open = blendshapes[26]
    blink_left = blendshapes[10]
    blink_right = blendshapes[11]

    print(f"JawOpen: {jaw_open:.2f} | Blinks: ({blink_left:.2f}, {blink_right:.2f})")
```

You can also download the full python receiver sample [here](https://github.com/soulcatentertainment/FaceTrack-Developer-Guide/blob/main/scripts/livecapture_python_sample.py) to test out the Live Capture streaming.

---

## C# / Unity Receiver (Thread-Safe Runtime)

This component uses a background listener thread to prevent main-thread latency spikes in Unity. The incoming payload is locked, copied into thread-safe buffers, and applied to a `SkinnedMeshRenderer` during Unity's standard `Update()` loop.

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

    [Header("Target Mesh")]
    public SkinnedMeshRenderer faceMesh;

    [Header("Optional Head Transform")]
    public Transform headBone;

    private Thread receiveThread;
    private UdpClient udpClient;
    private bool isRunning = false;

    private readonly object lockObject = new object();
    private readonly float[] incomingBlendshapes = new float[53];
    private readonly float[] currentWeights = new float[53];
    private Quaternion incomingRotation = Quaternion.identity;
    private Quaternion currentRotation = Quaternion.identity;
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

                // 1. Parse Head Orientation Quaternion (qx, qy, qz, qw)
                string rotPart = message.Substring(0, splitIndex);
                string[] rotValues = rotPart.Split(',');
                Quaternion parsedRotation = Quaternion.identity;
                if (rotValues.Length == 4)
                {
                    float qx = float.Parse(rotValues[0], CultureInfo.InvariantCulture);
                    float qy = float.Parse(rotValues[1], CultureInfo.InvariantCulture);
                    float qz = float.Parse(rotValues[2], CultureInfo.InvariantCulture);
                    float qw = float.Parse(rotValues[3], CultureInfo.InvariantCulture);
                    parsedRotation = new Quaternion(qx, qy, qz, qw);
                }

                // 2. Parse the 53 comma-separated blendshape weights
                string weightsPart = message.Substring(splitIndex + 1);
                string[] bsValues = weightsPart.Split(',');

                if (bsValues.Length == 53)
                {
                    lock (lockObject)
                    {
                        for (int i = 0; i < 53; i++)
                        {
                            incomingBlendshapes[i] = float.Parse(bsValues[i], CultureInfo.InvariantCulture);
                        }
                        incomingRotation = parsedRotation;
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
        lock (lockObject)
        {
            if (!hasNewFrame) return;

            System.Array.Copy(incomingBlendshapes, currentWeights, 53);
            currentRotation = incomingRotation;
            hasNewFrame = false;
        }

        // Apply head rotation if bound
        if (headBone != null)
        {
            headBone.localRotation = currentRotation;
        }

        // Apply weights (FaceTrack outputs 0.0–1.0; Unity blendshapes require 0–100)
        if (faceMesh != null && faceMesh.sharedMesh != null)
        {
            int shapeCount = Mathf.Min(53, faceMesh.sharedMesh.blendShapeCount);
            for (int i = 0; i < shapeCount; i++)
            {
                faceMesh.SetBlendShapeWeight(i, currentWeights[i] * 100.0f);
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
