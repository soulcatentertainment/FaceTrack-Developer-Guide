# Live Capture Integration Samples

## Python UDP Streaming Receiver

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

    [Header("Target Mesh")]
    public SkinnedMeshRenderer faceMesh;

    private Thread receiveThread;
    private UdpClient udpClient;
    private bool isRunning = false;

    private readonly object lockObject = new object();
    private readonly float[] incomingBlendshapes = new float[53];
    private readonly float[] currentWeights = new float[53];
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

                // Extract only the 53 comma-separated blendshape weights
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
        if (faceMesh == null) return;

        lock (lockObject)
        {
            if (!hasNewFrame) return;
            System.Array.Copy(incomingBlendshapes, currentWeights, 53);
            hasNewFrame = false;
        }

        // Apply weights (FaceTrack outputs 0.0–1.0; Unity blendshapes require 0–100)
        int shapeCount = Mathf.Min(53, faceMesh.sharedMesh.blendShapeCount);
        for (int i = 0; i < shapeCount; i++)
        {
            faceMesh.SetBlendShapeWeight(i, currentWeights[i] * 100.0f);
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
