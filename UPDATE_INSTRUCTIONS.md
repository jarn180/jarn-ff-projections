# How to Update Projections

The app uses cached data to avoid burning through API tokens. Follow these steps to refresh the projections:

## Weekly Update Process

**Run this command once per week (or whenever you want fresh data):**

```bash
python update_projections.py
```

This will:
- ✅ Fetch fresh player props from The Odds API
- ✅ Calculate projections for all formats (PPR, Half-PPR, Standard)
- ✅ Save everything to `data/projections_cache.json`
- ✅ Display how many API requests you have remaining

## For Vercel Deployment

When deploying to Vercel, the cached data file will be included in your deployment, so users see the projections without making API calls.

### Update workflow for production:

1. **Locally, update the cache:**
   ```bash
   python update_projections.py
   ```

2. **Commit and push the updated cache:**
   ```bash
   git add data/projections_cache.json
   git commit -m "Update projections for Week X"
   git push
   ```

3. **Vercel will auto-deploy** with the fresh data

## What Users See

- Data loads **instantly** from the cache (no API calls)
- Shows **"Last Updated: [date/time]"** so users know when data was refreshed
- **No tokens burned** by visitors viewing the site
- You control exactly when to refresh data

## API Token Usage

- Each update uses approximately **20-30 API calls** (depends on number of games)
- Free tier: **500 requests/month**
- This means you can update **~20 times per month** safely

## Tips

- Update **once per week** during the season (Sunday or Monday after games)
- Update **more frequently** as game day approaches if props change significantly
- Check remaining API calls in the script output
- The cache file is about 200-300KB (fine for git)
