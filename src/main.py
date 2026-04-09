"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from .recommender import (
    load_songs, recommend_songs, score_song,
    DEFAULT, GENRE_FIRST, MOOD_FIRST, ENERGY_FOCUSED, RankingStrategy,
)
from tabulate import tabulate


PROFILES = {
    "High-Energy Pop": {
        "genre": "pop",
        "mood": "happy",
        "energy": 0.9,
        "likes_acoustic": False,
        "min_popularity": 70,                          # only boost popular tracks
        "preferred_tags": ["upbeat", "energetic", "bright", "happy"],
    },
    "Chill Lofi": {
        "genre": "lofi",   # dataset uses "lofi", not "lo-fi"
        "mood": "chill",   # dataset uses "chill", not "calm"
        "energy": 0.2,
        "likes_acoustic": True,
        "preferred_tags": ["chill", "focused", "ambient", "peaceful"],
        "preferred_decade": 2020,                      # prefers recent releases
    },
    "Deep Intense Rock": {
        "genre": "rock",
        "mood": "angry",
        "energy": 0.95,
        "likes_acoustic": False,
        "preferred_decade": 1990,                      # classic rock era
        "preferred_tags": ["aggressive", "raw", "rebellious", "heavy", "intense"],
    },
    # Edge-case / adversarial: conflicting preferences
    "Conflicted Listener": {
        "genre": "classical",
        "mood": "sad",
        "energy": 0.9,   # high energy but sad mood — intentionally contradictory
        "likes_acoustic": True,
        "preferred_tags": ["melancholy", "introspective", "elegant", "sad"],
        "preferred_decade": 2010,
    },
}

# Weights mirror DEFAULT strategy — used by explain_top_song() for the signal breakdown
WEIGHTS = {
    "genre":   DEFAULT.genre_weight,
    "mood":    DEFAULT.mood_weight,
    "energy":  DEFAULT.energy_weight,
    "acoustic": DEFAULT.acoustic_weight,
}

# Per-profile strategy assignments — change any value to switch that profile's ranking mode
PROFILE_STRATEGIES = {
    "High-Energy Pop":    DEFAULT,
    "Chill Lofi":         MOOD_FIRST,
    "Deep Intense Rock":  ENERGY_FOCUSED,
    "Conflicted Listener": GENRE_FIRST,
}


def explain_top_song(user_prefs: dict, song: dict) -> None:
    """Prints a signal-by-signal score breakdown for why a song ranked #1."""
    genre_match = song["genre"] == user_prefs["genre"]
    mood_match  = song["mood"]  == user_prefs["mood"]
    energy_score = 1.0 - abs(song["energy"] - user_prefs["energy"])
    if user_prefs.get("likes_acoustic"):
        acoustic_score = song["acousticness"]
    else:
        acoustic_score = 1.0 - song["acousticness"]

    total = (WEIGHTS["genre"]   * (1.0 if genre_match else 0.0)
           + WEIGHTS["mood"]    * (1.0 if mood_match  else 0.0)
           + WEIGHTS["energy"]  * energy_score
           + WEIGHTS["acoustic"] * acoustic_score)

    print(f"  >> Why '{song['title']}' ranked #1:")
    print(f"     Genre match  ({WEIGHTS['genre']:.0%} weight): {'YES' if genre_match else 'NO ':3}  "
          f"({song['genre']} == {user_prefs['genre']}?)  → {WEIGHTS['genre'] * (1.0 if genre_match else 0.0):.3f}")
    print(f"     Mood match   ({WEIGHTS['mood']:.0%} weight): {'YES' if mood_match  else 'NO ':3}  "
          f"({song['mood']} == {user_prefs['mood']}?)  → {WEIGHTS['mood'] * (1.0 if mood_match else 0.0):.3f}")
    print(f"     Energy prox  ({WEIGHTS['energy']:.0%} weight): {energy_score:.2f}  "
          f"(1 - |{song['energy']:.2f} - {user_prefs['energy']:.2f}|)  → {WEIGHTS['energy'] * energy_score:.3f}")
    print(f"     Acoustic fit ({WEIGHTS['acoustic']:.0%} weight): {acoustic_score:.2f}  "
          f"(acousticness={song['acousticness']:.2f})  → {WEIGHTS['acoustic'] * acoustic_score:.3f}")
    print(f"     {'─'*40}")
    print(f"     Total score: {total:.4f}")
    print()


def compare_strategies(user_prefs: dict, songs: list, profile_name: str) -> None:
    """Runs the same profile through every strategy and shows the #1 winner for each."""
    print(f"\n{'#'*60}")
    print(f"  Strategy Comparison — Profile: {profile_name}")
    print(f"{'#'*60}\n")
    rows = []
    for strat in [DEFAULT, GENRE_FIRST, MOOD_FIRST, ENERGY_FOCUSED]:
        results = recommend_songs(user_prefs, songs, k=1, strategy=strat)
        if results:
            song, score, _ = results[0]
            rows.append([strat.name, song["title"], song["artist"], song["genre"], f"{score:.4f}"])
    print(tabulate(
        rows,
        headers=["Strategy", "#1 Title", "Artist", "Genre", "Score"],
        tablefmt="rounded_outline",
    ))
    print()


def run_profile(name: str, user_prefs: dict, songs: list, strategy: RankingStrategy = DEFAULT) -> None:
    print(f"\n{'='*60}")
    print(f"  Profile: {name}  [Strategy: {strategy.name}]")
    print(f"  genre={user_prefs['genre']} | mood={user_prefs['mood']} | "
          f"energy={user_prefs['energy']} | likes_acoustic={user_prefs['likes_acoustic']}")
    print("=" * 60)

    recommendations = recommend_songs(user_prefs, songs, k=5, strategy=strategy)

    print(f"\nTop {len(recommendations)} Recommendations:\n")
    table_rows = []
    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        reasons_formatted = "\n".join(f"• {r}" for r in explanation.split("; "))
        table_rows.append([
            rank,
            song["title"],
            song["artist"],
            song["genre"],
            f"{score:.4f}",
            reasons_formatted,
        ])
    print(tabulate(
        table_rows,
        headers=["#", "Title", "Artist", "Genre", "Score", "Reasons"],
        tablefmt="rounded_outline",
        colalign=("center", "left", "left", "left", "center", "left"),
    ))
    print()

    # Step 2: explain why the #1 song ranked first
    if recommendations:
        explain_top_song(user_prefs, recommendations[0][0])


def main() -> None:
    songs = load_songs("data/songs.csv")
    for name, prefs in PROFILES.items():
        run_profile(name, prefs, songs, PROFILE_STRATEGIES.get(name, DEFAULT))
    compare_strategies(PROFILES["Conflicted Listener"], songs, "Conflicted Listener")


if __name__ == "__main__":
    main()
