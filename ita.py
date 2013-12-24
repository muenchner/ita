#Author: Mahalia Miller
#Date: Jan. 21, 2013

#this code does iterative travel assignment.
import sys, util
import networkx as nx
import pdb

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
        # print origin
        paths_dict = nx.single_source_dijkstra_path(self.G, origin, cutoff = None, weight = 't_a') #Compute shortest path between source and all other reachable nodes for a weighted graph. Returns dict keyed by by target with the value being a list of node ids of the shortest path
        for destination in self.demand[origin].keys():
          # print destination
          od_flow = iteration_vals[i] * self.demand[origin][destination]*0.053 #to get morning flows, take 5.3% of daily driver values. 11.5/(4.5*6+11.5*10+14*4+4.5*4) from Figure S10 of http://www.nature.com/srep/2012/121220/srep01001/extref/srep01001-s1.pdf
          #get path
          path_list = paths_dict[destination] #list of nodes
          
          #increment flow on the paths and update t_a
          for index in range(0, len(path_list) - 1):
            u = path_list[index]
            v = path_list[index + 1]
            
            if self.G.is_multigraph():
              num_multi_edges =  len( self.G[u][v]) #if not multigraph, this just returns the number of edge attributes
              if num_multi_edges >1: #multi-edge
                # print 'multiedge: ', num_multi_edges
                #identify multi edge with lowest t_a
                best = 0
                best_t_a = float('inf')
                # print self.G[u][v].keys()
                for multi_edge in self.G[u][v].keys():
                  new_t_a = self.G[u][v][multi_edge]['t_a'] #causes problems
                  if (new_t_a < best_t_a) and (self.G[u][v][multi_edge]['capacity']>0):
                    best = multi_edge
                    best_t_a = new_t_a
              else:
                best = 0
              if (self.G[u][v][best]['capacity']>0):
                # print 'adding flow'
                self.G[u][v][best]['flow'] += od_flow
                t = util.TravelTime(self.G[u][v][best]['t_0'], self.G[u][v][best]['capacity'])
                travel_time= t.get_new_travel_time(od_flow) #TODO #min(t.get_new_travel_time(od_flow), self.G[u][v][best]['distance_0']*1.0/3600.0) #distance in miles, t_a in seconds!! So we are saying that the minimum of the t_a and distance (in miles) * (1 hr/ 1 mile) * (1hr / 3600s)
                if travel_time > self.G[u][v][best]['distance_0']*3600:
                  print travel_time
                  print 'and 1mph: ', self.G[u][v][best]['distance_0']*3600
                self.G[u][v][best]['t_a'] = travel_time
            else:
              if (self.G[u][v]['capacity']>0):
                # print 'adding flow'
                self.G[u][v]['flow'] += od_flow
                t = util.TravelTime(self.G[u][v]['t_0'], self.G[u][v]['capacity'])
                travel_time= t.get_new_travel_time(od_flow) #TODO #min(t.get_new_travel_time(od_flow), self.G[u][v][best]['distance_0']*1.0/3600.0) #distance in miles, t_a in seconds!! So we are saying that the minimum of the t_a and distance (in miles) * (1 hr/ 1 mile) * (1hr / 3600s)
                if travel_time > self.G[u][v]['distance_0']*3600: #if going less than 1mph, 
                  print travel_time
                  print 'and 1mph: ', self.G[u][v]['distance_0']*3600
                  # travel_time = self.G[u][v]['distance_0']*3600 #override the value. Caution!!
                self.G[u][v]['t_a'] = travel_time
    return self.G

      





def main():
  #get graph info
  G = nx.MultiDiGraph()
  G.add_node(1)
  G.add_node(2)
  G.add_edge(1,2,capacity_0=1000,capacity=1000,t_0=15,t_a=15,flow=0, distance=10)
  G.add_edge(1,2,capacity_0=3000,capacity=3000,t_0=20,t_a=20,flow=0, distance=10)
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
        print (n, nbr, eattr['flow'])
  print 'should have flow of 3200 and 4800'

  #try another one
  G = nx.MultiDiGraph()
  G.add_node('A')
  G.add_node('B')
  G.add_node('C')
  G.add_node('D')
  G.add_node('E')
#first type
  G.add_edge('A','B',capacity_0=5000,capacity=1000,t_0=15,t_a=15,flow=0)
  G.add_edge('A','D',capacity_0=5000,capacity=1000,t_0=15,t_a=15,flow=0)
  G.add_edge('D','F',capacity_0=5000,capacity=1000,t_0=15,t_a=15,flow=0)
  G.add_edge('E','C',capacity_0=5000,capacity=1000,t_0=15,t_a=15,flow=0)
  G.add_edge('B','A',capacity_0=5000,capacity=1000,t_0=15,t_a=15,flow=0)
  G.add_edge('D','A',capacity_0=5000,capacity=1000,t_0=15,t_a=15,flow=0)
  G.add_edge('F','D',capacity_0=5000,capacity=1000,t_0=15,t_a=15,flow=0)
  G.add_edge('C','E',capacity_0=5000,capacity=1000,t_0=15,t_a=15,flow=0)
#second type
  G.add_edge('B','D',capacity_0=5000,capacity=3000,t_0=20,t_a=20,flow=0)
  G.add_edge('D','B',capacity_0=5000,capacity=3000,t_0=20,t_a=20,flow=0)
  G.add_edge('A','E',capacity_0=5000,capacity=3000,t_0=20,t_a=20,flow=0)
  G.add_edge('E','A',capacity_0=5000,capacity=3000,t_0=20,t_a=20,flow=0)
  G.add_edge('E','F',capacity_0=5000,capacity=3000,t_0=20,t_a=20,flow=0)
  G.add_edge('F','E',capacity_0=5000,capacity=3000,t_0=20,t_a=20,flow=0)
  G.add_edge('F','C',capacity_0=5000,capacity=3000,t_0=20,t_a=20,flow=0)
  G.add_edge('C','F',capacity_0=5000,capacity=3000,t_0=20,t_a=20,flow=0)
  
  #get od info. This is in format of a dict keyed by od, like demand[sd1][sd2] = 200000.
  demand = {}
  demand['A'] = {}
  demand['C'] = {}
  demand['B'] = {}
  demand['A']['B'] =4000
  demand['A']['C'] =5000
  demand['C']['B'] =2000
  demand['B']['A'] =1000


  #call ita
  it = ITA(G,demand)
  newG = it.assign()
  print newG
  for n,nbrsdict in newG.adjacency_iter():
    for nbr,keydict in nbrsdict.items():
      for key,eattr in keydict.items():
        print (n, nbr, eattr['flow'])
  print 'and now clean up the graph'
  newG = util.clean_up_graph(newG)
  for n,nbrsdict in newG.adjacency_iter():
    for nbr,keydict in nbrsdict.items():
      for key,eattr in keydict.items():
        print (n, nbr, eattr['flow'])
        print (n, nbr, eattr['capacity'])


if __name__ == '__main__':
  main()
 # main(sys.argv[1:])
