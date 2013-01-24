#!/usr/bin/python2.7
'''
Created on Aug 9, 2012

@author: mahalia
This function finds the hazard curves for each site based on the full Monte Carlo suite of ground motion maps. These should be comparable to the hazard curves for each site based on PSHA.
The result is a pickled dictionary where the keys are the bridgeIDs and the values are a list of exceedance probabilities for a specified list of Sa(T=1s).
'''
import time, string, pickle
from math import log, exp, fabs
from numpy import random,argsort,sqrt, array

def knn_search(x, D, K):
    """ find K nearest neighbours of data among D """
    ndata = D.shape[1]
    K = K if K < ndata else ndata
    # euclidean distances from the other points
    sqd = sqrt(((D - x[:,:ndata])**2).sum(axis=0))
    idx = argsort(sqd) # sorting
    # return the indexes of K nearest neighbours
    return idx[:K]

def find_weight(Y_ir, hazard_dict_for_one_i):
    #finds the next highest Sa value (Y) for a given target, Y_ir from the hazard dict for one site and returns its weight
    index = 0
    hit_end_boolean = False
    while hazard_dict_for_one_i[index][0]<Y_ir:
        if index<(len(hazard_dict_for_one_i)-1):
            index += 1
        else:
            Y_ir = -1000
            hit_end_boolean = True
        #print 'hit top of hazard dict'
    if hit_end_boolean is True:
           weight_final = 0
    else:
           weight_final = hazard_dict_for_one_i[index][1]
#    print 'weight final: ', weight_final
    return weight_final

def find_Y_hat_ir(return_period, hazard_dict_for_one_i):
    #finds the next highest Sa value (Y) for a given target, Y_ir from the hazard dict for one site
    index = 0
   # print 'target prob: ', 1/float(return_period)
    while hazard_dict_for_one_i[index][1]>(1/float(return_period)):
           if index<(len(hazard_dict_for_one_i)-1):
                  index += 1
        #print hazard_dict_for_one_i[index][1]

           else:
        #print 'hit top of hazard dict in y hat so just going to choose the highest Sa value'
        #print 'for site: ', i    
               return_period = 1
    sa_final = hazard_dict_for_one_i[index][0]
#    print 'sa final: ', sa_final
   # print 'weight final: ', hazard_dict_for_one_i[index][1]
    return sa_final

class HazardDict(object):

    def __init__(self, filename=None):
        self.hazard_dict = {}
    
        
    def populate_hazard_dict(self, lnsas, weights, num_sites, true_total_weights=None):
        #creates dictionary where key=site and value=list with tuples where the first entry is P(Sa>x) and the second entry is the x
        #required that the sum of weights is the probability of an earthquake in the desired time period, even if using a subset of scenarios
        total_weights = 0
        other_total_weights = sum(weights)
        num_quakes = len(weights)
        #initialize hazard dict
        for site in range(0, num_sites):
            self.hazard_dict[site] = [(0,0)]*len(lnsas)
#        print 'number of earthquake scenarios ', num_quakes
#        print 'sets of the earthquake scenario suite: ', len(lnsas)/float(num_quakes)
        sets = len(lnsas)/float(num_quakes)
        if sets%1.0 == 0: #check we are doing a whole number of earthquake scenario suites
            weights = weights*int(sets)
            print 'length of duplicated weights: ', len(weights)
            print 'length of lnsas: ', len(lnsas)
            print 'sets using: ', sets
            tic = time.time()
            for site in range(num_sites):
                lnsas_i = [lnsas[j_map][site] for j_map in range(len(lnsas))]
            #print 'length of the lnsas for a given site i: ', len(lnsas_i)
    
                #pair up the lnsa realizations with the associated weight
                x_tuples = [(lnsas_i[j], weights[j]) for j in range(len(lnsas_i))]
    
                #sort the lnsa in ascending order (small to big)
                c1 = sorted(x_tuples,key=lambda lnsaPair: lnsaPair[0])
                weights_this_site = [pair[1] for pair in c1] #extracts the second element of each pair. This is important since the assigned variable isn't writing over "weights".
                total_prob = sum(weights_this_site)
 #               print 'annual probability of an earthquake: ', total_prob
                c1 = [pair[0] for pair in c1] #extracts the first element, which is x, the Sa value
    
                #get cumulative sums of the weights to find c2, the P(Sa>x)
                weights_this_site = weights_this_site[::-1] #reverse order
                c2 = [0]*len(weights_this_site)
                for weight_index in range(1, 1 + len(weights_this_site)):
                    c2[weight_index-1] = sum(weights_this_site[0:weight_index])
                c2 = c2[::-1] #reverse order back 
    
                #now, populate the hazard dict appropriately
                self.hazard_dict[site] = [(c1[i], c2[i]) for i in range(len(c1))] #(x, P(Sa>x) )
        
        else:
            print 'we are using a number of ground motion maps that is not a whole multiple of the number of earthquake scenarios'
                       
    def pickle_hazard_dict(self, filename=None):
        pkl_file = open(filename, 'wb')
        pickle.dump(self.hazard_dict, pkl_file)
        pkl_file.close()
            
    def unpickle_hazard_dict(self, filename=None):
        pkl_file  = open(filename, 'rb')
        self.hazard_dict = pickle.load(pkl_file)
        pkl_file.close()
        
    def print_hazard_dict(self):
        print self.hazard_dict


    def compute_MHCE(self, yir_table_filename, return_periods, python_site_indices=None):
    #computes the mean hazard curve error according to han and davidson. 
    #Inputs: 
    #    yir_table_filename: a filename of a table created by the script computepjir.py
    #    python_site_indices: the indices of the sites for which you want to compute the error.
        pkl_file = open(yir_table_filename,'rb') 
        yir_table = pickle.load(pkl_file)
        pkl_file.close()
        if python_site_indices is None:
            python_site_indices = range(len(yir_table))
        hce = 0 #initialize
        R = len(yir_table[0]) #number of return periods
        print 'using '+str(R)+' return periods, and I am inputting '+str(len(return_periods))
        I = len(python_site_indices) #number of sites
        print 'using '+str(I)+' sites'
         
    #loop over sites and return periods to compute the hazard curve error
        for i in python_site_indices:
            #L = [(item[0], 3*item[1]) for item in self.hazard_dict[i]] #hd.hazard_dict[i] #these are probabilities of exceedance
        
            for r_index in range(len(return_periods)):
                r = return_periods[r_index]
