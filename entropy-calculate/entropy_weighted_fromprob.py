import codecs
import numpy as np
from scipy import stats


f_prob = "./ido-merged/ido-merged_prob.txt"

#node_num = 11089 + 1  #doid
#node_num = 2533986 + 1  #antibio
node_num = 410 + 1  #antibio
prob = [0 for i in range(node_num)]
prob_sum = 0
prob_sum_fromgpu = 0

print("read prob")
with codecs.open(f_prob, 'r', 'utf-8') as f_in:
    line_no = 0
    i = 0
    for line in f_in:
        s = line.strip().split()[0]
        if (line_no == 0):
            prob_sum_fromgpu = float(s)
        else:
            prob[i] = float(s)
            prob_sum += prob[i]
            i += 1
        line_no += 1



prob1 = np.array(prob)
prob1 = prob1/float(prob_sum)
entropy = stats.entropy(prob1)
print(entropy)

prob2 = np.array(prob)
prob2 = prob2/float(prob_sum_fromgpu)
entropy = stats.entropy(prob2)
print(entropy)

