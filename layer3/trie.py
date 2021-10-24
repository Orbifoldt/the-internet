from __future__ import annotations

from typing import TypeVar, Optional, List, Generic

K = TypeVar('K')
V = TypeVar('V')


class Trie(Generic[K, V], object):
    def __init__(self, value: V = None):
        self.children: dict[K, Trie[K, V]] = {}
        self.value: V = value

    @property
    def is_valid(self):
        return self.value is not None

    def __contains__(self, key: K):
        if len(key) == 0:
            return self.is_valid
        head = key[0]
        if head not in self.children:
            return False
        return self.children[head].__contains__(key[1:])

    def __setitem__(self, key: K, value: V):
        if len(key) == 0:
            self.value = value
        else:
            head = key[0]
            if head not in self.children:
                self.children[head] = Trie()
            self.children[head].__setitem__(key[1:], value)

    def __getitem__(self, key: K) -> V:
        if len(key) == 0:
            if self.is_valid:
                return self.value
            else:
                raise KeyError(f"No value associated to provided key.")
        head = key[0]
        if head not in self.children:
            raise KeyError(f"Invalid key.")
        return self.children[head].__getitem__(key[1:])

    def __delitem__(self, key: K):
        if len(key) == 0:
            self.value = None
        else:
            head = key[0]
            if head in self.children:
                child = self.children[head]
                child.__delitem__(key[1:])
                if len(child.children) == 0:
                    del self.children[head]
            else:
                raise KeyError(f"Invalid key.")

    @staticmethod
    def find(trie: Trie, key: K, default: Optional[V] = None) -> Optional[V]:
        for char in key:
            if char in trie.children:
                trie = trie.children[char]
            else:
                return default
        return trie.value if not None else default

    def __len__(self):
        return len(self.keys())  # i.e. number of (valid) values

    @property
    def depth(self) -> int:
        return max(len(key) for key in self.keys())  # the root has depth 0

    @property
    def num_vertices(self) -> int:
        count = 1
        for head in self.children:
            count += self.children[head].num_vertices
        return count

    @property
    def num_edges(self) -> int:
        return self.num_vertices - 1

    # TODO: fix key finding algorithm to just need a single method with __keys__
    def keys(self) -> List[K]:
        keys = self.__keys__()
        if self.is_valid:
            keys.append([])
        return keys

    def __keys__(self) -> List[K]:
        keys = []
        for partial_key in self.children:
            child = self.children[partial_key]
            if child.is_valid:
                keys.append([partial_key])
            sub_keys = child.__keys__()
            for sub_key in sub_keys:
                keys.append([partial_key] + sub_key)
        return keys

    def __iter__(self):
        for key in self.keys():
            yield key
        return

    def __eq__(self, other):
        return isinstance(other, self.__class__) \
               and self.is_valid == other.is_valid \
               and self.value == other.value \
               and self.children == other.children

    # TODO: find algorithm to put this back into one method with __find_best_match__
    def find_best_match(self, key: K) -> K:
        match = self.__find_best_match__(key)
        if not self.is_valid and len(match) == 0:
            raise KeyError("No partial match found for key")
        else:
            return match

    def safe_find_best_match(self, key: K, default: Optional[K] = None) -> K:
        match = self.__find_best_match__(key)
        if not self.is_valid and len(match) == 0:
            return default
        else:
            return match

    def __find_best_match__(self, key: K) -> K:
        if len(key) == 0:
            return []
        head = key[0]
        if head in self.children:
            child = self.children[head]
            found = child.__find_best_match__(key[1:])
            if len(found) > 0:
                return [head] + found
            else:
                return [head] if child.is_valid else []
        else:
            return []

    def to_str(self, n=0) -> str:
        out = ""
        if n == 0:
            out += f"<ROOT>{f' : {self.value}' if self.is_valid else ''}\n"
        for key in self.children:
            child = self.children[key]
            out += "| " * (n + 1) + f"{key}{f' : {child.value}' if child.is_valid else ''}\n" + child.to_str(n + 1)
        return out


trie = Trie('root_val')
trie.__setitem__("az", "az")
# trie.__setitem__("a")
trie.__setitem__("ab", "ab")
trie.__setitem__("a123", "a123")
trie.__setitem__("abcde", "abcde")
trie.__setitem__("abxyz", "abxyz")
# trie.__setitem__("abc12")

print(trie.to_str())
print(trie.find_best_match("abc"))

del trie["ab"]
print("hello")
print(trie.to_str())
print(trie.keys())
print(len(trie))
print(trie.depth)
print(trie.num_vertices)
#
# print("done")