#                print i
#                print r
#                print 'yir: ', exp(yir_table[i][r_index])
#                print 'and other: ', self.hazard_dict[i]
                hce += fabs((exp(yir_table[i][r_index])- exp(find_Y_hat_ir(r, self.hazard_dict[i])))/(exp(yir_table[i][r_index])))
#        print 'hce: ', hce
        print 'woo, about to return from computing mhce'
        return  hce/(float(I*R))



    def compute_MHCE_vertical(self, yir_table_filename, return_periods, python_site_indices=None):
    #computes the mean hazard curve error according to me. It's basically computing the error in the probability of exceedance instead of error in Sa.
    #Inputs: 
    #    yir_table_filename: a filename of a table created by the script computepjir.py
    #    python_site_indices: the indices of the sites for which you want to compute the error.
    #bring in results for what the hazard curve should be at 13 return periods and 1557 sites:
        pkl_file = open(yir_table_filename,'rb') 
        yir_table = pickle.load(pkl_file)
        pkl_file.close()
        if python_site_indices is None:
            python_site_indices = range(len(yir_table))
        hce = 0 #initialize
        R = len(yir_table[0]) #number of return periods
        print 'using '+str(R)+' return periods, and compare that to the number I am inputting, which is '+str(len(return_periods))
        I = len(python_site_indices) #number of sites
        print 'using '+str(I)+' sites'
         
        #loop over sites and return periods to compute the hazard curve error
        for i in python_site_indices:
            for r_index in range(len(return_periods)):
                r = return_periods[r_index]
            #        print '1/r: ', 1/float(r)
                hce += fabs((1/float(r) - find_weight(yir_table[i][r_index], self.hazard_dict[i]))/(1/float(r)))
        #        print 'hce vertical: ', hce
        return  hce/(float(I*R))
        
class QuakeMaps(object):
    
    def __init__(self, totalfilename=None, magfilename=None, faultfilename=None, weightsfilename=None, scenariofilename=None):
        try:
            pkl_file = open(totalfilename, 'rb')
            self.lnsas = pickle.load(pkl_file) #entry 0 is weight. entry 1 onward has mean lnSa
            pkl_file.close() 
            self.num_sites = len(self.lnsas[0]) 
        except:
            print 'cannot open lnSa file'
            self.lnsas = []
            self.num_sites = []
        #sometimes it might be possible to have the magnitude and fault info but not the lnsas or scenario numbers
        try:
            pkl_file = open(magfilename, 'rb')
            self.magnitudes = pickle.load(pkl_file) 
            pkl_file.close() 
            pkl_file = open(faultfilename, 'rb')
            self.faults = pickle.load(pkl_file) 
            pkl_file.close() 
            pkl_file = open(weightsfilename, 'rb')
            self.weights = pickle.load(pkl_file) 
            pkl_file.close() 
            
        except:
            print 'cannot open magnitude and/or other details'
            self.magnitudes =[] #dictionary keyed by earthquake number
            self.faults = [] #dictionary keyed by earthquake number
            self.weights = [] #dictionary keyed by earthquake number
        try:
            pkl_file = open(scenariofilename, 'rb')
            self.scenario_nums = pickle.load(pkl_file) 
            pkl_file.close() 
        except:
            self.scenario_nums = []  #list where rows correspond to those of total lnsas and the value at each index is the original earthquake number

           
    def put_matlab_to_dicts(self, medianfilename=None, totalfilename=None, index=0, pickle_boolean=False):
        #define some constants and initialize variables
        weights = {}
        magnitudes = {}
        faults = {}
        hayward = range(27,33) + [126]
        north_san_andreas  = range(33,43) + [127] #source 127 has tons of rupture scenarios!!!!
        calaveras = range(0,6) + [123]

        print hayward
        print north_san_andreas
        print calaveras
        #figure out number of medians
        fsim = open(medianfilename, 'r')
        num_quakes = len(fsim.readlines())
        fsim.close()
        print 'number of quake scenarios: ', num_quakes
        #open up file with total lnsa file
        fsim = open(totalfilename, 'r')
        sim_lines = fsim.readlines()
        fsim.close()

        earthquake_counter = 0
        scenario_counter = 0
        lnsas = []
        scenario_nums = []
        tic = time.time()
        for line in sim_lines:
            line = string.split(line, '\t') #each token is a string
