#Author: Mahalia Miller
#Date: Jan. 21, 2013

#this code does iterative travel assignment.
import sys, util
import networkx as nx

iteration_vals = [0.4, 0.3, 0.2, 0.1] #assign od vals in this amount per iteration

class ITA:
  def __init__(self, G, demand):
    #G is a networkx graph, it can be damaged. Edges need to have a free flow travel time, a capacity, a variable called flow (which we'll change to keep track of flows assigned to each link), and a variable called t_a (which we'll change based on the flows)
    self.G = G
    self.demand = demand

  def assign(self):
    #does 4 iterations in which it assigns od, updates t_a. find paths to minimize travel time and we record route for each od pair
    for i in range(4): #do 4 iterations
      for origin in self.demand.keys():
        #find the shortest paths from this origin to each destination
        paths_dict = nx.single_source_dijkstra_path(self.G, origin, cutoff = None, weight = 't_a') #Compute shortest path between source and all other reachable nodes for a weighted graph. Returns dict keyed by by target with the value being a list of node ids of the shortest path
        for destination in self.demand[origin].keys():
          od_flow = iteration_vals[i] * self.demand[origin][destination]
          #get path
          print 'destination: ', destination
          print 'paths dict: ', paths_dict
          path_list = paths_dict[destination] #list of nodes
          
          #increment flow on the paths and update t_a
          for index in range(0, len(path_list) - 1):
            u = path_list[index]
            v = path_list[index + 1]
            num_multi_edges =  len( self.G[u][v])
            if num_multi_edges >1: #multi-edge
              #identify multi edge with lowest t_a
              best = 0
              best_t_a = float('inf')
              for multi_edge in self.G[u][v].keys():
                new_t_a = self.G[u][v][multi_edge]['t_a']
                if new_t_a < best_t_a:
                  best = multi_edge
                  best_t_a = new_t_a
            else:
              best = 0

            self.G[u][v][best]['flow'] += od_flow
            t = util.TravelTime(self.G[u][v][best]['t_0'], self.G[u][v][best]['capacity'])
            self.G[u][v][best]['t_a'] = t.get_new_travel_time(od_flow)
    return self.G

      





def main():
  #get graph info
  G = nx.MultiDiGraph()
  G.add_node(1)
  G.add_node(2)
  G.add_edge(1,2,capacity=1000,t_0=15,t_a=15,flow=0)
  G.add_edge(1,2,capacity=3000,t_0=20,t_a=20,flow=0)
  #get od info. This is in format of a dict keyed by od, like demand[sd1][sd2] = 200000.
  demand = {}
  demand[1] = {}
  demand[1][2] = 8000

  #call ita
  it = ITA(G,demand)
  newG = it.assign()
  print newG
  for n,nbrsdict in newG.adjacency_iter():
    for nbr,keydict in nbrsdict.items():
      for key,eattr in keydict.items():
        print 'key: ', key
        print 'attr: ', eattr

if __name__ == '__main__':
  main()
 # main(sys.argv[1:])
