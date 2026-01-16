import requests
BASE_URL = "http://127.0.0.1:80/api/v1"
API_KEY = "ragflow-HhmzuFOMEAtRtP6r0W9tejEhNYxUMejhsIGBt6WYTrE"
CHAT_ID = "b03d7a22f2f711f0894a26afde3a2d3d"
def create_session(session_name):
   url = f"{BASE_URL}/chats/{CHAT_ID}/sessions"
   headers = {
       "Authorization": f"Bearer {API_KEY}",
       "Content-Type": "application/json"
   }
   params = {"name": session_name}
   resp = requests.post(url, headers=headers, json=params).json()
   print(resp)
   return resp['data']['id']

def converse(session_id, question):
   url = f"{BASE_URL}/chats/{CHAT_ID}/completions"
   headers = {
       "Authorization": f"Bearer {API_KEY}",
       "Content-Type": "application/json"
   }
   params = {
       "session_id": session_id,
       "question": question,
       "stream": False
   }
   resp = requests.post(url, headers=headers, json=params).json()
   return resp['data']['answer']

def delete_session(session_id):
   url = f"{BASE_URL}/chats/{CHAT_ID}/sessions"
   headers = {
       "Authorization": f"Bearer {API_KEY}",
       "Content-Type": "application/json"
   }
   params = {"ids": [session_id]}
   requests.delete(url, headers=headers, json=params)