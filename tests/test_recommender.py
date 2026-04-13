import math
import pytest
from src.recommender import Song, UserProfile, Recommender, _weighted_distance, recommend_songs


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

def make_user(**overrides) -> UserProfile:
    """Returns a default pop/happy user; any field can be overridden."""
    defaults = dict(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        target_acousticness=0.2,
        target_valence=0.8,
        target_danceability=0.75,
        target_tempo_bpm=120.0,
    )
    defaults.update(overrides)
    return UserProfile(**defaults)


def make_song(**overrides) -> Song:
    """Returns a default pop/happy song; any field can be overridden."""
    defaults = dict(
        id=1,
        title="Default Song",
        artist="Test Artist",
        genre="pop",
        mood="happy",
        energy=0.8,
        tempo_bpm=120.0,
        valence=0.8,
        danceability=0.75,
        acousticness=0.2,
    )
    defaults.update(overrides)
    return Song(**defaults)


def make_catalog() -> Recommender:
    """Three songs covering clearly distinct profiles."""
    return Recommender([
        make_song(id=1, title="Pop Hit",    genre="pop",  mood="happy",   energy=0.8, valence=0.8, danceability=0.75, acousticness=0.2,  tempo_bpm=120.0),
        make_song(id=2, title="Lofi Chill", genre="lofi", mood="chill",   energy=0.4, valence=0.6, danceability=0.5,  acousticness=0.9,  tempo_bpm=80.0),
        make_song(id=3, title="Metal Storm", genre="metal", mood="intense", energy=0.96, valence=0.2, danceability=0.6, acousticness=0.05, tempo_bpm=176.0),
    ])


# ---------------------------------------------------------------------------
# Ranking / ordering
# ---------------------------------------------------------------------------

def test_top_result_matches_user_profile():
    """A song that matches genre, mood, and all continuous targets should rank first."""
    rec = make_catalog()
    user = make_user()
    results = rec.recommend(user, k=3)

    assert results[0].title == "Pop Hit"


def test_results_are_sorted_by_score_descending():
    """Scores must be non-increasing across the returned list."""
    rec = make_catalog()
    user = make_user()
    results = rec.recommend(user, k=3)

    scores = []
    for song in results:
        d = _weighted_distance(song.__dict__, {
            "favorite_genre": user.favorite_genre,
            "favorite_mood": user.favorite_mood,
            "target_energy": user.target_energy,
            "target_acousticness": user.target_acousticness,
            "target_valence": user.target_valence,
            "target_danceability": user.target_danceability,
            "target_tempo_bpm": user.target_tempo_bpm,
        })
        scores.append(1 / (1 + d))

    assert scores == sorted(scores, reverse=True)


def test_k_limits_number_of_results():
    """recommend should return exactly k songs when the catalog is large enough."""
    rec = make_catalog()
    user = make_user()

    assert len(rec.recommend(user, k=1)) == 1
    assert len(rec.recommend(user, k=2)) == 2
    assert len(rec.recommend(user, k=3)) == 3


def test_k_larger_than_catalog_returns_all_songs():
    """Asking for more songs than exist should return the whole catalog, not raise."""
    rec = make_catalog()
    user = make_user()
    results = rec.recommend(user, k=100)

    assert len(results) == 3


# ---------------------------------------------------------------------------
# Genre and mood multipliers
# ---------------------------------------------------------------------------

def test_genre_match_ranks_above_closer_non_matching_song():
    """
    Song A: moderately close continuous features, wrong genre → raw distance ≈ 0.73.
    Song B: closer continuous features, correct genre → raw distance ≈ 0.35, ×0.5 ≈ 0.18.
    The genre multiplier should pull Song B above Song A despite Song A being closer
    on features alone.
    """
    # Song A: moderate deviation from user targets, wrong genre (no multiplier)
    song_a = make_song(id=1, title="Wrong Genre", genre="rock", mood="chill",
                       energy=0.5, valence=0.5, danceability=0.5, acousticness=0.5, tempo_bpm=90.0)
    # Song B: smaller deviation from user targets, correct genre (×0.5 multiplier)
    song_b = make_song(id=2, title="Right Genre", genre="pop", mood="chill",
                       energy=0.65, valence=0.65, danceability=0.65, acousticness=0.35, tempo_bpm=110.0)

    rec = Recommender([song_a, song_b])
    user = make_user(favorite_genre="pop", favorite_mood="happy")
    results = rec.recommend(user, k=2)

    assert results[0].title == "Right Genre"


def test_both_multipliers_applied_together():
    """
    A song that matches both genre AND mood should score higher than one that
    matches only genre, even if their continuous features are identical.
    """
    base = dict(energy=0.7, valence=0.7, danceability=0.7, acousticness=0.3, tempo_bpm=110.0)
    song_genre_only = make_song(id=1, title="Genre Only", genre="pop", mood="chill", **base)
    song_both       = make_song(id=2, title="Genre And Mood", genre="pop", mood="happy", **base)

    rec = Recommender([song_genre_only, song_both])
    user = make_user(favorite_genre="pop", favorite_mood="happy")
    results = rec.recommend(user, k=2)

    assert results[0].title == "Genre And Mood"


