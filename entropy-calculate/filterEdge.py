import codecs

graph = dict()
with codecs.open('./ido-merged/gain.txt') as f_in:
    with codecs.open('./ido-merged/weight.txt', 'w','utf-8') as f_out:
        for line in f_in:
            node1, node2, gain = line.strip().split()
            if (node1,node2) not in graph and (node2,node1) not in graph:
                graph[(node1,node2)] = gain

        for pair in graph.keys():
            f_out.write(' '.join(list(pair)) + ' ' + graph[pair] + '\n')
