# Deployment Guide — GovCon Weekly Intelligence

Static HTML site. No build step, no dependencies.

---

## Option A: Netlify

### Drag-and-Drop (fastest)

1. Go to [app.netlify.com](https://app.netlify.com)
2. Drag the entire `landing/` folder onto the deploy area
3. Site goes live instantly at a random `*.netlify.app` subdomain
4. Go to **Site settings > Domain management** to add `govconweekly.com`

### CLI

```bash
# Install (one-time)
npm install -g netlify-cli

# Deploy from the landing directory
cd landing/

# Preview deploy (staging URL)
netlify deploy --dir=.

# Production deploy
netlify deploy --dir=. --prod
```

### Custom Domain (Netlify)

1. **Site settings > Domain management > Add custom domain**
2. Enter `govconweekly.com`
3. Netlify provides DNS records — add them at your registrar
4. SSL is provisioned automatically (Let's Encrypt)

---

## Option B: Vercel

### Drag-and-Drop

1. Go to [vercel.com/new](https://vercel.com/new)
2. Choose **Import Third-Party Git Repository** or click **Upload** (bottom of page)
3. Upload the `landing/` folder
4. Framework preset: **Other** (no framework)
5. Override output directory to `.` if prompted
6. Deploy

### CLI

```bash
# Install (one-time)
npm install -g vercel

# Deploy from the landing directory
cd landing/

# Preview deploy (staging URL)
vercel

# Production deploy
vercel --prod
```

### Custom Domain (Vercel)

1. **Project Settings > Domains**
2. Enter `govconweekly.com`
3. Vercel provides DNS records — add them at your registrar
4. SSL is automatic

---

## Post-Deploy Checklist

- [ ] Verify `index.html` loads correctly
- [ ] Verify `/terms` redirects to `terms.html` (once that page exists)
- [ ] Verify `/privacy` redirects to `privacy.html` (once that page exists)
- [ ] Verify `robots.txt` is accessible at `/robots.txt`
- [ ] Verify `sitemap.xml` is accessible at `/sitemap.xml`
- [ ] Configure custom domain and confirm SSL
- [ ] Submit sitemap to Google Search Console (`https://govconweekly.com/sitemap.xml`)
- [ ] Test on mobile

## Notes

- The `_redirects` file is Netlify-specific. Vercel uses `vercel.json` rewrites instead.
- Update `sitemap.xml` domain if using a different URL than `govconweekly.com`.
- Security headers are configured in both `netlify.toml` and `vercel.json`.
