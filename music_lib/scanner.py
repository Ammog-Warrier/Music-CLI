import os
import re
from typing import List, Optional




class Song:
    def __init__(self, path, artist, album, track_no, title, genre=None):
        self.path = path
        self.artist = artist
        self.album = album
        self.track_no = track_no
        self.title = title
        self.genre = genre #keeping this one optional since it dpends on mutagen
        self.tempo = None
        self.energy = None
        self.mood = None
        self.score = None

GENRE_MAP = {
    "Альтернативная музыка": "Alternative",
    "Поп": "Pop",
    "Рок": "Rock",
    "Джаз": "Jazz",
    "Классическая музыка": "Classical"
    
}# Doing this because sometimes mutagen returns thegenre in cyrillic just for mapping

def normalize_genre(genre: str) -> str:
    if genre is None:
        return "N/A"
    return GENRE_MAP.get(genre, genre)


def scan_library(library_path: str) -> List[Song]:
    songs = []
    supported_exts = {'.mp3', '.flac', '.m4a', '.ogg', '.wma'}

    try:
        from mutagen import File as MutagenFile
        mutagen_available = True
    except ImportError:
        mutagen_available = False

    for dirpath, dirnames, filenames in os.walk(library_path):# to etxract the base details as per provided problem statement
        try:
            relative_path = os.path.relpath(dirpath, library_path)
            if relative_path == ".":
                artist = os.path.basename(dirpath)
                album = "Unknown Album"
            else:
                parts = relative_path.split(os.sep)
                if len(parts) >= 2:
                    artist = parts[0]
                    album = parts[1]
                else:
                    artist = "Unknown Artist"
                    album = "Unknown Album"
        
        except ValueError:
            artist = "Unknown Artist"
            album = "Unknown Album"

        for filename in filenames:
            file_ext = os.path.splitext(filename)[1].lower() # here I have checked the allowed extensions
            if file_ext not in supported_exts:
                continue

            full_path = os.path.join(dirpath, filename)
            
            match = re.match(r'(\d+)\s*[-.]\s*(.+?)\..+', filename)# Extracting info via regex
            if not match:
                track_no = 0
                title = os.path.splitext(filename)[0]
            else:
                track_no = int(match.group(1))
                title = match.group(2)
            
            genre = None
            
            if mutagen_available: #deriving the genre
                try:
                    audio = MutagenFile(full_path)
                    if audio:
                        genre_list = audio.get('genre') or audio.get('TCON')
                        if genre_list:
                            genre = str(genre_list[0])
                            genre = normalize_genre(genre)# Generalising genre
                except Exception:
                    pass

            song = Song(
                path=full_path,
                artist=artist,
                album=album,
                track_no=track_no,
                title=title,
                genre=genre
            )
            songs.append(song)
    
    return songs