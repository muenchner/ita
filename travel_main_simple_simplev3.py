#Author: Mahalia Miller
#Date: Jan. 21, 2013


import time, random, pickle, pdb, string, os, pp
from math import log, exp, fabs, erfc
import networkx as nx
from scipy.stats import norm
from random  import seed

import ita
import bd
import util
from transit_to_damage import make_bart_dict, make_muni_dict, clear_transit_file, damage_bart, damage_caltrain, damage_muni, damage_vta, set_main_path
import transit_to_damage
from get_praveen_results import get_praveen_results
from groundTruthHazardjwb import QuakeMaps

#get bridge information

#first load the all-purpose dictionary linking info about the bridges
with open('input/20130114_master_bridge_dict.pkl','rb') as f:
  master_dict = pickle.load(f) #has 1743 keys. One per highway bridge. (NOT BART)
  '''
  dict with a bridge_key that ranges from 1 to 1889 and then the value is another dictionary with the following keys: 
    loren_row_number: the row number in Loren Turner's table that has info on all CA bridges (where the header line is row 0)
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
with open('input/20140114_master_transit_dict.pkl','rb') as f:
  master_transit_dict = pickle.load(f) #the keys go from 17440 to 31520 One per BART structure. The new_id values go from 1744 to 3152!!
# master_transit_dict = {}
# with open('input/id_mod_ext_com_beta.csv', 'rb') as f:
#   for line in f:
#     print line
#     tokens = string.split(line, ',')
#     print tokens
#     master_transit_dict[str(int(tokens[0])+10000)] = {'mod_lnSa': float(tokens[1])/100.0, 'ext_lnSa': float(tokens[2])/100.0, 'com_lnSa': float(tokens[3])/100.0, 'new_id': int(tokens[0]), 'beta': float(tokens[4])}
#     print master_transit_dict[str(int(tokens[0])+10000)]
# with open ('input/20140114_master_transit_dict.pkl', 'wb') as f:
#   pickle.dump(master_transit_dict, f)


def compute_flow(damaged_graph):

  s= 'sf'
  t = 'oak'
  try:
    flow = nx.max_flow(damaged_graph, s, t, capacity='capacity') #not supported by multigraph
  except nx.exception.NetworkXError as e:
    print 'found an ERROR: ', e
    flow = -1
    print s in damaged_graph
    print t in damaged_graph
    print len(damaged_graph.nodes())
    print len(damaged_graph.edges())
    pdb.set_trace()
  return flow

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
  vmt = util.find_vmt(damaged_graph)  
  ''' in the undamaged case, this should be around 172 million (http://www.mtc.ca.gov/maps_and_data/datamart/stats/vmt.htm) over the course of a day, so divide by 0.053 (see demand note in main). BUT our trip table has only around 11 million trips (instead of the 22 million mentioned here: http://www.mtc.ca.gov/maps_and_data/datamart/stats/baydemo.htmSo, that's **8-9 million vehicle-miles divided by 2, which equals around 4 million vehicle-miles!**
 

  '''
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

def make_cube_transit_damage(path, damaged_bridges_new):
  '''damages 4 public transit network based on the list of bridges. see the file transit_to_damage.py for more detalls. path is the destination of the damaged transit files. damaged bridges has the new ids (1-1743, 1744-3152'''
  try:
    if len(damaged_bridges_new) > 0:
      b = damaged_bridges_new[0]/10
  except TypeError:
    raise('Sorry. You must use the new ids, which are all numbers, not strings')
  #get the data
  set_main_path('/Users/mahalia/ita/trn/transit_lines/', path) #path_to_unmodified, path_to_what_I_will_modify
  bart_dict = make_bart_dict()
  muni_dict = make_muni_dict()

  #make sure the files are clear
  clear_transit_file('Transit_Lines.block') #copies over a clean file
  clear_transit_file('BART.TPL') #copies over a clean file
  clear_transit_file('Munimetro.tpl') #copies over a clean file

  #wreak havoc
  damage_bart(damaged_bridges_new, bart_dict)
  damage_caltrain(damaged_bridges_new)
  damage_muni(damaged_bridges_new, muni_dict) 
  damage_vta(damaged_bridges_new)

def damage_highway_network(damaged_bridges_internal, G, cube_folder_path, index):
  '''damaged bridges is a list of the original ids (1-1889, not the new ids 1-1743!!!!!!!) plus the transit ones (17440-315200)'''
  try:
    if len(damaged_bridges_internal) > 0:
      b = damaged_bridges_internal[0].lower()
  except AttributeError:
    raise('Sorry. You must use the original ids, which are strings')
  list_of_u_v = []
  counter = 0
  for site in damaged_bridges_internal:
    if int(site) <= 1889: #in original ids, not new ones since that is what is in the damaged bridges list
      affected_edges = master_dict[site]['a_b_pairs_direct'] + master_dict[site]['a_b_pairs_indirect']
      list_of_u_v += affected_edges
      for [u,v] in affected_edges:
        G[str(u)][str(v)]['t_a'] = float('inf')
        G[str(u)][str(v)]['capacity'] = 0 
        G[str(u)][str(v)]['distance'] = 20*G[str(u)][str(v)]['distance_0']
        counter += 1
  # assert counter >= len(damaged_bridges_internal), 'we should impact an edge per bridge minimum'
  # make_cube_network_damage(cube_folder_path+'modCapacities/', list_of_u_v, index)
  return G

def damage_transit_network(damaged_bridges_new, cube_folder_path, index):
  '''damaged bridges is a list of the new ids 1-1743!!!!!!!) plus the transit ones (1744-3152)'''
  try:
    if len(damaged_bridges_new) > 0:
      b = damaged_bridges_new[0]/10
  except TypeError:
    raise('Sorry. You must use the new ids, which are all numbers, not strings')
  make_cube_transit_damage(cube_folder_path + 'trn_staging/' + str(index) + '/', damaged_bridges_new)

def ground_motions(numeps, tolerance, ground_motion_filename):
  '''this function reads in some ground motion file where the first four columns have metadata (id, src_id, magnitude, weight)'''
  lnsas = []
  weights = []
  magnitudes = []
  with open(ground_motion_filename, 'r') as f:
    for line in f:
      split_line = string.split(line, '\t')
      line_weight = float(string.strip(split_line[3]))
      if int(line_weight*1000) >= int(1000*(tolerance/float(numeps))):
        weights.append(line_weight)
        lnsas.append([log(float(string.strip(i))) for i in split_line[4:len(split_line)]])
        magnitudes.append(float(string.strip(split_line[2])))
  return lnsas, weights, magnitudes

def damage_bridges(scenario):
  '''This function damages bridges based on the ground shaking values (demand) and the structural capacity (capacity). It returns two lists (could be empty) with damaged bridges (same thing, just different bridge numbering'''
  damaged_bridges_new = []
  damaged_bridges_internal = []
  counter = 0

  #first, highway bridges and overpasses
  beta = 0.6
  for site in master_dict.keys(): #1-1889 in Matlab indices (start at 1)
    lnSa = scenario[master_dict[site]['new_id'] - 1]
    if lnSa > master_dict[site]['ext_lnSa']:
      counter+=1
    # print site
    # print lnSa
    # print log(master_dict[site]['ext_lnSa'])
    prob_at_least_ext = norm.cdf((1/float(beta)) * (lnSa - log(master_dict[site]['ext_lnSa'])), 0, 1)
    U = random.uniform(0, 1)
    if U <= prob_at_least_ext:
      damaged_bridges_new.append(master_dict[site]['new_id']) #1-1743
      damaged_bridges_internal.append(site) #1-1889
      # print 'U: ', U
      # print 'cap:  ', master_dict[site]['ext_lnSa']
      # print 'that should be smaller than the Sa: ', exp(lnSa)
      # print 'at prob: ', prob_at_least_ext
  num_damaged_bridges = len(damaged_bridges_new)

  #now on to bart
  for site in master_transit_dict.keys():
    lnSa = scenario[master_transit_dict[site]['new_id'] - 1]
    prob_at_least_ext_t = norm.cdf((1/float(master_transit_dict[site]['beta'])) * (lnSa - log(master_transit_dict[site]['ext_lnSa'])), 0, 1)
    U = random.uniform(0, 1)
    if U <= prob_at_least_ext_t:
      damaged_bridges_new.append(master_transit_dict[site]['new_id'])
      damaged_bridges_internal.append(site)
  # pdb.set_trace()
  # print 'counter says: ', counter
  return damaged_bridges_internal, damaged_bridges_new, num_damaged_bridges

def damage_network(damaged_bridges_internal, damaged_bridges_new, G, cube_folder_path, index):
  '''damaged bridges is a list of the original ids (1-1889, not the new ids 1-1743!!!!!!!)'''
  if len(damaged_bridges_internal) > 0:
    make_directories([index])
    G = damage_highway_network(damaged_bridges_internal, G, cube_folder_path, index)
    # damage_transit_network(damaged_bridges_new, cube_folder_path, index) 
  return G

def measure_performance(damaged_graph, num_damaged_bridges, demand, no_damage_travel_time, no_damage_vmt):
  # returns flow, shortest_paths, travel_time, vmt
  import time
  import pickle
  import pdb
  
  if num_damaged_bridges == 0:
    flow = 18300
    shortest_paths = -1
    travel_time = no_damage_travel_time
    vmt = no_damage_vmt
  else:
    flow = compute_flow(damaged_graph)
    shortest_paths = compute_shortest_paths(damaged_graph, demand)
    travel_time, vmt = compute_tt_vmt(damaged_graph, demand)
  return flow, shortest_paths, travel_time, vmt

def test_big(numeps, lnsas, damaged_bridges, damaged_graph, num_bridges_out, flow, shortest_paths, travel_time, vmt):
  assert len(lnsas)==numeps*3909, 'number of scenarios should equal numeps * 3909'
  assert len(damaged_bridges)>=0, 'number of scenarios should equal numeps * 3909'
  assert (len(damaged_graph.edges())==24404) and (len(damaged_graph.nodes())==9635), 'graph should have 9635 nodes and 24404 edges '
  assert (num_bridges_out>=0) and (flow>=0) and (shortest_paths>=0) and (travel_time>=0) and (vmt>=0), 'we should have non-negative performance measures: '

def save_results(bridge_array_internal, bridge_array_new, travel_index_times, numeps):
    util.write_2dlist(time.strftime("%Y%m%d")+'_bridges_flow_path_tt_vmt_bridges' + str(numeps) + 'eps_extensive2.txt',travel_index_times)
    with open (time.strftime("%Y%m%d")+'_' + str(numeps) + 'eps_damagedBridgesInternal2.pkl', 'wb') as f:
      pickle.dump(bridge_array_internal, f)
    with open (time.strftime("%Y%m%d")+'_' + str(numeps) + 'eps_damagedBridgesNewID2.pkl', 'wb') as f:
      pickle.dump(bridge_array_new, f)

def compute_performance(scenario, G, index, demand, no_damage_travel_time, no_damage_vmt):
  import time
  import pickle
  import pdb
  import networkx 
  import util
  from travel_main_simple_simplev3 import damage_bridges
  from travel_main_simple_simplev3 import measure_performance
  from travel_main_simple_simplev3 import damage_network
  from travel_main_simple_simplev3 import get_graph
  start_time = time.time()

  if G == None:
    G = get_graph()

  #figure out bridge damage for each scenario
  damaged_bridges_internal, damaged_bridges_new, num_damaged_bridges = damage_bridges(scenario) #e.g., [1, 89, 598] #num_bridges_out is highway bridges only

  # #figure out network damage and output Cube files to this effect
  G = damage_network(damaged_bridges_internal, damaged_bridges_new, G, time.strftime("%Y%m%d")+'_filesForCube/', index)

  # #figure out impact (performance metrics)
  flow, shortest_paths, travel_time, vmt = measure_performance(G, num_damaged_bridges, demand, no_damage_travel_time, no_damage_vmt)
  G = util.clean_up_graph(G)
  print 'total scenario time: ', time.time() - start_time
  return damaged_bridges_internal, damaged_bridges_new, num_damaged_bridges, flow, shortest_paths, travel_time, vmt

def make_directories(scenario_indices):
  #make directories for these scenarios
  #input (transit). In one transit (trn) folder, I'll have a bunch of folders for different scenarios and then I can just copy over the three relevant files before each simulation (transit_lines.block, bart.tpl, muni.tpl)
  if not os.path.isdir(time.strftime("%Y%m%d")+'_filesForCube/'):
    os.mkdir(time.strftime("%Y%m%d")+'_filesForCube/')  

  if not os.path.isdir(time.strftime("%Y%m%d")+'_filesForCube/trn_staging/'):
    os.mkdir(time.strftime("%Y%m%d")+'_filesForCube/trn_staging/')  

  if not os.path.isdir(time.strftime("%Y%m%d")+'_filesForCube/modCapacities/'):
    os.mkdir(time.strftime("%Y%m%d")+'_filesForCube/modCapacities/')

  #output
  if not os.path.isdir(time.strftime("%Y%m%d")+'_filesForCube/aa_new/'):
    os.mkdir(time.strftime("%Y%m%d")+'_filesForCube/aa_new/')

  for scenario in scenario_indices:
    #still input
    if not os.path.isdir(time.strftime("%Y%m%d") + '_filesForCube/trn_staging/' + str(scenario) + '/'):
        os.mkdir(time.strftime("%Y%m%d") + '_filesForCube/trn_staging/' + str(scenario) + '/')

    #output
    if not os.path.isdir(time.strftime("%Y%m%d") + '_filesForCube/aa_new/' + str(scenario) + '/'):
        os.mkdir(time.strftime("%Y%m%d") + '_filesForCube/aa_new/' + str(scenario) + '/')

def add_superdistrict_centroids(G):
  '''adds 34 dummy nodes for superdistricts'''
  sd_table = util.read_2dlist('input/superdistricts_clean.csv', ',', False)
  for row in sd_table:
    i = int(row[0])
    G.add_node(str(1000000 + i))
    G.add_edge(str(1000000 + i), str(row[1]), capacity_0 = 100000,  capacity = 100000, lanes =1 , bridges=[], distance_0=1, distance = 1, t_a=1, t_0=1, flow=0, dailyvolume=1) #capacity in vehicles over all lanes, travel time in seconds, length in miles, flow in 
    G.add_edge(str(1000000 + i), str(row[2]), capacity_0 = 100000,  capacity = 100000, lanes =1 , bridges=[], distance_0=1, distance = 1, t_a=1, t_0=1, flow=0, dailyvolume=1) #capacity in vehicles over all lanes, travel time in seconds, length in miles, flow in 
    G.add_edge(str(row[3]), str(1000000 + i), capacity_0 = 100000,  capacity = 100000, lanes =1 , bridges=[], distance_0=1, distance = 1, t_a=1, t_0=1, flow=0, dailyvolume=1) #capacity in vehicles over all lanes, travel time in seconds, length in miles, flow in 
    G.add_edge(str(row[4]), str(1000000 + i), capacity_0 = 100000,  capacity = 100000, lanes =1 , bridges=[], distance_0=1, distance = 1, t_a=1, t_0=1, flow=0, dailyvolume=1) #capacity in vehicles over all lanes, travel time in seconds, length in miles, flow in 

  #add a sf dummy node and an oakland dummy node for max flow
  G.add_node('sf')
  G.add_node('oak')
  G.add_edge('sf', '1000001', capacity_0 = 100000,  capacity = 100000, lanes =1 , bridges=[], distance_0=1, distance = 1, t_a=1, t_0=1, flow=0, dailyvolume=1) #capacity in vehicles over all lanes, travel time in seconds, length in miles, flow in 
  G.add_edge('sf', '1000002', capacity_0 = 100000,  capacity = 100000, lanes =1 , bridges=[], distance_0=1, distance = 1, t_a=1, t_0=1, flow=0, dailyvolume=1) #capacity in vehicles over all lanes, travel time in seconds, length in miles, flow in 
  G.add_edge('sf', '1000003', capacity_0 = 100000,  capacity = 100000, lanes =1 , bridges=[], distance_0=1, distance = 1, t_a=1, t_0=1, flow=0, dailyvolume=1) #capacity in vehicles over all lanes, travel time in seconds, length in miles, flow in 
  G.add_edge('sf', '1000004', capacity_0 = 100000,  capacity = 100000, lanes =1 , bridges=[], distance_0=1, distance = 1, t_a=1, t_0=1, flow=0, dailyvolume=1) #capacity in vehicles over all lanes, travel time in seconds, length in miles, flow in 
  G.add_edge('sf', '1000005', capacity_0 = 100000,  capacity = 100000, lanes =1 , bridges=[], distance_0=1, distance = 1, t_a=1, t_0=1, flow=0, dailyvolume=1) #capacity in vehicles over all lanes, travel time in seconds, length in miles, flow in 
  G.add_edge('1000018', 'oak', capacity_0 = 100000,  capacity = 100000, lanes =1 , bridges=[], distance_0=1, distance = 1, t_a=1, t_0=1, flow=0, dailyvolume=1) #capacity in vehicles over all lanes, travel time in seconds, length in miles, flow in 
  G.add_edge('1000019', 'oak', capacity_0 = 100000,  capacity = 100000, lanes =1 , bridges=[], distance_0=1, distance = 1, t_a=1, t_0=1, flow=0, dailyvolume=1) #capacity in vehicles over all lanes, travel time in seconds, length in miles, flow in 
  G.add_edge('1000020', 'oak', capacity_0 = 100000,  capacity = 100000, lanes =1 , bridges=[], distance_0=1, distance = 1, t_a=1, t_0=1, flow=0, dailyvolume=1) #capacity in vehicles over all lanes, travel time in seconds, length in miles, flow in 

  return G

def get_graph():
  import networkx
  '''loads full mtc highway graph with dummy links and then adds a few fake centroidal nodes for max flow and traffic assignment'''
  G = networkx.read_gpickle("input/graphMTC_CentroidsLength3int.gpickle")
  G = add_superdistrict_centroids(G)
   # Directed! only one edge between nodes
  G = nx.freeze(G) #prevents edges or nodes to be added or deleted
  return G

def main():
  '''can change the number of epsilons below'''
  seed(0) #set seed 
  simple = False  #simple is just %bridges out, which is computationally efficient
  number_of_highway_bridges = 1743
  numeps = 3 #the number of epsilons
  tol = 0.00001 #the minimum annual rate that you care about in the original event set (the weight now is the original annual rate / number of epsilons per event)
  demand = bd.build_demand('input/BATS2000_34SuperD_TripTableData.csv', 'input/superdistricts_centroids_dummies.csv') #we just take a percentage in ita.py, namely  #to get morning flows, take 5.3% of daily driver values. 11.5/(4.5*6+11.5*10+14*4+4.5*4) from Figure S10 of http://www.nature.com/srep/2012/121220/srep01001/extref/srep01001-s1.pdf
  #figure out ground motions
  # lnsas, weights = ground_motions(numeps, tol, 'input/SF2_mtc_total_3909scenarios_1743bridgesPlusBART_1epsFake.txt')
  lnsas, weights, magnitudes = ground_motions(numeps, tol, 'input/SF2_mtc_total_3909scenarios_1743bridgesPlusBART_3eps.txt')
  # with open ('input/20140114_lnsas_1epsFake.pkl', 'wb') as f:
  #   pickle.dump(lnsas, f)
  with open ('input/20140114_magnitudes_3eps.pkl', 'wb') as f:
    pickle.dump(magnitudes, f)
  with open('input/20140114_lnsas_3eps.pkl','rb') as f:
    lnsas = pickle.load(f)
  # with open('input/20140114_lnsas_1epsFake.pkl','rb') as f:
  #   lnsas = pickle.load(f)
  print 'the number of ground motion events we are considering: ', len(lnsas)
  print 'first length: ', len(lnsas[0])

  bart_dict = transit_to_damage.make_bart_dict()
  muni_dict = transit_to_damage.make_muni_dict()

  bridge_array_new = []
  bridge_array_internal = []
  travel_index_times = []
  # G = nx.read_gpickle("input/graphMTC_noCentroidsLength15.gpickle")
  G = get_graph()

  print 'am I a multi graph? I really do not want to be!', G.is_multigraph() #An undirected graph class that can store multiedges. Multiedges are multiple edges between two nodes. Each edge can hold optional data or attributes.A MultiGraph holds undirected edges. Self loops are allowed.
  no_damage_travel_time, no_damage_vmt = compute_tt_vmt(G, demand)
  G = util.clean_up_graph(G)
  # make_directories(range(len(lnsas)))
  # transit_to_damage.set_main_path('input/trn/transit_lines/', 'input/trncopy/transit_lines/') #TODO: need to change THREE file paths (these plus bart)

  # run in SERIES
  #---------------------------------------------
  # targets = [0, 5000]
  # # targets = range(len(lnsas))
  # for i in targets:
  #   print i
  #   start = time.time()
  #   damaged_bridges_internal, damaged_bridges_new, num_damaged_bridges, flow, shortest_paths, travel_time, vmt = compute_performance(lnsas[i], G, i, demand, no_damage_travel_time, no_damage_vmt)
  #   bridge_array_internal.append(damaged_bridges_internal)
  #   bridge_array_new.append(damaged_bridges_new)
  #   travel_index_times.append((i, num_damaged_bridges, flow, shortest_paths, travel_time, vmt, num_damaged_bridges/float(number_of_highway_bridges), magnitudes[i]))
  #   print 'time for one: ', time.time() - start
  #   if i%3909 == 0:
      # save_results(bridge_array_internal, bridge_array_new, travel_index_times, int((i + 1)/float(3909)))
  
  #   # scenario = lnsas[i]
  #   # #figure out bridge damage for each scenario
  #   # damaged_bridges_internal, damaged_bridges_new, num_damaged_bridges = damage_bridges(scenario) #e.g., [1, 89, 598] #num_bridges_out is highway bridges only
  #   # bridge_array_internal.append(damaged_bridges_internal)
  #   # bridge_array_new.append(damaged_bridges_new)

  #   # #figure out network damage and output Cube files to this effect
  #   # G = damage_network(damaged_bridges_internal, damaged_bridges_new, G, time.strftime("%Y%m%d")+'_filesForCube/', i)

  #   # #figure out impact (performance metrics)
  #   # flow, shortest_paths, travel_time, vmt = measure_performance(G, num_damaged_bridges, demand, no_damage_travel_time, no_damage_vmt)
  #   # travel_index_times.append((i, num_damaged_bridges, flow, shortest_paths, travel_time, vmt, num_damaged_bridges/float(number_of_highway_bridges), magnitudes[i]))
  #   # G = util.clean_up_graph(G)
  #   # # if i%3909 == 0:
  #   # if i%1 == 0:
  #   #   save_results(bridge_array_internal, bridge_array_new, travel_index_times, int(i/float(3909)))

  # # #---------------------------------------------

  # # # run in PARALLEL
  # # # #---------------------------------------------
  ppservers = ()    
  # Creates jobserver with automatically detected number of workers
  job_server = pp.Server(ppservers=ppservers)
  print "Starting pp with", job_server.get_ncpus(), "workers"
  start_time = time.time()
  # set up jobs
  jobs = []
  targets = range(3909, len(lnsas)) #len(lnsas)) 7818, 
  # targets = [0, 33, 5000]
  # for i in range(len(lnsas)):
  for i in targets:
    jobs.append(job_server.submit(compute_performance, (lnsas[i], None, i, demand, no_damage_travel_time, no_damage_vmt, ), modules = ('networkx', ))) # functions, modules
  # get results
  # if len(jobs) != len(lnsas):
  #   pdb.set_trace() # error checking!
  index = 0
  for job in jobs:
    (damaged_bridges_internal, damaged_bridges_new, num_damaged_bridges, flow, shortest_paths, travel_time, vmt) = job()
    i = targets[index]
    print 'target id: ', i
    bridge_array_internal.append(damaged_bridges_internal)
    bridge_array_new.append(damaged_bridges_new)
    travel_index_times.append((i, num_damaged_bridges, flow, shortest_paths, travel_time, vmt, num_damaged_bridges/float(number_of_highway_bridges), magnitudes[i]))
    if i%3909 == 0:
      save_results(bridge_array_internal, bridge_array_new, travel_index_times, int((i + 1)/float(3909)))
    index += 1

  # #---------------------------------------------
  save_results(bridge_array_internal, bridge_array_new, travel_index_times, int((i + 1)/float(3909)))
  
  # test_big(numeps, lnsas, damaged_bridges_internal, damaged_graph, num_damaged_bridges, flow, shortest_paths, travel_time, vmt)

def test():
  scenario = [log(1.2), log(10), log(0.01), log(1)]

  global master_transit_dict
  global master_dict
  master_dict = {}
  master_transit_dict = {}
  master_dict['1'] = {'new_id': 1, 'ext_lnSa': 0.8}
  master_dict['12'] = {'new_id': 2, 'ext_lnSa': 0.8}
  master_dict['13'] = {'new_id': 3, 'ext_lnSa': 0.8}
  master_transit_dict['13'] = {'new_id': 4, 'beta': 1, 'ext_lnSa': 1.6}

  for thing in range(50):
    br_int, br, num = damage_bridges(scenario)
    print 'bridges out in terms of new ids: ', br
    assert len(br) >= 1, 'at least one bridge should fail'
    assert len(br) <= 3, 'no more than 3 bridges fail'
  print 'now let us try to test if we change the capacity, it fails'
  master_dict['13']['ext_lnSa'] = 0.001
  br_int, br, num = damage_bridges(scenario)
  assert 3 in br, 'now that bridge new id 3 has almost no structural demand capacity, it should fail'
  G = nx.read_gpickle("input/graphMTC_CentroidsLength6int.gpickle")
  num_nodes = len(G.nodes())
  G = add_superdistrict_centroids(G)
  assert len(G.nodes()) == 34 + 2 + num_nodes, 'nodes should have changed'
  print compute_flow(G)
  # test_big(numeps, lnsas, damaged_bridges, damaged_graph, num_bridges_out, flow, shortest_paths, travel_time, vmt)
if __name__ == '__main__':
  main()
