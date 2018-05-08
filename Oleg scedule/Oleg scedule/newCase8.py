from pylinprogmaster import linprog
import numpy as np
import random

debug = True
epsilon = 0.01
max_shift_time = 12.0
class Time:
    day = ""
    start = 0
    end = 0
    def __init__(self, day,start,end):
        self.day = day
        self.start = start
        self.end = end
        
class Employee:
    id = 0
    name = ""
    availability = [[]]
    jobs = []
    max_day = [1,1,1,1,1,1,1]
    max_week = 20
    def __init__(self, id, name, availability, jobs):
        self.id = id
        self.name = name
        self.availability = availability
        self.jobs = jobs

class Shift:
    id = 0
    time = Time("",0,0)
    job_id = 0
    number_employees_needed = 1
    def __init__(self,id, time, job_id):
        self.id = id
        self.time = time
        self.job_id = job_id
        self.number_employees_needed = 1

days = ["Sun","Mon","Tue","Wed","Thu","Fri","Sat"]

employees = [
	Employee(
		1, #employee_id
		"Ivan Drago",
		# can be available at this time period
		[
			Time("Sun", 8, 20),
			Time("Mon", 8, 20),
			Time("Wed", 8, 20),
			Time("Fri", 8, 20),
			Time("Sat", 8, 20),
		],
		[1,2] #job_ids
	),
	Employee(
		2, #employee_id
		"Rocky",
		# can be available at this time period
		[
			Time("Sun", 8, 20),
			Time("Mon", 8, 20),
			Time("Wed", 8, 20),
			Time("Fri", 8, 20),
			Time("Sat", 8, 20),
		],
		[1] #job_ids
	),
	Employee(
		3, #employee_id
		"Turbo Man",
		# can be available at this time period
		[
			Time("Sun", 8, 20),
			Time("Mon", 8, 20),
			Time("Wed", 8, 20),
			Time("Fri", 8, 20),
			Time("Sat", 8, 20),
		],
		[1] #job_ids
	),
]

shifts = [
	#shift_id - time period from to - job_id         Expected					Real    
	Shift(1, Time("Sun", 8, 12), 1),     #result -   empty						success
	Shift(2, Time("Mon", 10, 14), 1),    #result -   empty						success
	Shift(3, Time("Wed", 12, 16), 1),    #result -   empty						success
	Shift(4, Time("Fri", 14, 18), 1),    #result -   empty						success
	Shift(5, Time("Sat", 16, 20), 1),    #result -   empty						success

]

number_of_employees = len(employees)
number_of_shifts = len(shifts)

def collision(x,y):
    if(x.day != y.day):
        return(False)
    if(x.end <= y.start):
        return(False)
    if(x.start >= y.end):
        return(False)
    return(True)

def in_time(x,y):  # check if x is in y
    if(x.day != y.day):
        return(False)
    if(x.start < y.start):
        return(False)
    if(x.end > y.end):
        return(False)
    return(True)

def could_do_this_job(s,e): #shift,start time,employee
    if(s.job_id not in e.jobs):
        return(False)
    for t in e.availability:
        if in_time(s.time, t):
            return(True)
    return(False)

def total_time(t):
    res = t.end - t.start
    return res

def get_index(employee,shift,number_of_shifts):
    return(employee*number_of_shifts+shift)

#Ax<=b,max <c,x>
A = []
b = []  
c = []
eq_left = []
eq_right = []

number_variables = number_of_shifts * number_of_employees 
# variables are : 0 - shifts-1 those for employee1, and so on.  to get xij, do
# i * number_of_shifts)+j

#each employee is able to work in a single shift only one time
for i in range(number_variables):
    new_line = np.zeros(number_variables)
    new_line[i] = 1
    A.append(new_line)
    b.append(1)

#shifts constraints:
shift_num = -1
for s in range(number_of_shifts):
    shift_num += 1
    new_line = np.zeros(number_variables)
    for e in range(number_of_employees):
        if(could_do_this_job(shifts[s], employees[e])):  # the employee can do it?
            new_line[get_index(e,s,number_of_shifts)] = 1 # he is only one employee

        else:  # should kill this variable: (so adding the constaint of xij==0
            nl = np.zeros(number_variables)
            nl[get_index(e,s,number_of_shifts)] = 1
            eq_left.append(nl)
            eq_right.append(0)
    A.append(new_line)
    b.append(shifts[s].number_employees_needed)

#week constraints:
for e in range(number_of_employees):
    new_line = np.zeros(number_variables)
    for s in range(number_of_shifts):
        new_line[get_index(e,s,number_of_shifts)] = total_time(shifts[s].time)  # the length of this shift
    A.append(new_line)
    b.append(employees[e].max_week)

#day constraints:
for e in range(number_of_employees):
    for d in range(len(days)):
        new_line = np.zeros(number_variables)
        for s in range(number_of_shifts):
            if(shifts[s].time.day == days[d]):
                new_line[get_index(e,s,number_of_shifts)] = total_time(shifts[s].time)
        A.append(new_line)
        b.append(employees[e].max_day[d])

#check that each employee is only in one place at a time
for s1 in range(number_of_shifts):
    l_collisions = []
    for s2 in range(number_of_shifts):
        if(s1 >= s2):
            continue
        if(collision(shifts[s1].time, shifts[s2].time)):
            l_collisions.append(s2)
    for e in range(number_of_employees):
        new_line = np.zeros(number_variables)
        new_line[get_index(e,s1,number_of_shifts)] = 1
        for s2 in l_collisions:
            new_line[get_index(e,s2,number_of_shifts)] = 1
        A.append(new_line)
        b.append(1)

if(debug):
    for row in range(len(A)):
        output = str(A[row]) + "<=" + str(b[row])
        print(output)

c = np.zeros(number_variables)
for e in range(number_of_employees):
    for s in range(number_of_shifts):
        bonus = np.random.uniform(0,epsilon)
        c[get_index(e,s,number_of_shifts)] = - 1 - bonus

resolution,sol = linprog.linsolve(c,A,b,eq_left,eq_right,range(number_variables))

if(debug): print(sol)

if resolution != "solved":
    print(resolution)
else:
    for s in range(number_of_shifts):
        l = []
        print('shift' + str(shifts[s].id))
        for e in range(number_of_employees):
            if sol[get_index(e,s,number_of_shifts)] > 1 - 1/max_shift_time:
                l.append(employees[e])
            output = "No employee meet shifts requirements"
            if l:
                output = ""
            for e in l:
                output += str(e.name) + "," 
        print("employees: " + output)
