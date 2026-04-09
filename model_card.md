# Model Card: Music Recommender Simulation

## 1. Model Name

**GrooveGenius 1.0**

---

## 2. Intended Use

- Suggests up to 5 songs from a 30-song catalog based on stated user preferences
- Designed for **classroom exploration** of content-based filtering, not real-world deployment
- Assumes the user knows their preferences and can express them as simple labels
- Does **not** learn from listening history or adapt over time

---

## 3. How the Model Works

Each song is scored against four signals, then all songs are ranked highest to lowest:

| Signal | Type | Weight | How it's calculated |
|---|---|---|---|
| Genre match | Binary | **16%** | 1.0 if genre matches, 0.0 if not |
| Mood match | Binary | **28%** | 1.0 if mood matches, 0.0 if not |
| Energy proximity | Continuous | **47%** | `1 - \|song.energy - target\|` |
| Acoustic fit | Continuous | **9%** | `song.acousticness` if user likes acoustic, else `1 - acousticness` |

```
final score = 0.16 × genre + 0.28 × mood + 0.47 × energy + 0.09 × acoustic
```

Every song is scored (no pre-filtering). Top 5 are returned with a plain-language explanation.

![Sample terminal output](pics/sample_output.png)

---

## 4. Data

**30 songs** in `data/songs.csv`, 12 attributes each.

| Attribute | Coverage |
|---|---|
| Genres | 27 unique (lofi: 3 songs, pop: 2 songs, all others: 1 song each) |
| Moods | 25 unique (chill: 3×, happy/intense/relaxed: 2× each, rest: 1×) |
| Energy | 3 low (0.0–0.3), 11 mid (0.3–0.7), **16 high (0.7–1.0)** |
| Acousticness | **16 low** (<0.3), 4 mid, 10 high (>0.7) |

> Catalog skews toward **high-energy, non-acoustic** music. Most genres and moods appear only once.

---

## 5. Strengths

- **Transparent:** Every result includes a reason list explaining exactly which signals fired
- **No training needed:** Works instantly from a CSV, no machine learning required
- **Best case, High-Energy Pop:** Sunrise City scored **0.9462**, hitting all 4 signals at once

![High-Energy Pop top results](pics/weightshift_profiles_1.png)

- **Chill Lofi** also worked well after fixing string mismatches (`"lo-fi"` → `"lofi"`), with Library Rain scoring **0.9169**

![Chill Lofi top results](pics/weightshift_profiles_2.png)

---

## 6. Limitations and Bias

**Primary weakness: Genre lock-out from catalog sparsity**

- 25 of 27 genres have exactly **1 song** in the catalog
- That one song almost always ranks #1 for its genre, regardless of mood or energy fit
- Example: "Deep Intense Rock" wants `angry` rock. Only 1 rock song exists ("Storm Runner", mood=`intense`). It ranked #1 anyway under baseline weights.
- The remaining 4 recommendations are decided by energy + acoustic alone (only 56% of the score combined)

| Genre requests | Songs available | Problem |
|---|---|---|
| lofi | 3 songs | Works reasonably |
| pop | 2 songs | Limited variety |
| rock, metal, jazz, classical... | 1 song each | Winner decided before scoring |

**Other biases:**

- **Energy skew:** 53% of songs are high-energy; low-energy users have fewer close matches
- **Mood desert:** 21 of 25 moods appear only once; mood signal rarely fires twice
- **No conflict detection:** Contradictory preferences (e.g., `acoustic=True` + `energy=0.9`) return low scores silently with no warning

---

## 7. Diversity and Fairness

Without any diversity logic, a pure score-sort can produce a filter bubble: all 5 results come from the same artist or genre, which feels repetitive and reinforces a narrow slice of the catalog.

GrooveGenius uses a **greedy re-ranking loop** to counteract this. Before each selection, two penalties are subtracted from a song's raw score:

| Penalty | Amount | Trigger |
|---|---|---|
| Artist repeat | −0.30 | Artist already appears in the selected list |
| Genre repeat | −0.15 | Genre already appears in the selected list |

The artist penalty is intentionally larger (−0.30) because hearing the same artist back-to-back is the most jarring form of repetition. The genre penalty is smaller (−0.15) because some genre overlap is acceptable — a user who wants pop may still enjoy two pop songs as long as they aren't both from the same act.