#            lnSasMean = [log(float(string.strip(i))) for i in line[4:len(line)]]
            if earthquake_counter < num_quakes:
                    
                weights[earthquake_counter] = float(string.strip(line[3]))
                magnitudes[earthquake_counter] = float(string.strip(line[2]))
    #            print string.strip(line[0])
                if float(string.strip(line[1])) in hayward:
                    faults[earthquake_counter] = 'hayward'
    #                print 'hayward'
                elif float(string.strip(line[1])) in north_san_andreas:
                    faults[earthquake_counter] = 'north_san_andreas'
    #                print 'sa'
                elif float(string.strip(line[1])) in calaveras:
                    faults[earthquake_counter] = 'calaveras'
    #                print 'calaveras'
                else:
                    faults[earthquake_counter] = 'other'
    #                print 'other'
                earthquake_counter = earthquake_counter + 1
            
            lnsas.append([log(float(string.strip(i))) for i in line[4:len(line)]])
            scenario_nums.append(scenario_counter%earthquake_counter)
            scenario_counter = scenario_counter + 1
            if scenario_counter%1000==0:
                print 'finished scenario ', scenario_counter
                print 'in time: ', time.time()-tic
                print 'number of sites in file: ', len(line)
#        #open up file with total lnSa
##        fsim = open(totalfilename, 'r')
##        sim_lines = fsim.readlines()
##        fsim.close()
        
        print 'number of earthquake scenarios: ', earthquake_counter #since we added one after going through all the earthquake scenario lines
#        for line in sim_lines:
#            line = string.split(line, '\t') #each token is a string
        if pickle_boolean is True:   
            #pickle all these data structures
            output = open(time.strftime("%Y%m%d")+'_mtc_weights' + str(index) + '.pkl', 'wb')
            pickle.dump(weights, output)
            output.close()
            output = open(time.strftime("%Y%m%d")+'_mtc_magnitudes' + str(index) + '.pkl', 'wb')
            pickle.dump(magnitudes, output)
            output.close()
            output = open(time.strftime("%Y%m%d")+'_mtc_faults' + str(index) + '.pkl', 'wb')
            pickle.dump(faults, output)
            output.close()
            output = open(time.strftime("%Y%m%d")+'_mtc_total_lnsas' + str(index) + '.pkl', 'wb')
            pickle.dump(lnsas, output)
            output.close()
            output = open(time.strftime("%Y%m%d")+'_mtc_scenarios' + str(index) + '.pkl', 'wb')
            pickle.dump(scenario_nums, output)
            output.close()
        return weights, magnitudes, faults, lnsas, scenario_nums
            
def main2():
    q = QuakeMaps()
    weights, magnitudes1, faults, lnsas, scenario_nums = q.put_matlab_to_dicts('/Users/mahalia/Documents/matlab/Research/Herbst2011/output_data/SF_mtc_medians_4993scenarios.txt','/Users/mahalia/Documents/matlab/Research/Herbst2011/output_data/SF_mtc_total_4993scenariosTwoEps.txt',1, True)

def main():

    
    #-------------import network data---------------------
    #a...first 5 sitesTimes100

    #b...new MTC network
    
    #-------------import corresponding earthquake data---------------------
    #a...first 5 sitesTimes100
#    q = QuakeMaps('20120812_mtc_total_lnsas_mini.pkl','20120812_mtc_magnitudes.pkl', '20120812_mtc_faults.pkl', '20120812_mtc_weights.pkl', '20120812_mtc_scenarios.pkl')
    
    #b...new MTC network
#    q = QuakeMaps('20120812_mtc_total_lnsas.pkl','20120812_mtc_magnitudes.pkl', '20120812_mtc_faults.pkl', '20120812_mtc_weights.pkl', '20120812_mtc_scenarios.pkl')
    
    #-------------initialize basic parameters for what to save such as return periods---------------------
    
    
    #-------------do it---------------------
#    g = HazardDict()
#    print g.sa_bins_times100
    
