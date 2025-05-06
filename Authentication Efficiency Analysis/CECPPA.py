from math import log2
from time import sleep
from timeit import default_timer as timer
from charm.core.math.elliptic_curve import G, ZR
from charm.toolbox.ecgroup import ECGroup, elliptic_curve
from charm.toolbox.eccurve import secp256k1, secp160k1, prime256v1


def f(i, j):
    temp = i
    if ((temp >> j) & 1) == 1:
        return 1
    return -1


class CECPPA:
    def __init__(self):
        global group
        group = ECGroup(secp256k1)
        pass

    def PF(self, g, u1, a, params):
        L = []
        R = []
        n = len(g)
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

    def Verify(self, g, P, c, pai, params):
        (L, R, a, b) = pai
        n = len(g)
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
        a = group.random(ZR)
        P = group.random(G)
        u = group.random(G)
        Ppub = P ** a
        k = group.random(ZR)
        Tpub = P ** k
        params = {'P': P, 'Ppub': Ppub, 'Tpub': Tpub, 'u': u}
        msk = a
        tsk = k
        return params, msk, tsk

    def Setsecval(self, params):
        xi = group.random(ZR)
        Xi = params['P'] ** xi
        return xi, Xi

    def Partialkeyext(self, msk, IDi, params):
        di = group.random(ZR)
        Ri = params['P'] ** di
        h_IDi = group.hash(str(1) + str(IDi) + str(Ri) + str(params['Ppub']), ZR)
        pski = di + msk * h_IDi
        return pski, Ri

    def UserPub(self, Xi, Ri, IDi):
        pki = {'X': Xi, 'R': Ri, 'ID': IDi}
        return pki

    def UserPri(self, xi, pski):
        ski = {'x': xi, 'psk': pski}
        return ski

    def Sign(self, params, PK, sk_tau, E, m):
        e = group.hash(str(2)+str(E), ZR)
        l_Etau = group.hash(str(4)+str(E)+str(PK[-1]), ZR)
        length = len(PK)
        secret = sk_tau['psk'] + e * l_Etau * sk_tau['x']
        I = params['Tpub'] ** secret
        r = group.random(ZR)
        c = []
        g = []
        csum = group.init(ZR, 0)
        for i in range(length - 1):
            h_IDi = group.hash(str(1) + str(PK[i]['ID']) + str(PK[i]['R']) + str(params['Ppub']), ZR)
            l_Ei = group.hash(str(4) + str(E) + str(PK[i]), ZR)
            ci = group.random(ZR)
            c.append(ci)
            csum = csum + ci
            g.append((PK[i]['X'] ** (e * l_Ei)) * PK[i]['R'] * (params['Ppub'] ** h_IDi))
        L = (params['Tpub'] ** r) * (I ** csum)
        V = params['P'] ** r
        for i in range(len(c)):
            V = V * (g[i] ** c[i])
        t = group.hash(str(3) + str(E) + str(m) + str(PK) + str(I) + str(L) + str(V))
        c_tau = t - csum
        c.append(c_tau)
        z = r - c_tau * secret
        O = V * L / ((params['P'] * params['Tpub']) ** z)
        g.append((params['P'] ** secret))
        Q1 = []
        for i in range(length):
            Q1.append(g[i] * I)
        u1 = params['u'] ** (group.hash(str(O) + str(params['u']) + str(t), ZR))
        pai = self.PF(Q1, u1, c, params)
        sigma = {'z': z, 'I': I, 'L': L, 'V': V, 'pai': pai}
        return sigma

    def Verify_Sign(self, params, PK, sigma, E, m):
        e = group.hash(str(2)+str(E), ZR)
        t = group.hash(str(3) +str(E) + str(m) + str(PK) + str(sigma['I']) + str(sigma['L']) + str(sigma['V']))
        O = sigma['V'] * sigma['L'] / ((params['P'] * params['Tpub']) ** sigma['z'])
        Q = []
        for i in range(len(PK)):
            h_IDi = group.hash(str(1) + str(PK[i]['ID']) + str(PK[i]['R']) + str(params['Ppub']), ZR)
            l_Ei = group.hash(str(4) + str(E) + str(PK[i]), ZR)
            Q.append((PK[i]['X'] ** (e* l_Ei)) * PK[i]['R'] * (params['Ppub'] ** h_IDi) * sigma['I'])
        if self.Verify(Q, O, t, sigma['pai'], params) == 1:
            return 1
        return 0
