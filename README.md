# Marketplace Python TTS API client

The official Python API client for [Respeecher Marketplace](https://marketplace.respeecher.com/) TTS.

## TTS Docs

- [API overview](https://docs.respeecher.com/)
- [OpenAPI](https://gateway.respeecher.com/api/docs)

## Installation

Marketplace Python TTS API client requires Python 3.11 or higher.

```bash
pip install .
```

### Poetry 

Marketplace Python TTS API client recommends Poetry 1.7.11 or higher.

```bash
poetry shell
poetry install
```

## Usage example

```python
from respeecher_tts import RespeecherTTS
import soundfile as sf

tts = RespeecherTTS(api_key="<Respeecher_API_Token>", verbose=True)

print("All Voices:", [voice.name for voice in tts.voices])
print(
    f"Narration Styles for {tts.voices[0].name} voice:",
    [narration_style.name for narration_style in tts.voices[0].narration_styles],
)

au, sr = tts.synthesize(
    "In the quiet morning, the gentle breeze whispered through the leaves, bringing with it the promise of a new day.",
    voice="Roman",
    narration_style="Mellow, Raspy, Neutral",
)

# sf.write will reduce the bit depth to 16-bit by default, to avoid this we specify 'PCM_24'
sf.write("tts_sample.wav", au, sr, 'PCM_24')
```