#    HazardDict.populate_hazard_dict(g, q.lnsas, q.weights, q.num_sites)
#    HazardDict.pickle_hazard_dict(g, time.strftime("%Y%m%d")+'_hazard_dict.pkl')
#    HazardDict.print_hazard_dict(g)
    #idea for values of outside dict: matrix = {(0,3): 1, (2, 1): 2, (4, 3): 3}
    
#    HazardDict.print_hazard_dict(g)
    #-------------pickle output---------------------
#    HazardDict.pickle_hazard_dict(g, time.strftime("%Y%m%d")+'MTChazardDict.pkl')
    
    #check that it really worked
#    h = HazardDict()
###    HazardDict.print_hazard_dict(h)
#    HazardDict.unpickle_hazard_dict(h, '20120818_hazard_dictFromHuge.pkl')#'20120809MTChazardDict.pkl')
#    print h.sa_bins_times100
#    print h.hazard_dict[1]
#    d=[]
#    for thing in h.hazard_dict[0]:
#        d = d + [40.0*thing]
#    print d
#    print len(h.hazard_dict)
##    HazardDict.print_hazard_dict(h)
##    

    tic = time.time()
#    #play with quakemaps
#    q = QuakeMaps()
#    weights, magnitudes1, faults, lnsas, scenario_nums = q.put_matlab_to_dicts('SF_mtc_medians_4993scenarios.txt','SF_mtc_total_4993scenariosPruned.txt',1, False)
#    print 'first batch done in time ', time.time()-tic
#    q2 = QuakeMaps()
#    weights, magnitudes2, faults, lnsas2, scenario_nums = q2.put_matlab_to_dicts('SF_mtc_medians_4993scenarios.txt','SF_mtc_total_4993scenariosPruned2.txt',2, False)
#    print 'second batch done in time ', time.time()-tic
#    q3 = QuakeMaps()
#    weights, magnitudes3, faults, lnsas3, scenario_nums = q3.put_matlab_to_dicts('SF_mtc_medians_4993scenarios.txt','SF_mtc_total_4993scenariosPruned3.txt',3, False)
#    print 'third batch done in time ', time.time()-tic
#
#    q4 = QuakeMaps()
#    weights, magnitudes4, faults, lnsas4, scenario_nums = q4.put_matlab_to_dicts('SF_mtc_medians_4993scenarios.txt','SF_mtc_total_4993scenariosPruned4.txt',4, False)
#    print 'fourth batch done in time ', time.time()-tic
#
#    q5 = QuakeMaps()
#    weights, magnitudes5, faults, lnsas5, scenario_nums = q5.put_matlab_to_dicts('SF_mtc_medians_4993scenarios.txt','SF_mtc_total_4993scenariosPruned5.txt',5, False)
#    lnsas_final = lnsas + lnsas2 + lnsas3 + lnsas4 + lnsas5
#    print 'fifth batch done in time ', time.time()-tic
#    
#    g = HazardDict()
#    print 'num sites in main: ', len(lnsas[0])
#    HazardDict.populate_hazard_dict(g, lnsas_final, weights, len(lnsas[0]))
#    HazardDict.pickle_hazard_dict(g, time.strftime("%Y%m%d")+'_hazard_dictFromHuge.pkl')
#    print g.hazard_dict[0]
##    HazardDict.print_hazard_dict(g)
#    print 'yippeee'



#    #play with quakemaps
#    q = QuakeMaps('20120820_mtc_total_lnsas1.pkl', '20120820_mtc_magnitudes1.pkl', '20120820_mtc_faults1.pkl', '20120820_mtc_weights1.pkl', '20120820_mtc_scenarios1.pkl') #totalfilename=None, magfilename=None, faultfilename=None, weightsfilename=None, scenariofilename=None):
###    weights, magnitudes1, faults, lnsas, scenario_nums = q.put_matlab_to_dicts('/Users/mahalia/Documents/matlab/Research/Herbst2011/output_data/SF_mtc_medians_4993scenarios.txt','/Users/mahalia/Documents/matlab/Research/Herbst2011/output_data/SF_mtc_total_4993scenariosOneEps.txt',1, True)
 #   lnsas = q.lnsas
