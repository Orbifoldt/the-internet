from typing import TypeVar, Optional, List, Generic

K = TypeVar('K')
V = TypeVar('V')


class Trie(Generic[K, V]):
    def __init__(self, value: V = None):
        self.children: dict[K, Trie[K, V]] = {}
        self.value: V = value
        self.is_valid = value is not None

    def __contains__(self, key: K):
        if len(key) == 0:
            return self.is_valid
        head = key[0]
        if head not in self.children:
            return False
        return self.children[head].__contains__(key[1:])

    def __setitem__(self, key: K, value: V):
        if len(key) == 0:
            self.is_valid = True
            self.value = value
            return self
        head = key[0]
        if head not in self.children:
            self.children[head] = Trie(head)
        return self.children[head].__setitem__(key[1:], value)

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
            self.is_valid = False
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

    def __len__(self):
        return len(self.keys())  # i.e. number of (valid) values

    @property
    def depth(self) -> int:
        return max(len(key) for key in self.keys())

    @property
    def num_vertices(self) -> int:
        count = 0
        for head in self.children:
            count += 1 + self.children[head].num_vertices
        return count

    def keys(self) -> List[K]:
        keys = []
        for partial_key in self.children:
            child = self.children[partial_key]
            if child.is_valid:
                keys.append([partial_key])
            sub_keys = child.keys()
            for sub_key in sub_keys:
                keys.append([partial_key] + sub_key)
        return keys

    def __iter__(self):
        for key in self.keys():
            yield key
        return

    def __eq__(self, other):
        return other.isinstance(self.__class__) \
               and self.is_valid == other.is_valid \
               and self.value == other.value \
               and self.children == other.children

    def find_best_match(self, key: K) -> K:
        if len(key) == 0:
            return []
        head = key[0]
        if head in self.children:
            child = self.children[head]
            acc = [] if not child.is_valid else [head]
            found = child.find_best_match(key[1:])
            if len(found) > 0:
                return [head] + found
            else:
                return [head] if child.is_valid else []
        else:
            return []

    def to_str(self, n=0) -> str:
        out = ""
        for key in self.children:
            child = self.children[key]
            out += " " * n + f"{key}{f' : {child.value}' if child.is_valid else ''}\n" + child.to_str(n + 1)
        return out


trie = Trie('')
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
