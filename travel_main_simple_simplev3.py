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
import string
import os
import transit_to_damage
import pp # parallel python
from transit_to_damage import make_bart_dict, make_muni_dict, clear_transit_file, damage_bart, damage_caltrain, damage_muni, damage_vta, set_main_path
import networkx as nx
#get bridge information

#first load the all-purpose dictionary linking info about the bridges
with open('input/20130518_master_bridge_dict.pkl','rb') as f:
  master_dict = pickle.load(f) #has 1743 keys. One per highway bridge. (NOT BART)
  '''
  dict with a bridge_key that ranges from 1 to 1889 and then the value is another dictionary with the following keys: 
    loren_row_number: the row number in Loren Turner's table that has info on all CA bridges
    original_id: the original id (1-1889)
    new_id: the new id that excludes filtered out bridges (1-1743). Bridges are filtered out if a.) no seismic capacity data AND non-transbay bridge or b.) not located by Jessica (no edge list). this id is the new value that is the column number for the lnsa simulations.
    jessica_id: the id number jessica used. it's also the number in arcgis.
    a_b_pairs_direct: list of (a,b) tuples that would be directly impacted by bridge damage (bridge is carrying these roads)
    a_b_pairs_indirect: ditto but roads under the indirectly impacted bridges
    edge_ids_direct: edge object IDS for edges that would be directly impacted by bridge damage
    edge_ids_indirect: ditto but roads under the indirectly impacted bridges
    mod_lnSa: median lnSa for the moderate damage state. the dispersion (beta) for the lognormal distribution is 0.6. (See hazus/mceer method)
    ext_lnSa: median lnSa for the extensive damage state. the dispersion (beta) for the lognormal distribution is 0.6. (See hazus/mceer method)
    com_lnSa: median lnSa for the complete damage state. the dispersion (beta) for the lognormal distribution is 0.6. (See hazus/mceer method)
    '''
with open('input/20131212_master_transit_dict.pkl','rb') as f:
  master_transit_dict = pickle.load(f) #has xx keys. One per BART structure.
# master_transit_dict = {}
# with open('input/id_mod_ext_com_beta.csv', 'rb') as f:
#   for line in f:
#     print line
#     tokens = string.split(line, ',')
#     print tokens
#     master_transit_dict[tokens[0]] = {'mod_lnSa': float(tokens[1])/100.0, 'ext_lnSa': float(tokens[2])/100.0, 'com_lnSa': float(tokens[3])/100.0, 'new_id': int(tokens[0]), 'beta': float(tokens[4])}
#     print master_transit_dict[tokens[0]]
# with open ('input/20131212_master_transit_dict.pkl', 'wb') as f:
#   pickle.dump(master_transit_dict, f)

def compute_flow(damaged_graph):
  return -1

def compute_shortest_paths(damaged_graph, demand):
  return -1

def compute_tt_vmt(damaged_graph, demand):
  start = time.time()
  it = ita.ITA(damaged_graph,demand)
  newG = it.assign()
  print 'time to assign: ', time.time()-start
 # for n,nbrsdict in newG.adjacency_iter():
 #   for nbr,keydict in nbrsdict.items():
 #     for key,eattr in keydict.items():
 #       if eattr['flow']>0:
 #         print (n, nbr, eattr['flow'])
  travel_time = util.find_travel_time(damaged_graph) #this should be a little less than 252850.3941hours or **910,261,418.76seconds. **
  vmt = util.find_vmt(damaged_graph) #in the undamaged case, this should be around 172 million (http://www.mtc.ca.gov/maps_and_data/datamart/stats/vmt.htm) over the course of a day, so divide by 0.053 (see demand note in main). So, that's **8-9 million vehicle-miles**
  # print travel_time
  # print 'vmt: ', vmt
  return travel_time, vmt

def make_cube_network_damage(path, list_of_u_v, index):
  text_file = open(path + time.strftime("%Y%m%d")+'freeflowupdater'  + str(index) + 'extensiveDec.job', 'a')
  text_file.write('run pgm = hwynet' + '\r\n')
  text_file.write('\t' + r"neti = D:\mtc_travel_model\2010_nonode_TEST\INPUT\hwy\freeflow_undamaged.NET" + '\r\n')
  text_file.write('\t' + r"neto = D:\mtc_travel_model\2010_nonode_TEST\INPUT\hwy\freeflow" + str(index) + "extensive.net" + '\r\n')
  text_file.write('\t' + 'CTIM = FFT \r\n')
  #now loop over lines of the input file
  for line in list_of_u_v: # a line is an (a,b) pair
    # print 'a line: ', line
    text_file.write('\t' + 'if (a = ' + str.format(str(line[0]), '10.2f') + ' & b = ' + str.format(str(line[1]), '10.2f')  + ')' + ' CAPCLASS = 62'  + '\r\n')
    text_file.write('\t' + 'if (a = ' + str.format(str(line[0]), '10.2f') + ' & b = ' + str.format(str(line[1]), '10.2f')  + ')' + ' SPDCLASS = 62'  + '\r\n')
  text_file.write('endrun \r\n')
  text_file.close()

