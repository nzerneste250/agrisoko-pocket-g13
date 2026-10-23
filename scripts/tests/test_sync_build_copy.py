import importlib.util
import os
from pathlib import Path
import tempfile
import time
import unittest

spec = importlib.util.spec_from_file_location('sync_build_copy', Path(__file__).resolve().parents[1] / 'sync_build_copy.py')
sync = importlib.util.module_from_spec(spec); spec.loader.exec_module(sync)

class SyncSafetyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.source = Path(self.temp.name)/'main'; self.dest = Path(self.temp.name)/'build'
        for root in (self.source,self.dest): (root/'mobile/src').mkdir(parents=True)
    def test_plan_excludes_dependencies_caches_and_secrets(self):
        for name in ['App.tsx','node_modules/a.ts','.env','dist/bundle.js','src/network.ts']:
            p=self.source/'mobile'/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('new')
        plan=sync.make_plan(self.source,self.dest)
        self.assertEqual({r['path'] for r in plan['files']},{'mobile/App.tsx','mobile/src/network.ts'})
        self.assertFalse((self.dest/'mobile/App.tsx').exists())
    def test_apply_backs_up_and_copies_from_main(self):
        src=self.source/'mobile/App.tsx';dst=self.dest/'mobile/App.tsx';dst.write_text('old');src.write_text('new')
        self.assertEqual(sync.apply_plan(sync.make_plan(self.source,self.dest),self.source,self.dest),1)
        self.assertEqual(dst.read_text(),'new')
        self.assertEqual(next((self.dest/'.g13-sync-backups').rglob('App.tsx')).read_text(),'old')
    def test_changed_destination_after_review_is_not_overwritten(self):
        src=self.source/'mobile/App.tsx';dst=self.dest/'mobile/App.tsx';src.write_text('new');dst.write_text('old')
        plan=sync.make_plan(self.source,self.dest);dst.write_text('teammate changed this')
        with self.assertRaisesRegex(ValueError,'changed since plan'):sync.apply_plan(plan,self.source,self.dest)
        self.assertEqual(dst.read_text(),'teammate changed this')
    def test_newer_destination_and_path_escape_are_refused(self):
        src=self.source/'mobile/App.tsx';dst=self.dest/'mobile/App.tsx';src.write_text('new');dst.write_text('newer build-copy work')
        future=time.time()+10;os.utime(dst,(future,future))
        with self.assertRaisesRegex(ValueError,'Newer differing'):sync.apply_plan(sync.make_plan(self.source,self.dest),self.source,self.dest)
        with self.assertRaises(ValueError):sync.contained(self.dest,'../escape.ts')
        self.assertEqual(dst.read_text(),'newer build-copy work')
if __name__=='__main__':unittest.main()
