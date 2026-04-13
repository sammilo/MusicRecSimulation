# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

**Musicomaniac**

---

## 2. Intended Use  

Musicomaniac suggests up to five songs from a small fixed catalog based on a listener's taste profile. It explores how content-based filtering works, on a simpler level.

The system assumes each user can be described by a small set of stable preferences: a favorite genre, a favorite mood, and numeric targets for energy, acousticness, valence, danceability, and tempo. It does not learn from listening history, adapt over time, or account for context such as time of day or activity.

---

## 3. How the Model Works  

Every song in the catalog is described by seven pieces of information: genre, mood, energy, acousticness, mood, danceability, and tempo.

Each listener is described the same way: a favorite genre, a favorite mood, and target numbers for the other qualities.

To score a song, the system measures how far apart the song's numbers are from the listener's target numbers. Features that tend to have a bigger impact on whether you enjoy a song — like energy — are given more weight, so a mismatch there penalizes the song more than a mismatch in danceability. Tempo is scaled down before the calculation so that its larger raw numbers do not unfairly dominate.

Once distance is calculated, genre and mood are used as multipliers. If the song's genre matches the listener's favorite, the distance is halved, making the song rank higher. If the mood matches, the distance is reduced by another 25%. This reflects the idea that genre and mood are the first things most people use to sort their playlists, while the numeric features fine-tune the ranking within those categories.

The final score converts the distance into a number between 0 and 1, where 1 means a near-perfect match and lower numbers mean a weaker fit. Songs are returned in order from highest score to lowest.

The main change from the original starter logic was replacing binary acoustic preference and a small set of additive bonuses with a full weighted distance across all five continuous features, and replacing additive bonuses for genre and mood with proportional multipliers. This makes the scoring more consistent and avoids cases where a large bonus could override what are otherwise very different-sounding songs.

---

## 4. Data  

The catalog contains 20 songs stored in `data/songs.csv`. Each song has a title, artist, genre, mood, and five numeric features: energy, tempo in BPM, valence, danceability, and acousticness.

The 20 songs span 16 distinct genres including pop, lofi, rock, jazz, metal, electronic, folk, blues, classical, ambient, synthwave, indie pop, latin, darkwave, country, and pop punk. Moods represented include happy, chill, intense, relaxed, focused, moody, nostalgic, melancholic, peaceful, and energetic.

Some gaps in the data worth noting: the catalog skews toward Western popular genres and contains only one or two songs per genre in most cases. Genres like R&B, hip-hop, reggae, K-pop, and most non-Western traditions are absent. Since the system can only recommend what is in the catalog, listeners whose tastes fall outside these genres will never receive a genre-matched recommendation and will be ranked solely on continuous-feature distance. The 20-song catalog is also too small to surface meaningful variety — a real recommender would need thousands of entries to avoid repeatedly surfacing the same few songs.

---

## 5. Strengths  

The system works best for listeners whose favorite genre and mood are well represented in the catalog. In testing, the Pop Fan profile consistently received recommendations that matched intuition: the top result shared both genre and mood, and the remaining slots pulled in nearby genres like indie pop and latin that have similar sonic signatures. The Jazz Cafe Regular similarly received a strong top result and reasonable fallbacks from acoustically similar lofi and folk songs, which makes sense given how much those genres overlap on the acousticness and tempo dimensions.

---

## 6. Limitations and Bias  

**Missing features.** The model does not consider lyrics, language, song structure, or cultural context. Two songs can be close in feature space while sounding nothing alike to a human listener.

**Narrow catalog.** With only 20 songs and 16 genres, most genres appear once. A listener whose favorite genre has one entry will see that song first, then fall back to unrelated genres ranked purely by feature distance.

**Designer-defined weights.** The feature weights (energy: 2.0, acousticness: 1.5, etc.) were chosen by judgment, not learned from data. They reflect assumptions about what matters to a typical listener. For users who weight danceability over energy, or who care most about tempo, the rankings will be consistently off and there is no way for the system to detect or correct this.

**Genre and mood multipliers amplify narrow taste.** The 0.5 genre multiplier is strong enough to surface a song that is a moderate feature mismatch over a song that is a nearly perfect feature match. For users with specific genre preferences that happen to align with the catalog, this works well. For users with broad or cross-genre taste, it can produce results that feel forced.

**No diversity.** The system always returns the closest matches. It never intentionally introduces a surprising or different recommendation. Over repeated use, a real listener would likely receive the same small cluster of songs every time.

---

## 7. Evaluation  

Five distinct user profiles were tested, each designed to stress-test a different part of the scoring logic:

**Pop Fan** — high energy, upbeat, low acousticness. Both the genre (pop) and mood (happy) are well represented in the catalog. Results were strong: the top recommendation matched on genre, mood, and all five continuous features.

**Late-Night Lofi Listener** — low energy, high acousticness, slow tempo. Lofi has two entries in the catalog and both appeared in the top three, which is the expected behavior. The fourth result was an ambient song with a chill mood that made sense as a fallback.

**Metal Head** — extreme values across the board (energy near 1.0, valence near 0.2, tempo near 175 BPM). The single metal song scored highest by a wide margin. The next results were rock and electronic songs that matched the intense mood. This confirmed that the mood multiplier functions as a reasonable secondary filter when the primary genre is scarce.

**Jazz Cafe Regular** — mid-tempo, high acousticness, relaxed mood. Coffee Shop Stories was correctly identified as the top match. 

**Dance Floor Regular** — favorite genre is electronic, which has only one entry. That entry appeared first. The remaining four spots were filled by songs with the intense mood and high danceability, confirming that mood acts as a useful secondary signal when the genre catalog is thin.

One notable pattern across all profiles: when a song matched both genre and mood, it scored well above everything else, sometimes by a large margin. 

A suite of 15 automated tests was also written to verify that the scoring math, ranking order, multiplier behavior, and explanation logic all work as specified.

---

## 8. Future Work  
If I had more time to develop this project, I'd like to expand the recommender algorithm so that it considers more factors such as the song language, artist, and release date. 

I'd also like to expand songs.csv so that there are thousands of songs to draw from, to better test the algorithm's capabilites.
---

## 9. Personal Reflection  
My biggest learning moment was figuring out the math for determening how close two songs are in Eucledian space, especially given how many factors the recommender considers and the weights attributed to them. 

AI helped me find potential biases and limitations that I missed, allowing me to expand my code to consider more edge cases. 