# Fantasy Football Vegas Props Projections

A Python tool that generates fantasy football projections using Vegas player props from The Odds API. Supports multiple scoring formats (PPR, Half-PPR, Standard) and provides detailed breakdowns of projected fantasy points.

Available as both a **web application** and **command-line tool**.

## Features

- Fetches real-time player props from The Odds API
- Converts Vegas props (passing yards, rushing yards, TDs, etc.) to fantasy points
- Supports multiple scoring formats:
  - PPR (Points Per Reception)
  - Half-PPR
  - Standard (No PPR)
- Provides detailed breakdowns by category (passing, rushing, receiving)
- **Web App**: Modern, interactive UI with search and filtering
- **CLI**: Command-line interface with table output and JSON export

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/jarn-ff-projections.git
cd jarn-ff-projections
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your API key:
   - Get a free API key from [The Odds API](https://the-odds-api.com/)
   - Copy `.env.example` to `.env`:
     ```bash
     cp .env.example .env
     ```
   - Add your API key to `.env`:
     ```
     ODDS_API_KEY=your_api_key_here
     ```

## Usage

### Web Application (Recommended)

Start the web server:
```bash
python app.py
```

Then open your browser to `http://localhost:5000`

The web app provides:
- Interactive table with sortable columns
- Search functionality to find specific players
- Format selector (PPR, Half-PPR, Standard, or All)
- Detailed player breakdowns in modal popups
- Real-time data fetching from The Odds API
- Clean, modern interface

### Command-Line Interface

Get projections for all players in all formats:
```bash
python main.py
```

### Specific Format

Get projections for a specific scoring format:
```bash
python main.py --format PPR
python main.py --format HALF_PPR
python main.py --format STANDARD
```

### Detailed Breakdown

Show detailed breakdown for each player:
```bash
python main.py --detailed
```

### Specific Markets

Fetch specific prop markets only:
```bash
python main.py --markets player_pass_yds player_pass_tds player_rush_yds
```

### Export to JSON

Export projections to a JSON file:
```bash
python main.py --output projections.json
```

### Combined Options

```bash
python main.py --format PPR --detailed --output ppr_projections.json
```

## Project Structure

```
jarn-ff-projections/
├── config/
│   ├── __init__.py
│   └── scoring_formats.py    # Fantasy scoring format definitions
├── src/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── odds_api.py        # The Odds API client
│   └── projections/
│       ├── __init__.py
│       └── calculator.py      # Projection calculation logic
├── templates/
│   └── index.html             # Web app HTML template
├── static/
│   ├── css/
│   │   └── style.css          # Web app styles
│   └── js/
│       └── app.js             # Web app JavaScript
├── app.py                     # Flask web application
├── main.py                    # CLI entry point
├── requirements.txt
├── .env.example
└── README.md
```

## How It Works

1. **Fetch Props**: The tool fetches player props from The Odds API (passing yards, touchdowns, receptions, etc.)

2. **Parse Data**: Props from multiple bookmakers are averaged to get consensus lines

3. **Calculate Projections**: Props are converted to fantasy points using scoring format rules:
   - Passing: 1 pt per 25 yards, 4 pts per TD, -2 per INT
   - Rushing: 1 pt per 10 yards, 6 pts per TD
   - Receiving: 1 pt per 10 yards, 6 pts per TD, + reception bonus (1 for PPR, 0.5 for Half-PPR, 0 for Standard)
   - Fumbles: -2 per fumble lost

4. **Estimate Missing Stats**: When direct props aren't available, the tool estimates:
   - TDs from yardage props (historical ratios)
   - Fumbles from total touches

5. **Output**: Results are displayed in a formatted table or exported to JSON

## Available Prop Markets

The Odds API supports these NFL player prop markets:
- `player_pass_yds` - Passing yards
- `player_pass_tds` - Passing touchdowns
- `player_pass_completions` - Pass completions
- `player_pass_attempts` - Pass attempts
- `player_pass_interceptions` - Interceptions
- `player_rush_yds` - Rushing yards
- `player_rush_attempts` - Rush attempts
- `player_receptions` - Receptions
- `player_reception_yds` - Receiving yards
- `player_anytime_td` - Anytime touchdown scorer

## API Rate Limits

The Odds API has rate limits on the free tier. The tool displays remaining requests after each API call. Be mindful of your usage.

## Customization

### Adding Custom Scoring Formats

Edit `config/scoring_formats.py` to add your own scoring formats:

```python
SCORING_FORMATS["CUSTOM"] = {
    "name": "Custom Format",
    "passing": {"yards": 0.04, "touchdowns": 6, ...},
    "rushing": {"yards": 0.1, "touchdowns": 6, ...},
    # ...
}
```

### Adjusting Estimation Logic

Modify `src/projections/calculator.py` to adjust how missing stats are estimated (TD rates, fumble rates, etc.)

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.

## License

MIT License

## Disclaimer

This tool is for entertainment and research purposes only. Vegas props are not guarantees of actual performance. Always do your own research before making fantasy football or betting decisions.
