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
from get_praveen_results import get_praveen_results

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
  newG, capacities = damage_network(G, ground_motion, multi) #also returns the number of bridges out
  num_out = sum(x < 100 for x in capacities)
#  util.write_list(time.strftime("%Y%m%d")+'_bridges_scen_1.txt', capacities)   
  #get max flow
  start = time.time()
  #node 5753 is in superdistrict 12, which is santa clara county, and node 3144 is in superdistrict 18, which is alameda county. roughly these are san jose and oakland
  #node 7619 is in superdistrict 1 (7493 is also), which is sf, and node node 3144 is in superdistrict 18, which is alameda county. roughly these are san francisco and oakland
  s = '5753'
  t = '7493' #2702 
  flow = nx.max_flow(newG, s, t, capacity='capacity') #not supported by multigraph
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
  wout = []
  index = 0
  easy = True #whether to just take scenarios that are of engineering interest or do some complicated other thing
  print 'length of lnsas: ', len(lnsas)
  print 'length of weights: ', len(weights)
  numeps = float(round(len(lnsas)/4993.0))
  print 'numeps: ', numeps
  wsum = 0
  if easy == True:
    print 'easy'
    for w in weights:
      wsum += weights[w]
      if weights[w]> 0.0000001/numeps: #10^-5 divided by num eps because the weights get renormalized when take more than one epsilon realization per scenario
        scenarios.append(index)
        wout.append((index, weights[w]))
      index += 1
  else:
    (scenarios, wout) = get_praveen_results(lnsas)
  util.write_2dlist(time.strftime("%Y%m%d")+'_weights2.txt', wout) #save the weights of the chosen scenarios
  print 'number of chosen scenarios: ', len(scenarios)
  print 'weights of all scenarios: ', wsum
  print 'the sum of the subset weights: ', sum([ww[1] for ww in wout])
  return scenarios
#  return [1]
def damage_network(G, scenario, multi=True):
  capacities = [100]*len(scenario)
  num_out = 0
  for site in range(len(scenario)):
    lnSa = scenario[site]
    lnSa_cap = normalvariate(median_bridge_capacity[site],0.6) #CHECK THIS
    if float(lnSa) > float(lnSa_cap):#in the moderate damage state as defined by HAZUS
      #print 'bridge out'
      num_out += 1
      capacities[site] = 0
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
  print 'number of briges out: ', num_out
  return G, capacities

def main():
  seed(0) #set seed
  #get graph info
  G = nx.read_gpickle("input/graphMTC_CentroidsLength6.gpickle") #noCentroidsLength15.gpickle") #does not have centroidal links. There is also the choice of a proper multidigraph: nx.read_gpickle("input/graphMTC_CentroidsLength5.gpickle")
  G = nx.freeze(G) #prevents edges or nodes to be added or deleted
  #get od info. This is in format of a dict keyed by od, like demand[sd1][sd2] = 200000.
  demand = bd.build_demand('input/BATS2000_34SuperD_TripTableData.csv', 'input/superdistricts_centroids.csv')
  #get earthquake info
  q = QuakeMaps('input/20130210_mtc_total_lnsas3.pkl', 'input/20130210_mtc_magnitudes3.pkl', 'input/20130210_mtc_faults3.pkl', 'input/20130210_mtc_weights3.pkl', 'input/20130210_mtc_scenarios3.pkl') #('input/20130107_mtc_total_lnsas1.pkl', 'input/20130107_mtc_magnitudes1.pkl', 'input/20130107_mtc_faults1.pkl', 'input/20130107_mtc_weights1.pkl', 'input/20130107_mtc_scenarios1.pkl') #totalfilename=None, magfilename=None, faultfilename=None, weightsfilename=None, scenariofilename=None):
  q.num_sites = len(q.lnsas[0])
  #determine which scenarios you want to run
  good_indices = pick_scenarios(q.lnsas, q.weights)
  
  travel_index_times = []
  index = 0
  #loop over scenarios
  print 'size of lnsas: ', len(q.lnsas)
  for scenario in q.lnsas: #each 'scenario' has 1557 values of lnsa, i.e. one per site
    if index in good_indices:
      print 'index: ', index
      (bridges, flow, path, path2) = run_simple_iteration(G, scenario, demand, False)
      travel_index_times.append((index, bridges, flow, path, path2))
#      print 'new travel times: ', travel_index_times
      if index%1000 ==0:
        util.write_2dlist(time.strftime("%Y%m%d")+'_bridges_flow_paths3.txt',travel_index_times)
    index += 1 #IMPORTANT
  util.write_2dlist(time.strftime("%Y%m%d")+'_bridges_flow_paths3.txt',travel_index_times)
  print 'the number of scenarios I actually did: ', index

if __name__ == '__main__':
  main()
