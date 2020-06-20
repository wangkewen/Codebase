import sys
def cal(a):
    a **= a
    return 'a={}'.format(a)
def compute(x):
    ls = [x, cal]
    return ls[1](x)
print(compute(int(sys.argv[1])))
