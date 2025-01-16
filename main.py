import os
import subprocess
import whisper
import warnings
from yt_dlp import YoutubeDL
from translate import Translator

# Suppress specific warnings
warnings.filterwarnings("ignore", message="FP16 is not supported on CPU; using FP32 instead")

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
        # Split the text into smaller chunks
        max_chunk_size = 500  # Adjust this value as needed
        chunks = [text[i:i + max_chunk_size] for i in range(0, len(text), max_chunk_size)]
        translated_chunks = [translator.translate(chunk) for chunk in chunks]
        return ' '.join(translated_chunks)
    except Exception as e:
        print(f"Translation failed: {e}")
        return None

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
        
        # Step 5: Save transcription and translation to a text file
        with open(transcription_file, "w", encoding="utf-8") as f:
            f.write("Original Transcription:\n")
            f.write(transcription)
            if translation:
                f.write("\n\nTranslated to Portuguese:\n")
                f.write(translation)
            else:
                f.write("\n\nTranslation to Portuguese failed.")
        
        # Step 6: Display results
        print("Transcription and translation saved to:", transcription_file)