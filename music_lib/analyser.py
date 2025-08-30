import os
import re
from dataclasses import dataclass
from typing import List, Optional
import numpy as np
from .scanner import Song



import matplotlib.pyplot as plt
from collections import Counter

## Using Librosa
try:
    import librosa
    import librosa.display
    librosa_available = True
except ImportError:
    librosa_available = False


#First Loading
def _load_audio(filepath: str):
    if not librosa_available:
        print("Librosa is not installed. Cannot analyze audio features.")
        return None, None
    try:
        y, sr = librosa.load(filepath, sr=22050)

        if y is None or y.size == 0:
            return None, None
        
        return y, sr
    except Exception as e:
        return None, None

#The functions written after this are for recording tempo energy and mood all important to analysing the music more
def get_tempo(filepath: str) -> Optional[float]:
    y, sr = _load_audio(filepath)
    if y is None or sr is None:
        return None
    try:
        
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
        return tempo
    except Exception as e:
        print(f"Error extracting tempo from {filepath}: {e}")
        return None

def get_energy(filepath: str) -> Optional[float]:
    y, sr = _load_audio(filepath)
    if y is None or sr is None:
        return None
    try:
        rms = librosa.feature.rms(y=y)
        energy = np.mean(rms)
        return float(np.clip(energy * 10, 0, 1))
    except Exception as e:
        print(f"Error extracting energy from {filepath}: {e}")
        return None

def get_mood(filepath: str) -> Optional[str]:
    try:
        y, sr = librosa.load(filepath)
        chroma = librosa.feature.chroma_stft(y=y, sr=sr)
        centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0]

        rms = librosa.feature.rms(y=y)[0]


        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
        

        chroma_mean = np.mean(chroma)
        centroid_mean = np.mean(centroid)
        rms_mean = np.mean(rms)
        tempo_val = tempo

        

        if tempo_val > 120 and centroid_mean > 2500 and rms_mean > 0.05:
            return "Energetic"
        elif chroma_mean > 0.6 and centroid_mean > 2000:
            return "Happy"
        elif chroma_mean < 0.4 and centroid_mean < 1500 and rms_mean < 0.03:
            return "Sad"
        elif tempo_val < 80 and rms_mean < 0.04:
            return "Calm"
        else:
            return "Neutral"
    except Exception as e:
        return None


# Mood Score: A score I designed to simulate Spotify's tempo system, this helps me add a gradual flow for playlists using these scores
def get_mood_score(song: Song) -> float:
    
    if song.tempo is None or song.energy is None:
        return 0.5  # default neutral score

    # weightings the ratios which I used
    tempo_weight = 0.4
    energy_weight = 0.4
    mood_weight = 0.2

    # numeric mapping for mood categories
    mood_map = {
        "Energetic": 1.0,
        "Happy": 0.8,
        "Neutral": 0.5,
        "Calm": 0.3,
        "Sad": 0.1
    }
    mood_score = mood_map.get(song.mood, 0.5)

    score = (song.tempo / 200 * tempo_weight) + (song.energy * energy_weight) + (mood_score * mood_weight)
    return score


def analyze_songs(songs: List[Song]):
    if not librosa_available:
        print("Librosa is not installed. Cannot analyze audio features for songs.")
        return

    for song in songs:
        if not os.path.exists(song.path):
            print(f"File not found: {song.path}. Skipping analysis.")
            continue
        #Assigning the fields for each song
        print(f"Analyzing {song.title} by {song.artist}...")
        song.tempo = get_tempo(song.path)
        song.energy = get_energy(song.path)
        song.mood = get_mood(song.path)
        song.score = get_mood_score(song)




def generate_analysis_histograms(songs: List[Song], output_dir: str = None):
    # Flatten and filter values beofre we use them
    tempos = [float(s.tempo) for s in songs if s.tempo is not None]
    energies = [float(s.energy) for s in songs if s.energy is not None]
    moods = [s.mood for s in songs if s.mood is not None]

    if not tempos and not energies and not moods:
        print("No analyzed data available to generate histograms.")
        return

    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    #I've generated hostograms for each of Tempo, Energy and Mood for our entire library
    if tempos:
        plt.figure(figsize=(8,5))
        plt.hist(tempos, bins=10, color='skyblue', edgecolor='black')
        plt.title("Tempo Distribution")
        plt.xlabel("BPM")
        plt.ylabel("Number of Songs")
        plt.grid(axis='y', alpha=0.75)
        if output_dir:
            plt.savefig(os.path.join(output_dir, "tempo_histogram.png"))
            plt.close()
        else:
            plt.show()

    
    if energies:
        plt.figure(figsize=(8,5))
        plt.hist(energies, bins=10, color='salmon', edgecolor='black')
        plt.title("Energy Distribution")
        plt.xlabel("Energy (0-1)")
        plt.ylabel("Number of Songs")
        plt.grid(axis='y', alpha=0.75)
        if output_dir:
            plt.savefig(os.path.join(output_dir, "energy_histogram.png"))
            plt.close()
        else:
            plt.show()

    
    if moods:
        mood_counts = Counter(moods)
        plt.figure(figsize=(6,4))
        plt.bar(list(mood_counts.keys()), list(mood_counts.values()), color='lightgreen', edgecolor='black')
        plt.title("Mood Distribution")
        plt.xlabel("Mood")
        plt.ylabel("Number of Songs")
        if output_dir:
            plt.savefig(os.path.join(output_dir, "mood_histogram.png"))
            plt.close()
        else:
            plt.show()

    print("Histograms generated successfully." + (f" Saved in {output_dir}" if output_dir else ""))

