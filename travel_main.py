#Author: Mahalia Miller
#Date: Jan. 21, 2013

import ita
import bd

import networkx as nx
def main():
  #get graph info
  G = nx.read_gpickle("graphMTC_CentroidsLength5.gpickle") #noCentroidsLength15.gpickle") #does not have centroidal links 
  #get od info. This is in format of a dict keyed by od, like demand[sd1][sd2] = 200000.
  demand = bd.build_demand('BATS2000_34SuperD_TripTableData.csv', 'superdistricts_centroids.csv')
  demand['7493'] = {}
  demand['7493']['7838'] = 20000

  #call ita
  it = ita.ITA(G,demand)
  newG = it.assign()
  for n,nbrsdict in newG.adjacency_iter():
    for nbr,keydict in nbrsdict.items():
      for key,eattr in keydict.items():
        if eattr['flow']>0:
          print (n, nbr, eattr['flow'])

if __name__ == '__main__':
  main()
