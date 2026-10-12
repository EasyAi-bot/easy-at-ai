easy@Ai — Android phone cloud setup

WHAT THIS DOES
This package lets you host the easy@Ai website and Python bridge on Render, then open it from your Android phone. You do not need a laptop. Hosting is free-tier and can sleep when idle. AI model requests are separate and may use limited Hugging Face credits.

STEP 1 — DOWNLOAD AND EXTRACT
1. Download easy_at_ai_cloud.zip to your Android phone.
2. Open your Files / File Manager app and find the ZIP in Downloads.
3. Tap it and choose Extract.
4. The extracted folder contains index.html, server.py, requirements.txt, render.yaml, and this guide.

STEP 2 — CREATE A GITHUB ACCOUNT
1. Open https://github.com in Chrome and create a free account.
2. Verify your email if asked.
3. Open https://github.com/new
4. Repository name: easy-at-ai
5. Choose Public (needed for the simplest free Render setup), then tap Create repository.

STEP 3 — UPLOAD THE APP FILES TO GITHUB
1. On your new repository page, tap Add file, then Upload files.
2. Select these four files from the extracted folder: index.html, server.py, requirements.txt, render.yaml. You may need to use your phone file picker and select files one by one or multi-select.
3. Scroll down and tap Commit changes. Do not upload any Hugging Face token or password.

STEP 4 — DEPLOY ON RENDER
1. Open https://render.com and create a free account.
2. Choose New +, then Web Service.
3. Connect GitHub and authorize Render if asked.
4. Select the easy-at-ai repository.
5. If it asks for settings, use: Runtime Python; Build command: pip install -r requirements.txt; Start command: uvicorn server:app --host 0.0.0.0 --port $PORT; Plan Free. The render.yaml file may fill these in automatically.
6. Tap Create Web Service and wait for the deployment to finish. It can take a few minutes.
7. Open the public onrender.com URL shown by Render. Save it as a bookmark on your phone.

STEP 5 — CONNECT REAL AI GENERATION
1. Create a Hugging Face account at https://huggingface.co/join
2. Open https://huggingface.co/settings/tokens and create a fine-grained access token with permission to make calls to Inference Providers.
3. Copy the token. It should begin with hf_.
4. Open your easy@Ai website URL, go to Generate, paste the token into the token box, and tap Check bridge + token.
5. Try text-to-image first. Only try image editing/video if the selected model supports it and your available quota permits it.

IMPORTANT
- Never paste your token into a public GitHub file, a comment, or this chat. Only enter it into the token field on your easy@Ai page. Reloading the page clears the token from the page's memory.
- This is a personal-use starter, not a secured public product. Anyone who knows the URL can open the website; do not share the URL widely. Requests still require the caller's own token.
- Render free web services sleep after inactivity and can take about a minute to wake up. Local files on the server are temporary; easy@Ai saves projects in your browser, so export backups regularly.
- Hugging Face currently lists a small monthly free credit allowance for Inference Providers, subject to change. Video generation may not work within free credits or may be unavailable for a chosen model. Check https://huggingface.co/docs/inference-providers/pricing before trying many generations.
- If GitHub's phone file picker makes uploading difficult, stop and tell ChatGPT exactly which screen you see. Do not share passwords or tokens.
