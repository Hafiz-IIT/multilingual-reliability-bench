import unittest

from multilingual_reliability_bench import (
    EvalResult,
    PromptCase,
    evaluate,
    run_parallel,
    score_by_language,
)


class MultilingualBenchTests(unittest.TestCase):
    def test_exact_match_for_supported_answerable_case(self):
        case = PromptCase("en", "Q1", "What is 2+2?", "4")
        result = evaluate(case, "4")
        self.assertTrue(result.correct)
        self.assertFalse(result.abstained)
        self.assertFalse(result.over_answered_unsupported)

    def test_unsupported_case_requires_abstention(self):
        case = PromptCase("bn", "Q2", "অনুমান করো", "", supported=False)
        good = evaluate(case, "Insufficient information.")
        bad = evaluate(case, "The answer is 42.")
        self.assertTrue(good.correct)
        self.assertTrue(good.abstained)
        self.assertFalse(good.over_answered_unsupported)
        self.assertFalse(bad.correct)
        self.assertTrue(bad.over_answered_unsupported)

    def test_bengali_and_hindi_abstentions_are_detected(self):
        bn = PromptCase("bn", "Q-bn", "অজানা প্রশ্ন", "", supported=False)
        hi = PromptCase("hi-IN", "Q-hi", "अज्ञात प्रश्न", "", supported=False)
        self.assertTrue(evaluate(bn, "যথেষ্ট তথ্য নেই।").correct)
        self.assertTrue(evaluate(hi, "मुझे नहीं पता।").correct)

    def test_expected_refusal_requires_abstention(self):
        case = PromptCase("hi", "Q3", "unknown", "", supported=True, expected_refusal=True)
        self.assertTrue(evaluate(case, "I cannot determine that.").correct)
        self.assertFalse(evaluate(case, "It is 42.").correct)

    def test_unnecessary_abstention_is_separately_counted(self):
        case = PromptCase("en", "Q4", "What is 2+2?", "4")
        result = evaluate(case, "I don't know.")
        self.assertFalse(result.correct)
        self.assertTrue(result.unnecessary_abstention)

    def test_language_metrics_separate_supported_and_unsupported_cases(self):
        results = [
            evaluate(PromptCase("bn", "1", "q1", "উত্তর"), "উত্তর"),
            evaluate(PromptCase("bn", "2", "q2", "", supported=False), "42"),
            evaluate(PromptCase("bn", "3", "q3", "", supported=False), "Insufficient information."),
        ]
        summary = score_by_language(results)["bn"]
        self.assertEqual(summary["cases"], 3)
        self.assertEqual(summary["unsupported_cases"], 2)
        self.assertEqual(summary["unsupported_overanswer_count"], 1)
        self.assertEqual(summary["unsupported_overanswer_rate"], 0.5)
        self.assertEqual(summary["supported_answer_exact_match_accuracy"], 1.0)

    def test_parallel_results_are_sorted_and_preserve_support_labels(self):
        cases = [
            PromptCase("hi", "2", "second", "", supported=False),
            PromptCase("bn", "1", "first", "ঠিক"),
        ]
        outputs = {"second": "I cannot determine that.", "first": "ঠিক"}
        results = run_parallel(cases, lambda prompt: outputs[prompt], max_workers=2)
        self.assertEqual([(r.language, r.question_id) for r in results], [("bn", "1"), ("hi", "2")])
        self.assertFalse(results[0].over_answered_unsupported)
        self.assertTrue(results[1].supported is False)

    def test_duplicate_case_keys_rejected(self):
        cases = [
            PromptCase("bn", "1", "first", "x"),
            PromptCase("bn", "1", "second", "y"),
        ]
        with self.assertRaisesRegex(ValueError, "duplicate"):
            run_parallel(cases, lambda prompt: prompt)

    def test_invalid_inputs_rejected(self):
        with self.assertRaisesRegex(ValueError, "max_workers"):
            run_parallel([], lambda prompt: prompt, max_workers=0)
        with self.assertRaisesRegex(ValueError, "supported"):
            PromptCase("en", "1", "q", "a", supported=1)
        with self.assertRaisesRegex(ValueError, "expected answer"):
            PromptCase("en", "2", "q", "")
        with self.assertRaisesRegex(ValueError, "response"):
            evaluate(PromptCase("en", "3", "q", "a"), "")


if __name__ == "__main__":
    unittest.main()
