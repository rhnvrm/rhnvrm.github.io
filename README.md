# Rohan's GitHub workbench

A public project directory and daily GitHub work log. Built with Zola and the
[Doordarshan](https://github.com/oddship/doordarshan-zola) theme, pinned as a submodule.
Writing and personal pages live at https://rohanverma.net.

## Develop

```sh
git submodule update --init --recursive
python3 scripts/collect.py --offline
zola serve
```

Use Zola 0.21.0 and Python 3.12+. No pip or Node dependencies are required.
To refresh public GitHub data, run `GITHUB_TOKEN=… python3 scripts/collect.py`
with the token supplied through your environment, never committed.

## Data and daily updates

`data/settings.json` controls owners, excluded repositories, and selected projects.
The collector includes public original repositories from `rhnvrm` and `oddship`,
including archived ones. Repository push times are labeled as such; the homepage's
"Working on" section comes from Rohan's own recorded contributions.

The 06:47 IST workflow collects public events and authored commits from recently
pushed repositories over a rolling 14-day window. Push events discover contribution
repositories beyond the configured owners. Events include PR actions, reviews,
issues, and published releases; stars and private activity are excluded. This is
an observed public work log, not an exhaustive account of all GitHub work. GitHub
limits event history; the first snapshot is a recent backfill. Collected records
are deduplicated and retained in Git, with days grouped in Asia/Kolkata.

API failures stop the refresh before writes and deployment, retaining the last
published site. The saved snapshot allows builds without live API access. The
first snapshot was seeded from public repo metadata and authored commits.

`data/profile-activity.md` is generated from this same snapshot. The profile repo
reads this public file with its own workflow and own `GITHUB_TOKEN`, so no token
with cross-repository write permissions is needed. Merge the workbench PR before
running the profile updater. Activity history is also published at `/github.json`.

## Publish

After merging, set **Settings → Pages → Build and deployment → Source** to
**GitHub Actions** and run **Refresh and publish GitHub workbench** once. Subsequent
pushes and the daily schedule publish automatically. Pull requests build from the
saved snapshot and upload a downloadable `site-preview` artifact without deploying.
No additional secrets are needed. GitHub schedules can be delayed and may be
disabled after 60 days of repository inactivity; check the displayed update date
and re-enable the workflow if needed. Keep branch rules compatible with the bot's
history commit, or explicitly allow the updater.

The profile repository updates at 08:17 IST. Its manually written introduction and
selected-project list remain outside the generated markers.

## Legacy links

`data/redirects.json` maps all original Jekyll post paths to verified corresponding
paths in rohanverma.net's source. Static redirect pages retain a clickable fallback
and canonical link. Legacy post sources remain under `legacy/` for reference.
