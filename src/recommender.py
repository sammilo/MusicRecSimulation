import math
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
    target_acousticness: float
    target_valence: float
    target_danceability: float
    target_tempo_bpm: float

_WEIGHTS = {
    "energy": 2.0,
    "acousticness": 1.5,
    "valence": 1.5,
    "danceability": 1.0,
    "tempo_bpm": 1.0,
}

def _weighted_distance(song: Dict, user_prefs: Dict) -> float:
    """
    Computes weighted Euclidean distance between a song and a user's target values.
    Tempo is normalized to 0-1 by dividing by 200 so it doesn't dominate.
    Genre and mood matches act as multipliers that shrink the distance.
    """
    pairs = [
        ("energy",       song["energy"],                  user_prefs["target_energy"]),
        ("acousticness", song["acousticness"],             user_prefs["target_acousticness"]),
        ("valence",      song["valence"],                  user_prefs["target_valence"]),
        ("danceability", song["danceability"],             user_prefs["target_danceability"]),
        ("tempo_bpm",    song["tempo_bpm"] / 200.0,        user_prefs["target_tempo_bpm"] / 200.0),
    ]
    distance = math.sqrt(sum(_WEIGHTS[f] * (s - t) ** 2 for f, s, t in pairs))

    if song["genre"] == user_prefs["favorite_genre"]:
        distance *= 0.5
    if song["mood"] == user_prefs["favorite_mood"]:
        distance *= 0.75

    return distance


class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        scored = []
        for song in self.songs:
            distance = _weighted_distance(song.__dict__, {
                "favorite_genre": user.favorite_genre,
                "favorite_mood": user.favorite_mood,
                "target_energy": user.target_energy,
                "target_acousticness": user.target_acousticness,
                "target_valence": user.target_valence,
                "target_danceability": user.target_danceability,
                "target_tempo_bpm": user.target_tempo_bpm,
            })
            score = 1 / (1 + distance)
            scored.append((song, score))
        scored.sort(key=lambda x: x[1], reverse=True)
        return [song for song, _ in scored[:k]]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        reasons = []
        if song.genre == user.favorite_genre:
            reasons.append(f"genre matches your favorite ({song.genre})")
        if song.mood == user.favorite_mood:
            reasons.append(f"mood matches your favorite ({song.mood})")
        if not reasons:
            reasons.append("continuous features are close to your targets")
        return "Recommended because: " + ", ".join(reasons)

def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file.
    Required by src/main.py
    """
    import csv
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            songs.append({
                "id":           int(row["id"]),
                "title":        row["title"],
                "artist":       row["artist"],
                "genre":        row["genre"],
                "mood":         row["mood"],
                "energy":       float(row["energy"]),
                "tempo_bpm":    float(row["tempo_bpm"]),
                "valence":      float(row["valence"]),
                "danceability": float(row["danceability"]),
                "acousticness": float(row["acousticness"]),
            })
    return songs

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """
    Functional implementation of the recommendation logic.
    Required by src/main.py
    """
    scored = []
    for song in songs:
        distance = _weighted_distance(song, user_prefs)
        score = 1 / (1 + distance)
        reasons = []
        if song["genre"] == user_prefs["favorite_genre"]:
            reasons.append(f"genre matches your favorite ({song['genre']})")
        if song["mood"] == user_prefs["favorite_mood"]:
            reasons.append(f"mood matches your favorite ({song['mood']})")
        if not reasons:
            reasons.append("continuous features are close to your targets")
        explanation = " " + ", ".join(reasons)
        scored.append((song, score, explanation))
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:k]
