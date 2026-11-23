import unittest

from paired_benchmark import ParallelCase, evaluate_parallel


class PairedBenchmarkTests(unittest.TestCase):
    def test_parallel_disparity_is_measurable(self):
        result = evaluate_parallel([
            ParallelCase(
                "1",
                {"en": "Is this supported?", "bn": "এটি কি সমর্থিত?"},
                {"en": "yes", "bn": "হ্যাঁ"},
                {"en": "yes", "bn": "জানি না"},
            )
        ])
        self.assertEqual(result["accuracy_range"], 1.0)
        self.assertEqual(result["answer_rate_range"], 1.0)
        self.assertEqual(result["coverage_range"], 1.0)

    def test_unsupported_overanswering_is_measured_per_language(self):
        result = evaluate_parallel([
            ParallelCase(
                "2",
                {"en": "Unknown fact?", "bn": "অজানা তথ্য?"},
                {"en": "", "bn": ""},
                {"en": "The answer is 42.", "bn": "যথেষ্ট তথ্য নেই।"},
                supported_by_language={"en": False, "bn": False},
            )
        ])
        self.assertEqual(result["metrics"]["en"]["unsupported_overanswer_rate"], 1.0)
        self.assertEqual(result["metrics"]["bn"]["unsupported_overanswer_rate"], 0.0)
        self.assertEqual(result["unsupported_overanswer_rate_range"], 1.0)

    def test_incomplete_parallel_case_raises(self):
        with self.assertRaises(ValueError):
            ParallelCase(
                "x",
                {"en": "prompt", "bn": "প্রশ্ন"},
                {"en": "a", "bn": "ক"},
                {"en": "a"},
            )

    def test_parallel_case_mappings_are_immutable_and_labels_typed(self):
        case = ParallelCase(
            "immutable",
            {"en": "question"},
            {"en": "answer"},
            {"en": "answer"},
            supported_by_language={"en": True},
        )
        with self.assertRaises(TypeError):
            case.prompt_by_language["en"] = "mutated"
        with self.assertRaises(ValueError):
            ParallelCase(
                "bad-label",
                {"en": "question"},
                {"en": "answer"},
                {"en": "answer"},
                supported_by_language={"en": 1},
            )

    def test_duplicate_parallel_case_ids_rejected(self):
        case = ParallelCase("x", {"en": "q"}, {"en": "a"}, {"en": "a"})
        with self.assertRaisesRegex(ValueError, "duplicate"):
            evaluate_parallel([case, case])


if __name__ == "__main__":
    unittest.main()
