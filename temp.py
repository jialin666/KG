item = '2018-12-20@从抢人大战到孟晚舟事件：2018年人力资源十大观察'
date = item.split('@')[0].split(' ')[0].replace('-','')
print(item.split('@')[0])
print(item.split('@')[0].split(' ')[0])
print(date)

import numpy as np
#计算网页A ,B,C 的重要性
M =np.array( [[0.0,1.0,1.0],
     [0.0,0.0,0.0],
     [0.0,0.0,0.0]
])
print(M)
PR = np.array([1.0,1.0,1.0])
print(PR)
print(np.dot(M,PR))
for iter in range(1,100):
    PR = 0.15 + 0.85 * np.dot(M,PR)
    print(iter)
    print(PR)
