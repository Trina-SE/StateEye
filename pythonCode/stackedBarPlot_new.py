import numpy as np
import matplotlib.pyplot as plt

from globalNames import ORACLES, MUTATORS

oracleMap = {'warn': {'mutation': 'warn', 'total': 0, 'rted': 0, 'rted_text': 0, 'hist': 0, 'string': 0, 'string_content': 0, 'string_structure': 0, 'hybrid_oracle': 822}, 'SubtreeMutator': {'mutation': 'SubtreeMutator', 'total': 1141, 'rted': 1115, 'rted_text': 1141, 'hist': 1136, 'string': 1141, 'string_content': 1129, 'string_structure': 1141, 'hybrid_oracle': 1085}, 'SubtreeMutatorwarn': {'mutation': 'SubtreeMutatorwarn', 'total': 0, 'rted': 0, 'rted_text': 0, 'hist': 0, 'string': 0, 'string_content': 0, 'string_structure': 0, 'hybrid_oracle': 33}, 'TextNodeMutator': {'mutation': 'TextNodeMutator', 'total': 1047, 'rted': 262, 'rted_text': 1047, 'hist': 1047, 'string': 1047, 'string_content': 1047, 'string_structure': 1047, 'hybrid_oracle': 260}, 'TextNodeMutatorwarn': {'mutation': 'TextNodeMutatorwarn', 'total': 0, 'rted': 0, 'rted_text': 0, 'hist': 0, 'string': 0, 'string_content': 0, 'string_structure': 0, 'hybrid_oracle': 779}, 'TagMutator': {'mutation': 'TagMutator', 'total': 991, 'rted': 991, 'rted_text': 991, 'hist': 862, 'string': 991, 'string_content': 285, 'string_structure': 991, 'hybrid_oracle': 970}, 'TagMutatorwarn': {'mutation': 'TagMutatorwarn', 'total': 0, 'rted': 0, 'rted_text': 0, 'hist': 0, 'string': 0, 'string_content': 0, 'string_structure': 0, 'hybrid_oracle': 10}, 'AttributeMutator': {'mutation': 'AttributeMutator', 'total': 0, 'rted': 0, 'rted_text': 0, 'hist': 0, 'string': 0, 'string_content': 0, 'string_structure': 0, 'hybrid_oracle': 0}, 'AttributeMutatorwarn': {'mutation': 'AttributeMutatorwarn', 'total': 0, 'rted': 0, 'rted_text': 0, 'hist': 0, 'string': 0, 'string_content': 0, 'string_structure': 0, 'hybrid_oracle': 0}}

N = len(ORACLES)
ind_old = np.arange(N)    # the x locations for the groups
ind = [2*i for i in ind_old]

width = 1.5       # the width of the bars: can also be len(x) sequence

legenda = ()
legendb = ()
oracleTuple = ()
for oracle in ORACLES:
    # legendb = legendb + (oracle.value,)
    oracleTuple = oracleTuple + (str(oracle).split('.')[1],)

# oracleTuple = oracleTuple + ('total', )
oracleDataPrev = None
hatches = ['x', '/', '.', 'o', '+']
hatchInt = 0
for mutation in MUTATORS:
    if mutation == MUTATORS.ATTRIBUTE:
        continue
    legenda = legenda + (str(mutation).split('.')[1],)
    oracleDataRow = oracleMap[mutation.value]
    oracleData = list()
    for oracle in ORACLES:
        value = oracleDataRow[oracle.value]
        if oracle== ORACLES.FragGen:
            value += oracleMap[mutation.value+'warn'][oracle.value]
        oracleData.append(value+1)

    # oracleData.append(oracleDataRow['total']+1)
    print(mutation)
    if(oracleDataPrev is not None):
        p2 = plt.bar(ind, oracleData, width,
                     bottom=oracleDataPrev, hatch = hatches[hatchInt])
        oracleDataPrev = np.add(oracleDataPrev, oracleData).tolist()
    else:
        p1 = plt.bar(ind, oracleData, width, hatch= hatches[hatchInt])
        oracleDataPrev = oracleData

    hatchInt += 1


# legenda = legenda + ('warn',)
#
# oracleDataRow = oracleMap['warn']
# oracleData = list()
# for oracle in ORACLES:
#     oracleData.append(oracleDataRow[oracle.value] + 1)

# oracleData.append(oracleDataRow['total']+1)
# print('warn')
# p2 = plt.bar(ind, oracleData, width,
#                  bottom=oracleDataPrev, hatch = hatches[hatchInt])
    # oracleMap[oracle.value]
# menMeans = (20, 35, 30, 35, 27)
# womenMeans = (25, 32, 34, 20, 25)
# menStd = (2, 3, 4, 1, 2)
# womenStd = (3, 5, 2, 3, 3)
# ind = np.arange(N)    # the x locations for the groups
# width = 0.35       # the width of the bars: can also be len(x) sequence
#
# p1 = plt.bar(ind, menMeans, width, yerr=menStd)
# p2 = plt.bar(ind, womenMeans, width,
#              bottom=menMeans, yerr=womenStd)

print(oracleTuple)
# width:20, height:3
plt.ylabel('Killed Mutations', {'fontname':'Arial', 'size':'14'})
# plt.xlabel('ORACLES', {'fontname':'Arial', 'size':'20'})
# plt.title('Scores by group and gender')
plt.xticks(ind, oracleTuple, rotation = 15, size=12)
plt.yticks(np.arange(0, 3500, 500))
plt.ylim(0, 3500)
plt.legend(legenda, ncol=5, loc='upper center', fancybox=True, bbox_to_anchor=(0.5, 1.1))
#
# plt.figure(figsize=(20, 3))
plt.show()