from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        # TODO: Implement recommendation logic
        return self.songs[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        # TODO: Implement explanation logic
        return "Explanation placeholder"

def load_songs(csv_path: str) -> List[Dict]:
    """Reads songs from a CSV file and returns a list of dicts with typed fields."""
    import csv
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            songs.append({
                "id":               int(row["id"]),
                "title":            row["title"],
                "artist":           row["artist"],
                "genre":            row["genre"],
                "mood":             row["mood"],
                "energy":           float(row["energy"]),
                "tempo_bpm":        float(row["tempo_bpm"]),
                "valence":          float(row["valence"]),
                "danceability":     float(row["danceability"]),
                "acousticness":     float(row["acousticness"]),
                "instrumentalness": float(row["instrumentalness"]),
                "speechiness":      float(row["speechiness"]),
            })
    print(f"Loaded songs: {len(songs)}")
    return songs

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Scores a single song against user preferences; returns (score, reasons)."""
    reasons = []

    # Signal 1: Genre match (binary)
    if song["genre"] == user_prefs["genre"]:
        genre_score = 1.0
        reasons.append(f"Matches your favorite genre: {song['genre']}")
    else:
        genre_score = 0.0

    # Signal 2: Mood match (binary)
    if song["mood"] == user_prefs["mood"]:
        mood_score = 1.0
        reasons.append(f"Matches your favorite mood: {song['mood']}")
    else:
        mood_score = 0.0

    # Signal 3: Energy proximity
    energy_score = 1.0 - abs(song["energy"] - user_prefs["energy"])
    if energy_score >= 0.80:
        reasons.append(
            f"Close energy match ({song['energy']:.2f} vs your target {user_prefs['energy']:.2f})"
        )

    # Signal 4: Acoustic fit
    if user_prefs.get("likes_acoustic", False):
        acoustic_score = song["acousticness"]
        if acoustic_score >= 0.70:
            reasons.append("Strong acoustic character fits your preference")
    else:
        acoustic_score = 1.0 - song["acousticness"]
        if acoustic_score >= 0.70:
            reasons.append("Low acoustic level fits your preference")

    # Fallback
    if not reasons:
        reasons.append("Limited match to your preferences")

    score = (0.35 * genre_score
           + 0.30 * mood_score
           + 0.25 * energy_score
           + 0.10 * acoustic_score)

    return (score, reasons)

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """
    Functional implementation of the recommendation logic.
    Required by src/main.py
    """
    # TODO: Implement scoring and ranking logic
    # Expected return format: (song_dict, score, explanation)
    return []
