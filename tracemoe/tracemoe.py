from base64 import b64encode
from requests import Session

class tracemoe:
    def __init__(self, api_token=""):
        self.base_url = "https://trace.moe/"
        self.media_url = "https://media.trace.moe/"
        self.api_token = api_token
        self.r_session = Session()
        self.session.headers = {
            "Content-Type": "application/json"
        }
    
    def search(self, path, encode=True, is_url=False):
        url = f"{self.base_url}/api/search"
        if self.api_token:
            url += f"?token={self.api_token}"

        if is_url:
            return self.r_session.get(
                url, params={"url": path}
            ).json()

        elif encode:
            with open(path, "rb") as f:
                encoded = b64encode(f.read()).decode("utf-8")
                return self.r_session.post(
                url, json={"image": encoded}
                ).json()
        else:
            return self.r_session.post(
                url, json={"image": encoded}
                ).json()
    
    def create_preview(self, json, index = 0, path)
        json = json["docs"][index]
        url = f"{self.base_url}/{path}?anilist_id={json['anilist_id']}"\
              f"&file={json['file_name']}&t={json['at']}&token]{json['tokenthumb']}"
        return self.session.get(url).content
    
    def video_preview(self, json, index = 0):
        return self.create_preview(json, index, 'preview.php')
        
        
        