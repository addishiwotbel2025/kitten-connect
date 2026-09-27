# Deploying KittenConnect

Backend → **Render**, Frontend → **Vercel**. Both free. Do the steps in order:
the frontend needs the backend URL, and the backend needs the frontend URL.

---

## Step 0 — Push to GitHub

From the project folder:

```bash
git remote add origin https://github.com/<your-username>/kittenconnect.git
git branch -M main
git push -u origin main
```

(If you haven't created the empty repo yet, do it at https://github.com/new —
name it `kittenconnect`, leave it empty, then run the commands above.)

---

## Step 1 — Deploy the backend on Render

1. Go to https://render.com and sign in with GitHub.
2. Click **New +** → **Blueprint**.
3. Select your `kittenconnect` repo. Render reads `render.yaml` automatically.
4. It will create a web service called **kittenconnect-api** with `SECRET_KEY`
   auto-generated. Click **Apply**.
5. Wait for the first deploy (a few minutes). When done, copy your backend URL —
   it looks like `https://kittenconnect-api.onrender.com`.
6. Test it: open `https://kittenconnect-api.onrender.com/docs` — you should see
   the API docs.

> Leave `FRONTEND_URL` blank for now — you'll set it in Step 3.

---

## Step 2 — Deploy the frontend on Vercel

1. Go to https://vercel.com and sign in with GitHub.
2. Click **Add New…** → **Project** → import your `kittenconnect` repo.
3. Configure:
   - **Root Directory:** `frontend`
   - **Framework Preset:** Vite (auto-detected)
   - **Build Command:** `npm run build` (default)
   - **Output Directory:** `dist` (default)
4. Under **Environment Variables**, add:
   - **Name:** `VITE_API_URL`
   - **Value:** your Render backend URL from Step 1
     (e.g. `https://kittenconnect-api.onrender.com`) — no trailing slash
5. Click **Deploy**. When done, copy your frontend URL —
   e.g. `https://kittenconnect.vercel.app`. **This is the link for your resume.**

---

## Step 3 — Connect them (CORS)

The backend must allow the browser to call it from your Vercel URL.

1. In Render, open **kittenconnect-api** → **Environment**.
2. Add an environment variable:
   - **Key:** `FRONTEND_URL`
   - **Value:** your Vercel URL from Step 2 (e.g. `https://kittenconnect.vercel.app`)
3. Save. Render redeploys automatically.

Now open your Vercel URL, sign up, and post a kitten. 🎉

---

## Known free-tier limitations (fine for a demo)

- **Cold starts:** Render's free backend sleeps after ~15 min of inactivity, so
  the first request after a nap can take 30–50 seconds. Just wait and refresh.
- **Data resets:** the SQLite database and uploaded photos live on the server's
  temporary disk, so they reset when Render restarts/redeploys. To make data
  permanent later, switch to a hosted Postgres database and a persistent disk or
  cloud storage (e.g. Render Disks, or S3/Cloudinary for photos).

## Updating the live site

Any `git push` to `main` triggers automatic redeploys on both Render and Vercel.
