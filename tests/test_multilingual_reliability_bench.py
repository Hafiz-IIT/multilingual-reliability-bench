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
        self.assertEqual(metrics["bn"].supported_total, 1)
        self.assertEqual(metrics["bn"].accuracy, 1.0)
        self.assertEqual(metrics["bn"].unsupported_non_abstain, 1)

    def test_unsupported_correct_answer_does_not_inflate_supported_accuracy(self):
        cases = [
            Case("1", "bn", "হ্যাঁ", "ভুল", supported=True),
            Case("2", "bn", "না", "না", supported=False),
        ]
        metrics = evaluate(cases)["bn"]
        self.assertEqual(metrics.total, 2)
        self.assertEqual(metrics.supported_total, 1)
        self.assertEqual(metrics.correct, 0)
        self.assertEqual(metrics.accuracy, 0.0)
        self.assertEqual(metrics.unsupported_non_abstain, 1)

    def test_unsupported_only_accuracy_is_undefined(self):
        metric = evaluate([
            Case("1", "xx", "answer", "answer", supported=False)
        ])["xx"]
        self.assertIsNone(metric.accuracy)
        self.assertIsNone(metric.coverage)
        self.assertEqual(metric.unsupported_non_abstain, 1)

    def test_empty_gold_answer_is_rejected(self):
        for expected in ("", "   ", "---"):
            with self.subTest(expected=expected):
                with self.assertRaises(ValueError):
                    Case("1", "en", expected, expected)

    def test_case_id_and_language_are_canonicalized_before_duplicate_check(self):
        cases = [
            Case(" same ", "EN", "yes", "yes"),
            Case("same", "en", "no", "no"),
        ]
        with self.assertRaises(ValueError):
            evaluate(cases)

    def test_duplicate_case_language_pairs_rejected(self):
        cases = [Case("same", "en", "yes", "yes"), Case("same", "en", "no", "no")]
        with self.assertRaises(ValueError):
            evaluate(cases)

    def test_unsupported_only_language_excluded_from_gap(self):
        cases = [Case("1", "en", "yes", "yes"), Case("2", "xx", "yes", "no", supported=False)]
        self.assertEqual(accuracy_gap(evaluate(cases)), {})

    def test_gap(self):
        cases = [
            Case("1", "en", "a", "a"),
            Case("1", "bn", "ক", "খ"),
        ]
        gaps = accuracy_gap(evaluate(cases))
        self.assertEqual(gaps["bn"], 1.0)


if __name__ == "__main__":
    unittest.main()
