import importlib.util
from pathlib import Path
import unittest
import tempfile
import json
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('collect', Path(__file__).parents[1] / 'scripts/collect.py')
c = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c)

class CollectionTests(unittest.TestCase):
    def event(self, **changes):
        data = dict(id='1', public=True, actor={'login':'rhnvrm'}, repo={'name':'oddship/test'},
                    created_at='2026-10-18T22:00:00Z', type='IssuesEvent',
                    payload={'action':'opened','issue':{'title':'Fix <escaping>', 'html_url':'https://github.com/oddship/test/issues/1'}})
        return dict(data, **changes)

    def test_private_and_other_authors_excluded(self):
        self.assertIsNone(c.normalize_event(self.event(public=False), 'rhnvrm'))
        self.assertIsNone(c.normalize_event(self.event(actor={'login':'other'}), 'rhnvrm'))
        self.assertFalse(c.public_repo({'private':True}))
        self.assertFalse(c.public_repo({'private':False}))
        self.assertFalse(c.public_repo({'visibility':'public'}))

    def test_private_metadata_cannot_reach_any_rendered_output(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / 'data').mkdir()
            (root / 'static').mkdir()
            snapshot = dict(updated_at='2026-10-19T00:00:00Z', public_repositories=[],
                            projects=[dict(private=True, visibility='private', full_name='example/secret-project')],
                            activity=[dict(id='1',repo='example/secret-project',at='2026-10-19T00:00:00Z',kind='Commit',title='confidential-title',url='https://example.invalid')])
            with patch.object(c, 'ROOT', root):
                c.render(snapshot, {'featured':[], 'exclude':[]})
            for path in root.rglob('*'):
                if path.is_file():
                    self.assertNotIn('secret-project', path.read_text())
                    self.assertNotIn('confidential-title', path.read_text())
            self.assertEqual(json.loads((root / 'data/github.json').read_text())['activity'], [])

    def test_merged_pr_is_not_closed_pr(self):
        event = self.event(type='PullRequestEvent', payload={'action':'closed','pull_request':{'merged':True,'title':'Ship it','html_url':'https://github.com/a/b/pull/1'}})
        self.assertEqual(c.normalize_event(event, 'rhnvrm')['kind'], 'Merged PR')

    def test_pushes_and_stars_do_not_become_authored_work(self):
        for kind in ('PushEvent','WatchEvent'):
            self.assertIsNone(c.normalize_event(self.event(type=kind), 'rhnvrm'))

    def test_local_day_and_escaping(self):
        at = c.datetime.fromisoformat('2026-10-18T22:00:00+00:00')
        self.assertEqual(at.astimezone(c.IST).date().isoformat(), '2026-10-19')
        self.assertEqual(c.md('[bad]\ntext'), r'\[bad\] text')

if __name__ == '__main__':
    unittest.main()
