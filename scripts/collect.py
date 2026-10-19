#!/usr/bin/env python3
"""Collect public GitHub data and render both the site data and profile fragment.

No dependencies. API failures abort before writing; --offline renders saved data.
"""
import argparse
from collections import defaultdict
from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import re
import time
from urllib.parse import urlencode, urlparse
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
IST = ZoneInfo('Asia/Kolkata')


def api(path):
    headers = {'Accept': 'application/vnd.github+json', 'User-Agent': 'rhnvrm-workbench',
               'X-GitHub-Api-Version': '2022-11-28'}
    if os.getenv('GITHUB_TOKEN'):
        headers['Authorization'] = 'Bearer ' + os.environ['GITHUB_TOKEN']
    for attempt in range(3):
        try:
            with urlopen(Request('https://api.github.com' + path, headers=headers), timeout=30) as response:
                return json.load(response)
        except HTTPError as error:
            if error.code == 404:
                raise
            if attempt == 2:
                raise
            time.sleep(2 ** attempt)
        except Exception:
            if attempt == 2:
                raise
            time.sleep(2 ** attempt)


def pages(path):
    output = []
    page = 1
    while True:
        batch = api(path + ('&' if '?' in path else '?') + f'per_page=100&page={page}')
        if not isinstance(batch, list):
            raise ValueError('Expected a GitHub collection')
        output.extend(batch)
        if len(batch) < 100:
            return output
        page += 1


def public_repo(repo):
    return not repo.get('private', True) and repo.get('visibility', 'public') == 'public'


def project(repo):
    homepage = repo.get('homepage') or ''
    if urlparse(homepage).scheme not in ('http', 'https'):
        homepage = ''
    return dict(name=repo['name'], full_name=repo['full_name'], url=repo['html_url'],
                description=repo.get('description') or 'Source code and project notes on GitHub.',
                language=repo.get('language') or 'Other', stars=repo.get('stargazers_count', 0),
                archived=repo['archived'], pushed_at=repo['pushed_at'], homepage=homepage,
                owner=repo['owner']['login'], topics=repo.get('topics', []))


def normalize_event(event, user):
    if event.get('actor', {}).get('login', '').lower() != user.lower() or not event.get('public'):
        return None
    payload = event.get('payload', {})
    repo = event['repo']['name']
    kind = event['type']
    item = None
    if kind == 'PullRequestEvent':
        pr = payload.get('pull_request', {})
        if payload.get('action') in ('opened', 'reopened', 'closed'):
            verb = 'Merged PR' if pr.get('merged') else {'opened':'Opened PR', 'reopened':'Reopened PR', 'closed':'Closed PR'}[payload['action']]
            item = (verb, pr.get('title'), pr.get('html_url'))
    elif kind == 'IssuesEvent' and payload.get('action') in ('opened', 'closed', 'reopened'):
        issue = payload.get('issue', {})
        item = (payload['action'].capitalize() + ' issue', issue.get('title'), issue.get('html_url'))
    elif kind == 'ReleaseEvent' and payload.get('action') == 'published':
        release = payload.get('release', {})
        item = ('Published release', release.get('name') or release.get('tag_name'), release.get('html_url'))
    elif kind == 'PullRequestReviewEvent' and payload.get('action') == 'created':
        pr = payload.get('pull_request', {})
        item = ('Reviewed PR', pr.get('title'), payload.get('review', {}).get('html_url'))
    # Push events are expanded into authored commits separately; skip stars and bot noise.
    if not item or not all(item):
        return None
    return dict(id='event:' + event['id'], repo=repo, kind=item[0], title=item[1], url=item[2], at=event['created_at'])