def make_cube_transit_damage(path, damaged_bridges):
  '''damages 4 public transit network based on the list of bridges. see the file transit_to_damage.py for more detalls. path is the destination of the damaged transit files'''
  bridge_list = [int(bridge) for bridge in damaged_bridges] #indices start at 1

  #get the data
  set_main_path('/Users/mahalia/ita/trn/transit_lines/', path) #path_to_unmodified, path_to_what_I_will_modify
  bart_dict = make_bart_dict()
  muni_dict = make_muni_dict()

  #make sure the files are clear
  clear_transit_file('Transit_Lines.block') #copies over a clean file
  clear_transit_file('BART.TPL') #copies over a clean file
  clear_transit_file('Munimetro.tpl') #copies over a clean file

  #wreak havoc
  damage_bart(bridge_list, bart_dict)
  damage_caltrain(bridge_list)
  damage_muni(bridge_list, muni_dict) 
  damage_vta(bridge_list)

def damage_highway_network(damaged_bridges, G, cube_folder_path, index):
  list_of_u_v = []
  for site in damaged_bridges:
    if float(site) <= 1743:
      affected_edges = master_dict[site]['a_b_pairs_direct'] + master_dict[site]['a_b_pairs_indirect']
      list_of_u_v += affected_edges
      for [u,v] in affected_edges:
        G[str(u)][str(v)]['t_a'] = float('inf')
        G[str(u)][str(v)]['capacity'] = 0 
        G[str(u)][str(v)]['distance'] = 20*G[str(u)][str(v)]['distance_0']
  make_cube_network_damage(cube_folder_path+'modCapacities/', list_of_u_v, index)
  return G

def damage_transit_network(damaged_bridges, cube_folder_path, index):
  make_cube_transit_damage(cube_folder_path + 'trn_staging/' + str(index) + '/', damaged_bridges)

def ground_motions(numeps, tolerance, ground_motion_filename):
  '''this function reads in some ground motion file where the first four columns have metadata (id, src_id, magnitude, weight)'''
  lnsas = []
  weights = []
  with open(ground_motion_filename, 'r') as f:
    for line in f:
      split_line = string.split(line, '\t')
      line_weight = float(string.strip(split_line[3]))
      if int(line_weight*1000) >= int(1000*(tolerance/float(numeps))):
        weights.append(line_weight)
        lnsas.append([log(float(string.strip(i))) for i in split_line[4:len(split_line)]])
  return lnsas, weights

def damage_bridges(scenario):
  '''This function damages bridges based on the ground shaking values (demand) and the structural capacity (capacity). It returns a list (could be empty) with damaged bridges'''
  damaged_bridges = []
  for site in master_dict.keys(): #should be in Matlab indices
    lnSa = scenario[master_dict[site]['new_id']-1]
    lnSa_cap = normalvariate(master_dict[site]['ext_lnSa'],0.6) #CHECK THIS
    if float(lnSa) > float(lnSa_cap):#in the extensive damage state as defined by HAZUS
      damaged_bridges.append(site)
  num_damaged_bridges = len(damaged_bridges)
  for site in master_transit_dict.keys(): #bridges 1744 to 3152
    lnSa = scenario[master_transit_dict[site]['new_id']-1]
    lnSa_cap = normalvariate(master_transit_dict[site]['ext_lnSa'],master_transit_dict[site]['beta'])
    if float(lnSa) > float(lnSa_cap):#in the extensive damage state as defined by HAZUS
      damaged_bridges.append(site)

  return damaged_bridges, num_damaged_bridges

def damage_network(damaged_bridges, G, cube_folder_path, index):
  if len(damaged_bridges) > 0:
    G = damage_highway_network(damaged_bridges, G, cube_folder_path, index)
    damage_transit_network(damaged_bridges, cube_folder_path, index)
  return G

