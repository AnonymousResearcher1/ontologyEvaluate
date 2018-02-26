class WeightedQuickUnion(object):
    id=[]
    count=0
    sz=[]

    def __init__(self,n):
        self.count = n
        i=0
        while i<n:
            self.id.append(i)
            self.sz.append(1) # inital size of each tree is 1
            i+=1

    def connected(self,p,q):
        if self.find(p) == self.find(q):
            return True
        else:
            return False

    def find(self,p):
        while (p != self.id[p]):
            p = self.id[p]
        return p

    def union(self,p,q):
        idp = self.find(p)
        idq = self.find(q)
        if not self.connected(p,q):
            if (self.sz[idp] < self.sz[idq]):
                self.id[idp] = idq

                self.sz[idq] += self.sz[idp]
            else:
                self.id[idq] = idp
                self.sz[idp] += self.sz[idq]

            self.count -=1

