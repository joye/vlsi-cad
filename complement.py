from sys import argv
#the file format is like this:
#index size
#cube size
#cube list (cube item number the corresponding cube item)
def read_input(f):
	fp = open(f,'r')
	data = [line.strip() for line in fp.readlines()]
	fp.close()
	return data

def post_parse(data):
	index_size = int(data[0])
	cube_size =  int(data[1])
	cube_list = data[2:(cube_size+2)]
	return (index_size,cube_size,cube_list) #include index size and cube list

def checkforsimple(index_size,cube_size,cube_list):
	if cube_size == 1:
		return (True,1)
	elif cube_size == 0: #F = 0 issue
		return (True,0)
	else:
		for i in cube_list:
			if (i[0] == 0):
				return (True,2)
		return (False,0)

def select_most_binate(index_size,cube_size,cube_list):
	result = {} #this type is {2(index y):{1(y):[0,1,2],-1(-y):[3,4]},...} 
	unate_cube = {}
	binate_cube = {}
	for i in range(cube_size):
		cube = cube_list[i]
		real_cube = cube[1:]
		for cube_item in real_cube:
			data = int(cube_item/abs(cube_item))
			if abs(cube_item) in result:
				if data in result[abs(cube_item)]:
					result[abs(cube_item)][data].append(i)
				else:
					result[abs(cube_item)][data] = [i]
			else:
				result[abs(cube_item)] = {}
				result[abs(cube_item)][data] = [i]
	for item in result:
		if len(result[item].keys()) == 1: #unate
			for i in result[item].keys():
				unate_cube[item] = len(result[item][i])
		elif len(result[item].keys()) == 2: #binate
				T = len(result[item][1])
				C = len(result[item][-1])
				binate_cube[item] = abs(T-C)
	if len(binate_cube.keys()) != 0: 
		d = sorted(binate_cube.keys(),key = lambda x: binate_cube[x])
		return (d[0],result[d[0]])
	else:
		d = sorted(unate_cube.keys(),key = lambda x: unate_cube[x])
		return (d[0],result[d[0]]) #return the binate variable and the each cube's index including this variable
		
		
def positive_cofactor(index_size,cube_size,cube_list,variable,index_hash):
	temp_cube_list = [i for i in cube_list]
	for i in index_hash:
		index_list = index_hash[i]
		if i == 1:
			for index in index_list:
				cube = temp_cube_list[index]
				cube_s = cube[0]
				cube_t = cube[1:]
				cube_t.remove(variable)
				cube_s = cube_s - 1
				cube_t.insert(0,cube_s)
				temp_cube_list[index] = cube_t
		elif i == -1:
			for index in index_list:
				temp_cube_list[index] = 0 #has error, now should be fixed
				cube_size = cube_size - 1
	temp_cube_list = [i for i in temp_cube_list if i!=0]
	return (index_size-1,cube_size,temp_cube_list)
			
def negative_cofactor(index_size,cube_size,cube_list,variable,index_hash):
	temp_cube_list = [i for i in cube_list]
	for i in index_hash:
		index_list = index_hash[i]
		if i == 1:
			for index in index_list:
				temp_cube_list[index] = 0
				cube_size = cube_size - 1
		elif i == -1:
			for index in index_list:
				cube = temp_cube_list[index]
				cube_s = cube[0]
				cube_t = cube[1:]
				cube_t.remove(-variable)
				cube_s = cube_s - 1
				cube_t.insert(0,cube_s)
				temp_cube_list[index] = cube_t
	temp_cube_list = [i for i in temp_cube_list if i!=0]
	return (index_size-1,cube_size,temp_cube_list)			
		
def and_op(variable,index_size,cube_size,cube_list):
	index_size = index_size+1
	result_list = []
	for i in range(cube_size):
		cube_s = cube_list[i][0]
		cube_l = cube_list[i][1:]
		cube_l.append(variable)
		d = sorted(cube_l,key = lambda x: abs(x))
		d.insert(0,cube_s+1)
		result_list.append(d)
	return(index_size,cube_size,result_list)
		
def or_op(p_index_size,p_cube_size,p_cube_list,n_index_size,n_cube_size,n_cube_list):
	result_index_size = p_index_size
	result_cube_size = p_cube_size+n_cube_size
	result_cube_list = p_cube_list+n_cube_list
	return (result_index_size,result_cube_size,result_cube_list)
    		
def Complement(index_size,cube_size,cube_list):		
	(simple_result,simple_type) = checkforsimple(index_size,cube_size,cube_list)
	if simple_result == True:
		if simple_type == 0: #F = 0 issue
			result_index_size = index_size
			result_cube_size = 1
			result_cube_list = [[0]]
		elif simple_type == 1: #has one cube
			cube = cube_list[0] # still a list
			cube_item_size = cube[0]
		    #cube_items = cube[1:]
			if cube_item_size == 0: # F = 1 issue
				result_cube_list = [[]]
				result_cube_size = 0
				result_index_size = index_size
			else: #contains just one cube
				cube_items = cube[1:]
				result_index_size = index_size
				result_cube_size = len(cube_items)
				result_cube_list = [[1,0-item] for item in cube_items] #using DeMorgan Laws
				#result_cube_list.insert(0,cube_item_size)
		elif simple_type == 2: #has more cubes, contains all don't care cube
			result_cube_list = [[]]
			result_cube_size = 0
			result_index_size = index_size
		return (result_index_size,result_cube_size,result_cube_list)
	else:
		(variable,index_hash) = select_most_binate(index_size,cube_size,cube_list)
		(positive_index,positive_cube,positive_list) = positive_cofactor(index_size,cube_size,cube_list,variable,index_hash)
		(negative_index,negative_cube,negative_list) = negative_cofactor(index_size,cube_size,cube_list,variable,index_hash)
		(positive_r_i,positive_r_c,positive_r_l) = Complement(positive_index,positive_cube,positive_list) #P 
		(negative_r_i,negative_r_c,negative_r_l) = Complement(negative_index,negative_cube,negative_list) #N 
		(p_index_size,p_cube_size,p_cube_list) = and_op(variable,positive_r_i,positive_r_c,positive_r_l)
		(n_index_size,n_cube_size,n_cube_list) = and_op(-variable,negative_r_i,negative_r_c,negative_r_l)
		return or_op(p_index_size,p_cube_size,p_cube_list,n_index_size,n_cube_size,n_cube_list)
		
		
			
		
	
if __name__ == "__main__":
	data = read_input(argv[1])
	parsed = post_parse(data)
	index_size = parsed[0]
	cube_size = parsed[1]
	cube_list = parsed[2]
	cubes = [[cube] for cube in cube_list]
	t = [i.split() for cube in cubes for i in cube]
	cube_list = [[int(j) for j in i] for i in t]
	#print(cube_list)
	(result_index_size,result_cube_size,result_cube_list) = Complement(index_size,cube_size,cube_list)
	wr_fp = open(argv[1]+"_result",'w')
	wr_fp.write('%d\n' %(result_index_size))
	wr_fp.write('%d\n' %(result_cube_size))
	for i in result_cube_list:
		for j in i:
			wr_fp.write('%d ' %(j))
		wr_fp.write('\n')
	wr_fp.close()
	#print(result_cube_list)
	#simple_ = checkforsimple(index_size,cube_size,cube_list)
	
	
