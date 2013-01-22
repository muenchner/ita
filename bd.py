#Author: Mahalia Miller
#Date: Jan. 21, 2013

def build_demand(trip_filename, centroid_filename):
  demand_dict = {}
  sd_dict = {}
  with open(centroid_filename,'rb') as f:
    read_data = f.read().splitlines()
    for row in read_data[1:]:
      print row
      tokens = row.split(',')
      print tokens
      sd_dict[int(tokens[0])] =  int(tokens[2])
      demand_dict[int(tokens[2])] = {}

  with open(trip_filename,'rb') as f:
    read_data = f.read().splitlines()
    for row in read_data[4:]:
      print row
      tokens = row.split(',')
      print tokens
      demand_dict[sd_dict[int(tokens[0])]][sd_dict[int(tokens[1])]] = int(tokens[12])
  return demand_dict


if __name__=='__main__':
  print build_demand('BATS2000_34SuperD_TripTableData.csv', 'superdistricts_centroids.csv')
