import pickle
from .Reader import Customer, read_customers, read_customers_zhang

PATH = "Datasets\\"
FILENAME = "_distmatrix.txt"
CFILENAME = "_distmatrix_cpp.txt"
def generate_dist_matrix(customers):
    dist_matrix = []
    for customer in customers:
        temp = []
        for customer2 in customers:
            dist = round(((customer.info.x - customer2.info.x)**2 + (customer.info.y - customer2.info.y)**2)**(1/2),3) 
            temp.append(dist)
        dist_matrix.append(temp)
    return dist_matrix

def output_dist_matrix(data, filename):
    full_path = PATH + filename
    with open(full_path, 'w') as f:
        f.write(str(len(data))+'\n')
        for line in data:
            string = ' '.join(str(item) for item in line)
            f.write(string+'\n')

##for i in range (1, 3):
    ##for j in range (1, 9):
     ##   cust = read_customers_zhang('c'+str(i)+'0'+str(j)+'_100.txt')
      ##  mat = generate_dist_matrix(cust)
      ##  output_dist_matrix(mat, 'c'+str(i)+'0'+str(j)+'_100'+CFILENAME)
##
##for i in range (1, 10):
##    cust = read_customers('r'+'1'+'0'+str(i)+'.txt')
##    mat = generate_dist_matrix(cust)
##    output_dist_matrix(mat, 'r'+'1'+'0'+str(i)+CFILENAME)
##
##for i in range (11, 13):
##    cust = read_customers('r'+'1'+str(i)+'.txt')
##    mat = generate_dist_matrix(cust)
##    output_dist_matrix(mat, 'r'+'1'+str(i)+CFILENAME)    
##    
##for i in range (1, 10):
##    cust = read_customers('r'+'2'+'0'+str(i)+'.txt')
##    mat = generate_dist_matrix(cust)
##    output_dist_matrix(mat, 'r'+'2'+'0'+str(i)+CFILENAME)
##
##for i in range (11, 12):
##    cust = read_customers('r'+'2'+str(i)+'.txt')
##    mat = generate_dist_matrix(cust)
##    output_dist_matrix(mat, 'r'+'2'+str(i)+CFILENAME)

##for i in range (1, 3):
##    for j in range (1, 9):
##        cust = read_customers('rc'+str(i)+'0'+str(j)+'.txt')
##        mat = generate_dist_matrix(cust)
##        output_dist_matrix(mat, 'rc'+str(i)+'0'+str(j)+CFILENAME)
