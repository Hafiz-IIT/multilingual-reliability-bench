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

    def test_incomplete_parallel_case_raises(self):
        case = ParallelCase("x", {"en": "a", "bn": "ক"}, {"en": "a"})
        with self.assertRaises(ValueError):
            case.flatten()


if __name__ == "__main__":
    unittest.main()
