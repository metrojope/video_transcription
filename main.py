import os
import subprocess
import whisper
import warnings
from yt_dlp import YoutubeDL
from googletrans import Translator, LANGUAGES

# Suppress specific warnings
warnings.filterwarnings("ignore", message="FP16 is not supported on CPU; using FP32 instead")
warnings.filterwarnings("ignore", message="You are using `torch.load` with `weights_only=False` (the current default value), which uses the default pickle module implicitly. It is possible to construct malicious pickle data which will execute arbitrary code during unpickling (See https://github.com/pytorch/pytorch/blob/main/SECURITY.md#untrusted-models for more details). In a future release, the default value for `weights_only` will be flipped to `True`. This limits the functions that could be executed during unpickling. Arbitrary objects will no longer be allowed to be loaded via this mode unless they are explicitly allowlisted by the user via `torch.serialization.add_safe_globals`. We recommend you start setting `weights_only=True` for any use case where you don't have full control of the loaded file. Please open an issue on GitHub for any issues related to this experimental feature.")

def download_video(url, output_path):
    ydl_opts = {"outtmpl": output_path, "format": "bestaudio/best"}
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

def extract_audio(video_path, audio_path):
    # Use the absolute path to ffmpeg
    ffmpeg_path = r"C:\ffmpeg\bin\ffmpeg.exe"  # Replace with the actual path to ffmpeg

    # Check if ffmpeg is available
    try:
        subprocess.run([ffmpeg_path, "-version"], check=True)
    except subprocess.CalledProcessError:
        print("ffmpeg is not installed or not found in PATH.")
        return

    # Generate a new filename if the audio file already exists
    base, ext = os.path.splitext(audio_path)
    counter = 1
    new_audio_path = audio_path
    while os.path.exists(new_audio_path):
        new_audio_path = f"{base}_{counter}{ext}"
        counter += 1

    subprocess.run([ffmpeg_path, "-i", video_path, "-q:a", "0", "-map", "a", new_audio_path, "-y"])
    return new_audio_path

def transcribe_audio(audio_path):
    model = whisper.load_model("base")
    result = model.transcribe(audio_path)
    return result['text']

def translate_text(text, dest_language="pt"):
    translator = Translator()
    try:
        translation = translator.translate(text, dest=dest_language)
        return translation.text
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

        # Remove the video file as it's no longer needed
        os.remove(video_file)

        # Step 3: Transcribe audio
        print("Transcribing audio...")
        transcription = transcribe_audio(audio_file)
        
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