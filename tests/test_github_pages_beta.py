"""Public beta preparation must not remove noindex or conceal uncertainty."""
import importlib.util
import tempfile
import unittest
from pathlib import Path

SCRIPT=Path(__file__).resolve().parents[1]/"scripts/prepare_github_pages_beta.py"
spec=importlib.util.spec_from_file_location("beta_prep",SCRIPT)
prep=importlib.util.module_from_spec(spec)
spec.loader.exec_module(prep)

class BetaPrepTest(unittest.TestCase):
    def test_keeps_noindex_and_marks_every_page(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            for number in range(9000):
                # The real site has more than 13,000 pages. Exercise the
                # completeness threshold without allocating a large dataset.
                p=root/f"{number}.html"
                p.write_text('<html><head><meta name="robots" content="noindex,nofollow"></head>'
                             '<body><main>'+prep.FALSE_PRIVATE+'</main></body></html>',encoding="utf-8")
            out=prep.prepare(root)
            self.assertEqual(out["html_pages"],9000)
            self.assertEqual(out["noindex_retained"],9000)
            sample=(root/"0.html").read_text(encoding="utf-8")
            self.assertIn(prep.BETA_LABEL,sample)
            self.assertIn("指定権者",sample)
            self.assertNotIn(prep.FALSE_PRIVATE,sample)
            self.assertIn('name="robots" content="noindex',sample)

    def test_rejects_non_noindex_pages(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            for number in range(9000):
                (root/f"{number}.html").write_text('<html><body>text</body></html>',encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError,"noindex"):
                prep.prepare(root)

if __name__=="__main__":
    unittest.main()
