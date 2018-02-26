import numpy as np
import tensorflow as tf
from DataSet import dataSet
import config
import embed
import random

# load data
graph_path = '../datasets/antibio/graph.txt'
text_path = '../datasets/antibio/nodes_desc_ordered.txt'
f_out_name = '../datasets/antibio/embed.txt'

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
        print('start training.......')

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
            print('epoch: ', epoch + 1, ' loss: ', loss_epoch)

        print('start writing ......')
        file = open(f_out_name, 'wb')
        batches = data.generate_batches(mode='add')
        num_batch = len(batches)
        embed = [[] for _ in range(data.num_nodes)]
        embed_pair = [[] for _ in range(data.num_nodes)]
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
                embed_pair[node1[i]].append((node1[i], node2[i]))
                embed_pair[node2[i]].append((node2[i], node1[i]))
        for i in range(data.num_nodes):
            if embed[i]:
                # print embed[i]
                # cdy: embed is a list, which size is node_num*x.
                # the element of it is also list, len(list) is the edges_num of each node.
                # so we can use all of them, not only average
                tmp = np.sum(embed[i], axis=0) / len(embed[i])
                file.write(' '.join(map(str, tmp)) + '\n')
            else:
                file.write('\n')
