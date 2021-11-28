import enum
from typing import Optional, Final, Callable, Awaitable, Union, Dict

from vkwave import __api_version__
from vkwave.api.methods._error import APIError
from vkwave.http.http import AbstractHTTPClient, AIOHTTPClient


async def get_code_from_input() -> str:
    return input("Enter code: ")


class VKAuthType(enum.Enum):
    Android = "android"
    IPhone = "iphone"
    IPad = "ipad"
    WindowsPhone = "windows_phone"
    VKMe = "vk_me"
    KateMobile = "kate_mobile"
    Windows = "windows"


_auth_types: Dict[VKAuthType, Dict[str, Union[int, str]]] = {
    VKAuthType.Android: {
        "id": 2274003,
        "secret": "hHbZxrka2uZ6jB1inYsH"
    },
    VKAuthType.IPhone: {
        "id": 3140623,
        "secret": "VeWdmVclDCtn6ihuP1nt"
    },
    VKAuthType.IPad: {
        "id": 3140623,
        "secret": "VeWdmVclDCtn6ihuP1nt"
    },
    VKAuthType.WindowsPhone: {
        "id": 3140623,
        "secret": "VeWdmVclDCtn6ihuP1nt"
    },
    VKAuthType.VKMe: {
        "id": 3140623,
        "secret": "VeWdmVclDCtn6ihuP1nt"
    },
    VKAuthType.KateMobile: {
        "id": 3140623,
        "secret": "VeWdmVclDCtn6ihuP1nt"
    },
    VKAuthType.Windows: {
        "id": 3140623,
        "secret": "VeWdmVclDCtn6ihuP1nt"
    },
}


class VKAuth:
    AUTH_URL: Final = "https://oauth.vk.com/token"
    API_URL: Final = "https://api.vk.com/method/auth.validatePhone"

    def __init__(
        self,
        client_http: Optional[AbstractHTTPClient] = None,
        client_id: Optional[int] = None,
        client_secret: Optional[str] = None,
        auth_type: Optional[VKAuthType] = None,
    ):
        auth_type = _auth_types.get(auth_type, dict())

        self.client = client_http or AIOHTTPClient()
        self.client_id = client_id or auth_type.get("id") or _auth_types[VKAuthType.Android]["id"]
        self.client_secret = client_secret or auth_type.get("secret") or _auth_types[VKAuthType.Android]["secret"]

    async def _get_token(
        self,
        login: str,
        password: str,
        dfa: bool = False,
        code: Optional[str] = None,
        scope: Optional[str] = None
    ) -> Dict[str, str]:
        params = {
            "grant_type": "password",
            "scope": scope or "all",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "username": login,
            "password": password,
            "2fa_supported": 1,
        }

        if dfa:
            params["code"] = code or ""

        return await self.client.request_json(method="POST", url=self.AUTH_URL, data=params)

    async def get_token(
        self,
        login: str,
        password: str,
        get_code: Optional[Callable[[], Awaitable[str]]] = None,
        scope: Optional[str] = None,
        return_raw_response: bool = False
    ) -> Union[Dict[str, str], str]:
        response = await self._get_token(login=login, password=password, scope=scope)
        get_code = get_code or get_code_from_input

        if "validation_sid" in response:
            await self.client.request_json(method="POST", url=self.API_URL, data={
                "sid": response["validation_sid"],
                "v": __api_version__
            })
            code = await get_code()
            response = await self._get_token(login=login, password=password, dfa=True, code=code, scope=scope)

        if "error" in response:
            raise APIError(5, response["error_description"], response)

        if return_raw_response:
            return response

        return response["access_token"]
