#!/usr/bin/env python3
"""
Test CosyVoice TTS API
"""
import os
import dashscope
from dashscope.audio.tts_v2 import SpeechSynthesizer
from dotenv import load_dotenv

load_dotenv()

# Set API key
dashscope.api_key = os.getenv("DASHSCOPE_API_KEY")
print(f"API Key: {dashscope.api_key[:20]}...")

# Test voice list
print("\n=== Testing available voices ===")
voices_to_test = ['longxiaochun', 'longjun', 'stella']

for voice in voices_to_test:
    print(f"\n--- Testing voice: {voice} ---")
    try:
        synthesizer = SpeechSynthesizer(model='cosyvoice-v3-plus', voice=voice)
        text = "你好，世界。" if voice.startswith('long') else "Hello world."
        print(f"Synthesizing text: {text}")

        audio_data = synthesizer.call(text)

        if audio_data:
            print(f"✓ Success! Generated {len(audio_data)} bytes of audio")
            # Save to file
            filename = f"/tmp/test_{voice}.mp3"
            with open(filename, 'wb') as f:
                f.write(audio_data)
            print(f"✓ Saved to {filename}")
        else:
            print("✗ No audio data returned")

    except Exception as e:
        print(f"✗ Error: {e}")

print("\n=== Test completed ===")
