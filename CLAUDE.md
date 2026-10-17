# ff-projections

## Updating projections ("update projections")

This is a routine task — don't explore the codebase for it.

1. `pip install -q -r requirements.txt` (if deps missing). Needs `ODDS_API_KEY` in env or `.env`.
   The key lives in the local, gitignored `.env` (free tier, 500 credits/month — it gets
   swapped for a new key when the limit is hit). Never commit the key or paste it into tracked files.
2. `python update_projections.py` — prints events/players found, API credits used/remaining.
3. Commit only the cache: `git add data/projections_cache.json && git commit -m "Update projections to Week N"`
   (N = week shown in the script output / `week` field), then push.

Do NOT read, cat, or `git diff` `data/projections_cache.json` (~400KB, ~18k-line diffs).
Use `git diff --stat` if you need to confirm it changed.

If the script fails, the relevant code is `update_projections.py` and `src/api/odds_api.py` only.
