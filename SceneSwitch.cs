using UnityEngine;
using UnityEngine.SceneManagement;

public class EmotionSceneManager : MonoBehaviour
{
    // Call this method with detected emotion
    public void SwitchScene(string emotion)
    {
        switch (emotion.ToLower())
        {
            case "happy":
                SceneManager.LoadScene("Happy");
                break;
            case "sad":
                SceneManager.LoadScene("Sad");
                break;
            case "neutral":
                SceneManager.LoadScene("Neutral");
                break;
            case "angry":
                SceneManager.LoadScene("Angry");
                break;
            default:
                SceneManager.LoadScene("default");
                break;
        }
    }
}
