import json
import sys
import pickle

index="index"
#states
addressbook_default = [index,3,5,6,9,15,22,25,27,31,39,58,76,139,163,180,187,497,505]
addressbook_phash00  = [index,3,5,6,11,17,21,38,70,166]
addressbook_phash005 = [index,3,5,6,11,17, 21,38,70,90,96]
addressbook_phash01 = [index,4,6,12,52]
addressbook_phash015 = [index,4,6,27]
addressbook_phash02 = [index,4,6,27]
addressbook_levenstein08 = [index,3,5,8,10,16,23]
addressbook_levenstein09 = [index,3,5,6,11,17,21,23,29,32,37]
addressbook_levenstein095 = [index, 3,5,6,10,16,24,27,29,35,61]
addressbook_levenstein10 = [index,3,5,6,10,16,24,27,29,33,38,57,75,162,179,186]
addressbook_RTED_00 = [index,3,5,6,10,20,23,28,32,37,41,67,70,126,133,152,184,229,275]
addressbook_RTED_01= [index,3,5,6,10,24,27,29,33,38,63,101,104]
addressbook_RTED_02= [index,3,5,8,10,16,22,24,30,68,95,100,125,157]
addressbook_CHYST = [index,3,5,6,10,16,27,31,35,42,45,99,169,193,210,217,530,536]
addressbook_blockhash00 = [index,3,5,6,11,17,21,24,26,30,35,55,58,104,117]
addressbook_blockhash005 = [index,4,6,12,15,21,40,80,83,336]
addressbook_blockhash01 = [index,4,6,12,20,21,39,65,68,72,74,93]

petclinic_default = [index,5,7,9,17,26,45,86,101,123,154]
petclinic_phash00 = [index,3,5,7,15,24,43,85,102,124,130]
petclinic_phash005= [index,3,5,7,15,24,43,80,93,111,120]
petclinic_phash01 = [index,3,5,7,15,24,42,73,84,97]
petclinic_phash02 = [index,3,5,7,15,24,42,76,81]
petclinic_levenstein10 =[index,5,7,9,17,26,45,86,101,123,154]
petclinic_levenstein09 = [index,5,7,9,17,26,44,58,65]
petclinic_levenstein08 = [index,4,6]
petclinic_RTED_00 =[index,3,5,7,15,24,42,62,66,72,78]
petclinic_RTED_01 = [index,3,5,17,20,38,61,70]
petclinic_RTED_02 = [index,3,5,17,20,38,61,70]
petclinic_CHYST =[index,3,5,7,15,24,43,84,99,121,152]
petclinic_blockhash00 = [index,3,5,7,15,24,43,84,93,111,127]
petclinic_blockhash005 =[index,3,5,7,15,24,43,69,75,81,87]
petclinic_blockhash01 = [index,3,5,7,15,24,43,69,75,87,123]


claroline_default = [index,4,7,9,12,14,23,27,29,31,33,109,113,503]
claroline_phash00 = [index,3,6,8,11,21,25,27,71,117]
claroline_phash005= [index,3,6,8,20,26]
claroline_phash01 = [index,3]
claroline_phash02 = [index,3]
claroline_levenstein10 =[index,4,7,9,12,14,23,27,29,31,33,109,113]
claroline_levenstein09 = [index,3,6,8,11,20,24,31,130]
claroline_levenstein08 = [index]
claroline_RTED_00 = [index,3,6,8,11,13,21,25,27,29,31,84,88,177,202,209,320,456,460,478,494,498,521,526,538,554,557,581,591]
claroline_RTED_01 = [index,3,6,8,11,13,20,24,26,28,30,142,149,154,235,240,246,262,271,282,308,327,390,537,579,608,734,753]
claroline_RTED_02 = [index,3,6,8,11,20,24,31,112]
claroline_CHYST = [index,3,6,8,11,13,21,25,27,29,31,86,90,214,475,757]
claroline_blockhash00 = [index,3,6,8,11,13,21,25,27,29,31,87,91,204,242,263,507,695,914,936,965,971,1007,1010,1024,1055,1060]
claroline_blockhash005 = [index,3,6,8,11,13,21,25,27,29,31,87,91,196,229,244,444,678,700,747,761,780,794,809,813,816,849,906]
claroline_blockhash01 = [index,3,6,8,11,13,20,24,26,28,30,77,173,199,209,337,416,450,457,481,499,509,750,819]