##    lnsas = lnsas[0:1394]
##    print q.weights
##    weights = []
##    for i in range(1394):
##        weights = weights + [q.weights[i]]
##    print weights
###    weights = q.weights[0:1394]
##    print 'lnsas to deal with ', len(lnsas)
#    q1 = QuakeMaps()
#    weights, magnitudes, faults, lnsas, scenario_nums = q1.put_matlab_to_dicts('/Users/mahalia/Documents/matlab/Research/Herbst2011/output_data/SF_mtc_medians_4993scenarios.txt','/Users/mahalia/Documents/matlab/Research/Herbst2011/output_data/SF_mtc_total_4993scenariosPruned.txt',5, False)
#    print 'first loaded'
#    q2 = QuakeMaps()
#    weights, magnitudes2, faults, lnsas2, scenario_nums = q2.put_matlab_to_dicts('/Users/mahalia/Documents/matlab/Research/Herbst2011/output_data/SF_mtc_medians_4993scenarios.txt','/Users/mahalia/Documents/matlab/Research/Herbst2011/output_data/SF_mtc_total_4993scenariosPruned2.txt',1, False)
#    q3 = QuakeMaps()
#    print 'second loaded'
#    weights, magnitudes3, faults, lnsas3, scenario_nums = q3.put_matlab_to_dicts('/Users/mahalia/Documents/matlab/Research/Herbst2011/output_data/SF_mtc_medians_4993scenarios.txt','/Users/mahalia/Documents/matlab/Research/Herbst2011/output_data/SF_mtc_total_4993scenariosPruned3.txt',2, False)
#    q4 = QuakeMaps()
#    print 'third loaded'
##    weights, magnitudes4, faults, lnsas4, scenario_nums = q4.put_matlab_to_dicts('/Users/mahalia/Documents/matlab/Research/Herbst2011/output_data/SF_mtc_medians_4993scenarios.txt','/Users/mahalia/Documents/matlab/Research/Herbst2011/output_data/SF_mtc_total_4993scenariosPruned4.txt',3, False)
##    print 'fourth loaded'
##    q1 = QuakeMaps()
##    weights, magnitudes, faults, lnsas, scenario_nums = q1.put_matlab_to_dicts('SF_mtc_medians_4993scenarios.txt','SF_mtc_total_4993scenariosPruned.txt',5, False)
##    print 'first loaded'
##    q2 = QuakeMaps()
##    weights, magnitudes2, faults, lnsas2, scenario_nums = q2.put_matlab_to_dicts('SF_mtc_medians_4993scenarios.txt','SF_mtc_total_4993scenariosPruned2.txt',1, False)
##    q3 = QuakeMaps()
##    print 'second loaded'
##    weights, magnitudes3, faults, lnsas3, scenario_nums = q3.put_matlab_to_dicts('SF_mtc_medians_4993scenarios.txt','SF_mtc_total_4993scenariosPruned3.txt',2, False)
##    q4 = QuakeMaps()
##    print 'third loaded'
##    weights, magnitudes4, faults, lnsas4, scenario_nums = q4.put_matlab_to_dicts('SF_mtc_medians_4993scenarios.txt','SF_mtc_total_4993scenariosPruned4.txt',3, False)
##    print 'fourth loaded'
#
##    q5 = QuakeMaps()
##    weights, magnitudes5, faults, lnsas5, scenario_nums = q5.put_matlab_to_dicts('/Users/mahalia/Documents/matlab/Research/Herbst2011/output_data/SF_mtc_medians_4993scenarios.txt','/Users/mahalia/Documents/matlab/Research/Herbst2011/output_data/SF_mtc_total_4993scenariosPruned5.txt',4, False)
#    lnsas_final = lnsas + lnsas2 + lnsas3 #+ lnsas4# + lnsas5
#    print 'total number of ground motion maps: ', len(lnsas_final)
#    g = HazardDict()
#    HazardDict.populate_hazard_dict(g, lnsas, weights, len(lnsas[0]))
#    HazardDict.pickle_hazard_dict(g, time.strftime("%Y%m%d")+'_hazard_dictOneMassive.pkl')


#    #play with quakemaps
    q = QuakeMaps('20120820_mtc_total_lnsas1.pkl', '20120820_mtc_magnitudes1.pkl', '20120820_mtc_faults1.pkl', '20120820_mtc_weights1.pkl', '20120820_mtc_scenarios1.pkl') #totalfilename=None, magfilename=None, faultfilename=None, weightsfilename=None, scenariofilename=None):
#    q = QuakeMaps('20120911_mtc_total_lnsas2eps.pkl')#, '20120911_mtc_magnitudes1.pkl', '20120911_mtc_faults1.pkl', '20120911_mtc_weights1.pkl', '20120911_mtc_scenarios1.pkl') #totalfilename=None, magfilename=None, faultfilename=None, weightsfilename=None, scenariofilename=None):
    lnsas = q.lnsas

#    #subset with 10 centroid sites and 4993 ground motion maps
    pkl_file = open('20120919subset12_20_500ok.pkl','rb')#20120831subset10_4_200.pkl', 'rb') #CHANGE THIS
    subset = pickle.load(pkl_file)
    pkl_file.close()
    pkl_file = open('20120919weight12_20_500ok.pkl','rb')#20120831weight10_4_200.pkl', 'rb') #CHANGE THIS
    weights = pickle.load(pkl_file)
    pkl_file.close()
    yir_table_filename = '20120917_mtc_log_Y_ir_table_R50.pkl' #'20120912_mtc_log_Y_ir_table_R13.pkl'#'20120820_mtc_log_Y_ir_table.pkl'#'20120907_mtc_log_Y_ir_table_R20.pkl'#'20120820_mtc_log_Y_ir_table.pkl'#'20120907_mtc_log_Y_ir_table_R2.pkl' #'20120905_mtc_log_Y_ir_table.pkl' #13 return periods, 1557 sites #CHANGE THIS
    return_periods = [100.0, 107.0, 114.0, 122.0, 130.0, 139.0, 148.0, 158.0, 169.0, 181.0, 193.0, 206.0, 220.0, 235.0, 251.0, 268.0, 286.0, 305.0, 326.0, 348.0, 372.0, 397.0, 424.0, 453.0, 484.0, 517.0, 552.0, 589.0, 629.0, 672.0, 718.0, 766.0, 818.0, 874.0, 933.0, 997.0, 1064.0, 1137.0, 1214.0, 1296.0, 1384.0, 1478.0, 1579.0, 1686.0, 1800.0, 1922.0, 2053.0, 2192.0, 2341.0, 2500.0] #50 return periods equally spaced in base 10 log space between 100 and 2500 years
