# LM Studio Audio Transcription System

## Quick Start

### 1. Install Required Packages

```powershell
cd C:\Users\Trader\AI-Agent-Learning-Hub
.\venv\Scripts\Activate
python -m pip install openai-whisper requests --break-system-packages
```

### 2. Install FFmpeg (if not already installed)

```powershell
choco install ffmpeg
```

### 3. Start LM Studio

1. Open LM Studio
2. Load your Llama model
3. Go to "Local Server" tab
4. Click "Start Server" (should run on port 1234)

### 4. Run Transcription

```powershell
cd C:\Users\Trader\AI-Agent-Learning-Hub\03-Local-LLM\Audio-Transcription\scripts

# Basic usage
python transcribe_lmstudio.py "C:\path\to\audio.mp3"

# With analysis type
python transcribe_lmstudio.py "C:\path\to\audio.mp3" trade_ideas

# With specific Whisper model
python transcribe_lmstudio.py "C:\path\to\audio.mp3" summary small
```

## Analysis Types

- **summary** - Get a concise summary
- **key_points** - Extract main ideas
- **trade_ideas** - Extract trading strategies and insights
- **questions** - Generate study questions

## Whisper Models

- **tiny** - Fastest, basic accuracy (~75MB)
- **base** - Good balance (default) (~142MB)
- **small** - Better accuracy (~466MB)
- **medium** - High accuracy (~1.5GB)
- **large** - Best accuracy (~2.9GB)

## Folder Structure

- `scripts/` - Python scripts
- `audio_files/` - Place your audio files here
- `output/` - Transcripts and analyses saved here

## Example Workflows

### Transcribe Trading Podcast
```powershell
python transcribe_lmstudio.py "..\audio_files\podcast.mp3" summary base
```

### Extract Trade Ideas from Webinar
```powershell
python transcribe_lmstudio.py "..\audio_files\webinar.mp3" trade_ideas small
```

### Generate Study Questions
```powershell
python transcribe_lmstudio.py "..\audio_files\lesson.mp3" questions base
```

## Troubleshooting

**"Could not connect to LM Studio"**
- Make sure LM Studio is open
- Load a model
- Start the server (Local Server tab)

**"FFmpeg not found"**
- Install with: `choco install ffmpeg`
- Or download from: https://ffmpeg.org/download.html

**"Model not found" (Whisper)**
- First run downloads the model
- Models are cached in `~\.cache\whisper\`
- Requires internet connection for initial download

## Next Steps

1. Test with a short audio file
2. Create custom analysis types (edit the prompts dictionary)
3. Build automation scripts for batch processing
4. Integrate with your trade journal workflow

