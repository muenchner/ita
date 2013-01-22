#Author: Mahalia Miller
#Date: Jan. 21, 2013

import ita
import bd
import util
import time

import networkx as nx
def main():
  #get graph info
  G = nx.read_gpickle("graphMTC_CentroidsLength5.gpickle") #noCentroidsLength15.gpickle") #does not have centroidal links 
  #get od info. This is in format of a dict keyed by od, like demand[sd1][sd2] = 200000.
  demand = bd.build_demand('BATS2000_34SuperD_TripTableData.csv', 'superdistricts_centroids.csv')
 # demand['7493'] = {}
#  demand['7493']['7838'] = 20000

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
  print 'travel time: ', util.find_travel_time(newG)
  print 'vmt: ', util.find_vmt(G)
  newG = util.clean_up_graph(newG)

if __name__ == '__main__':
  main()
