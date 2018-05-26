import sys
import re
import itertools


phi = None
M = {}
MS = {}
I = []
T = [[]]
n = None
C = []
F = []
L = []
cannotBeTogether = []
mustHave = []
support_value_dict = {}
tCount_dict = {}
k = 0
set_count = {}


def getInputData(inputTransaction):
    global inputData, allItems

    with open(inputTransaction, 'r') as f:
        T = [re.findall(r'\d+',line.strip()) for line in f]

    for i in range(len(T)):
        T[i] = [int(x) for x in T[i]]


    return T


def getParameterData(parameterFile):
    global phi, MS, cannotBeTogether, mustHave

    file = open(parameterFile, "r")            #Opening the parameter.txt file in READ mode only

    for line in file:                          #Iterating through all the lines in the file

        if line[:3] == "MIS":                        #Comparing if the first three letters of the first item is 'MIS'
            element = re.match(r"MIS\((\d+)\)\s=\s(.*)", line)       #Matching with the regular expression MIS (digits from 0-9)space=space{matching all the characters}
            #element = re.search('\S*\((\d*)\)\D*(\d\.?\d*)', line)
            MS[int(element.group(1))] = float(element.group(2))

        if line[:3] == "SDC":                     #Comparing if the first three letters of the first item is 'SDC'
            element = re.match(r"SDC\s=\s(.*)", line)   #Matching with the regular expression  'SDC space=space {matching all the characters}'
            phi = float(element.group(1))

        if line[:18] == "cannot_be_together":      #Comparing if the first 18 letters of the first item is 'cannot_be_together'
            values = re.findall("{(\d+(,*\s*\d+)*)}", line)
            for value in values:
                allItems = re.findall(r"\d+", value[0])             #matching with the regex - one or more digits
                allItems = [int(i) for i in allItems]              # Parsing the string values to int type
                cannotBeTogether.append(allItems)

        if line[:9] == "must-have":             #Comparing if the first 9 letters of the first item is 'must-have'
            allItems = re.findall(r"\d+", line)    #matching with the regex - one or more digits
            allItems = [int(i) for i in allItems]     # Parsing the string values to int type
            for i in allItems:
                mustHave.append([i])

    file.close()
    return phi, MS, cannotBeTogether, mustHave


def sort(I,MS):
    global M
    M = dict(sorted(MS.items(), key=lambda x: x[1]))
    print("Sorted MIS with lowest MIS val",M)


def initpass(M,T):

    global L,F,n,support_value_dict,tCount_dict,k, C
    F = [[]] * len(MS.keys())
    C = [[]] * len(MS.keys())
    k = k+1
    for item in MS.keys():
        support_value_dict[item] = 0
        tCount_dict[item] = 0

    for item in MS.keys():
        for data in T:
            if item in data:
                tCount_dict[item] += data.count(item)
                support_value_dict[item] += data.count(item)/n

    print("Support value dict",support_value_dict)
    print("tCount",tCount_dict)


    counter=0
    for item in M.keys():
        counter += 1
        if support_value_dict[item] >= MS[item]:
            L.append(item)
            break


    if len(L) == 1:
        for item in list(M.keys())[counter:]:
            if tCount_dict[item]/n >= MS[L[0]]:
                L.append(item)
    f=[]
    for item in L:
        if tCount_dict[item]/n >= M[item]:
            f.append(item)
    F[1] = f


def level2_candidate_gen(L, phi):
    global k, tCount_dict, support_value_dict, MS
    global C
    temp_c = []
    for i in range(0,len(L)-1):
        if tCount_dict[L[i]]/n >= MS[L[i]]:
            for j in range(i+1,len(L)):
                if tCount_dict[L[j]]/n >= MS[L[i]] and abs(support_value_dict[L[j]]-support_value_dict[L[i]]) <= phi:
                    temp_c.append((L[i], L[j]))
    C[k] = temp_c


def MScandidate_gen(k, phi):
    Ck = []
    for i in range(0, len(F[k-1])):
        temp1 = F[k-1][i]
        for item in F[k-1][i:]:
            temp_list=[]
            if temp1[0] == item[0] and temp1[1:-2] == item[1:-2] and temp1[-1] < item[-1] and abs(support_value_dict[temp1[-1]] - support_value_dict[item[-1]]) <= phi :
                temp_list = [x for x in temp1]
                temp_list.append(item[-1])
                Ck.append(tuple(temp_list))
    print("Ck",Ck)
    print("length of Ck",len(Ck))
    print("k", k)
    temp_Ck = Ck
    print("Before pruning Ck",Ck)
    for c in Ck:
        s = [list(i)for i in itertools.combinations(c, k-1)]
        print("S", s)
        if c[0] in s or MS[c[1]] == MS[c[0]]:
            if s not in F[k-1]:
                print("C", c)
                temp_Ck.remove(c)
    print("after pruning", temp_Ck)
    C[k] = temp_Ck


def MSApriori():
    global C
    #data sorted
    sort(I, MS)

    #get L and F1
    initpass(M,T)
    global k
    k = k+1
    print("K = ",k)

    #while k != 6:
    while len(F[k-1]) != 0:
        if k == 2:
            level2_candidate_gen(L, phi)
        else:
            MScandidate_gen(k, phi)


        cCount = {}

        for eachC in C[k]:
            sorted_eachC = tuple(sorted(eachC, key=lambda i: MS[i]))
            cCount[sorted_eachC] = 0

        for t in T:
            for eachC in C[k]:
                if set(t) & set(eachC) == set(eachC):
                    sorted_eachC = tuple(sorted(eachC, key=lambda i: MS[i]))
                    cCount[sorted_eachC] += 1


        for item in cCount.keys():
            tCount_dict[item] = cCount[item]

        Fk=[]
        for eachC in C[k]:
            sorted_eachC = tuple(sorted(eachC, key=lambda i: MS[i]))
            if cCount[sorted_eachC]/n >= MS[eachC[0]]:
                Fk.append(eachC)

        F[k] = Fk
        print("F[k]", F[k])
        print("length", len(F[k]))
        k += 1


def apply_constraints(cannotBeTogether, mustHave):

    mustHave = [j for i in mustHave for j in i]
    print(mustHave)
    #k=0 #F is empty
    #k=1
    Final_list=[]
    for i in mustHave:
        for j in F[1]:
            if i == j:
                Final_list.append(j)

    #k>2
    temp_list = []
    for item in F[2:]:
        for i in mustHave:
            for j in item:
                if i in j:
                    temp_list.append(j)

    for i in cannotBeTogether:
        i_val = len(i)
        for item in temp_list:
            del_counter = 0
            for j in i:
                if j in item:
                    del_counter += 1
            if del_counter < i_val:
                Final_list.append(item)


    print("Final", Final_list)

    return Final_list



def main():
    global T, phi, MS, n
    inputTransaction = 'input-data.txt'
    parameterFile = 'parameter-file.txt'
    outputFile = 'result.txt'

    T = getInputData(inputTransaction)
    n = len(T)
    print("transaction DB", T)
    print("n", n)

    phi, MS, cannotBeTogether, mustHave = getParameterData(parameterFile)
    print("PHI", phi)
    print("MS", MS)

    MSApriori()
    print("F",F)
    print(tCount_dict)
    print(cannotBeTogether)
    print(mustHave)
    Final_list = apply_constraints(cannotBeTogether, mustHave)


    with open(outputFile, 'w') as w:
        for item in Final_list:
            w.write("{} : {}\n".format(item, tCount_dict[item]))


    w.close()


if __name__ == "__main__":
    main()