def measure_performance(damaged_graph, damaged_bridges, demand, no_damage_travel_time, no_damage_vmt):
  # returns bridges, flow, shortest_paths, travel_time, vmt
  import time
  import pickle
  import pdb

  num_bridges_out = len(damaged_bridges)
  flow = compute_flow(damaged_graph)
  if num_bridges_out == 0:
    shortest_paths = -1
    travel_time = no_damage_travel_time
    vmt = no_damage_vmt
  else:
    shortest_paths = compute_shortest_paths(damaged_graph, demand)
    travel_time, vmt = compute_tt_vmt(damaged_graph, demand)
  # print num_bridges_out, flow, shortest_paths, travel_time, vmt
  return flow, shortest_paths, travel_time, vmt

def test(numeps, lnsas, damaged_bridges, damaged_graph, num_bridges_out, flow, shortest_paths, travel_time, vmt):

  print 'number of scenarios should equal numeps * 3909', (len(lnsas)==numeps*3909)

  print 'damaged bridges should be a list: ', len(damaged_bridges)>=0

  print 'graph should have 9635 nodes and 24404 edges: ', (len(damaged_graph.edges())==24404) and (len(damaged_graph.nodes())==9635)

  print 'we should have non-negative performance measures: ', (num_bridges_out>=0) and (flow>=0) and (shortest_paths>=0) and (travel_time>=0) and (vmt>=0)

def save_results(bridge_array, travel_index_times, numeps):
    util.write_2dlist(time.strftime("%Y%m%d")+'_bridges_flow_path_tt_vmt_bridges' + str(numeps) + 'eps_extensive.txt',travel_index_times)
    with open (time.strftime("%Y%m%d")+'_' + str(numeps) + 'eps_damagedBridges.pkl', 'wb') as f:
      pickle.dump(bridge_array, f)

def compute_performance(scenario, G, index, demand, no_damage_travel_time, no_damage_vmt):
  import time
  import pickle
  import pdb
  import networkx 
  import util
  from travel_main_simple_simplev3 import damage_bridges
  from travel_main_simple_simplev3 import measure_performance
  from travel_main_simple_simplev3 import damage_network
  start_time = time.time()

  G = networkx.read_gpickle("input/graphMTC_CentroidsLength6.gpickle")
  #figure out bridge damage for each scenario
  damaged_bridges, num_bridges_out = damage_bridges(scenario) #e.g., [1, 89, 598] #num_bridges_out is highway bridges only

  # #figure out network damage and output Cube files to this effect
  G = damage_network(damaged_bridges, G, time.strftime("%Y%m%d")+'_filesForCube/', index)

  # #figure out impact (performance metrics)
  flow, shortest_paths, travel_time, vmt = measure_performance(G, damaged_bridges, demand, no_damage_travel_time, no_damage_vmt)
  G = util.clean_up_graph(G)
  print 'total scenario time: ', time.time() - start_time
  return damaged_bridges, num_bridges_out, flow, shortest_paths, travel_time, vmt
  # return num_bridges_out

def compute_performance_test(scenario):
  return 10

def compute_performance_test2():
  return 5

