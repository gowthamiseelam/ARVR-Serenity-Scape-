using UnityEngine;
using UnityEngine.Networking;
using System.Collections;

public class EmotionFetcher : MonoBehaviour
{
    public EmotionSceneManager sceneManager;
    private string url = "http://127.0.0.1:5000/detect_emotion";
    public string emotion = "default";

    void Start()
    {
        if (string.IsNullOrEmpty(url))
        {
            Debug.LogError("URL for emotion detection is not set.");
            return;
        }
        StartCoroutine(CheckEmotion());
    }

    IEnumerator CheckEmotion()
    {
        while (true)
        {
            Debug.Log("Fetching emotion from webcam: " + url);
            UnityWebRequest request = UnityWebRequest.Get(url);
            yield return request.SendWebRequest();

            if (request.result == UnityWebRequest.Result.Success)
            {
                string jsonResponse = request.downloadHandler.text;
                Debug.Log("Received JSON response: " + jsonResponse);

                try
                {
                    string detectedEmotion = JsonUtility.FromJson<EmotionResponse>(jsonResponse).emotion;
                    emotion = string.IsNullOrEmpty(detectedEmotion) ? "default" : detectedEmotion;
                    Debug.Log("Emotion detected: " + emotion);
                    sceneManager.SwitchScene(emotion);
                }
                catch (System.Exception ex)
                {
                    Debug.LogError("Failed to parse emotion response: " + ex.Message);
                    emotion = "default";
                }
            }
            else
            {
                Debug.LogError("Failed to get emotion: " + request.error);
                emotion = "default";
            }

            yield return new WaitForSeconds(10f); // Check emotion every 10 seconds

            // Reset to default after each check
            emotion = "default";
            sceneManager.SwitchScene(emotion);
            Debug.Log("Reset emotion to default");
        }
    }

    [System.Serializable]
    private class EmotionResponse
    {
        public string emotion;
    }
}
