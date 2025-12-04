import numpy as np
import matplotlib.pyplot as plt

from globalNames import ORACLES, MUTATORS

oracleMap = {'warn': {'mutation': 'warn', 'total': 0, 'rted': 0, 'rted_text': 0, 'hist': 0, 'string': 0, 'string_content': 0, 'string_structure': 0, 'hybrid_oracle': 1033}, 'SubtreeMutator': {'mutation': 'SubtreeMutator', 'total': 1350, 'rted': 166, 'rted_text': 209, 'hist': 208, 'string': 209, 'string_content': 205, 'string_structure': 209, 'hybrid_oracle': 85}, 'SubtreeMutatorwarn': {'mutation': 'SubtreeMutatorwarn', 'total': 0, 'rted': 0, 'rted_text': 0, 'hist': 0, 'string': 0, 'string_content': 0, 'string_structure': 0, 'hybrid_oracle': 43}, 'TextNodeMutator': {'mutation': 'TextNodeMutator', 'total': 1148, 'rted': 78, 'rted_text': 101, 'hist': 67, 'string': 101, 'string_content': 101, 'string_structure': 101, 'hybrid_oracle': 0}, 'TextNodeMutatorwarn': {'mutation': 'TextNodeMutatorwarn', 'total': 0, 'rted': 0, 'rted_text': 0, 'hist': 0, 'string': 0, 'string_content': 0, 'string_structure': 0, 'hybrid_oracle': 4}, 'TagMutator': {'mutation': 'TagMutator', 'total': 1167, 'rted': 176, 'rted_text': 176, 'hist': 165, 'string': 176, 'string_content': 46, 'string_structure': 176, 'hybrid_oracle': 7}, 'TagMutatorwarn': {'mutation': 'TagMutatorwarn', 'total': 0, 'rted': 0, 'rted_text': 0, 'hist': 0, 'string': 0, 'string_content': 0, 'string_structure': 0, 'hybrid_oracle': 0}, 'AttributeMutator': {'mutation': 'AttributeMutator', 'total': 770, 'rted': 10, 'rted_text': 770, 'hist': 585, 'string': 770, 'string_content': 241, 'string_structure': 770, 'hybrid_oracle': 1}, 'AttributeMutatorwarn': {'mutation': 'AttributeMutatorwarn', 'total': 0, 'rted': 0, 'rted_text': 0, 'hist': 0, 'string': 0, 'string_content': 0, 'string_structure': 0, 'hybrid_oracle': 165}, 'None': {'mutation': 'None', 'total': 185, 'rted': 198, 'rted_text': 2295, 'hist': 1964, 'string': 2456, 'string_content': 1387, 'string_structure': 2210, 'hybrid_oracle': 100}, 'Nonewarn': {'mutation': 'Nonewarn', 'total': 0, 'rted': 0, 'rted_text': 0, 'hist': 0, 'string': 0, 'string_content': 0, 'string_structure': 0, 'hybrid_oracle': 821}}

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
hatches = ['x', '/', '.', 'o', '+', '|']
hatchInt = 0

array = [mutator for mutator in MUTATORS]
array.append('None')
total = 5889

for mutator in array:
    mutationKey = 'None' if mutator == 'None' else mutator.value
    mutationString = 'None' if mutator == 'None' else str(mutator).split('.')[1]

    oracleDataRow = oracleMap[mutationKey]
    oracleData = list()
    for oracle in ORACLES:
        value = oracleDataRow[oracle.value]
        if oracle == ORACLES.FragGen:
            value += oracleMap[mutationKey + 'warn'][oracle.value]
        oracleData.append(value + 1)

    if (oracleDataPrev is not None):
        oracleDataPrev = np.add(oracleDataPrev, oracleData).tolist()
    else:
        oracleDataPrev = oracleData

remaining = [5900-val for val in oracleDataPrev]

legenda = legenda + ('success',)
# oracleData.append(oracleDataRow['total']+1)
print('remaining')
p2 = plt.bar(ind, remaining, width,
                  hatch = hatches[hatchInt])

oracleDataPrev = remaining
hatchInt  = 1

for mutator in array:
    # if mutation == MUTATORS.ATTRIBUTE:
    #     continue
    mutationKey = 'None' if mutator == 'None' else mutator.value
    mutationString = 'None' if mutator == 'None' else str(mutator).split('.')[1]
    legenda = legenda + (mutationString,)
    oracleDataRow = oracleMap[mutationKey]
    oracleData = list()
    for oracle in ORACLES:
        value = oracleDataRow[oracle.value]
        if oracle== ORACLES.FragGen:
            value += oracleMap[mutationKey+'warn'][oracle.value]
        oracleData.append(value+1)

    # oracleData.append(oracleDataRow['total']+1)
    print(mutationKey)
    if(oracleDataPrev is not None):
        p2 = plt.bar(ind, oracleData, width,
                     bottom=oracleDataPrev, hatch = hatches[hatchInt])
        oracleDataPrev = np.add(oracleDataPrev, oracleData).tolist()
    else:
        p1 = plt.bar(ind, oracleData, width, hatch= hatches[hatchInt])
        oracleDataPrev = oracleData

    hatchInt += 1


# for oracle in ORACLES:
#     oracleData.append(oracleDataRow[oracle.value] + 1)

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
plt.ylabel('Succesful Assertions', {'fontname':'Arial', 'size':'14'})
# plt.xlabel('ORACLES', {'fontname':'Arial', 'size':'20'})
# plt.title('Scores by group and gender')
plt.xticks(ind, oracleTuple, rotation = 15, size=12)
plt.yticks(np.arange(0, 6000, 500))
plt.ylim(0, 6000)
plt.legend(legenda, ncol=3, loc='upper left', fancybox=True, bbox_to_anchor=(0.2, 1.18))
#
# plt.figure(figsize=(20, 3))
# plt.gca().invert_yaxis()
plt.show()