def collect(settings, previous):
    user = settings['user']
    repos = []
    for owner in settings['owners']:
        repos.extend(pages(f'/users/{owner}/repos?type=owner&sort=pushed'))
    repos = [r for r in repos if public_repo(r) and not r['fork']]
    confirmed_public = {r['full_name'] for r in repos}
    events = pages(f'/users/{user}/events/public')
    activity = {a['id']: a for a in previous.get('activity', [])}
    for event in events:
        item = normalize_event(event, user)
        if item:
            activity[item['id']] = item
    # Recent pushes discover contribution repositories outside the configured owners.
    candidates = {r['full_name']: r for r in repos if not r['archived']}
    for event in events:
        if event.get('public') and event.get('type') == 'PushEvent' and event.get('actor', {}).get('login', '').lower() == user.lower():
            name = event['repo']['name']
            if name not in candidates:
                repo = api('/repos/' + name)
                if public_repo(repo):
                    candidates[name] = repo
    since = (datetime.now(timezone.utc) - timedelta(days=14)).isoformat()
    for name, repo in candidates.items():
        if repo['pushed_at'] < since or name in settings['exclude']:
            continue
        for commit in pages('/repos/' + name + '/commits?' + urlencode({'author':user, 'since':since})):
            if (commit.get('author') or {}).get('login', '').lower() != user.lower():
                continue
            # Authored time keeps old commits pushed today from becoming today's work.
            at = commit['commit']['author']['date']
            item = dict(id='commit:' + name + ':' + commit['sha'], repo=name, kind='Commit',
                        title=commit['commit']['message'].splitlines()[0], url=commit['html_url'], at=at)
            activity[item['id']] = item
    # Revalidate historical external repositories too: a repo can become private
    # after an event was public. Never retain its name or activity in new output.
    for name in {a['repo'] for a in activity.values()} - confirmed_public:
        try:
            repo = api('/repos/' + name)
        except HTTPError as error:
            if error.code == 404:
                continue
            raise
        if public_repo(repo):
            confirmed_public.add(name)
    activity = {key:value for key,value in activity.items() if value['repo'] in confirmed_public}
    return dict(updated_at=datetime.now(timezone.utc).isoformat(timespec='seconds'),
                projects=[project(r) for r in repos if r['full_name'] not in settings['exclude']],
                activity=sorted(activity.values(), key=lambda a:a['at'], reverse=True))


def md(text):
    return re.sub(r'([\\`*\[\]<>_])', r'\\\1', ' '.join(text.split()))


def render(snapshot, settings):
    snapshot['projects'].sort(key=lambda r:r['pushed_at'], reverse=True)
    projects = {r['full_name']:r for r in snapshot['projects']}
    snapshot['featured'] = [projects[n] for n in settings['featured'] if n in projects]
    groups = defaultdict(list)
    for item in snapshot['activity']:
        if item['repo'] in settings['exclude']:
            continue
        day = datetime.fromisoformat(item['at'].replace('Z', '+00:00')).astimezone(IST).date().isoformat()
        groups[day].append(item)
    snapshot['days'] = [dict(date=day, items=groups[day]) for day in sorted(groups, reverse=True)]
    latest = {}
    for item in snapshot['activity']:
        if item['repo'] in projects and item['repo'] not in latest:
            latest[item['repo']] = dict(projects[item['repo']], latest=item)
    snapshot['working_on'] = list(latest.values())[:6]
    lines = []
    for day in snapshot['days'][:3]:
        for item in day['items'][:3]:
            lines.append(f"- {day['date']} · **{md(item['repo'])}** — {item['kind']}: [{md(item['title'])}]({item['url']})")
        if len(lines) >= 6:
            break
    fragment = '\n'.join(lines[:6]) or 'Recent public activity will appear after the next successful update.'
    fragment += '\n\n[Full work log and projects →](https://rhnvrm.github.io/)\n'
    daily_dir = ROOT / 'content/activity'
    daily_dir.mkdir(parents=True, exist_ok=True)
    # Delete generated pages for records removed by public-visibility checks.
    for old in daily_dir.glob('????-??-??.md'):
        if old.stem not in groups:
            old.unlink()
    for day in snapshot['days']:
        body = ['+++', f'title = "{day["date"]}"', f'date = {day["date"]}', 'template = "page.html"', '+++', '', 'Public GitHub activity · Asia/Kolkata', '']
        by_repo = defaultdict(list)
        for item in day['items']:
            by_repo[item['repo']].append(item)
        for repo, items in by_repo.items():
            body.extend(['## ' + repo, ''])
            body.extend(f"- {a['kind']}: [{md(a['title'])}]({a['url']})" for a in items)
            body.append('')
        (daily_dir / (day['date'] + '.md')).write_text('\n'.join(body) + '\n')
    # Write only after all API calls succeeded. Workflow commits this archive to Git.
    (ROOT / 'data/github.json').write_text(json.dumps(snapshot, indent=2, ensure_ascii=False) + '\n')
    (ROOT / 'data/profile-activity.md').write_text(fragment)
    (ROOT / 'static/github.json').write_text(json.dumps(snapshot, ensure_ascii=False) + '\n')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--offline', action='store_true')
    args = parser.parse_args()
    settings = json.loads((ROOT / 'data/settings.json').read_text())
    saved = ROOT / 'data/github.json'
    previous = json.loads(saved.read_text()) if saved.exists() else {}
    snapshot = previous if args.offline else collect(settings, previous)
    render(snapshot, settings)
    print(f"Rendered {len(snapshot['projects'])} projects and {len(snapshot['activity'])} activity records")


if __name__ == '__main__':
    main()
