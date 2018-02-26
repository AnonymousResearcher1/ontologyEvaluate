from owlready2 import *
import codecs
#import rdflib
#g=rdflib.Graph()
#g.load('file:///home/cdy/research/ontology/ontos/idoden.owl')

#g.serialize("./idoden.nt", format='nt')
#with opencs.open("idoden.tri")
#for s,p,o in g:
    #print(s,p,o)

def extractNodes():
    #onto = get_ontology("file:///home/cdy/research/ontology/ontos/antibiotic_change_IRI.owl").load()
    onto = get_ontology("file:///home/cdy/research/ontology/ontos/doid.owl").load()
    file_name_ntri = u"./" + onto_name + "/" + onto_name + ".nt"
    onto.save(file_name_ntri, format='ntriples')

    file_name_desc = u"./" + onto_name +"/data.txt"
    f_desc = codecs.open(file_name_desc,"w", "utf-8")

    file_name_iris = u"./" + onto_name +"/nodes_iri.txt"
    f_iris = codecs.open(file_name_iris,"w", "utf-8")

    #all_nodes = list(onto.classes())
    #creat node-iri and nodes-list which has description
    with codecs.open(file_name_ntri, 'r', 'utf-8') as f:
        nodes_count = 0
        line_NO = 0
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

            description_marker = u"IAO_0000115"
            decs = re.compile(r'"(.*)"')
            if pred.find(description_marker) != -1:
                if len(decs.findall(obj)) == 0:
                    print(obj)
                elif sub == lastsub:
                    f_desc.write("\t" + decs.findall(obj)[0]) #add description into the end
                elif len(decs.findall(obj)[0]) != 0:
                    if nodes_count != 0:
                        f_desc.write("\n" ) #new entity, new line
                    f_desc.write(decs.findall(obj)[0]) #new entity, new line
                    f_iris.write(str(nodes_count) + "\t" + sub +"\n")
                    nodes_count += 1
                    lastsub = sub
            line_NO += 1



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

    file_name_iris = u"./" + onto_name +"/nodes_iri.txt"
    iri2id = dict()
    with codecs.open(file_name_iris,"r", "utf-8") as f:
        for line in f:
            (id, iri) = line.strip().split()
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
