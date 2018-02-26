import numpy as np
import tensorflow as tf
from DataSet import dataSet
import config
import embed
import random

# load data
graph_path = '../datasets/ido-merged/graph.txt'
text_path = '../datasets/ido-merged/data.txt'
f_emb_name = '../datasets/ido-merged/embed.txt'
f_gain_name = '../datasets/ido-merged/gain.txt'

data = dataSet(text_path, graph_path)

# start session

with tf.Graph().as_default():
    sess = tf.Session()
    with sess.as_default():
        model = cane.Model(data.num_vocab, data.num_nodes)
        opt = tf.train.AdamOptimizer(config.lr)
        train_op = opt.minimize(model.loss)
        sess.run(tf.global_variables_initializer())

        # training
        print 'start training.......'

        for epoch in range(config.num_epoch):
            loss_epoch = 0
            batches = data.generate_batches()
            h1 = 0
            num_batch = len(batches)
            for i in range(num_batch):
                batch = batches[i]

                node1, node2, node3 = zip(*batch)
                node1, node2, node3 = np.array(node1), np.array(node2), np.array(node3)
                text1, text2, text3 = data.text[node1], data.text[node2], data.text[node3]

                feed_dict = {
                    model.Text_a: text1,
                    model.Text_b: text2,
                    model.Text_neg: text3,
                    model.Node_a: node1,
                    model.Node_b: node2,
                    model.Node_neg: node3
                }

                # run the graph
                _, loss_batch = sess.run([train_op, model.loss], feed_dict=feed_dict)

                loss_epoch += loss_batch
            print 'epoch: ', epoch + 1, ' loss: ', loss_epoch

        print('start writing......')
        file_emb = open(f_emb_name, 'wb')
        file_gain = open(f_gain_name, 'wb')
        batches = data.generate_batches(mode='add')
        num_batch = len(batches)
        embed = [[] for _ in range(data.num_nodes)]
        #embed_pair = [[] for _ in range(data.num_nodes)]
        connection_gain = [[] for _ in range(data.num_nodes)]
        for i in range(num_batch):
            batch = batches[i]

            node1, node2, node3 = zip(*batch)
            node1, node2, node3 = np.array(node1), np.array(node2), np.array(node3)
            text1, text2, text3 = data.text[node1], data.text[node2], data.text[node3]

            feed_dict = {
                model.Text_a: text1,
                model.Text_b: text2,
                model.Text_neg: text3,
                model.Node_a: node1,
                model.Node_b: node2,
                model.Node_neg: node3
            }

            # run the graph
            convA, convB, TA, TB = sess.run([model.convA, model.convB, model.N_A, model.N_B], feed_dict=feed_dict)
            for i in range(config.batch_size):
                em = list(convA[i]) + list(TA[i])
                embed[node1[i]].append(em)
                em = list(convB[i]) + list(TB[i])
                embed[node2[i]].append(em)
                #embed_pair[node1[i]].append((node1[i], node2[i]))
                #embed_pair[node2[i]].append((node2[i], node1[i]))
                tmp_gain = np.dot(convA[i],convB[i].T) + np.dot(convA[i],TB[i].T) \
                           + np.dot(TA[i],convB[i].T) + np.dot(TA[i],TB[i].T)
                connection_gain[node1[i]].append([node1[i],node2[i], tmp_gain])
                connection_gain[node2[i]].append([node2[i],node1[i], tmp_gain])
        for i in range(data.num_nodes):
            if connection_gain[i]:
                for j in connection_gain[i]:
                    node1, node2, tmp_gain = j
                    file_gain.write(' '.join([str(node1),str(node2),str(tmp_gain)]) + '\n')
            if embed[i]:
                # print embed[i]
                # cdy: embed is a list, which size is node_num*x.
                # the element of it is also list, len(list) is the edges_num of each node.
                # so we can use all of them, not only average
                tmp = np.sum(embed[i], axis=0) / len(embed[i])
                file_emb.write(' '.join(map(str, tmp)) + '\n')
            else:
                file_emb.write('\n')
