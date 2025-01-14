import io
import math
import time
from functools import cache

import librosa
import numpy as np

from .api_client import RespeecherApiClient
from .constants import DEFAULT_FOLDER, DEFAULT_PROJECT, PAGINATION_LIMIT
from .datatypes import Folder, Project, Recording, RecordingStates, User, Voice


class RespeecherTTS:
    def __init__(
        self,
        api_key: str,
        poll_period: float = 0.5,
        timeout: float = 60 * 2,
        verbose: bool = False,
        domain: str = "https://gateway.respeecher.com",
    ):
        self.poll_period = poll_period
        self.timeout = timeout
        self.verbose = verbose
        self.client = RespeecherApiClient(domain, api_key)
        self.user: User = self.client.user_profile()
        self._voices: list[Voice] = []

    @property
    def voices(self) -> list[Voice]:
        if not self._voices:
            self._voices = self._get_voices()
        return self._voices

    def _get_voices(self) -> list[Voice]:
        result = self.client.voice_list()
        voices = result.list
        n_requests = math.ceil(result.pagination.count / PAGINATION_LIMIT)
        for i in range(1, n_requests):
            result = self.client.voice_list(offset=i * PAGINATION_LIMIT)
            voices.extend(result.list)
        voices = [v for v in voices if v.narration_styles]
        return voices

    @cache
    def _lookup_voice_and_ns(
        self, voice_name: str, narration_style_name: str | None = None
    ) -> tuple[str, str]:
        voice = next((v for v in self.voices if v.name == voice_name), None)
        if not voice:
            raise ValueError(f"Voice {voice_name} not found")

        if narration_style_name:
            narration_style = next(
                (
                    ns
                    for ns in voice.narration_styles
                    if ns.name == narration_style_name
                ),
                None,
            )
        else:
            narration_style = next(
                (ns for ns in voice.narration_styles if ns.is_default), None
            )
        if not narration_style:
            raise ValueError(f"Narration style for voice {voice_name} not found")

        if self.verbose:
            print(f"Selected narration style: {narration_style}")
        return voice.id, narration_style.id

    @cache
    def _get_project(self, name: str | None = None) -> Project:
        name = name or DEFAULT_PROJECT
        next_page = True
        offset = 0
        while next_page:
            result = self.client.project_list(offset=offset, owner=self.user.id)
            project = next((p for p in result.list if p.name == name), None)
            if project:
                return project
            if len(result.list) < result.pagination.limit:
                next_page = False
            offset += PAGINATION_LIMIT
        return self.client.create_project(self.user.id, name)

    @cache
    def _get_folder(self, project_id: str, name: str | None = None) -> Folder:
        name = name or DEFAULT_FOLDER
        next_page = True
        offset = 0
        while next_page:
            result = self.client.folder_list(project_id, offset=offset)
            folder = next((f for f in result.list if f.name == name), None)
            if folder:
                return folder
            if len(result.list) < result.pagination.limit:
                next_page = False
            offset += PAGINATION_LIMIT
        return self.client.create_folder(project_id, name)

    def _wait_for_conversion(self, conversion_id, timeout: int) -> Recording:
        start = time.time()
        while True:
            time.sleep(self.poll_period)
            conversion = self.client.get_recording(conversion_id)
            conversion_time = time.time() - start
            if conversion.state == RecordingStates.done:
                if self.verbose:
                    print(f"Conversion finished in {conversion_time} seconds.")
                return conversion
            elif conversion.state == RecordingStates.error:
                raise ValueError(f"Conversion failed with error: {conversion.error}")
            elif conversion_time > timeout:
                raise TimeoutError("Conversion timeout")

    def _download_audio(self, url: str) -> tuple[np.ndarray, int]:
        data = self.client.download_recording(url)
        audio, sample_rate = librosa.load(io.BytesIO(data), sr=None)
        return audio, sample_rate

    def synthesize(
        self,
        text: str,
        voice: str,
        narration_style: str | None = None,
        project_name: str | None = None,
        folder_name: str | None = None,
        return_direct_link: bool = False,
        language: str = "en",
    ) -> str | tuple[np.ndarray, int]:
        project = self._get_project(project_name)
        folder = self._get_folder(project.id, folder_name)
        voice_id, narration_style_id = self._lookup_voice_and_ns(voice, narration_style)
        original = self.client.create_original(folder.id, text, language)
        order = self.client.conversion_order(original.id, voice_id, narration_style_id)
        conversion = self._wait_for_conversion(order.conversion_id, self.timeout)
        if return_direct_link:
            return conversion.url
        else:
            return self._download_audio(conversion.url)
