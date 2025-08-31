import argparse
import os
from music_lib.scanner import scan_library, Song

import warnings
import pickle
import numpy as np


warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)
##warning ignorings for some FUTURE ERRORS

from music_lib.analyser import analyze_songs,get_mood,get_tempo,generate_analysis_histograms

from music_lib.playlist import create_genre_playlist, create_mood_transition_playlist,create_scenario_playlist



#CACHE FILE
CACHE_FILE = "./songs_cache.pkl"

#General functions written for cache usage
def save_cache(songs: list):
    try:
        with open(CACHE_FILE, 'wb') as f:
            pickle.dump(songs, f)
        print(f"Songs analysis cached in {CACHE_FILE}")
    except Exception as e:
        print(f"Could not save cache: {e}")

def load_cache() -> list:
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'rb') as f:
                songs = pickle.load(f)
            print(f"Loaded cached analysis from {CACHE_FILE}")
            return songs
        except Exception as e:
            print(f"Could not load cache: {e}")
    return []

#This prevents usage as part of an import
if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Scans and analyzes a music library for tempo, energy, and mood.'
    )
    parser.add_argument(
        '-p', '--path', 
        required=True,
        help='The root path of the music library folder to scan.'
    )
    parser.add_argument(
        '--playlist-genre',
        help='Generate a playlist for the given genre (case-insensitive, partial match).'
    )
    parser.add_argument('--mood-transition',
        nargs=2,
        metavar=('START_SONG', 'END_SONG'),
        help='Create a mood transition playlist given two songs (provide exact titles).'
    )
    parser.add_argument(
        '--output',
        help='The path where the generated playlist (.m3u) will be saved.',
        default='./playlist.m3u'
    )
    parser.add_argument('--max-songs',
        type=int,
        default=10, 
        help='Max number of songs in mood transition playlist.'
    )
    parser.add_argument("--force-refresh", 
        action="store_true",
        help="Re-scan and re-analyze library, ignoring cached data"
    )
    parser.add_argument('--scenario-playlist',
        nargs=1,
        metavar=('SCENARIO'),
        help="Generate a playlist for a predefined scenario (gym, exam, stroll, gaming, sleep)."
    )
    parser.add_argument(
        '--scenario-output',
        help="Output file path for the scenario playlist (.m3u). Default: ./scenario_playlists/<scenario>.m3u"
    )


    args = parser.parse_args()

    if not os.path.isdir(args.path):
        print(f"Error: The provided path '{args.path}' is not a valid directory.")
        exit(1)

    songs_list = [] if args.force_refresh else load_cache()

    if not songs_list:
        print(f"Scanning music library at '{args.path}'...")
        songs_list = scan_library(args.path)
        
        if not songs_list:
            print("No supported music files found.")
            exit(0)

        print(f"Analyzing {len(songs_list)} songs...")
        analyze_songs(songs_list)

        save_cache(songs_list)
    else:
        print(f"Using cached analysis for {len(songs_list)} songs.")


    if args.playlist_genre:
        print(f"Generating playlist for genre '{args.playlist_genre}'...")
        playlist_path = create_genre_playlist(songs_list, args.playlist_genre, args.output)
        if playlist_path:
            print(f"Playlist created successfully at: {playlist_path}")
        else:
            print("Playlist generation failed.")



    elif args.mood_transition:
        start_title, end_title = args.mood_transition
        start_song = next((s for s in songs_list if s.title.lower() == start_title.lower()), None)
        end_song = next((s for s in songs_list if s.title.lower() == end_title.lower()), None)



        if not start_song or not end_song:
            print("Could not find one or both songs for mood transition.")
            exit(1)
        for song in songs_list:
            if song.mood is None:
                song.mood = get_mood(song.path)
            if song.tempo is None:
                song.tempo = get_tempo(song.path)

        print(f"Generating mood transition playlist from '{start_title}' to '{end_title}'...")
        playlist_path = create_mood_transition_playlist(
            songs_list, start_song, end_song, args.output, max_songs=args.max_songs
        )
        if playlist_path:
            print(f"Mood transition playlist created successfully at: {playlist_path}")
        else:
            print("Mood transition playlist generation failed.")
    
    elif args.scenario_playlist:
        scenario_name = args.scenario_playlist[0].lower()
        output_file = args.scenario_output if args.scenario_output else None

        

        playlist_path = create_scenario_playlist(
            songs=songs_list,
            scenario=scenario_name,
            output_file=output_file,
            max_songs=args.max_songs
        )

        if playlist_path:
            print(f"Scenario playlist successfully created at: {playlist_path}")
        else:
            print("Scenario playlist generation failed.")
    
    else:
        tempos = [s.tempo for s in songs_list if s.tempo is not None]
        energies = [s.energy for s in songs_list if s.energy is not None]
        


        print("\n--- Analysis Results ---")
        for song in songs_list:
            print(f"Title: {song.title}")
            print(f"  Artist: {song.artist}")
            print(f"  Album: {song.album}")
            print(f"  Genre: {song.genre}" if song.genre is not None else "  Genre: N/A")
            if song.tempo is not None:
                print(f"  Tempo: {float(song.tempo):.2f} BPM")
            else:
                print("  Tempo: N/A")
            if song.energy is not None:
                print(f"  Energy: {float(song.energy):.2f}")
            else:
                print("  Energy: N/A")
            print(f"  Mood: {song.mood}" if song.mood is not None else "  Mood: N/A")
            print(f"  Mood Score: {float(song.score):.2f} " if song.score is not None else " Mood Score: N/A")

            if tempos:
                print(f"\nAverage Tempo: {np.mean(tempos):.2f} BPM")
            if energies:
                print(f"Average Energy: {np.mean(energies):.2f}")
            print("-" * 20)

        ch = input("Would you like a histogram-based summary of your songs to be generated in a file within this current directory? (Y/N): ")

        if ch.lower() == "y":
            output_dir = "./analysis_histograms"
            generate_analysis_histograms(songs_list, output_dir=output_dir)
            print(f"\n✅ Histogram summary saved in {output_dir}/")