#    chosen_sites = [1238,1497,248,1423,448,1103,29,262,776,583,996,1282]    

    #chosen_sites = [320, 841, 1295, 1492,1276]
    #chosen_sites = [1149,820,800,1044,1257,1542,160,63,329,1406,549,1435,1221,22,310,831,1217,353,1369,893,207,632,1093,535,1481,440,682,746,953,1338,73,445,504,205,1021]    
    #chosen_sites = [1238,1497,248,1423,448,1103,29,262,776,583,996,1282]    
#    chosen_sites = [1463,304,1542,1406,1084,1288,670,1107,163,663, 1435,1299,926,1103,1305,445,451,29]
#    #chosen_sites = [101,1422,1259,776,1542,1221,28,1479,323,574,793,702,1369,1381,933,1298,1095,121,1111,1435,1100,425,516,332,1402]
#    python_indices = [site_index-1 for site_index in chosen_sites] #these are the indices for Python
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
#    J_red = int(sum(subset))
    print 'J_red: ', J_red
    print 'vs sum of subset is: ', sum(subset)
    print 'and length of subset vector: ', len(subset)
#    
    g = HazardDict()
    lnsas_subset = [ [0 for i in range(q.num_sites)] for j in range(J_red) ] #just initializes list of lists of 0s
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
    #    print 'index: ', index
                weight = weights[index]
        #print 'weight*10,000: ', weight*10000
                if (weight <=  0.00001):# or (q.weights[index] <=  0.00001):#<= 0):
                    pass
                else:
                    good += 1
                    lnsas_subset[counter]=lnsas[index]
                    weights_subset[counter] = weights[index]
                    counter = counter+1
        print 'len before removing blacklist: ', len(lnsas_subset)
        black_list = [24, 25, 26, 144, 145, 146, 147, 180, 181, 182, 183, 184, 185] #far away scenarios with index ranging from 0 to 206
        #remove elements at indices of black list
        for index in black_list:
            del lnsas_subset[index]
            del weights_subset[index]
        print 'len after removing blacklist: ', len(lnsas_subset)
        print 'len after removing blacklist: ', len(weights_subset)   
        lnsas_subset_new = [lnsas_subset[i] for i in range(len(lnsas_subset)) if weights_subset[i] > 0.00001] 
        weights_subset_new = [weights_subset[i] for i in range(len(lnsas_subset)) if weights_subset[i] > 0.00001] 
        lnsas_subset = lnsas_subset_new
        weights_subset = weights_subset_new
                    
        print 'num sites in main: ', len(lnsas[0])
#        print 'number of sites (I): ', len(python_indices)

        print 'number of maps in subset: ', len(lnsas_subset)
        print 'number of maps with non-zero weight: ', good

        print weights_subset
        print 'weight subset: ', sum(weights_subset)
    #print [ln[0] for ln in lnsas_subset]
#        if len(lnsas_subset)>200: #chop off the scenarios with the smallest weight
#            #pair up the subsets with the associated weight
#            x_tuples = [(lnsas_subset[j], weights_subset[j]) for j in range(len(lnsas_subset))]
#            #sort the pairs in ascending order of weight(small to big)
#            c1 = sorted(x_tuples,key=lambda lnsaPair: lnsaPair[1])
##            c1 = c1[::-1] #change to big to small
#            weights_subset = [pair[1] for pair in c1] #extracts the second element of each pair.
#            lnsas_subset = [pair[0] for pair in c1] #extracts the first element, which is x, the Sa value
#            weights_subset = weights_subset[len(weights_subset)-200: len(weights_subset)]
#            lnsas_subset = lnsas_subset[len(weights_subset)-200: len(weights_subset)]
        print 'number of maps in subset now: ', len(lnsas_subset)
        HazardDict.populate_hazard_dict(g, lnsas_subset, weights_subset, len(lnsas[0]))
        HazardDict.pickle_hazard_dict(g, time.strftime("%Y%m%d")+'_hazard_dict10sitesAllQuakes.pkl')
        #print 'hazard dict first site: ', g.hazard_dict[0]
    #first for however many sites we actually have
