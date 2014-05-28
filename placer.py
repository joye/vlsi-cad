from gate import Gate
from sys import argv
from gate import Pad
from scipy.sparse import coo_matrix
from scipy.sparse.linalg import spsolve
import numpy

def parse_netlist(file):
	fp = open(file,'r')
	gate_net = [int(i) for i in fp.readline().strip().split()]
	gate_dic = {} #gate_index net_connection
	pad_dic = {}  #pad_index net_connection,x,y
	for i in range(gate_net[0]):
		gate_data = [int(j) for j in fp.readline().strip().split()]
		net_data = gate_data[2:]
		c = Gate(gate_data[0],net_data)
		gate_dic[i] = c
	pad_number = int(fp.readline().strip())
	for j in range(pad_number):
		pad_data = [int(t) for t in fp.readline().strip().split()]
		net_data = [pad_data[1]]
		x_cor = pad_data[2]
		y_cor = pad_data[3]
		d = Pad(net_data,x_cor,y_cor)
		pad_dic[j] = d
	fp.close()
	return (gate_dic,pad_dic)

def display_gate_info(gate):
	print "begin to display gate"
	print gate.net_connection
	print gate.index

def display_pad_info(pad):
	print "begin to display pad"
	print pad.net_connection
	print pad.x,pad.y

#this returns this format
#0 ===> [1,2,3] means gate 0 connected to gate 1,2,3 or pad 1,2,3
def connection_info(gate,pad):
	connect_gate = {} #this returns each gate index connected to the gate
	connect_pad = {}  #this returns each pad index connected to the gate
	for i in range(len(gate)):
		connect_gate[i] = []
		connect_pad[i] = []
	for i in range(len(gate)):
		for k in gate[i].net_connection:
			for j in range(i+1,len(gate)):
				if k in gate[j].net_connection:
					if j not in connect_gate[i]:
						connect_gate[i].append(j) 
					if i not in connect_gate[j]:
						connect_gate[j].append(i)
			for t in range(len(pad)):
				if k in pad[t].net_connection:
					if t not in connect_pad[i]:
						connect_pad[i].append(t)
	return (connect_gate,connect_pad)
	
def generate_matrix(gate,pad):
	C = {}
	b_x = {}
	b_y = {}
	for i in range(len(gate)):
		C[i] = {}
		for j in range(len(gate)):
			C[i][j] = 0
	for i in range(len(gate)):
		for k in gate[i].net_connection:
			for j in range(i+1,len(gate)):
				if k in gate[j].net_connection:
					C[i][j] = C[i][j]+1 #if gate i connected to gate j more than once, will add the weight 1
					C[j][i] = C[i][j]
			for t in range(len(pad)):
				if k in pad[t].net_connection:
					if i not in b_x:
						b_x[i] = pad[t].x
						b_y[i] = pad[t].y
						#print "in line 83", b_x[i],b_y[i]
					else:
						b_x[i] = b_x[i]+pad[t].x #if one gate connected to multiple pads, will calculate as w1x1+w2x2, now weight is 1. 
						b_y[i] = b_y[i]+pad[t].y
					C[i][i] = C[i][i]+1 #if one gate connected to multiple pads, will calculate each weight sum w
	for i in range(len(gate)):
		C[i][i] = sum(C[i].values())
	fp = open("data",'w')
	for i in C:
		for j in C[i]:
			if(C[i][j] != 0):
				if(i!=j):
					fp.write('%d %d %d\n' %(i,j,-C[i][j]))
				else:
					fp.write('%d %d %d\n' %(i,j,C[i][j]))
	fp.close()
	fp = open("b_x","w")
	for i in range(len(gate)):
		if i in b_x: 
			fp.write('%.10f\n' %(b_x[i]))
		else:
			fp.write('%f\n' %(0.0))
	fp.close()
	fp = open("b_y","w")
	for i in range(len(gate)):
		if i in b_y:
			fp.write('%.10f\n' %(b_y[i]))
		else:
			fp.write('%f\n' %(0.0))
	fp.close()
	A = numpy.genfromtxt('data')
	b_x_array = numpy.genfromtxt('b_x')
	b_y_array = numpy.genfromtxt('b_y')
	coo = coo_matrix((A[:, 2], (A[:, 0], A[:, 1])),shape = (len(gate),len(gate)))
	x = spsolve(coo.tocsr(), b_x_array)
	y = spsolve(coo.tocsr(), b_y_array)
	return (x,y)

