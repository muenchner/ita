#Author: Mahalia Miller
#Date: Jan. 21, 2013

def build_demand(trip_filename, centroid_filename):
  demand_dict = {}
  sd_dict = {}
  with open(centroid_filename,'rb') as f:
    read_data = f.read().splitlines()
    for row in read_data[1:]:
      tokens = row.split(',')
      sd_dict[str(int(tokens[0]))] =  str(int(tokens[2]))
      demand_dict[str(int(tokens[2]))] = {}

  with open(trip_filename,'rb') as f:
    read_data = f.read().splitlines()
    for row in read_data[4:]:
      tokens = row.split(',')
      print tokens
      demand_dict[str(sd_dict[str(int(tokens[0]))])][str(sd_dict[str(int(tokens[1]))])] = int(tokens[2]) + int(tokens[3]) + int(tokens[4]) + int(tokens[5]) + int(tokens[6]) #int(tokens[12])
      if (int(tokens[2]) + int(tokens[3]) + int(tokens[4]) + int(tokens[5]) + int(tokens[6])) > int(tokens[12]):
        print 'what is going on?'
  return demand_dict


if __name__=='__main__':
  print build_demand('BATS2000_34SuperD_TripTableData.csv', 'superdistricts_centroids.csv')
