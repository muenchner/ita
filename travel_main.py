#Author: Mahalia Miller
#Date: Jan. 21, 2013

import ita
import bd
import util
import time
from math import log, exp, fabs
from random import normalvariate
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

def run_iteration(G, ground_motion, demand):
  #change edge properties
  newG = damage_network(G, ground_motion)

  #call ita
  start = time.time()
#  print 'starting iterative travel assignment'
  it = ita.ITA(G,demand)
  newG = it.assign()
  print 'time to assign: ', time.time()-start
#  for n,nbrsdict in newG.adjacency_iter():
#    for nbr,keydict in nbrsdict.items():
#      for key,eattr in keydict.items():
#        if eattr['flow']>0:
#          print (n, nbr, eattr['flow'])
  travel_time = util.find_travel_time(newG)
  vmt = util.find_vmt(G)
#  print 'travel time: ', travel_time
#  print 'vmt: ', util.find_vmt(G) #in the undamaged case, this should be around 172 million (http://www.mtc.ca.gov/maps_and_data/datamart/stats/vmt.htm)
  newG = util.clean_up_graph(newG)
  return (travel_time, vmt)

def pick_scenarios(lnsas, weights):
  scenarios = []
  index = 0
  for w in weights:
    if weights[w]> 0.00001: #10^-5
      scenarios.append(index)
    index += 1
  print 'number of chosen scenarios: ', len(scenarios)
  return scenarios
def damage_network(G, scenario):
  for site in range(len(scenario)):
    lnSa = scenario[site]
    lnSa_cap = normalvariate(median_bridge_capacity[site],0.6) #CHECK THIS
    if float(lnSa) > float(lnSa_cap):#in the moderate damage state as defined by HAZUS
      #print 'bridge out'
      #determine (u,v) of the link(s) carried by or affected by this bridge
      affected_edges = row_u_v_dict[site + 1]
#      print 'affected edges: ', affected_edges
      #affected_edges = [('5633','12707'), ('5632', '5625')]
      for [u,v] in affected_edges:
        for multi_edge in G[str(u)][str(v)].keys():
          G[str(u)][str(v)][multi_edge]['t_a'] = float('inf')
#          G[u][v][multi_edge]['capacity'] = 0 
  return G

def main():
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
      (travel_time, vmt) = run_iteration(G, scenario, demand)
      travel_index_times.append((index, travel_time, vmt))
#      print 'new travel times: ', travel_index_times
      if index%10 ==0:
        util.write_2dlist(time.strftime("%Y%m%d")+'_travel_time.txt',travel_index_times)
    index += 1 #IMPORTANT
  util.write_2dlist(time.strftime("%Y%m%d")+'_travel_time.txt',travel_index_times)

if __name__ == '__main__':
  main()
