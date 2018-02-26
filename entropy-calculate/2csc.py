import scipy.sparse
import codecs
import numpy

node_count = 409+ 1
f_name = './ido-merged/weight.txt'
#f_name_out = './antibio/graph.csc'

#graph = numpy.zeros([node_count,node_count])
#graph = [[[] for i in range(node_count)] for i in range(node_count)]
graph = dict()
colum_nonzero_idx = [[]for i in range(node_count)]
with codecs.open(f_name) as f:
    line_count = 0
    for line in f:
        node1, node2, gain = line.strip().split()
        node1 = int(node1)
        node2 = int(node2)
        if (node1, node2) not in graph and (node2, node1) not in graph:
            colum_nonzero_idx[node2].extend([node1])
            graph[(node1, node2)] = gain
        #graph[int(node1)][int(node2)] = gain
        line_count += 1
print(line_count)

f_idx = ("./ido-merged/graph_idx.csc")
f_offset = ("./ido-merged/graph_offset.csc")
f_weight = ("./ido-merged/graph_weight.csc")

offset = 0
with codecs.open(f_idx, 'w', 'utf-8') as f1:
    with codecs.open(f_offset, 'w', 'utf-8') as f2:
        with codecs.open(f_weight, 'w', 'utf-8') as f3:
            # convert graph to csc sparse martrix
            for i in range(node_count):
                colum_nonzero_idx[i].sort()
                f2.write(str(offset) + '\n')
                colum_element_count = 0
                for node1 in colum_nonzero_idx[i]:
                    f3.write(graph[(node1,i)] + '\n')
                    colum_element_count += 1
                    f1.write(str(node1) + '\n')
                offset += colum_element_count
            f2.write(str(offset) + '\n')



#spares_graph = scipy.sparse.csc_matrix(graph)
#with codecs.open(f_name_out,'w','utf-8') as f:
#    f.write(' '.join(map(str,spares_graph.indices.tolist())))
#    f.write('\n')
#    f.write(' '.join(map(str,spares_graph.indptr.tolist())))
#    f.write('\n')
#    f.write(' '.join(map(str,spares_graph.data.tolist())))