def main():
  '''can change the number of epsilons below'''
  seed(0) #set seed
  simple = False  #simple is just %bridges out, which is computationally efficient
  number_of_highway_bridges = 1743
  numeps = 3 #the number of epsilons
  tol = 0.00001 #the minimum annual rate that you care about in the original event set (the weight now is the original annual rate / number of epsilons per event)
  demand = bd.build_demand('input/BATS2000_34SuperD_TripTableData.csv', 'input/superdistricts_centroids.csv') #we just take a percentage in ita.py, namely  #to get morning flows, take 5.3% of daily driver values. 11.5/(4.5*6+11.5*10+14*4+4.5*4) from Figure S10 of http://www.nature.com/srep/2012/121220/srep01001/extref/srep01001-s1.pdf
  #figure out ground motions
  # lnsas, weights = ground_motions(numeps, tol, 'input/SF2_mtc_total_3909scenarios_1743bridgesPlusBART_1epsFake.txt')
  lnsas, weights = ground_motions(numeps, tol, 'input/SF2_mtc_total_3909scenarios_1743bridgesPlusBART_3eps.txt')

  print 'first length: ', len(lnsas[0])

  bart_dict = transit_to_damage.make_bart_dict()
  muni_dict = transit_to_damage.make_muni_dict()
  transit_to_damage.set_main_path('input/trn/transit_lines/', 'input/trncopy/transit_lines/') #TODO: need to change THREE file paths (these plus bart)

  print 'the number of ground motion events we are considering: ', len(lnsas)
  index = 0
  bridge_array = []
  travel_index_times = []

  # G = nx.read_gpickle("input/graphMTC_noCentroidsLength15.gpickle")
  G = nx.read_gpickle("input/graphMTC_CentroidsLength6.gpickle")
   # Directed! only one edge between nodes
  G = nx.freeze(G) #prevents edges or nodes to be added or deleted
  print 'am I a multi graph? ', G.is_multigraph()
  no_damage_travel_time, no_damage_vmt = compute_tt_vmt(G, demand)
  if not os.path.isdir(time.strftime("%Y%m%d")+'_filesForCube/'):
    os.mkdir(time.strftime("%Y%m%d")+'_filesForCube/')
  if not os.path.isdir(time.strftime("%Y%m%d")+'_filesForCube/transit/'):
    os.mkdir(time.strftime("%Y%m%d")+'_filesForCube/transit/')
  if not os.path.isdir(time.strftime("%Y%m%d")+'_filesForCube/modCapacities/'):
    os.mkdir(time.strftime("%Y%m%d")+'_filesForCube/modCapacities/')



  # # run in SERIES
  # #---------------------------------------------
  # print 'computing features in series ...'
  # start_time = time.time()
  # for i in range(len(eqid_list)):
  #     (result, lon_temp, lat_temp) = getAllTweetFeatures(eqid_list[i], {eqid_list[i]: tweets[eqid_list[i]]}, radius)
  #     tweetFeatures = np.vstack([x for x in [tweetFeatures, result] if x.size>0])
  #     lon_meta = np.hstack([x for x in [lon_meta, lon_temp] if x.size>0])
  #     lat_meta = np.hstack([x for x in [lat_meta, lat_temp] if x.size>0])
  #     eqid_temp = np.array([eqid_list[i] for j in range(len(lon_temp))])
  #     eqid_meta = np.hstack([x for x in [eqid_meta, eqid_temp] if x.size>0])

    # for scenario in lnsas:
    # print index
    # #figure out bridge damage for each scenario
    # damaged_bridges, num_bridges_out = damage_bridges(scenario) #e.g., [1, 89, 598] #num_bridges_out is highway bridges only
    # bridge_array.append(damaged_bridges)

    # #figure out network damage and output Cube files to this effect
    # G = damage_network(damaged_bridges, G, time.strftime("%Y%m%d")+'_filesForCube/', index)

    # #figure out impact (performance metrics)
    # flow, shortest_paths, travel_time, vmt = measure_performance(G, damaged_bridges, demand, no_damage_travel_time, no_damage_vmt)
    # travel_index_times.append((index, num_bridges_out, flow, shortest_paths, travel_time, vmt, num_bridges_out/float(number_of_highway_bridges)))
    # G = util.clean_up_graph(G)
    # index +=1

    # # if index%3909 == 0:
    # if index%100 == 0:
    #   save_results(bridge_array, travel_index_times, int(index/float(3909)))

  # #---------------------------------------------

  # run in PARALLEL
  #---------------------------------------------
  ppservers = ()    
  # Creates jobserver with automatically detected number of workers
  job_server = pp.Server(ppservers=ppservers)
  print "Starting pp with", job_server.get_ncpus(), "workers"
  # compute all Tweet features in parallel
  print 'computing features ...'
  start_time = time.time()
  # set up jobs
  jobs = []
  for i in range(len(lnsas)):
    jobs.append(job_server.submit(compute_performance, (lnsas[i], 0, index, demand, no_damage_travel_time, no_damage_vmt, ), modules = ('networkx', ))) # functions, modules
    # jobs.append(job_server.submit(compute_performance_test, (lnsas[i]))) # functions, modules
    # jobs.append(job_server.submit(compute_performance_test, (lnsas[i], )))
  # get results
  if len(jobs) != len(lnsas):
    pdb.set_trace() # error checking!
  index = 0
  for job in jobs:
    (damaged_bridges, num_bridges_out, flow, shortest_paths, travel_time, vmt) = job()
    # vmt = job()
    bridge_array.append(damaged_bridges)
    travel_index_times.append((index, num_bridges_out, flow, shortest_paths, travel_time, vmt, num_bridges_out/float(number_of_highway_bridges)))
    if index%3909 == 0:
      save_results(bridge_array, travel_index_times, int(index/float(3909)))
    index += 1

  #---------------------------------------------
  save_results(bridge_array, travel_index_times, int(index/float(3909)))
  
  # test(numeps, lnsas, damaged_bridges, damaged_graph, num_bridges_out, flow, shortest_paths, travel_time, vmt)
  #save it all



if __name__ == '__main__':
  main()
