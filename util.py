#Author: Mahalia Miller
#Date: Jan. 21, 2012, i.e. date of Obama's second inauguration 

#import networkx as nx

class TravelTime:
  alpha = 0.15
  beta = 4
  def __init__(self, t_0, cap_0):
    self.t_0 = t_0
    self.cap_0 = cap_0

  def get_new_travel_time(self, flow):
    alpha = 0.15
    beta = 4
  
    return self.t_0*(1 + alpha*(flow/float(self.cap_0))**beta)  

def clean_up_graph(G):
  #takes a graph and makes all flows 0 and makes t_a equal to t_0
  for n,nbrsdict in G.adjacency_iter():
    for nbr,keydict in nbrsdict.items():
      for key,eattr in keydict.items():
        eattr['flow'] = 0
        eattr['t_a'] = eattr['t_0']
        eattr['capacity'] = eattr['capacity_0']
  return G
def find_travel_time(G):
  #G is a networkx graph. returns the cumulative travel time of all drivers.
  travel_time = 0
  for n,nbrsdict in G.adjacency_iter():
    for nbr,keydict in nbrsdict.items():
      for key,eattr in keydict.items():
        travel_time += eattr['flow']*eattr['t_a']
  return travel_time

def find_vmt(G):
  #G is a networkx graph. returns the cumulative vehicles miles traveled of all drivers.
  vmt = 0
  for n,nbrsdict in G.adjacency_iter():
    for nbr,keydict in nbrsdict.items():
      for key,eattr in keydict.items():
        vmt += eattr['flow']*eattr['distance']
  return vmt

def compute_delay(travel_time, undamaged_travel_time = None):
  if undamaged_travel_time is not None:
    return travel_time - undamaged_travel_time
  else:
    return 0

if __name__ == '__main__':
  import networkx as nx
  G = nx.MultiDiGraph()
  G.add_node(1)
  G.add_node(2)
  G.add_edge(1,2,capacity_0=1000,capacity=1000,t_0=15,t_a=15,flow=0, distance=10)
  G.add_edge(1,2,capacity_0=3000,capacity=3000,t_0=20,t_a=20,flow=0, distance=10)
  print 'should be 0: ', find_travel_time(G)
  G[1][2][0]['flow']=1000
  print 'should be 15000: ', find_travel_time(G)
  print 'should be 10000: ', find_vmt(G)
#
