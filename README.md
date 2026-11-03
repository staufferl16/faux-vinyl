# faux-vinyl
An online vinyl collection and virtual domicile for on-the-go audiophiles.


## About
Right now, I'm keeping this project as simple and pleasant as possible.  This will be an online
space for people to enjoy artwork while they listen to random albums of my recommendation.

Imagine a small corner of the internet with absolutely no intention for pushing advertisements or products.
It is simply a cozy virtual spot for watching whatever animations I jerry-rig to the UI.  Music plays in
the background.  Sit back.  Relax.  Enjoy a little time to yourself.


## Eventually
Soon, I'll have something available at `fauxvinyl.net`.

Maybe one day I can expand this to let people share their own faux vinyl recommendations.  I'll get
to that later.


## Task list

### Local stack
- [x] Run React (Vite) and Flask with Docker Compose, with live reload
- [x] Set up SQLite in WAL mode, with Alembic and a first migration for `users` and `spotify_tokens`
- [x] Add `.env.example` and ignore real `.env` files
- [x] Add a production image where Flask serves the built UI

### Spotify auth
- [ ] Register a Spotify developer app with the redirect URI `http://127.0.0.1:5173/auth/callback`
- [ ] Allowlist test users in the Spotify developer dashboard
- [ ] Add `/auth/login`, redirecting to Spotify with `state`
- [ ] Add `/auth/callback`, exchanging the code, storing tokens and setting an httpOnly session cookie
- [ ] Add `/auth/logout` and `/api/me`
- [ ] Encrypt refresh tokens at rest
- [ ] Add a Spotify client that refreshes tokens on demand and handles 429s (`Retry-After`, `QUOTA_EXCEEDED`)

### Deployment
- [ ] Choose a host with a persistent disk (a small VPS, Fly.io or Render)
- [ ] Refuse to start in production with the placeholder `SECRET_KEY`
- [ ] Publish at `fauxvinyl.net`


## Inspiration
https://poolsuite.net/


## Local development
You need Docker with Compose. No Spotify credentials are needed yet.

```sh
cp .env.example .env
docker compose up --build
```

| What | Where |
|---|---|
| App, with live reload | http://127.0.0.1:5173 |
| API, directly | http://127.0.0.1:5001/api/health |

Use `127.0.0.1` rather than `localhost`, because Spotify doesn't accept `localhost` redirect URIs.
The API is on host port 5001 because AirPlay Receiver holds port 5000 on macOS.

Migrations run when the backend starts. Other common commands:

```sh
docker compose exec backend pytest
docker compose exec backend alembic revision --autogenerate -m "describe the change"
docker compose exec frontend npm install <package>
docker compose down      # stop, keeping the database
docker compose down -v   # stop and delete the database
```

If you change `backend/requirements*.txt`, run `docker compose up --build` again.

To build and run the production image, where Flask serves the built UI on one port:

```sh
docker build --target prod -t faux-vinyl .
docker run --rm -p 127.0.0.1:8000:5000 --env-file .env -v faux-vinyl-prod-data:/data faux-vinyl
```
