from grid import Grid,Net_Connection
from heapq import heappush,heappop
from sys import exit,argv
def parse_grid(file):
	fp = open(file,'r')
	grids = [int(i) for i in fp.readline().strip().split()]
	x_gridsize = grids[0]
	y_gridsize = grids[1]
	BendPenalty = grids[2]
	ViaPenalty = grids[3]
	grid_l = []
	for i in range(y_gridsize):
		grids = [int(k) for k in fp.readline().strip().split()]
		for j in range(x_gridsize):
			c = Grid(j,i,grids[j],None,0) #x, y, cost, pred, layer
			grid_l.append(c)
	for i in range(y_gridsize):
		grids = [int(k) for k in fp.readline().strip().split()]
		for j in range(x_gridsize):
			c = Grid(j,i,grids[j],None,1) #x, y, cost, pred, layer
			grid_l.append(c)
	fp.close()
	return (grid_l,x_gridsize,y_gridsize,BendPenalty,ViaPenalty)
	

def parse_nl(file):
	fp = open(file,'r')
	netnumber = int(fp.readline().strip())
	nets = []
	for net in netnumber:
		net_info = [int(k) for k in fp.readline().strip().split()]
		d = Net_Connection(net_info[1],net_info[2],net_info[3],net_info[4],net_info[5],net_info[6])
		nets.append(d)
	fp.close()
	return nets
	
def route(net_connection,grid,x_gridsize,y_gridsize):
	(src_layer,src_x,src_y) = net_connection.get_src_info()
	(dst_layer,dst_x,dst_y) = net_connection.get_dst_info()
	wavefront = []
	traced  = []
	traced.append(grid[x_gridsize*y_gridsize*src_layer+x_gridsize*src_y+src_x])
	heappush(wavefront,(grid[x_gridsize*src_y+src_x].get_cost(),src_layer,src_x,src_y))
	while(1):
		if len(wavefront) == 0:
			sys.exit(1)
		d = heappop(wavefront) 
		if (d[1] == dst_layer) and (d[2] == dst_x) and (d[3] == dst_y):
			result = backtrace(grid,dst_layer,dst_x,dst_y,src_layer,src_x,src_y)
			cleanup(traced,result) #clear the unused grid as reachable
			break
		y = d[3]
		x = d[2]
		layer = d[1]
		cost = d[0]
		#for k in range(4): #at most 4 neighbours
		if (x-1) >= 0 and grid[x_gridsize*y_gridsize*layer+x_gridsize*y+(x-1)].get_reached():
			grid[x_gridsize*y_gridsize*layer+x_gridsize*y+(x-1)].set_reached(False)
			grid[x_gridsize*y_gridsize*layer+x_gridsize*y+x-1].set_pred("E")
			traced.append(grid[x_gridsize*y_gridsize*layer+x_gridsize*y+x-1])
			heappush(wavefront,(grid[x_gridsize*y+(x-1)].get_cost()+cost,layer,x-1,y))
		if (x+1) < x_gridsize and grid[x_gridsize*y_gridsize*layer+x_gridsize*y+(x+1)].get_reached():
			grid[x_gridsize*y_gridsize*layer+x_gridsize*y+(x+1)].set_reached(False)
			grid[x_gridsize*y_gridsize*layer+x_gridsize*y+x+1].set_pred("W")
			traced.append(grid[x_gridsize*y_gridsize*layer+x_gridsize*y+x+1])
			heappush(wavefront,(grid[x_gridsize*y+(x+1)].get_cost()+cost,layer,x+1,y))
		if (y-1) >= 0 and grid[x_gridsize*y_gridsize*layer+x_gridsize*(y-1)+x].get_reached():
			grid[x_gridsize*y_gridsize*layer+x_gridsize*(y-1)+x].set_reached(False)
			grid[x_gridsize*y_gridsize*layer+x_gridsize*(y-1)+x].set_pred("S")
			traced.append(grid[x_gridsize*y_gridsize*layer+x_gridsize*(y-1)+x])
			heappush(wavefront,(grid[x_gridsize*(y-1)+x].get_cost()+cost,layer,x,y-1))
		if (y+1) < y_gridsize and grid[x_gridsize*y_gridsize*layer+x_gridsize*(y+1)+x].get_reached():
			grid[x_gridsize*y_gridsize*layer+x_gridsize*(y+1)+x].set_reached(False)
			grid[x_gridsize*y_gridsize*layer+x_gridsize*(y+1)+x].set_pred("N")
			traced.append(grid[x_gridsize*y_gridsize*layer+x_gridsize*(y+1)+x])
			heappush(wavefront,(grid[x_gridsize*(y+1)+x].get_cost()+cost,layer,x,y+1))
	return result

def backtrace(grid,dst_layer,dst_x,dst_y,src_layer,src_x,src_y,x_gridsize,y_gridsize):
	result = [grid[x_gridsize*y_gridsize*dst_layer+x_gridsize*dst_y+dst_x]]
	while grid[x_gridsize*y_gridsize*src_layer+x_gridsize*src_y+src_x] not in result:
		top_grid = result[0]
		x = top_grid.x
		y = top_grid.y
		layer = top_grid.layer
		if top_grid.pred == "E":
			result.insert(0,grid[x_gridsize*y_gridsize*layer+x_gridsize*y+x+1])
		elif top_grid.pred == "W":
			result.insert(0,grid[x_gridsize*y_gridsize*layer+x_gridsize*y+x-1])
		elif top_grid.pred == "S":
			result.insert(0,grid[x_gridsize*y_gridsize*layer+x_gridsize*(y+1)+x])
		elif top_grid.pred == "N":
			result.insert(0,grid[x_gridsize*y_gridsize*layer+x_gridsize*(y-1)+x])
	return result
	
def cleanup(traced, result):
	d = [i for i in traced if i not in result]
	for k in d:
		k.set_reached(True)

if __name__ == "__main__":
	grid_file = argv[1]
	nl_file = argv[2]
	out_fp = open('out','w')
	(grid_l,x_gridsize,y_gridsize,BendPenalty,ViaPenalty) = parse_grid(grid_file)
	nets = parse_nl(nl_file)
	out_fp.write('%d\n' %(len(nets)))
	for i in range(len(nets)):
		out_fp.write('%d\n' %(i+1))
		result = route(nets[i],grid_l,x_gridsize,y_gridsize)
		for route_path in result:
			out_fp.write('%d %d %d\n' %(route_path.layer,route_path.x,route_path.y))
		out_fp.write.write('0\n')	
		
		
			
			
			
			
			
			
		
		
	
	
	
	
	


		
