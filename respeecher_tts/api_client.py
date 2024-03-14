from requests import Session

from .constants import PAGINATION_LIMIT
from .datatypes import (
    Folder,
    FolderListResponse,
    Order,
    Project,
    ProjectListResponse,
    Recording,
    User,
    VoiceListResponse,
)


class RespeecherApiClient:
    def __init__(self, domain: str, api_key: str) -> None:
        self.domain = domain
        self.session = Session()
        self.session.headers.update(
            {"api-key": api_key, "content-type": "application/json"}
        )

    def user_profile(self) -> User:
        result = self.session.post(
            f"{self.domain}/api/auth",
        )
        result.raise_for_status()
        return User.model_validate(result.json())

    def voice_list(self, offset: int = 0) -> VoiceListResponse:
        result = self.session.get(
            f"{self.domain}/api/v2/voices",
            params={
                "limit": PAGINATION_LIMIT,
                "offset": offset,
                "sort": "name",
                "direction": "asc",
            },
        )
        result.raise_for_status()
        return VoiceListResponse.model_validate(result.json())

    def project_list(
        self, offset: int = 0, owner: str | None = None
    ) -> ProjectListResponse:
        data = {"limit": PAGINATION_LIMIT, "offset": offset}
        if owner:
            data["owner"] = owner
        result = self.session.get(
            f"{self.domain}/api/projects",
            params=data,
        )
        result.raise_for_status()
        return ProjectListResponse.model_validate(result.json())

    def create_project(self, user_id: str, name: str | None = None) -> Project:
        data = {"owner": user_id, "models": {}}
        if name:
            data["name"] = name
        result = self.session.post(f"{self.domain}/api/projects", json=data)
        result.raise_for_status()
        return Project.model_validate(result.json())

    def folder_list(self, project_id: str, offset: int = 0) -> FolderListResponse:
        result = self.session.get(
            f"{self.domain}/api/folders",
            params={
                "project_id": project_id,
                "limit": PAGINATION_LIMIT,
                "offset": offset,
            },
        )
        result.raise_for_status()
        return FolderListResponse.model_validate(result.json())

    def create_folder(self, project_id: str, name: str | None = None) -> Folder:
        data = {"project_id": project_id}
        if name:
            data["name"] = name
        result = self.session.post(f"{self.domain}/api/folders", json=data)
        result.raise_for_status()
        return Folder.model_validate(result.json())

    def create_original(self, folder_id: str, text: str) -> Recording:
        result = self.session.post(
            f"{self.domain}/api/v2/recordings/tts",
            json={"parent_folder_id": folder_id, "text": text},
        )
        result.raise_for_status()
        return Recording.model_validate(result.json())

    def get_recording(self, recording_id: str) -> Recording:
        result = self.session.get(
            f"{self.domain}/api/recordings/{recording_id}",
        )
        result.raise_for_status()
        return Recording.model_validate(result.json())

    def download_recording(self, url: str) -> bytes:
        result = self.session.get(f"{self.domain}{url}")
        result.raise_for_status()
        return result.content

    def conversion_order(
        self, original_id: str, voice_id: str, narration_style_id: str
    ) -> Order:
        result = self.session.post(
            f"{self.domain}/api/v2/orders",
            json={
                "original_id": original_id,
                "conversions": [
                    {
                        "voice_id": voice_id,
                        "narration_style_id": narration_style_id,
                    }
                ],
            },
        )
        result.raise_for_status()
        return Order.model_validate(result.json()[0])
