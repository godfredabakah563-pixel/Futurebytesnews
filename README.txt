Futurebytesnews — BBC-style auto-updating bundle

What this ZIP contains:
- index.html    (client HTML, reads public/articles.json)
- style.css     (BBC-like light theme)
- script.js     (loads public/articles.json)
- update_fetcher.py   (fetches BBC Technology RSS, downloads images into public/images/, writes public/articles.json)
- .github/workflows/update-and-deploy.yml  (workflow: run fetcher, upload artifact, deploy to Pages)
- public/       (empty folder placeholder)

How to deploy:
1. Create a new public GitHub repo (e.g., futurebytesnews)
2. Upload all files and folders to the repo root (include .github)
3. In GitHub, go to Actions -> enable the workflow if prompted
4. Run the workflow manually once (Actions -> select workflow -> Run workflow)
5. After success, go to Settings -> Pages to confirm the published URL (or wait — the workflow deploy step publishes)
6. The workflow runs every 30 minutes to refresh articles and images

Notes:
- This environment cannot include external images inside the ZIP. The update_fetcher.py will download images when it runs on GitHub Actions.
- If you want to customize number of items, or change layout, tell me and I will update the bundle.
