# Time:  O(nlogn)
# Space: O(n)

# Template:
# https://github.com/kamyu104/LeetCode-Solutions/blob/master/Python/longest-substring-of-one-repeating-character.py
class SegmentTree(object):
    def __init__(self, N,
                 build_fn=lambda _: None,
                 query_fn=lambda x, y: y if x is None else x if y is None else x+y,
                 update_fn=lambda x, y: y if x is None else x+y):
        self.tree = [None]*(1<<((N-1).bit_length()+1))
        self.base = len(self.tree)>>1
        self.lazy = [None]*self.base
        self.query_fn = query_fn
        self.update_fn = update_fn
        for i in xrange(self.base, self.base+N):
            self.tree[i] = build_fn(i-self.base)
        for i in reversed(xrange(1, self.base)):
            self.tree[i] = query_fn(self.tree[i<<1], self.tree[(i<<1)+1])
        self.count = [1]*len(self.tree)  # added
        for i in reversed(xrange(1, self.base)):  # added
            self.count[i] = self.count[i<<1] + self.count[(i<<1)+1]

    def __apply(self, x, val):
        self.tree[x] = self.update_fn(self.tree[x], val*self.count[x])  # modified
        if x < self.base:
            self.lazy[x] = self.update_fn(self.lazy[x], val)

    def update(self, L, R, h):  # Time: O(logN), Space: O(N)
        def pull(x):
            while x > 1:
                x >>= 1
                self.tree[x] = self.query_fn(self.tree[x<<1], self.tree[(x<<1)+1])
                if self.lazy[x] is not None:
                    self.tree[x] = self.update_fn(self.tree[x], self.lazy[x]*self.count[x])  # modified

        L += self.base
        R += self.base
        L0, R0 = L, R
        while L <= R:
            if L & 1:  # is right child
                self.__apply(L, h)
                L += 1
            if R & 1 == 0:  # is left child
                self.__apply(R, h)
                R -= 1
            L >>= 1
            R >>= 1
        pull(L0)
        pull(R0)
    
    def query(self, L, R):
        def push(x):
            for n in reversed(xrange(1, self.base.bit_length())):
                y = x>>n
                if self.lazy[y] is not None:
                    self.__apply(y<<1, self.lazy[y])
                    self.__apply((y<<1)+1, self.lazy[y])
                    self.lazy[y] = None
    
        if L > R:
            return None
        L += self.base
        R += self.base
        push(L)
        push(R)
        left = right = None
        while L <= R:
            if L & 1:
                left = self.query_fn(left, self.tree[L])
                L += 1
            if R & 1 == 0:
                right = self.query_fn(self.tree[R], right)
                R -= 1
            L >>= 1
            R >>= 1
        return self.query_fn(left, right)


# dp, segment tree, math
class Solution(object):
    def sumCounts(self, nums):
        """
        :type nums: List[int]
        :rtype: int
        """
        MOD = 10**9+7
        result = accu = 0
        lookup = {}
        st = SegmentTree(len(nums))
        for i in xrange(len(nums)):
            j = lookup[nums[i]] if nums[i] in lookup else -1
            # sum(count(k, i)^2 for k in range(i+1)) - sum(count(k, i-1)^2 for k in range(i))
            # = sum(2*count(k, i-1)+1 for k in range(j+1, i+1))
            # = (i-j) + sum(2*count(k, i-1) for k in range(j+1, i+1))
            accu = (accu+((i-j)+2*max(st.query(j+1, i), 0)))%MOD 
            result = (result+accu)%MOD
            st.update(j+1, i, 1)  # count(k, i) = count(k, i-1)+(1 if k >= j+1 else 0) for k in range(i+1)
            lookup[nums[i]] = i
        return result