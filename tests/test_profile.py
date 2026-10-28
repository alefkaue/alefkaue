import importlib.util
from pathlib import Path
import unittest
import tempfile
import shutil
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / (name + '.py'))
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module); return module
fetch = load('fetch_languages')
render = load('render_session')

class ProfileTests(unittest.TestCase):
    def test_selected_rows_do_not_change_totals(self):
        total = {'Python':1000,'Java':150,'C#':200,'HTML':100,'CSS':50}
        data = fetch.build(total, 5)
        self.assertEqual(data['total_bytes'], 1500)
        self.assertEqual(sum(x['bytes'] for x in data['languages']), 1500)
        self.assertEqual(data['all_languages'], total)
        self.assertEqual(next(x['bytes'] for x in data['languages'] if x['name']=='Other'), 150)

    def test_absent_language_is_not_invented(self):
        self.assertNotIn('Java', [r['name'] for r in fetch.build({'Python':10},1)['languages']])

    def test_manual_profile_note_survives_regeneration(self):
        self.assertIn('3º lugar geral', render.readme())
        self.assertIn('dezembro de 2027', render.readme())

    def test_daily_render_keeps_the_edited_profile(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            shutil.copytree(ROOT / 'data', root / 'data')
            manual = (root / 'data/profile.md').read_text(encoding='utf-8') + '\nEditorial update to preserve.\n'
            (root / 'data/profile.md').write_text(manual, encoding='utf-8')
            (root / 'README.md').write_text('Previous layout', encoding='utf-8')
            with patch.object(render, 'ROOT', root), patch.object(render, 'OUT', root / 'assets/session'):
                render.main()
            self.assertEqual((root / 'README.md').read_text(encoding='utf-8'), manual)
            self.assertEqual((root / 'data/profile-note.md').read_bytes(), (ROOT / 'data/profile-note.md').read_bytes())

    def test_simoc_and_ctf_stay_featured(self):
        names = [p[1] for p in render.PROJECTS]
        self.assertIn('simoc-integrador', names)
        self.assertIn('cyber-ctf-writeups', names)
        self.assertEqual(len(names), len(set(names)))

if __name__ == '__main__': unittest.main()
