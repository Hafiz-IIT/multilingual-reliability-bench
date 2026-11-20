import unittest

from paired_benchmark import ParallelCase, evaluate_parallel


class PairedBenchmarkTests(unittest.TestCase):
    def test_parallel_disparity_is_measurable(self):
        result = evaluate_parallel([
            ParallelCase(
                "1",
                {"en": "yes", "bn": "হ্যাঁ"},
                {"en": "yes", "bn": "জানি না"},
            )
        ])
        self.assertEqual(result["accuracy_range"], 1.0)
        self.assertEqual(result["coverage_range"], 1.0)

    def test_duplicate_parallel_case_ids_rejected(self):
        rows = [
            ParallelCase("same", {"en": "yes"}, {"en": "yes"}),
            ParallelCase("same", {"en": "no"}, {"en": "no"}),
        ]
        with self.assertRaises(ValueError):
            evaluate_parallel(rows)

    def test_support_flag_mapping_type_is_validated(self):
        case = ParallelCase(
            "x", {"en": "yes"}, {"en": "yes"}, supported_by_language=[("en", True)]
        )
        with self.assertRaises(ValueError):
            case.flatten()

    def test_parallel_case_ids_are_trimmed_before_duplicate_check(self):
        rows = [
            ParallelCase(" same ", {"en": "yes"}, {"en": "yes"}),
            ParallelCase("same", {"en": "no"}, {"en": "no"}),
        ]
        with self.assertRaises(ValueError):
            evaluate_parallel(rows)

    def test_incomplete_parallel_case_raises(self):
        case = ParallelCase("x", {"en": "a", "bn": "ক"}, {"en": "a"})
        with self.assertRaises(ValueError):
            case.flatten()

    def test_empty_parallel_case_is_rejected(self):
        case = ParallelCase("empty", {}, {})
        with self.assertRaises(ValueError):
            case.flatten()

    def test_support_flags_are_propagated(self):
        result = evaluate_parallel([
            ParallelCase(
                "x", {"en": "yes", "bn": "হ্যাঁ"},
                {"en": "yes", "bn": "হ্যাঁ"},
                supported_by_language={"en": True, "bn": False},
            )
        ])
        self.assertEqual(result["metrics"]["bn"].unsupported, 1)
        self.assertEqual(result["metrics"]["bn"].supported_total, 0)


if __name__ == "__main__":
    unittest.main()
