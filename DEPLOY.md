# Deploy Carbon Labs to Supabase + Vercel

## Architecture

```
Browser (Vercel CDN)
    ↓  Supabase JS client
Supabase
    ├── Auth (login, signup, password reset)
    └── PostgreSQL (carts, orders, contact, newsletter)
```

No custom server needed in production. Vercel hosts static files; Supabase handles auth and data.

---

## Step 1 — Create a Supabase project

1. Go to [supabase.com](https://supabase.com) and create a project.
2. Open **SQL Editor** → **New query**.
3. Paste the contents of [`supabase/schema.sql`](supabase/schema.sql) and click **Run**.

This creates tables, triggers, and Row Level Security policies.

---

## Step 2 — Configure Supabase Auth

In **Authentication → URL Configuration**:

| Setting | Value |
|---------|--------|
| **Site URL** | `https://your-app.vercel.app` (update after first deploy) |
| **Redirect URLs** | `https://your-app.vercel.app/**` and `http://localhost:8000/**` |

For local testing without email confirmation:

**Authentication → Providers → Email** → turn off **Confirm email** (optional, simpler for dev).

Password reset emails use Supabase’s built-in mailer (or configure SMTP under **Project Settings → Auth**).

---

## Step 3 — Get your API keys

**Project Settings → API**:

- **Project URL** → `SUPABASE_URL`
- **anon public** key → `SUPABASE_ANON_KEY` (safe to use in the browser; RLS protects data)

Never put the `service_role` key in frontend code.

---

## Step 4 — Local development

```powershell
cd C:\Users\jackm\carbon-labs\public
copy config.example.js config.js
```

Edit `config.js` with your Supabase URL and anon key.

Serve the site locally (Python server still works for static files):

```powershell
cd C:\Users\jackm\carbon-labs\backend
py server.py
```

Open http://localhost:8000 — auth and data go to Supabase, not SQLite.

---

## Step 5 — Deploy to Vercel

### Option A: GitHub (recommended)

1. Push `carbon-labs` to a GitHub repo.
2. Go to [vercel.com](https://vercel.com) → **Add New Project** → import the repo.
3. Vercel detects `vercel.json` automatically:
   - **Build command:** `node scripts/inject-config.js`
   - **Output directory:** `public`
4. Add **Environment Variables**:

| Name | Value |
|------|--------|
| `SUPABASE_URL` | `https://xxxxx.supabase.co` |
| `SUPABASE_ANON_KEY` | your anon key |

5. Deploy.

The build script writes `public/config.js` from those env vars at deploy time.

### Option B: Vercel CLI

```powershell
npm i -g vercel
cd C:\Users\jackm\carbon-labs
vercel
vercel env add SUPABASE_URL
vercel env add SUPABASE_ANON_KEY
vercel --prod
```

---

## Step 6 — Update Supabase redirect URLs

After Vercel gives you a URL (e.g. `https://carbon-labs.vercel.app`), add it to Supabase **Authentication → URL Configuration** as Site URL and Redirect URL.

---

## Viewing data

In Supabase Dashboard:

- **Table Editor** → `orders`, `contact_messages`, `newsletter_subscribers`
- **Authentication** → Users

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| “Supabase is not configured” | `config.js` missing locally, or Vercel env vars not set |
| Signup works but can’t log in | Email confirmation enabled — check inbox or disable in Auth settings |
| Password reset doesn’t work | Add your Vercel URL to Supabase Redirect URLs |
| RLS errors on insert | Re-run `schema.sql`; ensure user is logged in for orders/cart |
| 31MB deploy size | Normal — `index.html` has embedded product images |

---

## What changed from the Python server

| Before | After |
|--------|--------|
| `backend/server.py` + SQLite | Supabase PostgreSQL |
| Custom JWT | Supabase Auth |
| `/api/*` routes | Direct Supabase client in `api.js` |

`backend/server.py` is only needed for **local static file hosting** now. Production uses Vercel + Supabase only.
