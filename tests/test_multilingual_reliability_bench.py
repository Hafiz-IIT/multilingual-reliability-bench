import unittest

from multilingual_reliability_bench import Case, accuracy_gap, evaluate, normalize


class MultilingualBenchTests(unittest.TestCase):
    def test_unicode_normalization(self):
        self.assertEqual(normalize("  দিল্লি! "), "দিল্লি")

    def test_metrics(self):
        cases = [
            Case("1", "en", "yes", "yes"),
            Case("2", "en", "no", "unknown"),
            Case("1", "bn", "হ্যাঁ", "হ্যাঁ"),
            Case("2", "bn", "না", "ভুল", supported=False),
        ]
        metrics = evaluate(cases)
        self.assertEqual(metrics["en"].correct, 1)
        self.assertEqual(metrics["en"].abstained, 1)
        self.assertEqual(metrics["bn"].unsupported, 1)

    def test_gap(self):
        cases = [
            Case("1", "en", "a", "a"),
            Case("1", "bn", "ক", "খ"),
        ]
        gaps = accuracy_gap(evaluate(cases))
        self.assertEqual(gaps["bn"], 1.0)


if __name__ == "__main__":
    unittest.main()