phonecat_default = [index,2]
phonecat_phash00 = [index,2]
phonecat_phash005= [index,2]
phonecat_phash01 = [index,2]
phonecat_phash02 = [index,2]
phonecat_levenstein10 =[index,2]
phonecat_levenstein09 = [index,2]
phonecat_levenstein08 = [index,2]
phonecat_RTED_00 =[index,2]
phonecat_RTED_01 = [index,2]
phonecat_RTED_02 = [index,2]
phonecat_CHYST =[index,2]
phonecat_blockhash00 = [index,2]
phonecat_blockhash005 = [index,2]
phonecat_blockhash01 =[index,2]

stateSet = {"addressbook_default" : addressbook_default,
"addressbook_phash00" : addressbook_phash00, 
"addressbook_phash005" : addressbook_phash005,
"addressbook_phash01" : addressbook_phash01,
"addressbook_phash02" : addressbook_phash02,
"addressbook_levenstein10" : addressbook_levenstein10,
"addressbook_levenstein09" : addressbook_levenstein09,
"addressbook_levenstein08" : addressbook_levenstein08,
"addressbook_RTED_00" : addressbook_RTED_00,
"addressbook_RTED_01" : addressbook_RTED_01,
"addressbook_RTED_02" : addressbook_RTED_02,
"addressbook_CHYST" : addressbook_CHYST,
"addressbook_blockhash00" : addressbook_blockhash00,
"addressbook_blockhash005" : addressbook_blockhash005,
"addressbook_blockhash01" : addressbook_blockhash01,

"petclinic_default" : petclinic_default,
"petclinic_phash00" : petclinic_phash00, 
"petclinic_phash005" : petclinic_phash005,
"petclinic_phash01" : petclinic_phash01,
"petclinic_phash02" : petclinic_phash02,
"petclinic_levenstein10" : petclinic_levenstein10,
"petclinic_levenstein09" : petclinic_levenstein09,
"petclinic_levenstein08" : petclinic_levenstein08,
"petclinic_RTED_00" : petclinic_RTED_00,
"petclinic_RTED_01" : petclinic_RTED_01,
"petclinic_RTED_02" : petclinic_RTED_02,
"petclinic_CHYST" : petclinic_CHYST,
"petclinic_blockhash00" : petclinic_blockhash00,
"petclinic_blockhash005" : petclinic_blockhash005,
"petclinic_blockhash01" : petclinic_blockhash01,

"claroline_default" : claroline_default,
"claroline_phash00" : claroline_phash00, 
"claroline_phash005" : claroline_phash005,
"claroline_phash01" : claroline_phash01,
"claroline_phash02" : claroline_phash02,
"claroline_levenstein10" : claroline_levenstein10,
"claroline_levenstein09" : claroline_levenstein09,
"claroline_levenstein08" : claroline_levenstein08,
"claroline_RTED_00" : claroline_RTED_00,
"claroline_RTED_01" : claroline_RTED_01,
"claroline_RTED_02" : claroline_RTED_02,
"claroline_CHYST" : claroline_CHYST,
"claroline_blockhash00" : claroline_blockhash00,
"claroline_blockhash005" : claroline_blockhash005,
"claroline_blockhash01" : claroline_blockhash01,

"phonecat_default" : phonecat_default,
"phonecat_phash00" : phonecat_phash00, 
"phonecat_phash005" : phonecat_phash005,
"phonecat_phash01" : phonecat_phash01,
"phonecat_phash02" : phonecat_phash02,
"phonecat_levenstein10" : phonecat_levenstein10,
"phonecat_levenstein09" : phonecat_levenstein09,
"phonecat_levenstein08" : phonecat_levenstein08,
"phonecat_RTED_00" : phonecat_RTED_00,
"phonecat_RTED_01" : phonecat_RTED_01,
"phonecat_RTED_02" : phonecat_RTED_02,
"phonecat_CHYST" : phonecat_CHYST,
"phonecat_blockhash00" : phonecat_blockhash00,
"phonecat_blockhash005" : phonecat_blockhash005,
"phonecat_blockhash01" : phonecat_blockhash01
        }
#locations


