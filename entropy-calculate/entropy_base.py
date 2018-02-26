import codecs
import numpy as np
from scipy import stats

f_name = "./ido-merged/connectedComponent.txt"
f_out_name = f_name.replace('connectedComponent', 'entropy')

node_num = 409 + 1
prob = [[] for i in range(node_num)]
compo_count = dict()  # how many node belongs to corresponding component
node_compo = dict()

with codecs.open(f_name, 'r', 'utf-8') as f_in:
    for line in f_in:
        node_id, compo_id = line.strip().split()
        node_id = int(node_id)
        compo_id = int(compo_id)
        node_compo[node_id] = compo_id
        if compo_id in compo_count:
            compo_count[compo_id] += 1
        else:
            compo_count[compo_id] = 1

compo_count_sum = 0
for i in range(node_num):
    prob[i] = compo_count[node_compo[i]]
    compo_count_sum += prob[i]

prob = np.array(prob)
prob = prob/float(compo_count_sum)
entropy = stats.entropy(prob)
print(entropy)