**How it reduces filter bubbles:** A second song by Neon Echo that scores 0.72 raw will be treated as if it scored 0.42 (0.72 − 0.30), making it less competitive than a 0.55-scoring song from a fresh artist. The catalog's weaker matches get a real shot at the top 5.

**Fairness benefit:** The penalty is applied dynamically, not as a hard ban. An artist can still appear twice if they genuinely dominate on score — but only after every other artist has been given a fair chance to rank. This mirrors how real platforms balance "best match" against "don't play the same artist three times in a row."

---

## 8. Evaluation

### Profiles Tested

| Profile | genre | mood | energy | acoustic | Top Result | Score |
|---|---|---|---|---|---|---|
| High-Energy Pop | pop | happy | 0.9 | No | Sunrise City | 0.9462 |
| Chill Lofi | lofi | chill | 0.2 | Yes | Library Rain | 0.9169 |
| Deep Intense Rock | rock | angry | 0.95 | No | Iron Curtain | 0.8346 |
| Conflicted Listener | classical | sad | 0.9 | Yes | Hollow Rain | 0.5472 |

### What Surprised Us

- **Chill Lofi was completely broken** until string values were corrected (`"lo-fi"` and `"calm"` don't exist in the dataset)
- **Deep Intense Rock** never found a song matching both `rock` and `angry`; genre and mood were split across two different songs
- **Conflicted Listener** peaked at only 0.5472; no song in the catalog is both acoustic and high-energy

### Weight Shift Experiment

Genre weight halved, energy weight doubled, then renormalized:

| Signal | Baseline | Shifted (active) |
|---|---|---|
| Genre | 0.35 | **0.16** |
| Mood | 0.30 | **0.28** |
| Energy | 0.25 | **0.47** |
| Acoustic | 0.10 | **0.09** |

**Results by profile:**

| Profile | Changed? | What changed |
|---|---|---|
| High-Energy Pop | Minor | #2 and #3 swapped (Rooftop Lights up, Gym Hero down) |
| Chill Lofi | Yes | Spacewalk Thoughts promoted (closer energy) over Focus Flow |
| Deep Intense Rock | **Yes, clearest win** | Iron Curtain (#1) displaced Storm Runner; mood+energy beats genre-only |
| Conflicted Listener | No improvement | Neither config can resolve contradictory preferences |

Full experiment: [`docs/weight_shift_experiment.md`](docs/weight_shift_experiment.md)

![Deep Intense Rock, shifted weights](pics/weightshift_profiles_3.png)
![Conflicted Listener, shifted weights](pics/weightshift_profiles_4.png)

---

## 8. Future Work

| Idea | Problem it solves |
|---|---|
| Genre similarity graph | Partial credit for related genres (lofi ~ ambient), breaks winner-takes-all |
| Conflict detection | Warn users when preferences contradict each other |
| Larger balanced catalog | 3–5 songs per genre so all signals can actually differentiate |
| Continuous mood scoring | "angry" and "intense" should be closer than "angry" and "peaceful" |

---

## 9. Personal Reflection

The biggest surprise: the scoring formula looked balanced on paper (genre=35%, mood=30%, energy=25%), but genre dominated nearly every result in practice. Not because its weight was too high, but because 25 of 27 genres had only one song to compete with. Intended weight and actual influence are two different things.

The weight shift experiment confirmed this. When I halved genre's weight and doubled energy's, 2 of 4 profiles got more accurate results — most clearly "Deep Intense Rock," where a metal song with a perfect angry mood and exact energy match was rightly promoted over a rock song that only matched on genre. The formula wasn't broken; it was just over-rewarding genre in a catalog where genre matches are nearly guaranteed to be unique.

The other lesson came from comparing profile pairs. Two profiles can request the same energy (0.9) and get scores 0.40 apart, because one has preferences the catalog can satisfy and the other doesn't. Result quality depends as much on catalog coverage as on the algorithm — and the system gives no warning when it can't find a good match.

Real apps like Spotify feel more varied not because their algorithms are smarter, but because millions of songs per genre give every signal a real chance to matter.
