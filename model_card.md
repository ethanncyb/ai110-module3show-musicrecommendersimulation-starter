# Model Card: Music Recommender Simulation

## 1. Model Name

**VibeFinder 1.0**

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

## 7. Evaluation

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
| Diversity enforcement | Prevent 5 near-identical songs from dominating the top results |
| Larger balanced catalog | 3–5 songs per genre so all signals can actually differentiate |
| Continuous mood scoring | "angry" and "intense" should be closer than "angry" and "peaceful" |

---

## 9. Personal Reflection

The biggest surprise: the scoring formula looked balanced on paper (genre=35%, mood=30%, energy=25%), but genre dominated nearly every result in practice. Not because its weight was too high, but because 25 of 27 genres had only one song to compete with. Intended weight and actual influence are two different things. Real apps like Spotify feel more varied not because their algorithms are smarter, but because millions of songs per genre give every signal a real chance to matter.