location_addressbook_default = "/home/fraggen/localhost/addressbook/Addressbook_default_1hr/"
location_addressbook_phash00 = "/home/fraggen/localhost/addressbook/Addressbook_phash_0.0_1hr/"
location_addressbook_phash005 = "/home/fraggen/localhost/addressbook/Addressbook_phash_0.05_1hr/"
location_addressbook_phash01 = "/home/fraggen/localhost/addressbook/Addressbook_phash_0.1_1hr/"
location_addressbook_phash015 = "/home/fraggen/localhost/addressbook/Addressbook_phash_0.15_1hr/"
location_addressbook_phash02 = "/home/fraggen/localhost/addressbook/Addressbook_phash_0.2_1hr/"
location_addressbook_levenstein08 = "/home/fraggen/localhost/addressbook/Addressbook_levenstein_0.8_1hr/"
location_addressbook_levenstein09 = "/home/fraggen/localhost/addressbook/Addressbook_levenstein_0.9_1hr/"
location_addressbook_levenstein095 = "/home/fraggen/localhost/addressbook/Addressbook_levenstein_0.95_1hr/"
location_addressbook_levenstein10 = "/home/fraggen/localhost/addressbook/Addressbook_levenstein_1.0_1hr/"
location_addressbook_RTED_00 = "/home/fraggen/localhost/addressbook/Addressbook_RTED_0.0_1hr/"
location_addressbook_RTED_01 ="/home/fraggen/localhost/addressbook/Addressbook_RTED_0.1_1hr/"
location_addressbook_RTED_02 = "/home/fraggen/localhost/addressbook/Addressbook_RTED_0.2_1hr/"
location_addressbook_CHYST = "/home/fraggen/localhost/addressbook/addressbook_chyst_1hr/"
location_addressbook_blockhash00 = "/home/fraggen/localhost/addressbook/Addressbook_blockHash_0.0_1hr/" 
location_addressbook_blockhash005 = "/home/fraggen/localhost/addressbook/Addressbook_blockHash_0.05_1hr/" 
location_addressbook_blockhash01 = "/home/fraggen/localhost/addressbook/Addressbook_blockHash_0.1_1hr/" 


location_petclinic_default ="/home/fraggen/localhost/Petclinic/petclinic_default_1hr/"
location_petclinic_phash00 = "/home/fraggen/localhost/Petclinic/Petclinic_phash_0.0_1hr/"
location_petclinic_phash005 = "/home/fraggen/localhost/Petclinic/Petclinic_phash_0.05_1hr/"
location_petclinic_phash01 = "/home/fraggen/localhost/Petclinic/Petclinic_phash_0.1_1hr/"
location_petclinic_phash02 = "/home/fraggen/localhost/Petclinic/Petclinic_phash_0.2_1hr/"
location_petclinic_levenstein10 = "/home/fraggen/localhost/Petclinic/Petclinic_levenstein_1.0_1hr/"
location_petclinic_levenstein09 = "/home/fraggen/localhost/Petclinic/Petclinic_levenstein_0.9_1hr/"
location_petclinic_levenstein08 = "/home/fraggen/localhost/Petclinic/Petclinic_levenstein_0.8_1hr/"
location_petclinic_RTED_00 = "/home/fraggen/localhost/Petclinic/petclinic_RTED_0_1hr/"
location_petclinic_RTED_01 = "/home/fraggen/localhost/Petclinic/petclinic_RTED_0.1_1hr/"
location_petclinic_RTED_02 = "/home/fraggen/localhost/Petclinic/petclinic_RTED_0.2_1hr/"
location_petclinic_CHYST = "/home/fraggen/localhost/Petclinic/Petclinic_cHyst_1.0_1hr_150states/"
location_petclinic_blockhash00 = "/home/fraggen/localhost/Petclinic/Petclinic_blockHash_0.0_1hr/"
location_petclinic_blockhash005 = "/home/fraggen/localhost/Petclinic/Petclinic_blockHash_0.05_1hr/"
location_petclinic_blockhash01 = "/home/fraggen/localhost/Petclinic/Petclinic_blockHash_0.1_1hr/"

