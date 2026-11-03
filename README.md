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

I also want an option for the player to play music from my personal library, not just Spotify.  How that
works is still to be decided.


## How the music works
I curate a few Spotify playlists.  The backend syncs the albums in them and stores the list.  The player
picks a random album from that list and plays it from start to finish, like someone spinning a record.
When the album ends, it picks another.  If you leave and come back, it picks a fresh one.

- Albums and EPs count.  Singles and compilations don't.
- Spotify has no EP type.  The API reports EPs as `single`, so a "single" with 4 or more tracks counts as
  an EP.  (Spotify calls a release an EP when it has 4 to 6 tracks and runs under 30 minutes.  Track count
  alone is close enough here.)
- Each album is played whole, in order, with shuffle and repeat turned off.


## Spotify restrictions
These are Spotify's rules for apps in Development Mode, as of February 2026.  For now, I accept them.

- **Premium required.**  Playback in the browser uses the Web Playback SDK, which only works for Premium
  listeners.  The app owner (me) also needs Premium, or the app stops working.
- **5 users.**  Development Mode apps allow 5 allowlisted users.  Extended Quota Mode removes the limit,
  but Spotify only grants it to established businesses, so a public `fauxvinyl.net` isn't possible on
  Spotify alone.
- **Desktop only.**  The Web Playback SDK doesn't support mobile browsers.
- **Own playlists only.**  `GET /playlists/{id}/items` (renamed from `/tracks`) only returns the contents of
  playlists the signed-in user owns or collaborates on.  Anything else returns `403`, including Spotify's
  own playlists like Discover Weekly.  This is why the albums come from my curated playlists, synced with my
  own token.
- **No bulk lookups.**  `GET /albums`, `GET /tracks` and `GET /artists` (several at once) were removed.
  Playback uses the album URI directly, so album track lists aren't needed.
- **Shared rate limit.**  Development Mode quotas count across the whole developer account.  A `429`
  response includes `Retry-After`, and sometimes `"reason": "QUOTA_EXCEEDED"`.  Syncs only refetch a
  playlist when its `snapshot_id` changes.
- **Removed fields.**  `popularity`, `label` and `available_markets` no longer come back on albums and tracks,
  and `GET /me` no longer returns `email`, `country` or `product`.

References:
[February 2026 migration guide](https://developer.spotify.com/documentation/web-api/tutorials/february-2026-migration-guide),
[February 2026 changelog](https://developer.spotify.com/documentation/web-api/references/changes/february-2026),
[July 2026 changelog](https://developer.spotify.com/documentation/web-api/references/changes/july-2026)


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
- [ ] Request the scopes `streaming`, `user-read-email`, `user-read-private`, `user-modify-playback-state`,
  `user-read-playback-state`, `playlist-read-private` and `playlist-read-collaborative`
- [ ] Add `/api/spotify/token`, giving the browser a fresh access token (refresh tokens stay on the server)

### Curated playlists
- [ ] Add a migration for `playlists` (with `snapshot_id`), `albums` and `playlist_albums`
- [ ] Sync a curated playlist with my token: page through `/playlists/{id}/items`, keep albums and EPs,
  skip singles, compilations, episodes and local files, and remove duplicate albums
- [ ] Re-sync only when the playlist's `snapshot_id` changes

### Player
- [ ] Load the Web Playback SDK and register the browser as a playback device
- [ ] Add a "drop the needle" button, since browsers block audio until the user clicks
- [ ] Pick a random album without repeats until every album has played
- [ ] Play the album with `context_uri`, with shuffle and repeat off
- [ ] Detect when the album ends, or when Spotify autoplay starts a different album, and pick the next one
- [ ] Disconnect the player when the listener leaves

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
