from owlready2 import *
import codecs
import wikipedia
import random
from gevent import pool,monkey;monkey.patch_all()
import gevent
import time
#import rdflib
#g=rdflib.Graph()
#g.load('file:///home/cdy/research/ontology/ontos/idoden.owl')

#g.serialize("./idoden.nt", format='nt')
#with opencs.open("idoden.tri")
#for s,p,o in g:
    #print(s,p,o)


def getsummary_fromwiki(label, id):
    try:
       description = wikipedia.summary(label,sentences=3)
       description = description.replace('\n', ' ')
       #print(str(id) +"\t" + str(len(description)) + "\n")
       #f.write(str(id) + "\t" + description + '\n')
    except:
        description = ''
        #print("no des\n")
    return id, description


def crawlWiki(iris_id, iris_labels, iris_fathers, f_desc_name, skipwiki,use_label_astext):
    ids_desc = dict()
    #type of id_iris: int -> str
    id_iris = dict()
    id_no_desc = set()
    for iri in iris_id:
        id_iris[iris_id[iri]] = iri

    with codecs.open(f_desc_name, 'r', 'utf-8') as f:
        line_num = 1
        for line in f:
            # skip first line
            if line_num == 1:
                line_num += 1
                continue
            words = line.strip().split()
            node_id = words[0]
            node_desc = ' '.join(words[1:-1])
            ids_desc[int(node_id)] = node_desc
            line_num += 1
    print("len(ids_desc):\t" + str(len(ids_desc)))




    if use_label_astext:
        with codecs.open(f_desc_name, 'a', 'utf-8') as f:
            for i in range(len(iris_id)):
                if i in ids_desc:
                    continue
                else:
                    label = iris_labels[id_iris[i]]
                    f.write(str(i) + "\t" + label + '\n')
        return



    if not skipwiki:
        with codecs.open(f_desc_name, 'a', 'utf-8') as f:
            labels_ids = []  # [[label1,id1] , [label2,id2] ...]
            for i in range(len(iris_id)):
                if i in ids_desc:
                    continue
                else:
                    label = iris_labels[id_iris[i]]
                    labels_ids.append([label,i])
            print("len(labels_ids):\t" + str(len(labels_ids)) + "\n")
            print("label0,id0:\t" + labels_ids[0][0] + "\t" + str(labels_ids[0][1]) + "\n")

            print(time.asctime( time.localtime(time.time())))
            p = pool.Pool(500)
            batch_size = 100000
            batch_num_subone = len(labels_ids) // batch_size
            end = 0
            for begin in range(batch_num_subone + 1):
                if begin == batch_num_subone:  # the last batch
                    jobs = [p.spawn(getsummary_fromwiki, label, id) for label, id in labels_ids[end:-1]]
                else:
                    begin = begin * batch_size
                    end = begin + batch_size
                    jobs = [p.spawn(getsummary_fromwiki, label, id) for label, id in labels_ids[begin:end]]
                gevent.joinall(jobs, timeout=5)
                for job in jobs:
                    if job.value is None:
                        continue
                    id, description = job.value
                    if len(description) > 0:
                        ids_desc[id] = description
                        f.write(str(id) + "\t" + description + '\n')
                    else:
                        id_no_desc.add(id)
                print(time.asctime( time.localtime(time.time())) + ":\tbatch begin:" + str(begin) + "\n")
    else:
        for i in range(len(iris_id)):
            if i in ids_desc:
                continue
            else:
                id_no_desc.add(i)

    print(len(ids_desc))
    print(len(id_no_desc))
    if len(ids_desc) + len(id_no_desc) != len(labels_ids):
        for label, id in labels_ids:
            if id not in ids_desc and id not in id_no_desc:
                id_no_desc.add(id)

    # copy from dads who has text description
    tried_all_count = 0
    with codecs.open(f_desc_name, 'a', 'utf-8') as f:
        while len(id_no_desc) != 0 and tried_all_count <= 8:
            found_once= False
            ids = list(id_no_desc)
            if tried_all_count >= 4:
                random.shuffle(ids)
            for id in ids:
                # no description, no dad
                if id_iris[id] not in iris_fathers:
                    continue
                # find dads' description
                dads = iris_fathers[id_iris[id]]
                present_id_found = False
                while len(dads) > 0 and present_id_found is False:
                    # present dad has description
                    if dads[0] in ids_desc:
                        ids_desc[id] = ids_desc[dads[0]]
                        found_once = True
                        present_id_found = True
                        id_no_desc.remove(id)
                        f.write(str(id) + "\t" + ids_desc[id] + '\n')
                    # present dad has no description but has fathers
                    elif id_iris[dads[0]] in iris_fathers and len(iris_fathers[id_iris[dads[0]]]) > 0:
                        dads.extend(iris_fathers[id_iris[dads[0]]])
                    #del present dad, checked.
                    dads.pop(0)
            if not found_once:
                tried_all_count += 1

    print(len(id_no_desc))
    #print(id_no_desc)






