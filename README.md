# Music Tool - Audio Analysis & Playlist Generation

A Python-based music library analyzer that scans your music collection, analyzes audio features (tempo, energy, mood), and generates intelligent playlists based on various criteria.Librosa and Mutagen are the most essential libraries used.

## Features

- **Audio Analysis**: Extract tempo (BPM), energy levels, and mood from music files
- **Smart Playlists**: Generate playlists by genre, mood transitions.
- **Library Scanning**: Automatically scan and organize your music library
- **Caching**: Fast subsequent runs using cached analysis results
- **Visualization**: Generate histograms showing distribution of audio features
- **Multiple Formats**: Support for MP3, FLAC, M4A, OGG, and WMA files
- **Personalised Features**: As a proud SNU Chennai student, a few perosnalised features for our college students for generating playlists for their  everyday college use

## Prerequisites

- Python 3.7 or higher
- A music library with supported audio formats and a format similiar to ~/music/{artist}/{album}/{track no} - {track name}.{ext}
- Sufficient disk space for analysis caching

## Setup

### 1. Pull Repo and Create Python Virtual Environment

```bash

#Change directory into the directory where you have pulled repository to for eg:
cd library-analyser # this fully depends on which folder you have pulled changes to

# Create a new virtual environment
python3 -m venv music-tool-env

# Activate the virtual environment
# On Linux/macOS:
source music-tool-env/bin/activate

# On Windows:
music-tool-env\Scripts\activate
```

### 2. Install Dependencies

```bash
# Install required packages
pip install librosa numpy matplotlib mutagen

# Or install from requirements.txt if available
pip install -r requirements.txt
```

**Note**: Librosa installation might take some time as it includes audio processing libraries.

### 3. Verify Installation

```bash
# Test if librosa is working
python -c "import librosa; print('Librosa installed successfully')"
```

## Project Structure

```
library-analyser/
├── cli.py                 # Main command-line interface
├── music_lib/
│   ├── __init__.py
│   ├── scanner.py         # Music library scanner
│   ├── analyser.py        # Audio feature analysis
│   └── playlist.py        # Playlist generation
├── songs_cache.pkl        # Cached analysis results (auto-generated)
├── analysis_histograms/   # Generated visualization files
└── scenario_playlists/    # Generated scenario playlists
```

## Usage

### Basic Library Analysis

```bash
# Scan and analyze your music library
python cli.py -p /path/to/your/music/library

# Force refresh (ignore cached data)
python cli.py -p /path/to/your/music/library --force-refresh
```

### Playlist Generation

#### 1. Genre-based Playlists

```bash
# Create a playlist for a specific genre
python cli.py -p /path/to/music --playlist-genre "Rock" --output ./rock_playlist.m3u

# Available genres depend on your music files' metadata
# Common genres: Rock, Pop, Jazz, Classical, Alternative(Subject to Mutagen's defined classes)
```

#### 2. Mood Transition Playlists

   **Logic behind the mood changing playlists**
   We calculate mood score for each song using tempo energy and mood using a point system. This helps us assign an approximate mood score for all songs of a particular mode thus helping for the creation of a mood shifting playlist based on a gradual change in this score and order them accordingly. This is synonyomous with spotify's mood socres based on which they implement many features on their platform


```bash
# Create a playlist that transitions between two songs
python cli.py -p /path/to/music --mood-transition "Song Title 1" "Song Title 2" --output ./transition.m3u --max-songs 15

# This creates a playlist that smoothly transitions from the mood of the first song to the second
```

#### 3. Scenario-based Playlists
   Whether you're buckling under the stress for endsem exams, having fun at the SNU gym,taking a peaceful stroll  or grinding Minecraft nonstop from your room we got you SNU students. A comprehensive way to generate playlists depending on your situation.

```bash
# Generate playlists for specific activities
python cli.py -p /path/to/music --scenario-playlist "gym" --max-songs 20
python cli.py -p /path/to/music --scenario-playlist "sleep" --max-songs 15
python cli.py -p /path/to/music --scenario-playlist "exam" --max-songs 25

# Available scenarios:
# - gym: High energy, fast tempo (Pop, Rock, Alternative)
# - exam: Calm, low tempo (Classical, Jazz)
# - stroll: Moderate tempo and energy (Jazz, Classical, Alternative)
# - gaming: Medium-high energy (Rock, Pop, Alternative)
# - sleep: Very calm, low energy (Classical, Jazz)
```