#    print 'mhce alternate for all sites: ', HazardDict.compute_MHCE_vertical(g, yir_table_filename, return_periods)
    print 'mhce for all sites: ', HazardDict.compute_MHCE(g, yir_table_filename, return_periods)

    #second for just the chosen sites
    #print 'mhce alternate: ', HazardDict.compute_MHCE_vertical(g, yir_table_filename, return_periods, chosen_sites)
#    print 'mhce: ', HazardDict.compute_MHCE(g, yir_table_filename, return_periods, chosen_sites)

    #print 'mhce for optimized: ', HazardDict.compute_MHCE_subset(g,  yir_table_filename, python_indices)

    #    HazardDict.print_hazard_dict(g)
    print 'sum: ', sum(weights_subset)
    print 'length: ', len(weights_subset)
    print 'yippeee'
  #  print g.hazard_dict[362]
#    pkl_file = open('20120727_w_saMu_1630bridges.pkl', 'rb')
#    test = pickle.load(pkl_file)
#    pkl_file.close()
#    print test[0][0:4]
#    print 'ok'
#    tic = time.time()
##    q = QuakeMaps('20120812_mtc_total_lnsas.pkl','20120812_mtc_magnitudes.pkl', '20120812_mtc_faults.pkl', '20120812_mtc_weights.pkl') #takes 227 seconds to open. urg.
#    print time.time() - tic
#    print 'number of sites from q: ', q.num_sites
#    print 'length of weights: ', len(q.weights)
#    print 'random fault: ', q.faults
#    print 'random scenarios', q.scenarios[0:10]
#    print 'random magnitude', q.magnitudes[0]
#    print len(q.scenarios)
#    
#    q = QuakeMaps('20120727_w_saMu_1630bridges.pkl', '20120727_10eps_1630bridges.pkl')
#    sa, weight = QuakeMaps.get_sa_and_weight(q, 0,0)
#    print sa[0:5]
#    print weight
#    sa, weight = QuakeMaps.get_sa_and_weight(q, 0,1)
#    print sa[0:5]
#    print weight
#    sa, weight = QuakeMaps.get_sa_and_weight(q, 1,1)
#    print sa[0:5]
#    print weight
#    print q.residuals[0]
#    print q.residuals[1]
#    print len(q.residuals)

def print_stats():
#    #play with quakemaps
    q = QuakeMaps('20120820_mtc_total_lnsas1.pkl', '20120820_mtc_magnitudes1.pkl', '20120820_mtc_faults1.pkl', '20120820_mtc_weights1.pkl', '20120820_mtc_scenarios1.pkl') #totalfilename=None, magfilename=None, faultfilename=None, weightsfilename=None, scenariofilename=None):
#    q = QuakeMaps('20120911_mtc_total_lnsas2eps.pkl')#, '20120911_mtc_magnitudes1.pkl', '20120911_mtc_faults1.pkl', '20120911_mtc_weights1.pkl', '20120911_mtc_scenarios1.pkl') #totalfilename=None, magfilename=None, faultfilename=None, weightsfilename=None, scenariofilename=None):
    lnsas = q.lnsas
    print len(q.weights)
    summm = 0
    for i in range(len(q.weights)):
        print q.weights[i]
        summm += q.weights[i]
    print 'actual sum of weights: ', summm
#    #subset with 10 centroid sites and 4993 ground motion maps
    pkl_file = open('20120919subset12_20_500ok.pkl','rb')#20120831subset10_4_200.pkl', 'rb') #CHANGE THIS
    subset = pickle.load(pkl_file)
    pkl_file.close()
    pkl_file = open('20120919weight12_20_500ok.pkl','rb')#20120831weight10_4_200.pkl', 'rb') #CHANGE THIS
    weights = pickle.load(pkl_file)
    pkl_file.close()
    yir_table_filename = '20120917_mtc_log_Y_ir_table_R50.pkl' #'20120912_mtc_log_Y_ir_table_R13.pkl'#'20120820_mtc_log_Y_ir_table.pkl'#'20120907_mtc_log_Y_ir_table_R20.pkl'#'20120820_mtc_log_Y_ir_table.pkl'#'20120907_mtc_log_Y_ir_table_R2.pkl' #'20120905_mtc_log_Y_ir_table.pkl' #13 return periods, 1557 sites #CHANGE THIS
    return_periods = [100.0, 107.0, 114.0, 122.0, 130.0, 139.0, 148.0, 158.0, 169.0, 181.0, 193.0, 206.0, 220.0, 235.0, 251.0, 268.0, 286.0, 305.0, 326.0, 348.0, 372.0, 397.0, 424.0, 453.0, 484.0, 517.0, 552.0, 589.0, 629.0, 672.0, 718.0, 766.0, 818.0, 874.0, 933.0, 997.0, 1064.0, 1137.0, 1214.0, 1296.0, 1384.0, 1478.0, 1579.0, 1686.0, 1800.0, 1922.0, 2053.0, 2192.0, 2341.0, 2500.0] #50 return periods equally spaced in base 10 log space between 100 and 2500 years
    chosen_sites = [1238,1497,248,1423,448,1103,29,262,776,583,996,1282]    

    #chosen_sites = [320, 841, 1295, 1492,1276]
    #chosen_sites = [1149,820,800,1044,1257,1542,160,63,329,1406,549,1435,1221,22,310,831,1217,353,1369,893,207,632,1093,535,1481,440,682,746,953,1338,73,445,504,205,1021]    
    #chosen_sites = [1238,1497,248,1423,448,1103,29,262,776,583,996,1282]    
