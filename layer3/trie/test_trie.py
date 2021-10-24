from unittest import TestCase

from layer3.trie.trie import Trie


class TestTrie(TestCase):

    def setUp(self) -> None:
        self.trie = Trie()
        self.trie["a"] = "val1"
        self.trie["abc"] = "val2"
        self.trie["ab12"] = "val3"

    def test_keys_are_inserted_properly(self):
        trie = Trie()
        trie["a"] = "val1"
        self.assertEqual(1, len(trie.children))
        self.assertTrue("a" in trie.children)

        trie["abc"] = "val2"
        self.assertTrue("a" in trie.children)
        self.assertTrue("b" in trie.children['a'].children)
        self.assertTrue("c" in trie.children['a'].children['b'].children)

        trie["ab12"] = "val3"
        self.assertTrue("a" in trie.children)
        self.assertTrue("b" in trie.children['a'].children)
        self.assertTrue("c" in trie.children['a'].children['b'].children)
        self.assertTrue("1" in trie.children['a'].children['b'].children)
        self.assertTrue("2" in trie.children['a'].children['b'].children["1"].children)

    def test_contains_operator_recognizes_keys_of_the_trie(self):
        self.assertTrue("a" in self.trie)
        self.assertTrue("ab12" in self.trie)
        self.assertTrue("abc" in self.trie)

    def test_contains_operator_should_return_false_for_unrelated_keys(self):
        self.assertFalse("b" in self.trie)
        self.assertFalse("xyz" in self.trie)

    def test_contains_operator_should_return_false_for_partial_key_matches(self):
        self.assertFalse('' in self.trie)
        self.assertFalse("ab" in self.trie)
        self.assertFalse("ab1" in self.trie)
        self.assertFalse("ab123" in self.trie)

    def test_values_are_inserted_properly(self):
        trie = Trie()
        trie["a"] = "val1"
        self.assertTrue(trie.children["a"].is_valid)
        self.assertEqual("val1", trie.children["a"].value)
        self.assertEqual("val1", trie['a'])

        trie["abc"] = "val2"
        trie["ab12"] = "val3"

        self.assertTrue(trie.children['a'].children["b"].children["c"].is_valid)
        self.assertEqual("val2", trie.children['a'].children["b"].children["c"].value)
        self.assertEqual("val2", trie['abc'])

        self.assertTrue(trie.children['a'].children["b"].children["1"].children["2"].is_valid)
        self.assertEqual("val3", trie.children['a'].children["b"].children["1"].children["2"].value)
        self.assertEqual("val3", trie['ab12'])

        # First inserted value did not get mutated
        self.assertTrue(trie.children["a"].is_valid)
        self.assertEqual("val1", trie.children["a"].value)
        self.assertEqual("val1", trie['a'])

    def test_overwriting_value_of_an_existing_key_should_replace_old_value(self):
        self.trie["a"] = "val666"

        self.assertTrue(self.trie.children["a"].is_valid)
        self.assertEqual("val666", self.trie.children["a"].value)
        self.assertEqual("val666", self.trie['a'])

    def test_partial_keys_without_valid_values_are_none_and_is_valid_is_false(self):
        self.assertFalse(self.trie.children['a'].children["b"].is_valid)
        self.assertIsNone(self.trie.children['a'].children["b"].value)
        self.assertFalse(self.trie.children['a'].children["b"].children["1"].is_valid)
        self.assertIsNone(self.trie.children['a'].children["b"].children["1"].value)

    def test_partial_keys_will_raise_key_error(self):
        with self.assertRaises(KeyError):
            _ = self.trie[""]
        with self.assertRaises(KeyError):
            _ = self.trie["ab"]
        with self.assertRaises(KeyError):
            _ = self.trie["ab1"]

    def test_long_keys_with_partial_match_will_raise_key_error(self):
        with self.assertRaises(KeyError):
            _ = self.trie["abcz"]
        with self.assertRaises(KeyError):
            _ = self.trie["ab12z"]
        with self.assertRaises(KeyError):
            _ = self.trie["abz"]

    def test_unrelated_keys_will_raise_key_error(self):
        with self.assertRaises(KeyError):
            _ = self.trie["x"]
        with self.assertRaises(KeyError):
            _ = self.trie["xabc"]
        with self.assertRaises(KeyError):
            _ = self.trie["zzzz"]

    def test_length_and_depth_and_num_vertices_and_num_edges_are_calculated_correctly(self):
        self.assertEqual(3, len(self.trie))
        self.assertEqual(4, self.trie.depth)
        self.assertEqual(6, self.trie.num_vertices)  # this should include the root
        self.assertEqual(5, self.trie.num_edges)

    def test_del_operator_on_leaf_of_the_tree_should_delete_an_entry_from_the_trie(self):
        del self.trie["abc"]

        self.assertFalse("c" in self.trie.children['a'].children["b"].children)
        self.assertFalse("abc" in self.trie)
        with self.assertRaises(KeyError):
            _ = self.trie["abc"]

        self.assertEqual(2, len(self.trie))
        self.assertEqual(4, self.trie.depth)
        self.assertEqual(5, self.trie.num_vertices)
        self.assertEqual(4, self.trie.num_edges)

    def test_del_operator_on_leaf_of_the_tree_should_not_mutate_other_entries(self):
        del self.trie["abc"]

        self.assertEqual("val1", self.trie['a'])
        self.assertTrue(self.trie.children["a"].is_valid)
        self.assertEqual("val1", self.trie.children["a"].value)

        self.assertEqual("val3", self.trie['ab12'])
        self.assertTrue(self.trie.children['a'].children["b"].children["1"].children["2"].is_valid)
        self.assertEqual("val3", self.trie.children['a'].children["b"].children["1"].children["2"].value)

    def test_del_operator_on_internal_vertex_with_descendants_should_delete_an_entry_from_the_trie(self):
        del self.trie["a"]

        self.assertFalse("a" in self.trie)
        with self.assertRaises(KeyError):
            _ = self.trie["a"]
        self.assertFalse(self.trie.children["a"].is_valid)
        self.assertIsNone(self.trie.children["a"].value)

        self.assertEqual(2, len(self.trie))
        self.assertEqual(4, self.trie.depth)
        self.assertEqual(6, self.trie.num_vertices)
        self.assertEqual(5, self.trie.num_edges)

    def test_del_operator_on_internal_vertex_with_descendants_should_not_mutate_rest_of_trie(self):
        del self.trie["a"]

        self.assertTrue(self.trie.children['a'].children["b"].children["c"].is_valid)
        self.assertEqual("val2", self.trie.children['a'].children["b"].children["c"].value)
        self.assertEqual("val2", self.trie['abc'])

        self.assertEqual("val3", self.trie['ab12'])
        self.assertTrue(self.trie.children['a'].children["b"].children["1"].children["2"].is_valid)
        self.assertEqual("val3", self.trie.children['a'].children["b"].children["1"].children["2"].value)

    def test_inserting_new_entry_after_deleting_should_replace_old_value(self):
        del self.trie["a"]
        self.trie["a"] = "val666"

        self.assertTrue(self.trie.children["a"].is_valid)
        self.assertEqual("val666", self.trie.children["a"].value)
        self.assertEqual("val666", self.trie['a'])

    def test_keys_method_returns_all_valid_keys(self):
        keys = self.trie.keys()
        self.assertTrue(["a"] in keys)
        self.assertTrue(["a", "b", "c"] in keys)
        self.assertTrue(["a", "b", "1", "2"] in keys)
        self.assertEqual(3, len(keys))

    def test_keys_method_is_updated_properly_after_deleting_a_key(self):
        del self.trie["a"]

        keys = self.trie.keys()
        self.assertFalse(["a"] in keys)
        self.assertTrue(["a", "b", "c"] in keys)
        self.assertTrue(["a", "b", "1", "2"] in keys)
        self.assertEqual(2, len(keys))

    def test_iterator_correctly_iterates_over_all_valid_keys(self):
        keys = []
        for key in self.trie:
            keys.append(key)

        self.assertTrue(["a"] in keys)
        self.assertTrue(["a", "b", "c"] in keys)
        self.assertTrue(["a", "b", "1", "2"] in keys)
        self.assertEqual(3, len(keys))

    def test_equality_operator_returns_true_for_equal_tries(self):
        other = Trie()
        other["a"] = "val1"
        other["abc"] = "val2"
        other["ab12"] = "val3"

        self.assertTrue(self.trie == other)
        self.assertTrue(other == self.trie)

    def test_equality_operator_returns_false_for_tries_with_different_amount_of_keys(self):
        other = Trie()
        other["a"] = "val1"
        other["abc"] = "val2"
        self.assertFalse(self.trie == other)
        self.assertFalse(other == self.trie)

    def test_equality_operator_returns_false_for_same_tries_with_different_values(self):
        other = Trie()
        other["a"] = "val1"
        other["abc"] = "val666"
        other["ab12"] = "val3"
        self.assertFalse(self.trie == other)
        self.assertFalse(other == self.trie)

    def test_equality_operator_returns_false_after_deleting_a_key(self):
        other = Trie()
        other["a"] = "val1"
        other["abc"] = "val2"
        other["ab12"] = "val3"
        del other["ab12"]

        self.assertFalse(self.trie == other)
        self.assertFalse(other == self.trie)

    def test_trie_with_value_at_the_root(self):
        trie = Trie("root_value")
        trie["a"] = "val1"
        trie["abc"] = "val2"

        self.assertEqual("root_value", trie.value)
        self.assertTrue(trie.is_valid)
        self.assertTrue('' in trie)
        self.assertTrue([] in trie)
        self.assertEqual("root_value", trie[''])
        self.assertEqual("root_value", trie[[]])

    def test_trie_with_value_at_the_root_has_length_and_depth_and_num_vertices_and_num_edges_calculated_correctly(self):
        trie = Trie("root_value")
        trie["a"] = "val1"
        trie["abc"] = "val2"

        self.assertEqual(3, len(trie))
        self.assertEqual(3, trie.depth)
        self.assertEqual(4, trie.num_vertices)
        self.assertEqual(3, trie.num_edges)

    def test_trie_with_root_value_should_not_equal_same_trie_without_root_value(self):
        other = Trie("root_value")
        other["a"] = "val1"
        other["abc"] = "val2"
        other["ab12"] = "val3"
        self.assertFalse(self.trie == other)
        self.assertFalse(other == self.trie)

    def test_tries_with_different_root_values_should_not_be_equal(self):
        self.trie[''] = "some_root_value"
        other = Trie("other_root_value")
        other["a"] = "val1"
        other["abc"] = "val2"
        other["ab12"] = "val3"
        self.assertFalse(self.trie == other)
        self.assertFalse(other == self.trie)

    def test_find_best_match_should_return_key_itself_if_key_is_part_of_the_trie(self):
        self.trie[''] = "root_value"

        self.assertEqual([], self.trie.find_best_match(''))
        self.assertEqual(["a"], self.trie.find_best_match("a"))
        self.assertEqual(["a", "b", "c"], self.trie.find_best_match("abc"))
        self.assertEqual(["a", "b", "1", "2"], self.trie.find_best_match("ab12"))

    def test_find_best_match_should_return_best_match_for_partial_match(self):
        self.assertEqual(["a"], self.trie.find_best_match("ab"))
        self.assertEqual(["a"], self.trie.find_best_match("az"))
        self.assertEqual(["a", "b", "c"], self.trie.find_best_match("abcz"))
        self.assertEqual(["a", "b", "c"], self.trie.find_best_match("abczyxwvuts"))
        self.assertEqual(["a", "b", "1", "2"], self.trie.find_best_match("ab12z"))

    def test_find_best_match_in_trie_with_root_value_should_return_root_key_if_no_match_is_possible(self):
        self.trie[''] = "root_value"

        self.assertEqual([], self.trie.find_best_match('x'))
        self.assertEqual([], self.trie.find_best_match('zzzzzzz'))

    def test_find_best_match_in_trie_without_root_value_should_raise_key_error(self):
        with self.assertRaises(KeyError):
            self.trie.find_best_match('x')
        with self.assertRaises(KeyError):
            self.trie.find_best_match('zzzzzzz')

    def test_safe_find_best_match_in_trie_without_root_value_should_return_default_value(self):
        self.assertIsNone(self.trie.safe_find_best_match("x"))
        self.assertIsNone(self.trie.safe_find_best_match("zzzzzz"))

        default_val = "z"
        self.assertEqual(default_val, self.trie.safe_find_best_match("x", default_val))
        self.assertEqual(default_val, self.trie.safe_find_best_match("zzzzzz", default_val))

        # Keys that (partially) match are still returned correctly
        self.assertEqual(["a"], self.trie.safe_find_best_match("a"))
        self.assertEqual(["a"], self.trie.safe_find_best_match("ab"))
