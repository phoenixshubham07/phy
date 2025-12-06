# How to Deploy to Vercel

Since your code is now on GitHub, deploying to Vercel is easy.

1.  **Log in to Vercel**: Go to [vercel.com](https://vercel.com) and log in (usually with GitHub).
2.  **Add New Project**: Click **"Add New..."** -> **"Project"**.
3.  **Import GitHub Repo**: Finds `phoenixshubham07/phy` and click **"Import"**.
4.  **Configure Project**:
    *   **Project Name**: Leave as is or change it (e.g., `physics-bank`).
    *   **Framework Preset**: Select **"Other"**.
    *   **Root Directory**: Click "Edit" and select **`output`**. 
        *   *(This is critical because the actual website files are inside the `output` folder).*
5.  **Environment Variables**:
    *   Go to **Settings** -> **Environment Variables**.
    *   Add a new variable:
        *   **Key**: `GEMINI_API_KEY`
        *   **Value**: `AIzaSyA4meddsqrMMhQ47MSq2jHXDZF3Jwnyp-M` (or your preferred key)
    *   Click **Save**.
6.  **Deploy**: Click **"Deploy"**.

Vercel will build the site and deploy the serverless function.
