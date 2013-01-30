#Author: Mahalia Miller
#Date: Jan 30, 2013

from groundTruthHazardjwb import QuakeMaps

'''This is a hack code that just returns the scenario numbers (0-4992) that are in the specified subset, which was chosen by mixed-integer optimization running on Praveen's computer using zibopt based on Han and Davidson 2012'''


def get_praveen_results(lnsas):
  num_sites = len(lnsas)
  scenarios = [] #scenario numbers (0-4992) that are in the specified subset
#  #subset with 12 centroid sites and 4993 ground motion maps
  pkl_file = open('20120919subset12_20_500ok.pkl','rb')#20120831subset10_4_200.pkl', 'rb') #CHANGE THIS
  subset = pickle.load(pkl_file)
  pkl_file.close()
  pkl_file = open('20120919weight12_20_500ok.pkl','rb')#20120831weight10_4_200.pkl', 'rb') #CHANGE THIS
  weights = pickle.load(pkl_file)
  pkl_file.close()
#  yir_table_filename = '20120917_mtc_log_Y_ir_table_R50.pkl' #'20120912_mtc_log_Y_ir_table_R13.pkl'#'20120820_mtc_log_Y_ir_table.pkl'#'20120907_mtc_log_Y_ir_table_R20.pkl'#'20120820_mtc_log_Y_ir_table.pkl'#'20120907_mtc_log_Y_ir_table_R2.pkl' #'20120905_mtc_log_Y_ir_table.pkl' #13 return periods, 1557 sites #CHANGE THIS
  return_periods = [100.0, 107.0, 114.0, 122.0, 130.0, 139.0, 148.0, 158.0, 169.0, 181.0, 193.0, 206.0, 220.0, 235.0, 251.0, 268.0, 286.0, 305.0, 326.0, 348.0, 372.0, 397.0, 424.0, 453.0, 484.0, 517.0, 552.0, 589.0, 629.0, 672.0, 718.0, 766.0, 818.0, 874.0, 933.0, 997.0, 1064.0, 1137.0, 1214.0, 1296.0, 1384.0, 1478.0, 1579.0, 1686.0, 1800.0, 1922.0, 2053.0, 2192.0, 2341.0, 2500.0] #50 return periods equally spaced in base 10 log space between 100 and 2500 years
  J_red = 0
  for index in range(len(subset)):
    if (subset[index] < 1.05) and (subset[index] > 0.95) and (weights[index] >0.00001):#0): #this map is part of subset
      J_red += 1
      print 1
    else:
      print 0
  for i in range(4993-4993): #1394):
    subset+=[0]
    weights+=[0]
  #print subset  
#  J_red = int(sum(subset))
  print 'J_red: ', J_red
  print 'vs sum of subset is: ', sum(subset)
  print 'and length of subset vector: ', len(subset)
#  
  lnsas_subset = [ [0 for i in range(num_sites)] for j in range(J_red) ] #just initializes list of lists of 0s
  weights_subset = [ [0] for j in range(J_red) ] #list of 0s
  if len(subset)!=len(lnsas):
    print 'yo. You do not have the right number of entries in your subset list.'
    print len(subset)
    print len(lnsas)
  else:
    counter = 0 #counter for subset of maps
    good = 0
    for index in range(len(subset)):
      if (subset[index] < 1.05) and (subset[index] > 0.95): #this map is part of subset
  #  print 'index: ', index
        weight = weights[index]
    #print 'weight*10,000: ', weight*10000
        if (weight <=  0.00001):# or (q.weights[index] <=  0.00001):#<= 0):
          pass
        else:
          good += 1
          lnsas_subset[counter]=lnsas[index]
          weights_subset[counter] = weights[index]
          counter = counter+1
          scenarios.append(index)
    print 'len before removing blacklist: ', len(lnsas_subset)
    black_list = [24, 25, 26, 144, 145, 146, 147, 180, 181, 182, 183, 184, 185] #far away scenarios with index ranging from 0 to 206
    #remove elements at indices of black list
    for index in black_list:
      del lnsas_subset[index]
      del weights_subset[index]
    print 'len of scenarios in scenario list before: ', len(scenarios)
    for scenario in scenarios:
      bad = False #in blacklist
      for item in black_list:
        if scenario == item:
          bad = True
      if bad == False:
        new_scenarios.append(scenario)
   # new_scenarios = [scenario in scenarios if scenario is not in black_list]
    print 'len of scenarios in scenario list after: ', len(new_scenarios)

    print 'len after removing blacklist: ', len(lnsas_subset)
    print 'len after removing blacklist: ', len(weights_subset)   
    lnsas_subset_new = [lnsas_subset[i] for i in range(len(lnsas_subset)) if weights_subset[i] > 0.00001] 
    weights_subset_new = [weights_subset[i] for i in range(len(lnsas_subset)) if weights_subset[i] > 0.00001] 
    lnsas_subset = lnsas_subset_new
    weights_subset = weights_subset_new
          
    print 'num sites in main: ', len(lnsas[0])
#    print 'number of sites (I): ', len(python_indices)

    print 'number of maps in subset: ', len(lnsas_subset)
    print 'number of maps with non-zero weight: ', good

    print weights_subset
    print 'weight subset: ', sum(weights_subset)
    print 'number of maps in subset now: ', len(lnsas_subset)
if __name__ == '__main__':
  q = QuakeMaps('input/20130107_mtc_total_lnsas1.pkl', 'input/20130107_mtc_magnitudes1.pkl', 'input/20130107_mtc_faults1.pkl', 'input/20130107_mtc_weights1.pkl', 'input/20130107_mtc_scenarios1.pkl') #totalfilename=None, magfilename=None, faultfilename=None, weightsfilename=None, scenariofilename=None):
  num_sites = len(lnsas[0])
 
  get_praveen_results(q.lnsas)  
