from .helpers.superdict import convert, SuperDict
from .helpers.constants import BASE_URL, BASE_MEDIA_URL, IMAGE_PREVIEW, VIDEO_PREVIEW
from .errors import EmptyImage, InvalidToken, ServerError, TooManyRequests

from typing import Union, Optional
from base64 import b64encode
from urllib.parse import quote


try:
    import ujson
except ImportError:
    ujson = False

import aiohttp


class AsyncTrace:

    """Tracemoe class with all the stuff."""

    def __init__(self, api_token: str="", session: Union[aiohttp.ClientSession, bool]=False):
        """Setup all urls and session."""
        self.base_url = BASE_URL
        self.media_url = BASE_MEDIA_URL
        self.api_token = api_token
        if not session:
            self.aio_session = aiohttp.ClientSession(
                # headers = {"Content-Type": "application/json"}
            )
        else:
            self.aio_session = session

    async def get_me(self) -> SuperDict:
        """
        Lets you check the search quota and limit for your account (or IP address).
        Returns:
          SuperDict: response from server
        """
        url = f"{self.base_url}me"
        if self.api_token:
            url += f"?token={self.api_token}"
        response = await self.aio_session.get(url)
        if ujson:
            return convert((await response.json(loads = ujson.loads)))
        return convert((await response.json()))

    async def search(
        self, path: str, encode: bool = False, upload_file=False, is_url: bool = False
    ) -> SuperDict:
        """
        Args:
           path: Image url or Img file name or base64 encoded Image or Image path
           encode: True if Img file name is given
           is_url: Treat the path as a url or not
           upload_file: Upload file
        Returns:
           SuperDict: response from server
        Raises:
           EmptyImage: Raised If Image Is empty
           InvalidToken: Raised when token provided Is Invalid
           ServerError: Raised If server Is having problem or Image Is malformed.
           TooManyRequests: Raised when you are making too many requests
        """
        url = f"{self.base_url}api/search"
        if self.api_token:
            url += f"?token={self.api_token}"

        if is_url:
            response = await self.aio_session.get(url, params={"url": path})
        elif upload_file:
            response = await self.aio_session.post(
                url, data={"image": open(path, "rb")}
            )
        elif encode:
            with open(path, "rb") as f:
                encoded = b64encode(f.read()).decode("utf-8")
                response = await self.aio_session.post(url, json={"image": encoded})
        else:
            response = await self.aio_session.post(url, json={"image": encoded})
        if response.status == 200:
            if ujson:
                return convert((await response.json(loads = ujson.loads)))
            return convert((await response.json()))
        elif response.status == 400:
            raise EmptyImage("Image provided was empty!")
        elif response.status == 403:
            raise InvalidToken("You are using Invalid token!")
        elif response.status in [500, 503]:
            raise ServerError("Image is malformed or Something went wrong")
        elif response.status == 429:
            raise TooManyRequests(response.text)
        else:
            raise ServerError(f"Unknown error: {response.status}")

    async def create_preview(
        self,
        json: Union[dict, SuperDict],
        path: str,
        index: int = 0,
    ) -> bytes:
        """
        Args:
           json: Python dict given by search
           index: Which result to get
           path: Path to use, preview.php, thumbnail.php etc.
        Returns:
           bytes: Video/Image content
        """
        json = json["docs"][index]
        url = (
            f"{self.base_url}{path}?anilist_id={json['anilist_id']}"
            f"&file={quote(json['filename'])}&t={json['at']}&token={json['tokenthumb']}"
        )
        return await (await self.aio_session.get(url)).content.read()

    async def natural_preview(
        self, response: Union[dict, SuperDict], index: int = 0, mute: bool = False
    ) -> bytes:
        """
        Video Preview with Natural Scene Cutting
        Args:
            response: server response
            index: which result to get
            mute: mute video or not.
        Returns:
            bytes: Video content
        """
        response = response["docs"][index]
        url = (
            f'{self.media_url}video/{response["anilist_id"]}/'
            f'{quote(response["filename"])}?t={response["at"]}&token={response["tokenthumb"]}'
        )
        if mute:
            url += "&mute"
        return await (await self.aio_session.get(url)).content.read()

    async def image_preview(
        self, json: Union[dict, SuperDict], index: int = 0
    ) -> bytes:
        """
        Args:
           json: Python dict given by search
           index: Which result to get
        Returns:
           bytes: Video content
        """
        return await self.create_preview(json, IMAGE_PREVIEW, index)

    async def video_preview(
        self, json: Union[dict, SuperDict], index: int = 0
    ) -> bytes:
        """
        Args:
           json: Python dict given by search
           index: Which result to get
        Returns:
           bytes: Video content
        """
        return await self.create_preview(json, VIDEO_PREVIEW, index)


Async_Trace = AsyncTrace