def assignment(x,y,gate):
	result = {i:(100000*x[i]+y[i]) for i in range(len(x))}
	d = sorted(result.keys(),key = lambda x: result[x])
	left_half = d[0:len(d)/2] #this is left gate index
	right_half = d[len(d)/2:] #right gate index
	for i in right_half:
		gate[i].set_left(False) #set left flag to false
	return (left_half,right_half)

def containment(half_index,gate,pad,connect_gate,connect_pad,x,y,left_flag):
	gate_dic = {}
	pad_dic = {}
	gate_index_map = {}
	exist_cor = {}   #used as gate 
	exist_pad_cor = {} #used as pad
	pad_indx = 0
	gate_indx = 0
	for i in half_index: #gate index
		gate_dic[gate_indx] = gate[i]
		gate_index_map[gate_indx] = i #how this gate_indx mapped to real gate index
		gate_indx = gate_indx+1
		if len(connect_gate[i]) != 0:
			for k in connect_gate[i]:
				if left_flag == True:
					if gate[k].left == False:
						if k not in exist_cor:  #one gate only generate one pad, this makes sure if multiple gates in one side connected to one gate in another side,change from coordinate value to index
							exist_cor[k] = 1
							c = Pad(gate[k].net_connection,50.0,y[k]) #generate pad
							pad_dic[pad_indx] = c
							pad_indx = pad_indx+1
				else:
					if gate[k].left == True:
						if k not in exist_cor:
							exist_cor[k] = 1
							c = Pad(gate[k].net_connection,50.0,y[k])
							pad_dic[pad_indx] = c
							pad_indx = pad_indx+1
		if len(connect_pad[i]) != 0:
			for t in connect_pad[i]:
				if left_flag == True:
					if t not in exist_pad_cor:
						exist_pad_cor[t] = 1
						if (pad[t].x > 50.0):
							c = Pad(pad[t].net_connection,50.0,pad[t].y)
							pad_dic[pad_indx] = c
							pad_indx = pad_indx+1
						else:
							pad_dic[pad_indx] = pad[t]
							pad_indx = pad_indx+1
				else:
					if t not in exist_pad_cor:
						exist_pad_cor[t] = 1
						if (pad[t].x < 50.0):
							c = Pad(pad[t].net_connection,50.0,pad[t].y)
							pad_dic[pad_indx] = c
							pad_indx = pad_indx+1
						else:
							pad_dic[pad_indx] = pad[t]
							pad_indx = pad_indx+1
	return (gate_dic,pad_dic,gate_index_map)	
				
		
if __name__ == "__main__":
	(gate,pad) = parse_netlist(argv[1])
	(connect_gate,connect_pad) = connection_info(gate,pad)
	(x,y) = generate_matrix(gate,pad)
	(left,right) = assignment(x,y,gate)
	(gate_left,pad_left,gate_index_left) = containment(left,gate,pad,connect_gate,connect_pad,x,y,True)  #the last is from the generated gate map to real gate
	(x_left,y_left) = generate_matrix(gate_left,pad_left)
	for i in gate_index_left:
		x[gate_index_left[i]] = x_left[i]
		y[gate_index_left[i]] = y_left[i]   #make sure update the left gate coordinate
	(gate_right,pad_right,gate_index_right) = containment(right,gate,pad,connect_gate,connect_pad,x,y,False)  #the last is from the generated gate map to real gate
	(x_right,y_right) = generate_matrix(gate_right,pad_right)
	x_result = {}
	y_result = {}
	for i in gate_index_left:
		x_result[gate_index_left[i]] = x_left[i]
		y_result[gate_index_left[i]] = y_left[i]
	for i in gate_index_right:
		x_result[gate_index_right[i]] = x_right[i]
		y_result[gate_index_right[i]] = y_right[i]
	fp = open('result','w')
	for k in range(len(x_result)):
		fp.write('%d %.8f %.8f\n' %(k+1,x_result[k],y_result[k]))
	fp.close()
	
		
	