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
import pdb

import networkx as nx
#get bridge information

#first load the all-purpose dictionary linking info about the bridges
with open('input/20130518_master_bridge_dict.pkl','rb') as f:
  master_dict = pickle.load(f)

BRIDGE_DAMAGE_DATASET = [] # in matlab indices (start at 1)
SPECIALLY_RETROFITTED_BRIDGES = []#[968,610,937,958, 920, 1022, 973, 817, 1086, 1085, 510, 1385, 728, 1089, 1069, 386, 970, 1075, 1416, 1062] #top 20 bridges with highest annual rates of failure in our scenarios
def update_bridge_damage_dataset(capacities):
  '''adds an element to the global variable, bridge damage dataset based on damaged bridges'''
  affected_bridges = []
  for i in range(len(capacities)):
    if capacities[i] < 100:
      affected_bridges.append(str(i+1))
  BRIDGE_DAMAGE_DATASET.append(affected_bridges)

def run_simple_iteration(G, ground_motion, demand, multi, j, targets, clean_up = True):
  #G is a graph (not a multigraph!), demand is a dictionary keyed by source and target of demand per weekday. multi is a boolean that is true if it is a multigraph (can have two parallel edges between nodes)
  #change edge properties
  newG, capacities = damage_network(G, ground_motion, multi) #also returns the number of bridges out
  num_out = sum(x < 100 for x in capacities)
  update_bridge_damage_dataset(capacities)
  if j in targets:
    affected_bridges = []
    for i in range(len(capacities)):
      if capacities[i] < 100:
        if (i+1) not in SPECIALLY_RETROFITTED_BRIDGES:
          affected_bridges.append(str(i+1))
    util.write_list('20130902_modifyingCapacity/' + time.strftime("%Y%m%d")+'_modifyingCapacitytab' + str(j) + '.txt', affected_bridges) 
  #get max flow
  start = time.time()
  #node 5753 is in superdistrict 12, which is santa clara county, and node 3144 is in superdistrict 18, which is alameda county. roughly these are san jose and oakland
  #node 7619 is in superdistrict 1 (7493 is also), which is sf, and node node 3144 is in superdistrict 18, which is alameda county. roughly these are san francisco and oakland
  s = '3144'
  t = '7493' #2702 
  try:
    flow = nx.max_flow(newG, s, t, capacity='capacity') #not supported by multigraph
  except nx.exception.NetworkXError as e:
    print 'found an ERROR: ', e
    flow = -1
    print s in newG
    print t in newG
    print len(newG.nodes())
    print len(newG.edges())
  # sp_dict = nx.single_source_dijkstra_path_length(newG,'7493',weight='distance')
  # sp = sum(sp_dict.values())/float(len(sp_dict.values()))
  # sp2 = 0
  # for target in demand.keys():
  #   sp2 += sp_dict[target]
  # sp2 = sp2 / float(len(demand.keys()))
  sp = 0
  sp2 = 0
  if clean_up == True:
    damagedG= util.clean_up_graph(newG)
  return (num_out, flow, sp, sp2, newG) 

def run_iteration(G, ground_motion, demand, damagedG, clean_up=True):
  '''this function runs iterative traffic assignment to find the vehicle miles traveled (VMT) and the travel time'''
  if damagedG == None:
    print 'damaging network'
    damagedG = damage_network(G, ground_motion)
  travel_time = -1
  vmt = -1
  #call ita
 #  start = time.time()
 #  it = ita.ITA(damagedG,demand)
 #  newG = it.assign()
 #  print 'time to assign: ', time.time()-start
 # # for n,nbrsdict in newG.adjacency_iter():
 # #   for nbr,keydict in nbrsdict.items():
 # #     for key,eattr in keydict.items():
 # #       if eattr['flow']>0:
 # #         print (n, nbr, eattr['flow'])
 #  travel_time = util.find_travel_time(damagedG) #this should be a little less than 252850.3941hours or **910,261,418.76seconds. **
 #  vmt = util.find_vmt(damagedG) #in the undamaged case, this should be around 172 million (http://www.mtc.ca.gov/maps_and_data/datamart/stats/vmt.htm) over the course of a day, so divide by 0.053 (see demand note in main). So, that's **8-9 million vehicle-miles**
  if clean_up == True:
    damagedG= util.clean_up_graph(damagedG)
  return (travel_time, vmt)

