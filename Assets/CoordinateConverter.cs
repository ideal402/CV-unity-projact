using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class CoordinateConverter : MonoBehaviour
{
    // 직각 좌표계에서의 x, y, z 값
    public float xCoordinate;
    public float yCoordinate;
    public float zCoordinate;
    public Vector3 position;
    
    public Transform RightArm;
    public Transform start;
    public Transform end;
    void Start()
    {
        // Debug.Log("start");
        RightArm = transform;
    }

    void Update(){
        
        Vector3 startP = start.position;
        Vector3 endP = end.position;
        
        position = new Vector3(startP.x-endP.x,startP.y-endP.y,startP.z-endP.z);
        
        // Debug.Log(position);

        SetObjectRotation();
    }


    

    void SetObjectRotation()
    {
        Vector3 eulerRotation = Quaternion.LookRotation(position.normalized,Vector3.up).eulerAngles + new Vector3(270, 0, 0);
        Quaternion newRotation = Quaternion.Euler(eulerRotation);
        // Debug.Log("neR:"+eulerRotation);
        // 오브젝트의 rotation을 새로운 값으로 설정
        RightArm.rotation = newRotation;
    }
}