def extractNodes():
    #onto = get_ontology("file:///home/cdy/research/ontology/ontos/antibiotic_change_IRI.owl").load()
    #onto = get_ontology("file:///home/cdy/research/ontology/ontos/doid.owl").load()
    file_name_ntri = u"./" + onto_name + "/" + onto_name + ".nt"
    #onto.save(file_name_ntri, format='ntriples')

    file_name_desc = u"./" + onto_name +"/nodes_desc.txt"
    skipWiki = True
    if not skipWiki:
        f_desc = codecs.open(file_name_desc,"w", "utf-8")

    file_name_iris = u"./" + onto_name +"/nodes_iri_label.txt"
    f_iris_labels = codecs.open(file_name_iris,"w", "utf-8")


    #all_nodes = list(onto.classes())
    #creat node-iri and nodes-list which has description
    iris_label = dict()
    iris_id = dict()
    with codecs.open(file_name_ntri, 'r', 'utf-8') as f:
        nodes_count = 0
        line_NO = 0
        label_marker_match_count = 0
        #the first label_matches are meta-label, not real class
        skip_label_match_num = -1
        for line in f:
            line = line.strip('.\n').strip()
            if(len(line.split("> ")) != 3):
                print(line)
                print(line.split("> "))
            #(sub,pred,obj) =  line.split("> ")
            sub =''
            pred = ''
            obj = ''
            item_count = 0
            for item in line.split("> "):
                if item_count == 0:
                    sub = item.strip('<')
                elif item_count == 1:
                    pred = item.strip('<')
                else:
                    obj = obj + item
                item_count += 1

            # construct node_id and nodes_label
            subclass_marker = u"schema#label"
            decs = re.compile(r'"(.*)"')
            if pred.find(subclass_marker) != -1:
                if len(decs.findall(obj)) == 0:
                    #print(obj)
                    pass
                elif len(decs.findall(obj)[0]) != 0 and label_marker_match_count <= skip_label_match_num:
                    label_marker_match_count += 1
                elif len(decs.findall(obj)[0]) != 0:
                    iris_id[sub] = nodes_count
                    iris_label[sub] = decs.findall(obj)[0]
                    nodes_count += 1
                    f_iris_labels.write(str(iris_id[sub]) + "\t" + sub + '\t' + iris_label[sub] + "\n")
            line_NO += 1
        print(label_marker_match_count)

    iris_fathers = dict()
    with codecs.open(file_name_ntri, 'r', 'utf-8') as f:
        lastsub = '' #some nodes has multi-line description
        for line in f:
            line = line.strip('.\n').strip()
            if(len(line.split("> ")) != 3):
                print(line)
                print(line.split("> "))
            #(sub,pred,obj) =  line.split("> ")
            sub =''
            pred = ''
            obj = ''
            item_count = 0
            for item in line.split("> "):
                if item_count == 0:
                    sub = item.strip('<')
                elif item_count == 1:
                    pred = item.strip('<')
                else:
                    obj = obj + item
                item_count += 1

            # constuct nodes_father and nodes_description
            description_marker = u"IAO_0000115"
            description_marker = u"description"
            subclass_marker = u"schema#subClassOf"
            decs = re.compile(r'"(.*)"')
            obj = obj.strip('<>')
            if pred.find(subclass_marker) != -1:
                if obj in iris_id and sub in iris_id:
                    if sub in iris_fathers:
                        iris_fathers[sub].append(iris_id[obj])
                    else:
                        iris_fathers[sub] = [iris_id[obj]]
            if pred.find(description_marker) != -1 and not skipWiki:
                if len(decs.findall(obj)) == 0:
                    #print(obj)
                    pass
                elif sub == lastsub:
                    f_desc.write("\t" + decs.findall(obj)[0]) #add description into the end
                elif len(decs.findall(obj)[0]) != 0 and sub in iris_id:
                    if nodes_count != 0:
                        f_desc.write("\n" ) #new entity, new line
                    f_desc.write(str(iris_id[sub]) + '\t' + decs.findall(obj)[0])
                    lastsub = sub
    file_nodes_father = u"./" + onto_name + "/nodes_fathers.txt"
    with codecs.open(file_nodes_father, 'w', 'utf-8') as fout:
        for node in iris_fathers:
            fathers = [str(father) for father in iris_fathers[node]]
            fout.write(str(iris_id[node]) + '\t' + ','.join(fathers) + '\n')

    if not skipWiki:
        f_desc.close()
    f_iris_labels.close()
    crawlWiki(iris_id,iris_label,iris_fathers,file_name_desc,skipwiki= False,use_label_astext=True)




    #for c in list(onto.classes()):
    #    nodes.append(c.iri)
    # #   print(c.iri)
    #
    #count1 = 0
    #for c in list(onto.annotation_properties()):
    #    count1 += 1
    #    #print(c)
    #
    #print('\n')
    #
    #count2 = 0
    #for c in list(onto.object_properties()):
    #    count2 += 1
    #    print(c.iri)
    #
    #print("\n")
