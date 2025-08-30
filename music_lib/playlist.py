import os
from typing import List, Optional
from .scanner import Song
from .analyser import get_mood, get_tempo, get_energy
import numpy as np
from .analyser import get_mood_score


def _write_playlist_file(songs: List[Song], output_file: str, playlist_name: str = "playlist") -> Optional[str]:
    # A general function just to write these songs to files for playlist generation
    try:
        output_dir = os.path.dirname(output_file)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("#EXTM3U\n")
            for song in songs:
                if song.artist and song.title:
                    f.write(f"#EXTINF:-1,{song.artist} - {song.title}\n")
                f.write(f"{song.path}\n")
        
        full_path = os.path.abspath(output_file)
        
        return full_path

    except IOError as e:
        print(f"Error writing to file '{output_file}': {e}")
        return None


def _print_playlist_stats(songs: List[Song], playlist_name: str = "playlist"):
    #Prints metadata for each of these playlists
    tempos = [s.tempo for s in songs if s.tempo is not None]
    energies = [s.energy for s in songs if s.energy is not None]
    scores = [s.score for s in songs if hasattr(s, 'score') and s.score is not None]

    print(f"\n--- {playlist_name.title()} Stats ---")
    if tempos:
        print(f"Average Tempo: {np.mean(tempos):.2f} BPM")
    if energies:
        print(f"Average Energy: {np.mean(energies):.2f}")
    if scores:
        print(f"Average Mood Score: {np.mean(scores):.2f}")
    print("-" * 30)

#Scenario definitions
SCENARIO_DEFS = {
    "gym": {
        "genres": ["Pop", "Rock", "Alternative"],
        "min_tempo": 110,
        "min_energy": 0.5
    },
    "exam": {
        "genres": ["Classical", "Jazz"],
        "max_tempo": 100,
        "max_energy": 0.4
    },
    "stroll": {
        "genres": ["Jazz", "Classical", "Alternative"],
        "max_tempo": 120,
        "max_energy": 0.6
    },
    "gaming": {
        "genres": ["Rock", "Pop", "Alternative"],
        "min_tempo": 100,
        "min_energy": 0.5
    },
    "sleep": {
        "genres": ["Classical", "Jazz"],
        "max_tempo": 80,
        "max_energy": 0.3
    }
}
# A general function to create playlists based on genre
def create_genre_playlist(songs: List[Song], genre: str, output_file: str) -> Optional[str]:
    matching_songs = [
        song for song in songs
        if song.genre and genre.lower() in song.genre.lower()
    ]

    if not matching_songs:
        print(f"No songs found for the genre '{genre}'.")
        return None

    _print_playlist_stats(matching_songs, f"genre '{genre}' playlist")
    
    return _write_playlist_file(matching_songs, output_file, f"genre '{genre}' playlist")

# Mood Transition Playlist
def create_mood_transition_playlist(
    songs: List[Song],
    start_song: Song,
    end_song: Song,
    output_file: str,
    max_songs: int = 10
) -> Optional[str]:

    for song in [start_song, end_song]:
        if song.mood is None:
            song.mood = get_mood(song.path)
        if song.tempo is None:
            song.tempo = get_tempo(song.path)
        if song.score is None:
            song.score = get_mood_score(song)

    if start_song.mood is None or end_song.mood is None:
        print("Could not determine mood for start or end song. Cannot create playlist.")
        return None

    intermediary_songs = [s for s in songs if s.path not in [start_song.path, end_song.path]]

    start_mood_songs = [s for s in intermediary_songs if s.mood == start_song.mood ]
    end_mood_songs = [s for s in intermediary_songs if s.mood == end_song.mood ]

    for s in start_mood_songs + end_mood_songs:
        if s.tempo is None:
            s.tempo = get_tempo(s.path)

    half = (max_songs - 2) // 2
    start_mood_songs_sorted = sorted(start_mood_songs, key=lambda s: s.score, reverse=True)[:half]
    end_mood_songs_sorted = sorted(end_mood_songs, key=lambda s: s.score)[:half]

    if len(start_mood_songs_sorted) < half:
        print(f"Warning: Only {len(start_mood_songs_sorted)} songs found for start mood (needed {half}).")
    if len(end_mood_songs_sorted) < half:
        print(f"Warning: Only {len(end_mood_songs_sorted)} songs found for end mood (needed {half}).")

    final_playlist = [start_song] + start_mood_songs_sorted + end_mood_songs_sorted + [end_song]

    _print_playlist_stats(final_playlist, "mood transition playlist")

    return _write_playlist_file(final_playlist, output_file, "mood transition playlist")

#Creating a scenario for the playlists we designed
def create_scenario_playlist(
    songs: List[Song],
    scenario: str,
    output_file: str = None,
    max_songs: int = 10
) -> Optional[str]:
    scenario = scenario.lower()
    if scenario not in SCENARIO_DEFS:
        print(f"Scenario '{scenario}' is not defined.")
        return None

    for s in songs:
        if s.tempo is None:
            s.tempo = get_tempo(s.path)
        if s.energy is None:
            s.energy = get_energy(s.path)
        if s.mood is None:
            s.mood = get_mood(s.path)
        if s.score is None:
            s.score = get_mood_score(s)

    params = SCENARIO_DEFS[scenario]

    filtered_songs = []
    for s in songs:
        #Prioritise genres which fit the scenario and then move onto metadata based filtering
        if s.genre and any(s.genre.lower() == g.lower() for g in params["genres"]):
            filtered_songs.append(s)
        else:
            min_tempo = params.get("min_tempo", 0)
            max_tempo = params.get("max_tempo", float("inf"))
            min_energy = params.get("min_energy", 0)
            max_energy = params.get("max_energy", float("inf"))
            if s.tempo is not None and s.energy is not None:
                if min_tempo <= s.tempo <= max_tempo and min_energy <= s.energy <= max_energy:
                    filtered_songs.append(s)

    if not filtered_songs:
        print(f"No songs matched the '{scenario}' scenario criteria.")
        return None

    filtered_songs_sorted = sorted(filtered_songs, key=lambda x: x.score or 0, reverse=True)[:max_songs]

    if not output_file:
        output_dir = "./scenario_playlists"
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, f"{scenario}.m3u")
    else:
        output_dir = os.path.dirname(output_file)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

    _print_playlist_stats(filtered_songs_sorted, f"scenario '{scenario}' playlist")

    return _write_playlist_file(filtered_songs_sorted, output_file, f"scenario '{scenario}' playlist")