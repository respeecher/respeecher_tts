from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class User(BaseModel):
    id: str
    email: str
    username: str
    verified: bool
    roles: list[str]


class Pagination(BaseModel):
    count: int
    limit: int
    offset: int


class NarrationStyleTag(BaseModel):
    name: str


class NarrationStyle(BaseModel):
    id: str
    is_default: bool
    tags: list[NarrationStyleTag]
    name: str | None = None


class Voice(BaseModel):
    id: str
    name: str
    narration_styles: list[NarrationStyle]


class VoiceListResponse(BaseModel):
    list: list[Voice]
    pagination: Pagination


class Project(BaseModel):
    id: str
    name: str
    owner: str
    slug: str
    created_at: datetime


class ProjectListResponse(BaseModel):
    list: list[Project]
    pagination: Pagination


class Folder(BaseModel):
    id: str
    name: str
    project_id: str
    created_at: datetime


class FolderListResponse(BaseModel):
    list: list[Folder]
    pagination: Pagination


class RecordingStates(str, Enum):
    processing = "processing"
    postprocessing = "postprocessing"
    done = "done"
    error = "error"


class RecordingTypes(str, Enum):
    original = "original"
    converted = "converted"


class Recording(BaseModel):
    id: str
    project_id: str
    parent_folder_id: str
    type: RecordingTypes
    state: RecordingStates
    url: str | None
    text: str | None
    error: str | None
    created_at: datetime


class Order(BaseModel):
    id: str
    original_id: str
    conversion_id: str
    created_at: datetime
