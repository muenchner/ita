#Author: Mahalia Miller
#Date: Jan. 21, 2013

import ita
import bd
import util
import time
from math import log, exp, fabs
from groundTruthHazardjwb import QuakeMaps

import networkx as nx
#get bridge information
with open( 'input/MedBridgeCap.txt','rb') as f:
  median_bridge_capacity = f.readlines()
median_bridge_capacity = [log(float(thing)) for thing in median_bridge_capacity] #convert to log
print 'ok, have median bridge capacities'

def run_iteration(G, ground_motion, demand):
  #change edge properties
  newG = damage_network(G, ground_motion)

  #call ita
  start = time.time()
  print 'starting iterative travel assignment'
  it = ita.ITA(G,demand)
  newG = it.assign()
  print 'time to assign: ', time.time()-start
  for n,nbrsdict in newG.adjacency_iter():
    for nbr,keydict in nbrsdict.items():
      for key,eattr in keydict.items():
        if eattr['flow']>0:
          print (n, nbr, eattr['flow'])
  travel_time = util.find_travel_time(newG)
  print 'travel time: ', travel_time
  print 'vmt: ', util.find_vmt(G) #in the undamaged case, this should be around 172 million (http://www.mtc.ca.gov/maps_and_data/datamart/stats/vmt.htm)
  newG = util.clean_up_graph(newG)
  return travel_time

def pick_scenarios(lnsas, weights):
  #TODO
  return [1, 3]

def damage_network(G, scenario):
  for site in range(num_sites):
    lnSa = scenario[site]
    lnSa_cap = random.normalvariate(median_bridge_capacity[site],0.6) #CHECK THIS
#                print 'lnSa: ', lnSa
#                print 'lnSa_cap: ',lnSa_cap
    if float(lnSa) > float(lnSa_cap):#in the moderate damage state as defined by HAZUS
      pass
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
      travel_index_times.append((index, run_iteration(G, scenario, demand)))
      print 'new travel times: ', travel_times
      if index%10 ==0:
        util.write_2dlist(time.strftime("%Y%m%d")+'_travel_time.txt',travel_times)

    index += 1 #IMPORTANT
  util.write_2dlist(time.strftime("%Y%m%d")+'_travel_time.txt',travel_times)

if __name__ == '__main__':
  main()
