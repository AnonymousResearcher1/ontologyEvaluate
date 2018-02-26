import codecs

from preproccess import WeightedQuickUnion

f_name = "./ido-merged/graph.txt"
f_out_name = f_name.replace('graph', 'connectedComponent')

node_num = 409 + 1
wqu = WeightedQuickUnion.WeightedQuickUnion(node_num)
write2file = False
write2file_ascomponent = True

with codecs.open(f_name, 'r', 'utf-8') as f_in:
    with codecs.open(f_out_name, 'w', 'utf-8') as f_out:
        print("construct union from all deges")
        for line in f_in:
            a,b = line.strip().split()
            wqu.union(int(a), int(b))
        print("construction end")

        if write2file_ascomponent:
            for i in range(node_num):
                out_s = "%d\t%d\n" % (i,wqu.find(i))
                f_out.write(out_s)
                if i%100000 == 0:
                    print("write node id %d\n" % i)



        if write2file:
            for i in range(node_num):
                for j in range(i,node_num):
                    if wqu.connected(i,j):
                        out_s = "%d\t%d\t1\n" % (i,j)
                        f_out.write(out_s)

        print(wqu.count)