location_claroline_default = "/home/fraggen/localhost/claroline/claroline_user_course_default_1hr/"
location_claroline_phash00 = "/home/fraggen/localhost/claroline/claroline_user_course_Phash_00_1hr/"
location_claroline_phash005 = "/home/fraggen/localhost/claroline/claroline_user_course_Phash_0.05_1hr/"
location_claroline_phash01 = "/home/fraggen/localhost/claroline/claroline_user_course_Phash_0.1_1hr/"
location_claroline_phash02 = "/home/fraggen/localhost/claroline/claroline_user_course_Phash_0.2_1hr/"
location_claroline_levenstein10 = "/home/fraggen/localhost/claroline/claroline_user_course_levenstein_1.0_1hr/"
location_claroline_levenstein09 = "/home/fraggen/localhost/claroline/claroline_user_course_levenstein_0.9_1hr/"
location_claroline_levenstein08 = "/home/fraggen/localhost/claroline/claroline_user_course_levenstein_1.0_1hr/"
location_claroline_RTED_00 = "/home/fraggen/localhost/claroline/claroline_user_course_RTED_00_1hr/"
location_claroline_RTED_01 ="/home/fraggen/localhost/claroline/claroline_user_course_RTED_0.1_1hr/"
location_claroline_RTED_02 ="/home/fraggen/localhost/claroline/claroline_user_course_RTED_0.2_1hr/"
location_claroline_CHYST = "/home/fraggen/localhost/claroline/Claroline_user_course_cHyst_1hr/"
location_claroline_blockhash00 = "/home/fraggen/localhost/claroline/claroline_user_course_blockHash_0.0_1hr/"
location_claroline_blockhash005 = "/home/fraggen/localhost/claroline/claroline_user_course_blockHash_0.05_1hr/"
location_claroline_blockhash01 = "/home/fraggen/localhost/claroline/claroline_user_course_blockHash_0.1_1hr/"

location_phonecat_default = "/home/fraggen/localhost/Phonecat/phonecat_default_1hr/"
location_phonecat_phash00 = "/home/fraggen/localhost/Phonecat/Phonecat_phash_0.0_1hr/"
location_phonecat_phash005 = "/home/fraggen/localhost/Phonecat/Phonecat_phash_0.05_1hr/"
location_phonecat_phash01 = "/home/fraggen/localhost/Phonecat/Phonecat_phash_0.1_1hr/"
location_phonecat_phash02 = "/home/fraggen/localhost/Phonecat/Phonecat_phash_0.1_1hr/"
location_phonecat_levenstein10 = "/home/fraggen/localhost/Phonecat/phonecat_levenstein_1.0_1hr/"
location_phonecat_levenstein09 = "/home/fraggen/localhost/Phonecat/phonecat_levenstein_0.9_1hr/"
location_phonecat_levenstein08 = "/home/fraggen/localhost/Phonecat/phonecat_levenstein_0.8_1hr/"
location_phonecat_RTED_00 = "/home/fraggen/localhost/Phonecat/phonecat_RTED_0.0_1hr/"
location_phonecat_RTED_01 = "/home/fraggen/localhost/Phonecat/phonecat_RTED_0.1_1hr/"
location_phonecat_RTED_02 = "/home/fraggen/localhost/Phonecat/phonecat_RTED_0.2_1hr/"
location_phonecat_CHYST = "/home/fraggen/localhost/Phonecat/Phonecat_chyst_1hr/"
location_phonecat_blockhash00 = "/home/fraggen/localhost/Phonecat/Phonecat_blockHash_0.0_1hr/"
location_phonecat_blockhash005 = "/home/fraggen/localhost/Phonecat/Phonecat_blockHash_0.05_1hr/"
location_phonecat_blockhash01 = "/home/fraggen/localhost/Phonecat/Phonecat_blockHash_0.1_1hr/"

