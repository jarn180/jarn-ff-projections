# JarnFF frontend

React + Vite + Tailwind CSS + Framer Motion + Lucide icons, served by the Flask app in `../app.py` as a single-page app.

## Develop

```bash
npm install
npm run dev
```

The dev server proxies `/api/*` requests to Flask on `localhost:5000` (see `vite.config.js`), so run `python ../app.py` alongside it.

## Build for deployment

```bash
npm run build
```

Outputs to `../static/app` with fixed filenames (`main.js`, `main.css`) so `templates/index.html` can reference them directly. There's no build step in the deployment pipeline, so the built output in `static/app` must be committed after any frontend change.
