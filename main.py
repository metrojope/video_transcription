import os
import subprocess
import whisper
import warnings
from yt_dlp import YoutubeDL
from translate import Translator
import tempfile
from openai import OpenAI
import requests

# Suppress specific warnings
warnings.filterwarnings("ignore", message="FP16 is not supported on CPU; using FP32 instead")

# Set your OpenAI API key
client = OpenAI(
  api_key=""
)

def download_video(url, output_path):
    ydl_opts = {"outtmpl": output_path, "format": "bestaudio/best"}
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

def extract_audio(video_path, audio_path):
    # Use the absolute path to ffmpeg
    ffmpeg_path = r"C:\ffmpeg\bin\ffmpeg.exe"  # Replace with the actual path to ffmpeg

    # Generate a new filename if the audio file already exists
    base, ext = os.path.splitext(audio_path)
    counter = 1
    new_audio_path = audio_path
    while os.path.exists(new_audio_path):
        new_audio_path = f"{base}_{counter}{ext}"
        counter += 1

    # Debugging information
    print(f"Extracting audio from {video_path} to {new_audio_path}")

    result = subprocess.run([ffmpeg_path, "-i", video_path, "-q:a", "0", "-map", "a", new_audio_path, "-y"], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error extracting audio: {result.stderr}")
    else:
        print(f"Audio extracted successfully to {new_audio_path}")
    return new_audio_path

def transcribe_audio(audio_path):
    if not os.path.exists(audio_path):
        print(f"Audio file {audio_path} does not exist.")
        return None
    model = whisper.load_model("base")
    result = model.transcribe(audio_path)
    return result['text']

def translate_text(text, dest_language="pt"):
    translator = Translator(to_lang=dest_language)
    try:
        translation = translator.translate(text)
        return translation
    except Exception as e:
        print(f"Translation failed: {e}")
        return None

def fetch_examples():
    response = requests.get('http://127.0.0.1:8080/examples')
    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to fetch examples")
        return []

def adapt_text_to_style(text):
    examples = fetch_examples()
    examples_text = "\n".join(examples)
    prompt = f"{examples_text}\n\nAdapt this text to my style: {text}"
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        store=True,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=500,
        n=1,
        stop=None,
        temperature=0.7,
    )
    adapted_text = response.choices[0].message['content'].strip()
    return adapted_text

if __name__ == "__main__":
    while True:
        video_url = input("Enter the video URL (or type 'exit' to quit): ")
        if video_url.lower() == 'exit':
            break
        folder_name = input("Enter the name for the folder: ")
        
        # Define the folder path on the desktop
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        base_folder_path = os.path.join(desktop_path, "video_transcripts")
        folder_path = os.path.join(base_folder_path, folder_name)
        
        # Create the folder if it doesn't exist
        os.makedirs(folder_path, exist_ok=True)
        
        video_file = os.path.join(folder_path, "video.mp4")
        audio_file = os.path.join(folder_path, "audio.wav")
        transcription_file = os.path.join(folder_path, "transcription.txt")

        # Step 1: Download the video
        print("Downloading video...")
        download_video(video_url, video_file)

        # Step 2: Extract audio
        print("Extracting audio...")
        audio_file = extract_audio(video_file, audio_file)

        # Debugging information
        print(f"Audio file path: {audio_file}")

        # Remove the video file as it's no longer needed
        os.remove(video_file)

        # Step 3: Transcribe audio
        print("Transcribing audio...")
        transcription = transcribe_audio(audio_file)
        if transcription is None:
            print("Failed to transcribe audio.")
            continue
        
        # Step 4: Translate transcription to Portuguese
        print("Translating transcription to Portuguese...")
        translation = translate_text(transcription, dest_language="pt")
        
        # Step 5: Adapt the translated text to your style
        print("Adapting translated text to your style...")
        adapted_text = adapt_text_to_style(translation)
        
        # Step 6: Save transcription, translation, and adapted text to a text file
        with open(transcription_file, "w", encoding="utf-8") as f:
            f.write("Original Transcription:\n")
            f.write(transcription)
            if translation:
                f.write("\n\nTranslated to Portuguese:\n")
                f.write(translation)
                f.write("\n\nAdapted Text:\n")
                f.write(adapted_text)
            else:
                f.write("\n\nTranslation to Portuguese failed.")
        
        # Step 7: Display results
        print("Transcription, translation, and adapted text saved to:", transcription_file)