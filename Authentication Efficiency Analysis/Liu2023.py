from math import log2
from time import sleep
from timeit import default_timer as timer
from charm.core.math.elliptic_curve import G, ZR
from charm.toolbox.ecgroup import ECGroup, elliptic_curve
from charm.toolbox.eccurve import secp256k1, secp160k1, prime256v1
#YuLin Liu 10.1109/TIV.2022.3216949
def f(i, j):
    temp = i
    if ((temp >> j) & 1) == 1:
        return 1
    return -1

class Liu2023:
    def __init__(self):
        global group
        group = ECGroup(secp256k1)
        pass
    def PF(self, g,I, u1, a):
        L = []
        R = []
        n = len(g)
        for i in range(n):
            g[i] = g[i]*I[i]
        b = [1] * n
        while (n != 1):
            n1 = int(n / 2)
            cl = a[0] * b[n1]
            cr = a[n1] * b[0]
            for i in range(1, n1):
                cl = cl + a[i] * b[n1 + i]
            for i in range(n1 + 1, n):
                cr = cr + a[i] * b[i - n1]
            R1 = u1 ** cr
            for i in range(n1):
                R1 = R1 * (g[i] ** a[n1 + i])
            L1 = u1 ** cl
            for i in range(n1):
                L1 = L1 * (g[n1 + i] ** a[i])
            L.append(L1)
            R.append(R1)
            x = group.hash(str(L1) + str(R1), ZR)
            g1 = []
            a1 = []
            b1 = []
            for i in range(n1):
                g1.append((g[i] ** (x ** (-1))) * (g[i + n1] ** x))
                a1.append(x * a[i] + (x ** (-1)) * a[n1 + i])
                b1.append((x ** (-1)) * b[i] + x * b[n1 + i])
            g = g1
            a = a1
            n = n1
            b = b1
        pai = (L, R, a, b)
        return pai

    def Verify(self, g,I, P, c, pai, params):
        (L, R, a, b) = pai
        n = len(g)
        for i in range(n):
            g[i] = g[i]*I[i]
        P1 = P * (params['u'] ** (c * group.hash(str(P) + str(params['u']) + str(c), ZR)))
        x = []
        y = []
        logn = int(log2(n))

        for i in range(logn):
            x.append(group.hash(str(L[i]) + str(R[i]), ZR))
        for i in range(n):
            flag = 1
            for j in range(logn):
                flag = flag * (x[logn - j - 1] ** f(i, j))
            y.append(flag)
        flag1 = P1
        for i in range(logn):
            flag1 = flag1 * (L[i] ** (x[i] * x[i])) * (R[i] ** ((x[i] * x[i]) ** (-1)))

        flag2 = params['u'] ** (a[0] * b[0] * group.hash(str(P) + str(params['u']) + str(c), ZR))
        for i in range(n):
            flag2 = flag2 * (g[i] ** (a[0] * y[i]))
        if (flag1 == flag2):
            return 1
        return 0
    def setup(self):
        g = group.random(G)
        u = group.random(G)
        params = {'g':g,'u':u}
        return params
    def KeyGen(self,params):
        xi = group.random(ZR)
        yi = params['g']**xi
        ski = xi
        pki = yi
        return ski,pki
    def Sign(self,params,PK,sk_pai,m):
        H = []
        length = len(PK)
        for i in range(length):
            Hi = group.hash(PK[i],G)
            H.append(Hi)
        I = H[-1]**sk_pai

        rn = group.random(ZR)
        alphan = group.random(ZR)
        c =[]
        L = params['g']**rn
        R = I**alphan
        ctotal = group.init(ZR,0)
        for i in range(length-1):
            ci = group.random(ZR)
            c.append(ci)
            L = L * (PK[i]**ci)
            R = R * (H[i]**ci)
            ctotal = ctotal + ci
        chal = group.hash(str(R)+str(L)+str(m),ZR)
        cn = chal - ctotal
        s = rn - cn * sk_pai
        z = alphan - cn * (sk_pai**(-1))
        c.append(cn)

        P = (L / (params['g']**s)) * (R / (I**z))
        u1 = params['u'] ** (group.hash(str(P) + str(params['u']) + str(chal), ZR))
        pai = self.PF(PK, H, u1, c)
        sigma = {'s':s, 'z':z,'L':L,'R':R,'I':I,'pai':pai}
        return sigma
    def Verify_Sign(self,params,PK,sigma,m):
        H = []
        length = len(PK)
        for i in range(length):
            Hi = group.hash(PK[i], G)
            H.append(Hi)
        P1 = (sigma['L'] / (params['g'] ** sigma['s'])) * (sigma['R'] / (sigma['I'] ** sigma['z']))
        chal = group.hash(str(sigma['R'])+str(sigma['L'])+str(m),ZR)
        if self.Verify(PK,H,P1,chal,sigma['pai'],params) == 1:
            return 1
        return 0