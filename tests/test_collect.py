import importlib.util
from pathlib import Path
import unittest

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
