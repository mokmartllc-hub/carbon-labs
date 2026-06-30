# Carbon Labs

Research peptide storefront with Supabase (auth + database) and Vercel (hosting).

## Production deploy

See **[DEPLOY.md](DEPLOY.md)** for the full Supabase + Vercel setup guide.

Quick summary:

1. Run `supabase/schema.sql` in your Supabase SQL Editor
2. Copy `public/config.example.js` → `public/config.js` (local only)
3. Push to GitHub and import into Vercel
4. Set `SUPABASE_URL` and `SUPABASE_ANON_KEY` in Vercel env vars

## Local development

```powershell
# 1. Configure Supabase keys
cd public
copy config.example.js config.js
# Edit config.js with your Supabase URL + anon key

# 2. Serve the site
cd ..\backend
py server.py
```

Open http://localhost:8000

## Project structure

```
carbon-labs/
├── public/           ← static site (deployed to Vercel)
│   ├── index.html
│   ├── api.js        ← Supabase client integration
│   └── config.js     ← your keys (local only, gitignored)
├── supabase/
│   └── schema.sql    ← run once in Supabase dashboard
├── scripts/
│   └── inject-config.js  ← Vercel build: writes config.js from env
├── vercel.json
└── DEPLOY.md
```

`backend/server.py` is optional — only for serving static files locally.
