from pathlib import Path
from shutil import copyfile
from tempfile import TemporaryDirectory
import unittest
from scripts.check_site import check


class SiteChecks(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        source = Path(__file__).resolve().parents[1]
        for name in ['index.html', 'privacy.html', 'terms.html']:
            copyfile(source / name, self.root / name)

    def mutate(self, old, new, page='privacy.html'):
        path = self.root / page
        content = path.read_text()
        self.assertIn(old, content)
        path.write_text(content.replace(old, new))

    def test_current_pages_pass(self):
        self.assertEqual(check(self.root), [])

    def test_broken_file_and_fragment_fail(self):
        self.mutate('href="index.html"', 'href="missing.html"')
        self.mutate('href="terms.html"', 'href="terms.html#missing"', page='index.html')
        errors = check(self.root)
        self.assertTrue(any('broken internal link' in error for error in errors))
        self.assertTrue(any('missing internal fragment' in error for error in errors))

    def test_malformed_markup_fails(self):
        self.mutate('</main>', '</section>')
        self.assertTrue(any('Mismatched closing tag' in error for error in check(self.root)))

    def test_missing_retention_disclosure_fails(self):
        self.mutate('7. Data Retention and Deletion', '7. Other information')
        self.assertTrue(any('missing disclosure section Data Retention' in error for error in check(self.root)))

    def test_future_review_date_fails(self):
        self.mutate('datetime="2026-11-18"', 'datetime="2999-01-01"')
        self.assertTrue(any('future review date' in error for error in check(self.root)))

    def test_executable_service_embed_fails(self):
        self.mutate('</main>', '<script src="https://example.com/app.js"></script></main>')
        self.assertTrue(any('executable services' in error for error in check(self.root)))


if __name__ == '__main__':
    unittest.main()
