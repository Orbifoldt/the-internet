from unittest import TestCase

from layer3.trie import Trie


class TestTrie(TestCase):
    def test_set_contains_and_get(self):
        trie = Trie('')
        trie["a"] = "val1"
        self.assertEqual(1, len(trie.children))
        self.assertTrue("a" in trie.children)
        self.assertTrue("a" in trie)
        self.assertFalse("b" in trie)
        self.assertTrue(trie.children['a'].is_valid)
        self.assertEqual("val1", trie.children['a'].value)
        self.assertEqual("val1", trie['a'])

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

        self.assertTrue("ab12" in trie)
        self.assertTrue("abc" in trie)
        self.assertEqual("val2", trie['abc'])
        self.assertEqual("val3", trie['ab12'])

        self.assertFalse("ab" in trie)
        self.assertFalse("xyz" in trie)

    def test_find_best_match(self):
        self.fail()

    def test_remove(self):
        self.fail()
