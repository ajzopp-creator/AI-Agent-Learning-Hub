"""
Audio Transcription using Standalone Whisper + LM Studio for Analysis
"""

import os
import sys
import whisper
import requests
import json
from pathlib import Path

class LMStudioTranscriber:
    def __init__(self, lm_studio_url="http://localhost:1234/v1"):
        """
        Initialize transcriber with LM Studio connection
        
        Args:
            lm_studio_url: LM Studio server URL (default: http://localhost:1234/v1)
        """
        self.lm_studio_url = lm_studio_url
        self.whisper_model = None
        
    def load_whisper_model(self, model_size="base"):
        """
        Load Whisper model for transcription
        
        Args:
            model_size: tiny, base, small, medium, large
        """
        print(f"Loading Whisper {model_size} model...")
        self.whisper_model = whisper.load_model(model_size)
        print("Model loaded successfully!")
        
    def transcribe_audio(self, audio_file):
        """
        Transcribe audio file using Whisper
        
        Args:
            audio_file: Path to audio file
            
        Returns:
            Transcription text
        """
        if not self.whisper_model:
            self.load_whisper_model()
            
        print(f"\nTranscribing: {audio_file}")
        print("This may take a few minutes...")
        
        result = self.whisper_model.transcribe(audio_file)
        
        return result['text']
    
    def analyze_with_llama(self, transcript, analysis_type="summary"):
        """
        Send transcript to LM Studio Llama for analysis
        
        Args:
            transcript: Transcription text
            analysis_type: summary, key_points, trade_ideas, etc.
            
        Returns:
            Analysis from Llama
        """
        
        prompts = {
            "summary": f"Please provide a concise summary of this transcript:\n\n{transcript}",
            "key_points": f"Extract the key points and main ideas from this transcript:\n\n{transcript}",
            "trade_ideas": f"Analyze this trading-related transcript and extract actionable trading ideas, strategies, and important market insights:\n\n{transcript}",
            "questions": f"Generate thoughtful follow-up questions based on this transcript:\n\n{transcript}"
        }
        
        prompt = prompts.get(analysis_type, prompts["summary"])
        
        print(f"\nSending to LM Studio for {analysis_type}...")
        
        try:
            response = requests.post(
                f"{self.lm_studio_url}/chat/completions",
                headers={"Content-Type": "application/json"},
                json={
                    "model": "llama-4-scout-17b-16e-instruct",
                    "messages": [
                        {"role": "system", "content": "You are a helpful AI assistant analyzing audio transcripts for a trader."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 3000
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                return f"Error: {response.status_code} - {response.text}"
                
        except requests.exceptions.ConnectionError:
            return "Error: Could not connect to LM Studio. Make sure LM Studio is running with a model loaded and server started."
        except Exception as e:
            return f"Error: {str(e)}"
    
    def transcribe_and_analyze(self, audio_file, analysis_type="summary", save_output=True):
        """
        Complete workflow: Transcribe audio and analyze with Llama
        
        Args:
            audio_file: Path to audio file
            analysis_type: Type of analysis to perform
            save_output: Save results to files
            
        Returns:
            Dictionary with transcript and analysis
        """
        
        # Step 1: Transcribe
        transcript = self.transcribe_audio(audio_file)
        
        print(f"\n{'='*60}")
        print("TRANSCRIPT")
        print(f"{'='*60}")
        print(transcript)
        print(f"{'='*60}\n")
        
        # Step 2: Analyze with Llama
        analysis = self.analyze_with_llama(transcript, analysis_type)
        
        print(f"\n{'='*60}")
        print(f"{analysis_type.upper()} (by Llama)")
        print(f"{'='*60}")
        print(analysis)
        print(f"{'='*60}\n")
        
        # Step 3: Save outputs
        if save_output:
            base_name = Path(audio_file).stem
            output_dir = Path(__file__).parent.parent / "output"
            
            # Save transcript
            transcript_file = output_dir / f"{base_name}_transcript.txt"
            with open(transcript_file, 'w', encoding='utf-8') as f:
                f.write(transcript)
            print(f"Transcript saved: {transcript_file}")
            
            # Save analysis
            analysis_file = output_dir / f"{base_name}_{analysis_type}.txt"
            with open(analysis_file, 'w', encoding='utf-8') as f:
                f.write(f"TRANSCRIPT:\n{transcript}\n\n")
                f.write(f"{'='*60}\n\n")
                f.write(f"{analysis_type.upper()}:\n{analysis}\n")
            print(f"Analysis saved: {analysis_file}")
        
        return {
            'transcript': transcript,
            'analysis': analysis
        }


def main():
    """Command line interface"""
    
    if len(sys.argv) < 2:
        print("Usage: python transcribe_lmstudio.py <audio_file> [analysis_type] [whisper_model]")
        print("\nAnalysis Types:")
        print("  - summary (default)")
        print("  - key_points")
        print("  - trade_ideas")
        print("  - questions")
        print("\nWhisper Models: tiny, base, small, medium, large")
        print("  - base (default) - Good balance of speed/accuracy")
        print("  - small - Better accuracy, slower")
        print("  - medium - High accuracy, much slower")
        print("\nExample: python transcribe_lmstudio.py podcast.mp3 trade_ideas small")
        sys.exit(1)
    
    audio_file = sys.argv[1]
    analysis_type = sys.argv[2] if len(sys.argv) > 2 else "summary"
    whisper_model = sys.argv[3] if len(sys.argv) > 3 else "base"
    
    if not os.path.exists(audio_file):
        print(f"Error: Audio file not found: {audio_file}")
        sys.exit(1)
    
    # Check if LM Studio is running
    print("Checking LM Studio connection...")
    try:
        response = requests.get("http://localhost:1234/v1/models", timeout=2)
        if response.status_code == 200:
            print("✓ LM Studio is running and ready")
        else:
            print("⚠ LM Studio may not be ready. Make sure a model is loaded.")
    except:
        print("⚠ Warning: Could not connect to LM Studio")
        print("  Make sure LM Studio is running with a model loaded")
        print("  (Server must be started in LM Studio)")
    
    # Run transcription and analysis
    transcriber = LMStudioTranscriber()
    transcriber.load_whisper_model(whisper_model)
    transcriber.transcribe_and_analyze(audio_file, analysis_type)

if __name__ == "__main__":
    main()

