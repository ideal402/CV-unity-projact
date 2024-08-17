using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.SceneManagement;

public class Change : MonoBehaviour
{
    public string sceneToLoad = "MainScene";

    public void ChangeScene()
    {   
        SceneManager.LoadScene(sceneToLoad);
    }
}
