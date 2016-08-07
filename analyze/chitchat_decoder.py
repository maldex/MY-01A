from pprint import pprint
l = []
lc = []
# Free Serial Port Monitor export as ANSI
with  open('sampledata.csv') as fd:
    for line in fd.readlines():
        d = line.split(',')
        if not ( d[1].endswith('READ') or d[1].endswith('WRITE') and  d[2] == 'UP') or d[5] == '':
            continue
        #if  not( d[5].endswith('1B ') or d[5].endswith('1C ')):
        #    continue
        l.append ( [  d[1].strip() , d[5].strip() , d[6].strip() ] )

i = -1

try:
    while i < len(l):
        i += 1
        if l[i][0].endswith('WRITE'):
            # lc.append(l[i][1])

            i += 1

            # if not l[i][0].endswith('READ'):
            #     continue
            # if not l[i-1][1].startswith('01 01 1D'): continue  # 1B 18 1C 1F 1D 1E 22 18 14 16
            # meaningfull vilicht: 14, 16 -18 1C 1D(vol)
            lc.append ( str( l[i-1]) + ' ' + str( l[i] ) )
except IndexError:
    pass
lc = list(set(lc))
for each in lc:
    print each
    # e = each.split(' ')
    # r = 'print "' + each + '",   x._io([0x' + e[0] +', 0x' + e[1] + ', 0x' + e[2] + '])'
