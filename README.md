# Canteen Care

A web application for canteen food ordering and complaint management.

## Live Demo

[Open Canteen Care](https://canteen-care.onrender.com)

> The Render free service may take a short time to wake up on its first visit.

## Features

- Browse available food items
- Place canteen orders
- Submit complaints
- Admin-protected order and complaint management APIs
- Data stored with Supabase

## Tech Stack

- Backend: FastAPI and Uvicorn
- Database: Supabase
- Frontend: HTML, CSS, and JavaScript
- Deployment: Render

## Run Locally

1. Clone the repository and enter the project directory.
2. Create a `.env` file with:

   ```env
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_key
   ADMIN_KEY=your_admin_key
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Start the server:

   ```bash
   uvicorn main:app --reload
   ```

5. Open `http://127.0.0.1:8000` in your browser.

## API Documentation

When running locally, open `http://127.0.0.1:8000/docs`. The deployed API documentation is available at `https://canteen-care.onrender.com/docs`.
