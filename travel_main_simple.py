#Author: Mahalia Miller
#Date: Jan. 21, 2013

import ita
import bd
import util
import time
from math import log, exp, fabs
from random import normalvariate, seed
from groundTruthHazardjwb import QuakeMaps
import pickle

import networkx as nx
#get bridge information
with open( 'input/MedBridgeCap.txt','rb') as f:
  median_bridge_capacity = f.readlines()
median_bridge_capacity = [log(float(thing)) for thing in median_bridge_capacity] #convert to log
print 'ok, have median bridge capacities'

with open('input/20130123_mtc_bridgerow_u_v_dict.pkl','rb') as filename:
  row_u_v_dict = pickle.load(filename) #key=bridge row number (1-1557), value=list of pairs of start and end node ID
print 'ok, have relations between bridges and the network'

def run_simple_iteration(G, ground_motion, demand, multi):
  #G is a graph, demand is a dictionary keyed by source and target of demand per weekday. multi is a boolean that is true if it is a multigraph (can have two parallel edges between nodes)
  #change edge properties
  newG, num_out = damage_network(G, ground_motion, multi) #also returns the number of bridges out

  #get max flow
  start = time.time()
  #node 5753 is in superdistrict 12, which is santa clara county, and node 3144 is in superdistrict 18, which is alameda county. roughly these are san jose and oakland
  #node 7619 is in superdistrict 1 (7493 is also), which is sf, and node node 3144 is in superdistrict 18, which is alameda county. roughly these are san francisco and oakland
  s = '7619'
  t = '3144'
  flow = nx.max_flow(newG, s, t , capacity='capacity') #not supported by multigraph
  print 'time to get max flow: ', time.time() - start
#  flow = -1 
  #get ave. shortest path
#  start = time.time()
  sp_dict = nx.single_source_dijkstra_path_length(newG,'7619',weight='distance')
  sp = sum(sp_dict.values())/float(len(sp_dict.values()))
  sp2 = 0
  for target in demand.keys():
    sp2 += sp_dict[target]
  sp2 = sp2 / float(len(demand.keys()))
#  print 'time to get shortest path: ', time.time() - start
  newG = util.clean_up_graph(newG, multi)
  return (num_out, flow, sp, sp2) 

def pick_scenarios(lnsas, weights, multi=True):
  scenarios = []
  index = 0
  for w in weights:
    if weights[w]> 0.00001: #10^-5
      scenarios.append(index)
    index += 1
  print 'number of chosen scenarios: ', len(scenarios)
#  return scenarios
  return [1, 3]
def damage_network(G, scenario, multi=True):
  num_out = 0
  for site in range(len(scenario)):
    lnSa = scenario[site]
    lnSa_cap = normalvariate(median_bridge_capacity[site],0.6) #CHECK THIS
    if float(lnSa) > float(lnSa_cap):#in the moderate damage state as defined by HAZUS
      #print 'bridge out'
      num_out += 1
      #determine (u,v) of the link(s) carried by or affected by this bridge
      affected_edges = row_u_v_dict[site + 1]
#      print 'affected edges: ', affected_edges
      #affected_edges = [('5633','12707'), ('5632', '5625')]
      for [u,v] in affected_edges:
        if multi == True:
          for multi_edge in G[str(u)][str(v)].keys():
            G[str(u)][str(v)][multi_edge]['t_a'] = float('inf')
            G[str(u)][str(v)][multi_edge]['capacity'] = 0 
            G[str(u)][str(v)][multi_edge]['distance'] = 20*G[str(u)][str(v)][multi_edge]['distance_0']
        else:
          G[str(u)][str(v)]['t_a'] = float('inf')
          G[str(u)][str(v)]['capacity'] = 0 
          G[str(u)][str(v)]['distance'] = 20*G[str(u)][str(v)]['distance_0']
          
  return G, num_out

def main():
  seed(0) #set seed
  #get graph info
  G = nx.read_gpickle("input/graphMTC_CentroidsLength5.gpickle") #noCentroidsLength15.gpickle") #does not have centroidal links 
  G = nx.freeze(G) #prevents edges or nodes to be added or deleted
  #get od info. This is in format of a dict keyed by od, like demand[sd1][sd2] = 200000.
  demand = bd.build_demand('input/BATS2000_34SuperD_TripTableData.csv', 'input/superdistricts_centroids.csv')
  #get earthquake info
  q = QuakeMaps('input/20130107_mtc_total_lnsas1.pkl', 'input/20130107_mtc_magnitudes1.pkl', 'input/20130107_mtc_faults1.pkl', 'input/20130107_mtc_weights1.pkl', 'input/20130107_mtc_scenarios1.pkl') #totalfilename=None, magfilename=None, faultfilename=None, weightsfilename=None, scenariofilename=None):
  q.num_sites = len(q.lnsas[0])
  #determine which scenarios you want to run
  good_indices = pick_scenarios(q.lnsas, q.weights)
  
  travel_index_times = []
  index = 0
  #loop over scenarios
  for scenario in q.lnsas: #each 'scenario' has 1557 values of lnsa, i.e. one per site
    if index in good_indices:
      print 'index: ', index
      (bridges, flow, path, path2) = run_simple_iteration(G, scenario, demand, True)
      travel_index_times.append((index, bridges, flow, path, path2))
#      print 'new travel times: ', travel_index_times
      if index%100 ==0:
        util.write_2dlist(time.strftime("%Y%m%d")+'_bridges_flow_paths.txt',travel_index_times)
    index += 1 #IMPORTANT
  util.write_2dlist(time.strftime("%Y%m%d")+'_bridges_flow_paths.txt',travel_index_times)

def main2():
  seed(0) #set seed
  #get graph info
  G = nx.read_gpickle("input/graphMTC_CentroidsLength6.gpickle") #noCentroidsLength15.gpickle") #does not have centroidal links 
  G = nx.freeze(G) #prevents edges or nodes to be added or deleted
  #get od info. This is in format of a dict keyed by od, like demand[sd1][sd2] = 200000.
  demand = bd.build_demand('input/BATS2000_34SuperD_TripTableData.csv', 'input/superdistricts_centroids.csv')
  #get earthquake info
  q = QuakeMaps('input/20130107_mtc_total_lnsas1.pkl', 'input/20130107_mtc_magnitudes1.pkl', 'input/20130107_mtc_faults1.pkl', 'input/20130107_mtc_weights1.pkl', 'input/20130107_mtc_scenarios1.pkl') #totalfilename=None, magfilename=None, faultfilename=None, weightsfilename=None, scenariofilename=None):
  q.num_sites = len(q.lnsas[0])
  #determine which scenarios you want to run
  good_indices = pick_scenarios(q.lnsas, q.weights)
  
  travel_index_times = []
  index = 0
  #loop over scenarios
  for scenario in q.lnsas: #each 'scenario' has 1557 values of lnsa, i.e. one per site
    if index in good_indices:
      print 'index: ', index
      (bridges, flow, path, path2) = run_simple_iteration(G, scenario, demand, False)
      travel_index_times.append((index, bridges, flow, path, path2))
#      print 'new travel times: ', travel_index_times
      if index%100 ==0:
        util.write_2dlist(time.strftime("%Y%m%d")+'_bridges_flow_paths.txt',travel_index_times)
    index += 1 #IMPORTANT
  util.write_2dlist(time.strftime("%Y%m%d")+'_bridges_flow_paths.txt',travel_index_times)


if __name__ == '__main__':
  main2()