#
#count3 = 0
#for c in list(onto.data_properties()):
#    count3 += 1
#    #print(c)
#
#print(count,count1,count2,count3)

def extractEdges():
    file_name_ntri = u"./" + onto_name + "/" + onto_name + ".nt"

    file_name_graph = u"./" + onto_name +"/graph.txt"
    f_graph = codecs.open(file_name_graph,"w", "utf-8")

    file_name_iris = u"./" + onto_name +"/nodes_iri_label.txt"
    iri2id = dict()
    with codecs.open(file_name_iris,"r", "utf-8") as f:
        for line in f:
            (id, iri) = line.strip().split()[:2]
            iri2id[iri] = id
    iris = iri2id.keys()

    blank_nodes = dict()
    #construct dict [blank_node:iri_node]
    with codecs.open(file_name_ntri, 'r', 'utf-8') as f:
        count = 0
        for line in f:
            if(len(line.split(" <")) == 3):
                (sub,pred,obj) =  line.strip('.\n').strip().split(" <")
                sub = sub.strip('<>')
                obj = obj.strip('<>')
                pred = pred.strip('<>')
            if(sub[:2] == "_:") and obj in iris \
                and 'someValuesFrom' in pred:
                blank_nodes[sub] = obj
            count += 1


    with codecs.open(file_name_ntri, 'r', 'utf-8') as f:
        line_no = 0
        for line in f:
            line = line.strip('.\n').strip()
            sub =''
            pred = ''
            obj = ''
            item_count = 0
            for item in line.split("> "):
                if item_count == 0:
                    sub = item.strip('<>')
                elif item_count == 1:
                    pred = item.strip('<>')
                else:
                   obj = obj + item.strip('<>')
                item_count += 1
            if obj in blank_nodes.keys():
                obj = blank_nodes[obj]
            if sub in iris and obj in iris:
                f_graph.write(iri2id[sub] + "\t" + iri2id[obj] + "\n")
            line_no += 1
    f_graph.close()






onto_name = u"doid"
#extractNodes()
extractEdges()
