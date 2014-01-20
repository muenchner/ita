#Author: Mahalia Miller
#Date: October 19, 2011
#Project: ICASP to journal

import networkx as nx
import matplotlib.pyplot as plt
import string
import time
import pstats
import cProfile
import pickle

def files_to_R2(G):
    #adjacency list
    nx.write_adjlist(G,"file_output/20120711adjlistFULL.csv")
    #node list
    text_file = open("file_output/20120710nodes2FULL.csv", "a")#
    for node in G:
        text_file.write(str.format(str(node), '10.2f') + ',' + str.format(str(G.position[node][0]), '10.2f') + ', ' + str.format(str(G.position[node][1]), '10.2f') + '\n')
    text_file.close()
    #capacity of each edge
    text_file = open("file_output/20120626edgesFULL.csv", "a")#
    for edge in G.edges(data=True):
        text_file.write(str.format(str(edge[0]), '10.2f') + ',' + str.format(str(edge[1]), '10.2f') + ', ' + str.format(str(edge[2]['capacity']), '10.2f') + '\n')
    text_file.close()
def main():
    #Import data
    filename_edges='input/20120711EdgesLatLong.txt'
    rows_edges = open(filename_edges).read().splitlines()
    
    #Create graph
#    singleGraph=nx.MultiGraph()
    singleGraph = nx.DiGraph()
    singleGraph.position={}
    dummyCounter= 0
    linecounter = 0
    for row in rows_edges[1:]:
        tokens = row.split(',')
        
        tokens.pop() #removes the shape length
#        print 'whole line: ', tokens
#        print tokens[1]
#        print tokens[2]
#        print 'x,y: ', tokens[-2]
#        print tokens[-1]
        if int(tokens[13])==16:#'centroid connector/dummy link if this is a 6'
            dummyCounter += 1
        else:
            #add nodes
            singleGraph.add_node(str(tokens[1]))
            singleGraph.position[tokens[1]]=(float(tokens[-4]), float(tokens[-3]))
            singleGraph.add_node(str(tokens[2]))
            singleGraph.position[str(tokens[2])]=(float(tokens[-2]), float(tokens[-1]))
            #add edge
            travel_time_0 = int(60.0*60.0*float(tokens[3])*(1.0/float(tokens[18]))) #in seconds     #        travel_time_0 = 60.0*60.0*distance*(1.0/velocity) #in seconds
            cap = int(float(tokens[6])*float(tokens[11]))
            vol = int(float(tokens[156]))
            singleGraph.add_edge(str(tokens[1]), str(tokens[2]), capacity_0 = cap,  capacity = cap, lanes =int(tokens[6]) , bridges=[], distance_0=float(tokens[3]), distance = float(tokens[3]), t_a=travel_time_0, t_0=travel_time_0, flow=0, dailyvolume=vol) #capacity in vehicles over all lanes, travel time in seconds, length in miles, flow in 
            linecounter += 1
    print 'Number of nodes before pruning:', len(singleGraph)
    print 'Number of dummy links: ', dummyCounter
    print 'line counter: ', linecounter
    #PRUNE
    counter=0
    for n in singleGraph:
        if singleGraph.degree(n)==0:
            counter=counter+1
            singleGraph.remove_node(n)
    print 'counter on removals', counter
    print 'after pruning: ', len(singleGraph)
    print 'Number of edges in graph: ', len(singleGraph.edges())
    #files_to_R2(singleGraph)
    nx.write_gpickle(singleGraph, "input/graphMTC_CentroidsLength3int.gpickle")

#     #now, add those bridges
#     G = singleGraph.copy()
#     pkl_file = open('input/20130121_mtc_edge_dict.pkl','rb')  #this one from august sucks!!'20120828_mtc_edge_dict.pkl','rb')
#     edge_dict = pickle.load(pkl_file)  #key=edge objectID, value=pair of start and end node ID
#     pkl_file.close()
#     pkl_file = open('input/20130121_mtc_bridgeID_dict.pkl','rb')
#     bridgeID_dict = pickle.load(pkl_file) #key=1:1557 number, value=bridgeID
#     pkl_file.close()
#     pkl_file = open('input/20120829_mtc_bridge_edge_dict.pkl','rb') #has 1889 bridges!
#     bridge_edge_dict = pickle.load(pkl_file) #key=bridge id, value= list of edge object id that are affected
#     pkl_file.close()    
#     not_k = 0
#     good_k = 0
#     reverse_bridge_dict = {}
#     for lk, bv in bridgeID_dict.items():
#         reverse_bridge_dict[bv] = lk
#     #say which bridges are on each link
#     for k, values in bridge_edge_dict.items():
#         #print 'bridge id: ', k
#         #print values
#         if k in reverse_bridge_dict.keys(): 
#             good_k += 1
#             for edge_id in values:
#                 try:
#                     #print 'edge id: ', edge_id
                    
#                     edge = edge_dict[edge_id]
#                     #figure out what the 1-1557 number is for this bridgeID
#                     littlenum = reverse_bridge_dict[k]
#                     #print 'k: ', k
#                     for i in range(len(G[str(edge[0])][str(edge[1])].keys())):
#                       G[str(edge[0])][str(edge[1])][i]['bridges'].append(littlenum)
#                     #print 'bridge id: ', littlenum

#                 except KeyError as e:
#                     print 'error: ', e
#                     print 'could not find edge_dict key ', edge_id
# #                    print 'or bridge id: ', k
#         else:
#             not_k += 1
#             print 'bridge id: ', k
#             print 'and values: ', values
#     print 'num of bridges not in bridgeID dict: ', not_k
#     print good_k
#     nx.write_gpickle(G, "graphMTC_CentroidsLength6int.gpickle")
    nx.draw(singleGraph,singleGraph.position, width=4,alpha=0.4,edge_color='0.75',node_color='b',node_size=50, font_size=2) #,with_labels=False
    plt.savefig("20120626highwaymapMTC_lll.pdf")
    #plt.show()
if __name__ == '__main__':
    main()
#    cProfile.run('main()', 'fooprof')
#    p = pstats.Stats('fooprof')
#    p.sort_stats('time').print_stats(30)
#    p.print_callers(30)
#    p.sort_stats('cumulative').print_stats(30)
#    p.print_callers(30)