#    chosen_sites = [1463,304,1542,1406,1084,1288,670,1107,163,663, 1435,1299,926,1103,1305,445,451,29]
#    #chosen_sites = [101,1422,1259,776,1542,1221,28,1479,323,574,793,702,1369,1381,933,1298,1095,121,1111,1435,1100,425,516,332,1402]
    python_indices = [site_index-1 for site_index in chosen_sites] #these are the indices for Python
    J_red = 0
    for index in range(len(subset)):
        if (subset[index] < 1.05) and (subset[index] > 0.95) and (weights[index] >0): #this map is part of subset
            J_red += 1
            print 1
        else:
            print 0
    for i in range(4993-4993): #1394):
        subset+=[0]
        weights+=[0]
    #print subset    
#    J_red = int(sum(subset))
    print 'J_red: ', J_red
    print 'vs sum of subset is: ', sum(subset)
    total_weights = 0
    other_weights = 0
    g = HazardDict()
    lines_subset = [ [] for j in range(J_red) ] #list of empty lists
    if len(subset)!=len(lnsas):
        print 'yo. You do not have the right number of entries in your subset list.'
        print len(subset)
        print len(lnsas)
    else:
        counter = 0 #counter for subset of maps
        good = 0
        for index in range(len(subset)):
            if (subset[index] < 1.05) and (subset[index] > 0.95): #this map is part of subset
    #    print 'index: ', index
                weight = weights[index] #This is different than q.weights since q.weights has the info before optimizing!!!!
        #print 'weight*10,000: ', weight*10000
                if (weight < 0 or weight==0):
                    pass
                else:
                    good += 1
#                    total_weights += q.weights[index] #original weights efore optimization
                    other_weights += weight
                    lines_subset[counter] = [(counter+1), q.magnitudes[index], q.faults[index], weights[index], index, q.scenario_nums[index]] + [exp(q.lnsas[index][bridge]) for bridge in python_indices]
		    print [(counter+1), q.magnitudes[index], q.faults[index], weights[index], index, q.scenario_nums[index]] + [exp(q.lnsas[index][bridge]) for bridge in python_indices]

                    counter = counter+1
                    
        print 'num sites in main: ', len(lnsas[0])
#        print 'number of sites (I): ', len(python_indices)

        print 'number of maps in subset: ', len(lines_subset)
        print 'number of maps with non-zero weight: ', good
    	print 'number of maps to start with: ', len(q.lnsas)
	print len(q.lnsas)
	print len(q.lnsas[python_indices[0]])
	#write out data to a tab-deliminated file
	f = open(time.strftime("%Y%m%d")+'_12_20_500ok_scenario_matrix.txt', 'wb')
	for line in lines_subset:
	    for item in line:
		f.write("%s\t" % item)
	    f.write("\n")
	
    print total_weights
    print other_weights
    print q.weights
    print len(q.weights)

if __name__ == '__main__':
    main()
#    print_stats()    







#    def get_sa_and_weight(self, scenario_num, residual_num):
#        sa_mu = self.meansPlus[scenario_num][1:]
#        weight = self.meansPlus[scenario_num][0]
#        residual = self.residuals[residual_num]
#        array = [sa_mu, residual]
#        return [sum(a) for a in zip(*array)], weight

    #                print 'satimes100: ', sa_times100
    #                print 'length of sabins', len(self.sa_bins_times100)
    #                print 'hazard dict at this site', self.hazard_dict[site][0:int(sa_times100)]
    #                print 'what weight should be: ', float(weights[int(scenario_counter%num_quakes)])
    ##                self.hazard_dict[site][0:int(sa_times100)]+=1
    #
    #                print 'and hazard dict now: ', self.hazard_dict[site][0:int(sa_times100)]
    ##                q_counter = 0
    ##                for q in self.sa_bins_times100:
    ##                    g = q - sa_times100 #order switched
    ##                    if g <= 0: #failure, i.e. the scenario Sa is bigger than the x Sa bin
    ##                        self.hazard_dict[site][q_counter]+=float(weights[scenario_counter%num_quakes])/float(sets)
    ##                    q_counter += 1
                
                        
                    
                    
#            print 'total weights: ', total_weights
#            print 'other total weights: ', other_total_weights
#            print self.hazard_dict[1500][0:10]
#            print self.hazard_dict[1500][100:110]
            








