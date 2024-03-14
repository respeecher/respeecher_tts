# Respeecher Python TTS API

## Installation

Respeecher Python TTS API requires Python 3.11 or higher.

```
pip install .
```

## Usage example

```python
from tts_api import RespeecherTTS
import soundfile as sf

tts = RespeecherTTS(api_key="<Respeecher_API_Token>", verbose=True)

print("All Voices:", [voice.name for voice in tts.voices])
print(
    f"Narration Styles for {tts.voices[0].name} voice:",
    [narration_style.info.name for narration_style in tts.voices[0].narration_styles],
)

au, sr = tts.synthesize(
    "In the quiet morning, the gentle breeze whispered through the leaves, bringing with it the promise of a new day.",
    voice="Vincent",
    narration_style="Neutral",
)

sf.write("tts_sample.wav", au, sr)
```