locations = {"location_addressbook_default" : location_addressbook_default,
"location_addressbook_phash00" : location_addressbook_phash00, 
"location_addressbook_phash005" : location_addressbook_phash005,
"location_addressbook_phash01" : location_addressbook_phash01,
"location_addressbook_phash02" : location_addressbook_phash02,
"location_addressbook_levenstein10" : location_addressbook_levenstein10,
"location_addressbook_levenstein09" : location_addressbook_levenstein09,
"location_addressbook_levenstein08" : location_addressbook_levenstein08,
"location_addressbook_RTED_00" : location_addressbook_RTED_00,
"location_addressbook_RTED_01" : location_addressbook_RTED_01,
"location_addressbook_RTED_02" : location_addressbook_RTED_02,
"location_addressbook_CHYST" : location_addressbook_CHYST,
"location_addressbook_blockhash00" : location_addressbook_blockhash00,
"location_addressbook_blockhash005" : location_addressbook_blockhash005,
"location_addressbook_blockhash01" : location_addressbook_blockhash01,

"location_petclinic_default" : location_petclinic_default,
"location_petclinic_phash00" : location_petclinic_phash00, 
"location_petclinic_phash005" : location_petclinic_phash005,
"location_petclinic_phash01" : location_petclinic_phash01,
"location_petclinic_phash02" : location_petclinic_phash02,
"location_petclinic_levenstein10" : location_petclinic_levenstein10,
"location_petclinic_levenstein09" : location_petclinic_levenstein09,
"location_petclinic_levenstein08" : location_petclinic_levenstein08,
"location_petclinic_RTED_00" : location_petclinic_RTED_00,
"location_petclinic_RTED_01" : location_petclinic_RTED_01,
"location_petclinic_RTED_02" : location_petclinic_RTED_02,
"location_petclinic_CHYST" : location_petclinic_CHYST,
"location_petclinic_blockhash00" : location_petclinic_blockhash00,
"location_petclinic_blockhash005" : location_petclinic_blockhash005,
"location_petclinic_blockhash01" : location_petclinic_blockhash01,

"location_claroline_default" : location_claroline_default,
"location_claroline_phash00" : location_claroline_phash00, 
"location_claroline_phash005" : location_claroline_phash005,
"location_claroline_phash01" : location_claroline_phash01,
"location_claroline_phash02" : location_claroline_phash02,
"location_claroline_levenstein10" : location_claroline_levenstein10,
"location_claroline_levenstein09" : location_claroline_levenstein09,
"location_claroline_levenstein08" : location_claroline_levenstein08,
"location_claroline_RTED_00" : location_claroline_RTED_00,
"location_claroline_RTED_01" : location_claroline_RTED_01,
"location_claroline_RTED_02" : location_claroline_RTED_02,
"location_claroline_CHYST" : location_claroline_CHYST,
"location_claroline_blockhash00" : location_claroline_blockhash00,
"location_claroline_blockhash005" : location_claroline_blockhash005,
"location_claroline_blockhash01" : location_claroline_blockhash01,

"location_phonecat_default" : location_phonecat_default,
"location_phonecat_phash00" : location_phonecat_phash00, 
"location_phonecat_phash005" : location_phonecat_phash005,
"location_phonecat_phash01" : location_phonecat_phash01,
"location_phonecat_phash02" : location_phonecat_phash02,
"location_phonecat_levenstein10" : location_phonecat_levenstein10,
"location_phonecat_levenstein09" : location_phonecat_levenstein09,
"location_phonecat_levenstein08" : location_phonecat_levenstein08,
"location_phonecat_RTED_00" : location_phonecat_RTED_00,
"location_phonecat_RTED_01" : location_phonecat_RTED_01,
"location_phonecat_RTED_02" : location_phonecat_RTED_02,
"location_phonecat_CHYST" : location_phonecat_CHYST,
"location_phonecat_blockhash00" : location_phonecat_blockhash00,
"location_phonecat_blockhash005" : location_phonecat_blockhash005,
"location_phonecat_blockhash01" : location_phonecat_blockhash01
        }

#####################################################
#configuration
for resultName in stateSet:
    location = locations["location_" + resultName]
    states = stateSet[resultName]
    
    #print(location)
    #print(states)
    #code
    indexTime = 0;
    timedata = []

    #print(location)

    with open(location+"result.json", encoding="utf-8") as read_file:
            data = json.load(read_file)
            indexTime = data["states"][index]["timeAdded"]
            timedata.append(0)
            for state in states:
                    if(state == index):
                            continue
                    timeAdded = data["states"]["state"+str(state)]["timeAdded"]
                    timeAdded = (timeAdded-indexTime)/60000
                    timedata.append(timeAdded)

    with open(location+'timedata.json', 'w') as fp:
        json.dump(timedata, fp)

    #f = open(location+"timedata.txt",'wb')
    #pickle.dump(timedata,f, protocol=pickle.HIGHEST_PROTOCOL)
    #f.close()
    resultNameroot = resultName[:resultName.find("_")]
    print("x_" + resultName + " <- c(" + str(timedata)[1:-1] + ")")
    print("y_" + resultName + " <- c()")
    print("for (i in 1:length(x_" + resultName + "))" + "{" + "y_" + resultName + "[i] <- (i/maxy" + "_" + resultNameroot + ")*100}")
    print()


        