def pick_scenarios(lnsas, weights, multi, numeps):
  '''this function takes some scenarios with an annual rate of occurrence > 10e-5 OR does it based on some other criteria, called get_praveen_results'''
  scenarios = []
  wout = []
  index = 0
  easy = True #whether to just take scenarios that are of engineering interest or do some complicated other thing
  print 'length of lnsas: ', len(lnsas)
  print 'length of weights: ', len(weights)
  print 'numeps: ', numeps
  wsum = 0
  if easy == True:
    print 'easy'
    for w in weights:
      wsum += weights[w]
      if weights[w]> 0.00001/float(numeps): #0.0000001/numeps: #10^-5 divided by num eps because the weights get renormalized when take more than one epsilon realization per scenario
        scenarios.append(index)
        wout.append((index, weights[w]))
      index += 1
  else:
    (scenarios, wout) = get_praveen_results(lnsas)
  util.write_2dlist(time.strftime("%Y%m%d")+'_weights_' + str(numeps) + 'eps.txt', wout) #save the weights of the chosen scenarios
  print 'number of chosen scenarios: ', len(scenarios)
  print 'weights of all scenarios: ', wsum
  print 'the sum of the subset weights: ', sum([ww[1] for ww in wout])
  return scenarios

def damage_network(G, scenario, multi=True):
  capacities = [100]*len(scenario)
  num_out = 0
  for site in master_dict.keys():
    lnSa = scenario[master_dict[site]['new_id']-1]
    lnSa_cap = normalvariate(master_dict[site]['ext_lnSa'],0.6) #CHECK THIS
    if float(lnSa) > float(lnSa_cap):#in the moderate damage state as defined by HAZUS
      #print 'bridge out'
      num_out += 1
      capacities[master_dict[site]['new_id']-1] = 0
      #determine (u,v) of the link(s) carried by or affected by this bridge
      affected_edges = master_dict[site]['a_b_pairs_direct'] + master_dict[site]['a_b_pairs_indirect']

      for [u,v] in affected_edges:
        try:
          if multi == True:
            for multi_edge in G[str(u)][str(v)].keys():
              G[str(u)][str(v)][multi_edge]['t_a'] = float('inf')
              G[str(u)][str(v)][multi_edge]['capacity'] = 0 
              G[str(u)][str(v)][multi_edge]['distance'] = 20*G[str(u)][str(v)][multi_edge]['distance_0']
          else:
            G[str(u)][str(v)]['t_a'] = float('inf')
            G[str(u)][str(v)]['capacity'] = 0 
            G[str(u)][str(v)]['distance'] = 20*G[str(u)][str(v)]['distance_0']
        except:
          pass
  print 'number of briges out: ', num_out
  return G, capacities

