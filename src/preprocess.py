import os
import torch
import torchaudio
import numpy as np
from pydub import AudioSegment
from pathlib import Path
from silero_vad import load_silero_vad, get_speech_timestamps

# ==============================
# CONFIG
# ==============================

RAW_DIR = "data/raw"
OUT_DIR = "data/processed"
SEG_DIR = os.path.join(OUT_DIR, "segments")

SAMPLE_RATE = 22050
TARGET_DBFS = -20

MIN_SEG = 2.0
MAX_SEG = 8.0

ENERGY_THRESHOLD = 0.01


# ==============================
# SETUP
# ==============================

def setup():

    os.makedirs(RAW_DIR, exist_ok=True)
    os.makedirs(SEG_DIR, exist_ok=True)


# ==============================
# NORMALIZE AUDIO
# ==============================

def normalize_audio(audio):

    audio = audio.set_channels(1)
    audio = audio.set_frame_rate(SAMPLE_RATE)

    change = TARGET_DBFS - audio.dBFS
    audio = audio.apply_gain(change)

    return audio


# ==============================
# LOAD AUDIO
# ==============================

def load_audio(path):

    audio = AudioSegment.from_file(path)
    audio = normalize_audio(audio)

    temp = "temp.wav"
    audio.export(temp, format="wav")

    wav, sr = torchaudio.load(temp)

    return wav.squeeze(), sr, audio


# ==============================
# ENERGY FILTER
# ==============================

def is_valid_energy(segment):

    samples = np.array(segment.get_array_of_samples()).astype(np.float32)

    energy = np.mean(samples ** 2)

    return energy > ENERGY_THRESHOLD


# ==============================
# SAVE SEGMENTS
# ==============================

def save_segments(audio, timestamps, name):

    saved = 0
    metadata = []

    for i, ts in enumerate(timestamps):

        start = ts["start"] / SAMPLE_RATE
        end = ts["end"] / SAMPLE_RATE

        duration = end - start

        if not (MIN_SEG <= duration <= MAX_SEG):
            continue

        segment = audio[start * 1000:end * 1000]

        if not is_valid_energy(segment):
            continue

        filename = f"{name}_seg_{saved:05d}.wav"

        path = os.path.join(SEG_DIR, filename)

        segment.export(path, format="wav")

        metadata.append(f"{filename}|")

        saved += 1

    return saved, metadata


# ==============================
# MAIN
# ==============================

def main():

    setup()

    print("Loading Silero VAD...")

    model = load_silero_vad()

    raw_files = [
        f for f in os.listdir(RAW_DIR)
        if f.endswith((".wav", ".mp3", ".m4a"))
    ]

    all_metadata = []
    total = 0

    for file in raw_files:

        path = os.path.join(RAW_DIR, file)
        name = Path(file).stem

        print(f"\nProcessing: {file}")

        wav, sr, audio = load_audio(path)

        speech = get_speech_timestamps(
            wav,
            model,
            sampling_rate=sr
        )

        num, metadata = save_segments(audio, speech, name)

        total += num
        all_metadata.extend(metadata)

        print("Segments:", num)

    metadata_path = os.path.join(OUT_DIR, "metadata.csv")

    with open(metadata_path, "w", encoding="utf8") as f:
        for line in all_metadata:
            f.write(line + "\n")

    print("\n===================")
    print("DONE")
    print("Total segments:", total)
    print("Dataset:", SEG_DIR)
    print("Metadata:", metadata_path)


if __name__ == "__main__":
    main()