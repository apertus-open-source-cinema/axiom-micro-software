import numpy as np
# from tqdm import tqdm

a = np.fromfile('dump.ram', dtype='<u4')

diffs = a[1:] - a[:-1]
print(diffs[diffs != 1])
print(np.argwhere(diffs != 1))
print(a[np.argwhere(diffs != 1)])

# last = a[0]
# 
# diffs = []
# 
# for i in tqdm(a[1:]):
#     if i != last + 1:
#          diffs.append(i - last)
#          print("shit", last, i)
#     last = i
# 
# print(list(reversed(sorted(diffs)))[:100])
