'''Author: Mahalia Miller
Date: this file takes the bridge results and then gets them ready for a run in cube'''

import pickle, string, time, pdb, os
import networkx as nx

import util
from travel_main_simple_simplev3 import damage_highway_network, damage_transit_network

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

def intize_list(my_list):
	'''takes a list where elements are strings and makes them ints if it can'''
	return [int(string.strip(s)) for s in my_list]

def post_process_bridges(bridge_list, G, index):
	counter = 0
	bridge_list_with_arcane_ids = []
	for key in master_dict.keys():
		if int(key) in bridge_list:
			counter += 1
			bridge_list_with_arcane_ids.append(str(key))

	print counter
	cube_folder_path = time.strftime("%Y%m%d")+'_filesForCube/'

	#road damage
	damage_highway_network(bridge_list_with_arcane_ids, G, cube_folder_path, index)
	#transit damage
	damage_transit_network(bridge_list, cube_folder_path, index)

def retrofit(bridge_list, holy_bridges):
	new_list = []
	for bridge in bridge_list:
		if int(bridge) not in holy_bridges:
			new_list.append(bridge)
	return new_list

def main():
	# holy_bridges = [1036, 991, 986, 483, 596,  692, 1095, 1193, 1520, 1322, 832, 1039, 1103, 1228,   663,  423,  914,  1015, 1378, 1102] #bridges for which we assume no damage. indices start at 1
	# holy_bridges = util.read_list('/Users/mahalia/Documents/matlab/research/Herbst2011/output_data/20140113_top435.txt')
	# holy_bridges = [int(b) for b in holy_bridges]
	holy_bridges = []
	print 'We are considering that this many bridges will not fail: ', len(holy_bridges)
	G = nx.read_gpickle("input/graphMTC_CentroidsLength6.gpickle")

	with open('20131212_1eps_damagedBridges2.pkl', 'rb') as f:
		bridge_array = pickle.load(f) #lists of dmaged bridges by scenario. indices start at 1 (matlab indices)

	# with open('/Users/mahalia/Documents/matlab/research/Herbst2011/output_data/20131212_25_scenario_indices_python_indices.txt', 'rb') as f:
	with open('/Users/mahalia/Documents/matlab/research/Herbst2011/output_data/20131212_25_scenario_indices_python_indices.txt', 'rb') as f:
		TODO
		scenario_indices = f.readlines()
	scenario_indices = intize_list(scenario_indices)

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


	new_bridge_array = [bridge_array[i] for i in scenario_indices]
	index = 0
	for scenario in new_bridge_array:
		if 692 in scenario:
			print 'wooooo: ', index
		retrofitted_scenario = retrofit(intize_list(scenario), holy_bridges)
		post_process_bridges(retrofitted_scenario, G, scenario_indices[index])
		index +=1



	# pdb.set_trace()

def test():
	holy_bridges = [1,2,3]
	print retrofit([1,1,5,6,7], holy_bridges)

if __name__ == '__main__':
	main()