### Output Options

```bash
# Custom output paths
python cli.py -p /path/to/music --scenario-playlist "gym" --scenario-output ./my_playlists/workout.m3u

# Default output locations:
# - Genre playlists: ./playlist.m3u
# - Mood transitions: ./playlist.m3u
# - Scenario playlists: ./scenario_playlists/<scenario>.m3u
```

## Command Line Options

| Option | Description | Required |
|--------|-------------|----------|
| `-p, --path` | Root path of music library to scan | Yes |
| `--playlist-genre` | Generate playlist for specific genre | No |
| `--mood-transition` | Create mood transition playlist (requires 2 song titles) | No |
| `--scenario-playlist` | Generate scenario-based playlist | No |
| `--output` | Output path for playlist (.m3u) | No (default: ./playlist.m3u) |
| `--scenario-output` | Custom output for scenario playlists | No |
| `--max-songs` | Maximum songs in playlist (default: 10) | No |
| `--force-refresh` | Re-scan and re-analyze library | No |

## Audio Analysis Features

### Tempo (BPM)
- Extracted using librosa's beat tracking
- Range: Typically 60-200 BPM
- Used for energy-based filtering and mood classification

### Energy
- Calculated from RMS (Root Mean Square) of audio signal
- Range: 0.0 to 1.0
- Higher values indicate more energetic songs

### Mood Classification
- **Energetic**: High tempo (>120 BPM), high energy, bright spectral features
- **Happy**: High chroma features, bright spectral centroid
- **Sad**: Low chroma, low spectral centroid, low energy
- **Calm**: Low tempo (<80 BPM), low energy
- **Neutral**: Default category for songs that don't fit other moods

### Mood Score
- Custom algorithm combining tempo, energy, and mood
- Range: 0.0 to 1.0
- Used for playlist ordering and filtering

## File Format Support

- **MP3** (.mp3) - Most common, good metadata support
- **FLAC** (.flac) - Lossless, excellent quality
- **M4A** (.m4a) - Apple format, good metadata
- **OGG** (.ogg) - Open source, good compression
- **WMA** (.wma) - Windows Media Audio

## Caching

The tool automatically caches analysis results in `songs_cache.pkl` to speed up subsequent runs. Use `--force-refresh` to regenerate the cache.

## Visualization

When running basic analysis, you can generate histograms showing:
- Tempo distribution across your library
- Energy level distribution
- Mood distribution

Files are saved in `./analysis_histograms/` directory.

## Troubleshooting

### Common Issues

1. **Librosa Import Error**
   ```bash
   # Reinstall librosa
   pip uninstall librosa
   pip install librosa
   ```

2. **Memory Issues with Large Libraries**
   - Use `--force-refresh` sparingly
   - Process libraries in smaller batches
   - Ensure sufficient RAM (4GB+ recommended)

3. **Audio File Corruption**
   - The tool skips corrupted files automatically
   - Check console output for skipped files

4. **Slow Analysis**
   - First run is always slowest
   - Subsequent runs use cached data
   - Consider analyzing during off-peak hours

### Performance Tips

- Use SSD storage for faster file access
- Ensure sufficient RAM for audio processing
- Close other applications during analysis
- Use caching for repeated analysis

## Examples

### Complete Workflow Example

```bash
# 1. Set up environment
python3 -m venv music-tool-env
source music-tool-env/bin/activate
pip install librosa numpy matplotlib mutagen

# 2. Analyze library
python cli.py -p ~/Music

# 3. Generate workout playlist
python cli.py -p ~/Music --scenario-playlist "gym" --max-songs 30

# 4. Create mood transition
python cli.py -p ~/Music --mood-transition "Bohemian Rhapsody" "Stairway to Heaven" --max-songs 20
```

### Batch Processing

```bash
# Generate multiple scenario playlists
for scenario in gym exam stroll gaming sleep; do
    python cli.py -p ~/Music --scenario-playlist "$scenario" --max-songs 25
done
```

## Contributing

Feel free to contribute improvements:
- Audio feature extraction algorithms
- New playlist generation strategies
- Additional file format support
- Performance optimizations

## License

This project is open source. Please check individual file headers for specific licensing information.

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Verify your Python environment and dependencies
3. Check that your audio files are not corrupted
4. Ensure sufficient system resources

---

**Happy Music Analysis! 🎵**