def main():
  '''can change the number of epsilons below'''
  seed(0) #set seed
  simple = False #False #simple is just %bridges out, which is computationally efficient
  #get graph info
  # G = nx.read_gpickle("input/graphMTC_CentroidsLength6.gpickle") #noCentroidsLength15.gpickle") #does not have centroidal links. There is also the choice of a proper multidigraph: nx.read_gpickle("input/graphMTC_CentroidsLength5.gpickle")
  G = nx.read_gpickle("input/graphMTC_CentroidsLength6highways.gpickle") #noCentroidsLength15.gpickle") #does not have centroidal links. Directed! only one edge between nodes
  # G1 = nx.read_gpickle("input/graphMTC_CentroidsLength5.gpickle") #undirected, multiple edges. It is a little funky because it has two links between A and B and two between B and A so is that double-counting?
  # '''a multigraph: An undirected graph class that can store multiedges.
  #   Multiedges are multiple edges between two nodes.  Each edge
  #   can hold optional data or attributes.
  #   A MultiGraph holds undirected edges.  Self loops are allowed.'''
  print 'nodes: ', len(G.nodes())
  G = nx.freeze(G) #prevents edges or nodes to be added or deleted
  # G1 = nx.freeze(G1)
  #get od info. This is in format of a dict keyed by od, like demand[sd1][sd2] = 200000.
  demand = bd.build_demand('input/BATS2000_34SuperD_TripTableData.csv', 'input/superdistricts_centroids.csv') #we just take a percentage in ita.py, namely  #to get morning flows, take 5.3% of daily driver values. 11.5/(4.5*6+11.5*10+14*4+4.5*4) from Figure S10 of http://www.nature.com/srep/2012/121220/srep01001/extref/srep01001-s1.pdf
          #get path
  #get earthquake info #UPDATED May 23, 2013
  #TODO
  q = QuakeMaps('input/20130612_mtc_total_lnsas5.pkl', 'input/20130612_mtc_magnitudes5.pkl', 'input/20130612_mtc_faults5.pkl', 'input/20130612_mtc_weights5.pkl', 'input/20130612_mtc_scenarios5.pkl') #input/20130107_mtc_total_lnsas1.pkl', 'input/20130107_mtc_magnitudes1.pkl','input/20130107_mtc_faults1.pkl', 'input/20130107_mtc_weights1.pkl', 'input/20130107_mtc_scenarios1.pkl') #'input/20130210_mtc_total_lnsas3.pkl', 'input/20130210_mtc_magnitudes3.pkl', 'input/20130210_mtc_faults3.pkl', 'input/20130210_mtc_weights3.pkl', 'input/20130210_mtc_scenarios3.pkl') #('input/20130107_mtc_total_lnsas1.pkl', 'input/20130107_mtc_magnitudes1.pkl',  #totalfilename=None, magfilename=None, faultfilename=None, weightsfilename=None, scenariofilename=None):
  q.num_sites = len(q.lnsas[0])
  numeps = 5 #CAHNGE THIS CHANGE THIS!!!!!!!!
  #determine which scenarios you want to run
  good_indices = pick_scenarios(q.lnsas, q.weights,True, numeps)
  targets = good_indices #[12, 35, 55, 71, 75, 82, 86, 87, 88, 106, 108, 115, 121, 231, 241, 247, 256, 258, 260, 261, 676, 730, 733, 1231, 1548] #indices between 0 and 2110. the scenarios for which you want to save the damaged bridge data
  print 'the number of scenarios for which I want to save bridge info: ', len(targets)

  travel_index_times = []
  index = 0
  good_index = 0
  # pdb.set_trace()
  #figure out what the travel time and vmt are if no damage to any bridges
  no_damage_travel_time = -1
  no_damage_vmt = -1
  found_no_damage = False
  for scenario in q.lnsas: #each 'scenario' has 1xxx values of lnsa, i.e. one per site
    while found_no_damage == False:
      (bridges, flow, path, path2, newG) = run_simple_iteration(G, scenario, demand, False, good_index, targets, True) #since looking for no damage case, it is ok to clean up
      if bridges == 0:
        found_no_damage = True
        print 'found case with no damage so I will save those and save you work later on'
        (no_damage_travel_time, no_damage_vmt) = run_iteration(G, scenario, demand, newG)

  #loop over scenarios
  print 'size of lnsas: ', len(q.lnsas)
  for scenario in q.lnsas: #each 'scenario' has 1xxx values of lnsa, i.e. one per site
    if index in good_indices:
      print 'index: ', index
      if simple == True:
        (bridges, flow, path, path2, newG) = run_simple_iteration(G, scenario, demand, False, good_index, targets)
        travel_index_times.append((index, bridges, flow, path, path2, -1, -1, bridges/float(q.num_sites), -1))
      else:
        (bridges, flow, path, path2, newG) = run_simple_iteration(G, scenario, demand, False, good_index, targets, False) #doesn't clean up the damage
        print 'what i found for bridges: ', bridges
        if bridges == 0:
          travel_time = no_damage_travel_time; 
          vmt = no_damage_vmt; 
        else:
          print 'attempting new'
          (travel_time, vmt) = run_iteration(G, scenario, demand, newG, True)
        print 'what i have for (tt, vmt): ', (travel_time, vmt)
        travel_index_times.append((index, bridges, flow, path, path2, travel_time, vmt, bridges/float(q.num_sites), -1))
      good_index += 1
        # travel_index_times.append((index, travel_time, vmt))
#      print 'new travel times: ', travel_index_times
    if index%1000 ==0:
      print 'index: ', index
      util.write_2dlist(time.strftime("%Y%m%d")+'_bridges_flow_paths_5eps_extensive.txt',travel_index_times)
    index += 1 #IMPORTANT
  util.write_2dlist(time.strftime("%Y%m%d")+'_bridges_flow_paths_5eps_extensive.txt',travel_index_times)
  print 'the number of scenarios I considered doing: ', index
  print 'the number of scenarios I actually did: ', len(travel_index_times)
  print 'i.e.: ', good_index
  print 'and now, I will save a dataset of damaged bridges in each scenario'
  util.write_2dlist(time.strftime("%Y%m%d")+'_damaged_bridges_5eps_extensive.txt',BRIDGE_DAMAGE_DATASET)
  with open(time.strftime("%Y%m%d")+'_damaged_bridges_5eps_extensive.pkl', 'wb') as f:
    pickle.dump(BRIDGE_DAMAGE_DATASET, f)

if __name__ == '__main__':
  main()
