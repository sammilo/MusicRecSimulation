"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from recommender import load_songs, recommend_songs


USERS = [
    {
        "name": "Pop Fan",
        "description": "High-energy, upbeat pop lover who prefers produced sound over acoustic",
        "favorite_genre":      "pop",
        "favorite_mood":       "happy",
        "target_energy":       0.85,
        "target_acousticness": 0.15,
        "target_valence":      0.85,
        "target_danceability": 0.80,
        "target_tempo_bpm":    120.0,
    },
    {
        "name": "Late-Night Lofi Listener",
        "description": "Calm, focused listener who likes slow, acoustic-leaning instrumental music",
        "favorite_genre":      "lofi",
        "favorite_mood":       "chill",
        "target_energy":       0.35,
        "target_acousticness": 0.80,
        "target_valence":      0.55,
        "target_danceability": 0.50,
        "target_tempo_bpm":    78.0,
    },
    {
        "name": "Metal Head",
        "description": "Wants nothing but maximum aggression — fast, loud, and fully produced",
        "favorite_genre":      "metal",
        "favorite_mood":       "intense",
        "target_energy":       0.97,
        "target_acousticness": 0.05,
        "target_valence":      0.20,
        "target_danceability": 0.65,
        "target_tempo_bpm":    175.0,
    },
    {
        "name": "Jazz Cafe Regular",
        "description": "Relaxed listener who gravitates toward warm, mid-tempo acoustic tones",
        "favorite_genre":      "jazz",
        "favorite_mood":       "relaxed",
        "target_energy":       0.40,
        "target_acousticness": 0.85,
        "target_valence":      0.65,
        "target_danceability": 0.55,
        "target_tempo_bpm":    92.0,
    },
    {
        "name": "Dance Floor Regular",
        "description": "Lives for danceable, high-BPM tracks regardless of genre",
        "favorite_genre":      "electronic",
        "favorite_mood":       "intense",
        "target_energy":       0.90,
        "target_acousticness": 0.05,
        "target_valence":      0.60,
        "target_danceability": 0.95,
        "target_tempo_bpm":    140.0,
    },
]


def run_user(user_prefs: dict, songs: list, k: int = 5) -> None:
    name        = user_prefs["name"]
    description = user_prefs["description"]

    # Strip display-only fields before passing to recommender
    prefs = {k: v for k, v in user_prefs.items() if k not in ("name", "description")}

    print("=" * 60)
    print(f"  {name}")
    print(f"  {description}")
    print(f"  Genre: {prefs['favorite_genre']}  |  Mood: {prefs['favorite_mood']}")
    print(f"  Energy: {prefs['target_energy']}  |  Acousticness: {prefs['target_acousticness']}")
    print(f"  Valence: {prefs['target_valence']}  |  Danceability: {prefs['target_danceability']}")
    print(f"  Tempo: {prefs['target_tempo_bpm']} BPM")
    print("-" * 60)

    recommendations = recommend_songs(prefs, songs, k=k)

    for i, rec in enumerate(recommendations, start=1):
        song, score, explanation = rec
        print(f"  {i}. {song['title']} by {song['artist']}")
        print(f"     Score: {score:.3f}  |  Genre: {song['genre']}  |  Mood: {song['mood']}")
        print(f"     {explanation}")
    print()


def main() -> None:
    songs = load_songs("data/songs.csv")

    for user in USERS:
        run_user(user, songs, k=5)


if __name__ == "__main__":
    main()
