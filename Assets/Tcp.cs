using System;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using System.IO;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using System.Diagnostics;
using UnityEngine;
using UnityEngine.UI;

public class Tcp : MonoBehaviour
{
    IPAddress localCurrentIP;
    private Thread tcpListenerThread;
    private TcpListener tcpListener;
    private TcpClient connectedTcpClient;
    [SerializeField]
    private Text ShowInformation;
    [SerializeField]
    private Text StateText;
    private int port = 8053;
    string clientMessage;

    private static Tcp _instance;
    
    public int i;
    
    private Queue<float> myQueue = new Queue<float>();
    public GameObject[] Body;
    List<string> lines;
    float timer = 0f;
    float updateInterval = 1f / 15f;
    int StartFlag;
    public Vector3 position = new Vector3(0,0,0);


    
    void Start()
    {
        DontDestroyOnLoad(gameObject);
        IPAddress[] localIPs = Dns.GetHostAddresses(Dns.GetHostName());
        foreach (IPAddress addr in localIPs)
        {
            if (addr.AddressFamily == AddressFamily.InterNetwork)
            {
                UnityEngine.Debug.Log("현재 사용하고 있는 ip주소 : " + addr);
                ShowInformation.text = string.Format("IP : {0}" + System.Environment.NewLine + "port : {1}", addr, port);
                localCurrentIP = addr;
            }
        }
        
        tcpListenerThread = new Thread(new ThreadStart(ListenForIncomingRequests));
        tcpListenerThread.IsBackground = true;
        tcpListenerThread.Start();
        StateText.text = string.Format("Server is listening");
        
    }
    
    
    private void ListenForIncomingRequests()
    {
        try
        {
            tcpListener = new TcpListener(localCurrentIP, port);
            tcpListener.Start();
            UnityEngine.Debug.Log("Server is listening");

            Byte[] bytes = new Byte[1024 * 40];
            
            while (true)
            {
                using (connectedTcpClient = tcpListener.AcceptTcpClient())
                {
                    using (NetworkStream stream = connectedTcpClient.GetStream())
                    {
                        int length;
                        while ((length = stream.Read(bytes, 0, bytes.Length)) != 0)
                        {
                            var incommingData = new byte[length];
                            Array.Copy(bytes, 0, incommingData, 0, length);
                            string clientMessage = Encoding.ASCII.GetString(incommingData);
                            UnityEngine.Debug.Log(clientMessage);

                            // UnityEngine.Debug.Log("length : " + length);
                            
                            if (clientMessage[0] == '[')
                            {
                                string[] textArray = clientMessage.Substring(1, clientMessage.Length - 2).Split(new[] { ' ' }, StringSplitOptions.RemoveEmptyEntries);
                                // Process the text array and add integers to the global buffer
                                for (int i = 0; i < 3 * 3; i++)
                                {
                                    if (i < textArray.Length)
                                    {
                                        if (float.TryParse(textArray[i], out float FloatValue))
                                        {
                                            myQueue.Enqueue(FloatValue);
                                            //UnityEngine.Debug.Log("getnum");
                                        }
                                        else
                                        {
                                            UnityEngine.Debug.LogError($"Failed to parse {textArray} as an integer.");
                                        }
                                    }
                                    else
                                    {
                                        UnityEngine.Debug.LogError("Not enough elements in the text array.");
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        catch (SocketException socketException)
        {
            UnityEngine.Debug.Log("SocketException " + socketException.ToString());
        }
    }

    public void SendMessageToClient(string message)
    {
        if (connectedTcpClient == null)
        {
            StateText.text = string.Format("Error: Please Check The Connection");
            UnityEngine.Debug.LogError("Not connected to any client.");
            return;
        }
        try
        {   
            StateText.text = string.Format("Now connecting...");
            NetworkStream stream = connectedTcpClient.GetStream();
            byte[] bytesToSend = Encoding.ASCII.GetBytes(message);
            stream.Write(bytesToSend, 0, bytesToSend.Length);
            UnityEngine.Debug.Log("Message sent to client: " + message);
            StateText.text = string.Format("Connection success");
            StartFlag = 1;
        }
        catch (Exception e)
        {
            UnityEngine.Debug.LogError("Error sending message to client: " + e.Message);
        }
    }

    void Update()
    {
        if (StartFlag == 1)
        {
            timer += Time.deltaTime;
            // updateInterval 시간마다 업데이트
            while (timer >= updateInterval)
            {
                if (myQueue.Count > 1)
                {
                    float[] x = new float[3]{0,0,0};
                    float[] y = new float[3]{0,0,0};
                    float[] z = new float[3]{0,0,0};
                    for (int i = 0; i < 3; i++)
                    {    
                        x[i] = -myQueue.Dequeue()/100;
                        
                        y[i] = myQueue.Dequeue()/100;
                        
                        z[i] = myQueue.Dequeue()/100;
                        
                        Body[i].transform.localPosition = new Vector3(x[i], y[i], z[i]);
                    
                        //UnityEngine.Debug.Log(i+"  "+Body[i].transform.localPosition);
                    }     
                }
                else
                {
                    UnityEngine.Debug.Log("null");
                }
                timer -= updateInterval;
            }
        }
    }


    
}