def test_no_genre_match_falls_back_to_feature_distance():
    """
    When no song matches the user's genre, ranking should still work and
    be determined by continuous-feature closeness alone.
    """
    song_close = make_song(id=1, title="Close Features", genre="jazz", mood="chill",
                           energy=0.81, valence=0.79, danceability=0.74, acousticness=0.21, tempo_bpm=121.0)
    song_far   = make_song(id=2, title="Far Features", genre="metal", mood="intense",
                           energy=0.2, valence=0.2, danceability=0.2, acousticness=0.9, tempo_bpm=170.0)

    rec = Recommender([song_close, song_far])
    user = make_user(favorite_genre="pop")
    results = rec.recommend(user, k=2)

    assert results[0].title == "Close Features"


# ---------------------------------------------------------------------------
# Continuous feature distance
# ---------------------------------------------------------------------------

def test_perfect_continuous_match_has_distance_zero():
    """A song whose features exactly equal the user's targets should have distance 0."""
    user = make_user()
    song = make_song(
        energy=user.target_energy,
        acousticness=user.target_acousticness,
        valence=user.target_valence,
        danceability=user.target_danceability,
        tempo_bpm=user.target_tempo_bpm,
        genre="other",   # no multiplier
        mood="other",
    )
    prefs = {
        "favorite_genre": user.favorite_genre,
        "favorite_mood": user.favorite_mood,
        "target_energy": user.target_energy,
        "target_acousticness": user.target_acousticness,
        "target_valence": user.target_valence,
        "target_danceability": user.target_danceability,
        "target_tempo_bpm": user.target_tempo_bpm,
    }
    assert _weighted_distance(song.__dict__, prefs) == pytest.approx(0.0)


def test_energy_weight_is_highest():
    """
    Two songs differ from the user's targets by the same raw amount on one
    feature each. The song that differs on energy should have a larger
    distance because energy carries the highest weight (2.0).
    """
    user = make_user()
    delta = 0.3

    song_energy_off = make_song(
        energy=user.target_energy + delta,
        acousticness=user.target_acousticness,
        valence=user.target_valence,
        danceability=user.target_danceability,
        tempo_bpm=user.target_tempo_bpm,
        genre="other", mood="other",
    )
    song_dance_off = make_song(
        energy=user.target_energy,
        acousticness=user.target_acousticness,
        valence=user.target_valence,
        danceability=user.target_danceability + delta,
        tempo_bpm=user.target_tempo_bpm,
        genre="other", mood="other",
    )
    prefs = {
        "favorite_genre": user.favorite_genre,
        "favorite_mood": user.favorite_mood,
        "target_energy": user.target_energy,
        "target_acousticness": user.target_acousticness,
        "target_valence": user.target_valence,
        "target_danceability": user.target_danceability,
        "target_tempo_bpm": user.target_tempo_bpm,
    }

    d_energy = _weighted_distance(song_energy_off.__dict__, prefs)
    d_dance  = _weighted_distance(song_dance_off.__dict__, prefs)

    assert d_energy > d_dance


def test_score_is_between_zero_and_one():
    """Score = 1 / (1 + distance) must always be in (0, 1]."""
    rec = make_catalog()
    user = make_user()
    for song in rec.songs:
        prefs = {
            "favorite_genre": user.favorite_genre,
            "favorite_mood": user.favorite_mood,
            "target_energy": user.target_energy,
            "target_acousticness": user.target_acousticness,
            "target_valence": user.target_valence,
            "target_danceability": user.target_danceability,
            "target_tempo_bpm": user.target_tempo_bpm,
        }
        d = _weighted_distance(song.__dict__, prefs)
        score = 1 / (1 + d)
        assert 0 < score <= 1


# ---------------------------------------------------------------------------
# Explanation text
# ---------------------------------------------------------------------------

def test_explain_mentions_genre_when_matched():
    rec = make_catalog()
    user = make_user(favorite_genre="pop")
    song = make_song(genre="pop", mood="chill")
    explanation = rec.explain_recommendation(user, song)
    assert "pop" in explanation


def test_explain_mentions_mood_when_matched():
    rec = make_catalog()
    user = make_user(favorite_mood="happy")
    song = make_song(genre="rock", mood="happy")
    explanation = rec.explain_recommendation(user, song)
    assert "happy" in explanation


def test_explain_returns_fallback_when_nothing_matches():
    rec = make_catalog()
    user = make_user(favorite_genre="pop", favorite_mood="happy")
    song = make_song(genre="metal", mood="intense")
    explanation = rec.explain_recommendation(user, song)
    assert isinstance(explanation, str)
    assert explanation.strip() != ""


# ---------------------------------------------------------------------------
# recommend_songs (functional path)
# ---------------------------------------------------------------------------

def test_recommend_songs_returns_tuple_structure():
    """Each item should be a (dict, float, str) triple."""
    songs = [make_song().__dict__]
    user_prefs = {
        "favorite_genre": "pop",
        "favorite_mood": "happy",
        "target_energy": 0.8,
        "target_acousticness": 0.2,
        "target_valence": 0.8,
        "target_danceability": 0.75,
        "target_tempo_bpm": 120.0,
    }
    results = recommend_songs(user_prefs, songs, k=1)
    assert len(results) == 1
    song, score, explanation = results[0]
    assert isinstance(song, dict)
    assert isinstance(score, float)
    assert isinstance(explanation, str)


def test_recommend_songs_empty_catalog_returns_empty():
    user_prefs = {
        "favorite_genre": "pop",
        "favorite_mood": "happy",
        "target_energy": 0.8,
        "target_acousticness": 0.2,
        "target_valence": 0.8,
        "target_danceability": 0.75,
        "target_tempo_bpm": 120.0,
    }
    assert recommend_songs(user_prefs, [], k=5) == []
