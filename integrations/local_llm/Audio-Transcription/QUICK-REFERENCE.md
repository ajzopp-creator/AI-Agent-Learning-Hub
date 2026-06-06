# LM Studio Transcription - Quick Reference

## Installation (One-Time Setup)

1. **Run SETUP.bat** in the Audio-Transcription folder
2. **Install FFmpeg**: `choco install ffmpeg`
3. **Open LM Studio** → Load model → Start Server

## Daily Usage

### Start LM Studio
1. Open LM Studio
2. Load your Llama model (any model works)
3. Click "Start Server" (Local Server tab)
4. Verify: http://localhost:1234

### Transcribe Audio

**Location:**
```
C:\Users\Trader\AI-Agent-Learning-Hub\03-Local-LLM\Audio-Transcription
```

**Basic Command:**
```powershell
cd scripts
python transcribe_lmstudio.py "path\to\audio.mp3"
```

**With Analysis:**
```powershell
python transcribe_lmstudio.py "audio.mp3" trade_ideas small
```

## Analysis Types

| Type | Use For |
|------|---------|
| `summary` | Quick overview |
| `key_points` | Main ideas and takeaways |
| `trade_ideas` | Trading strategies and market insights |
| `questions` | Study questions for learning |

## Whisper Models

| Model | Speed | Quality | Best For |
|-------|-------|---------|----------|
| `tiny` | Fastest | Basic | Testing, quick drafts |
| `base` | Fast | Good | **Daily use (recommended)** |
| `small` | Moderate | Better | Important content |
| `medium` | Slow | Great | Critical content |
| `large` | Slowest | Best | Maximum accuracy needed |

## Common Workflows

### 1. Morning Podcast Review
```powershell
python transcribe_lmstudio.py "morning_podcast.mp3" summary base
```

### 2. Webinar Analysis
```powershell
python transcribe_lmstudio.py "webinar.mp3" trade_ideas small
```

### 3. Educational Content
```powershell
python transcribe_lmstudio.py "lesson.mp3" key_points base
```

### 4. Generate Study Questions
```powershell
python transcribe_lmstudio.py "tutorial.mp3" questions base
```

## Output Files

All files saved to: `Audio-Transcription\output\`

- `filename_transcript.txt` - Full transcript
- `filename_summary.txt` - Transcript + Llama analysis

## Troubleshooting

**Can't connect to LM Studio?**
- Run `TEST_LMSTUDIO.bat` to check connection
- Make sure server is started in LM Studio

**FFmpeg error?**
- Install: `choco install ffmpeg`
- Or download from: https://ffmpeg.org

**Slow transcription?**
- Use `tiny` or `base` model
- First run downloads model (requires internet)

## Tips

1. **Place audio files** in `audio_files\` folder
2. **Use relative paths**: `python transcribe_lmstudio.py "..\audio_files\file.mp3"`
3. **Start with `base` model** - good speed/quality balance
4. **Keep LM Studio server running** for multiple transcriptions
5. **Check `output\` folder** for results

## Next Steps

1. Test with sample audio
2. Create batch scripts for routine processing
3. Integrate with trade journal
4. Build your trading content library
