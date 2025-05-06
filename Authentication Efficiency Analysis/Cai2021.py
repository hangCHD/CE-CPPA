from time import sleep

from charm.toolbox.pairinggroup import PairingGroup, ZR, G1, GT, pair
from timeit import default_timer as timer
from charm.toolbox.pairingcurves import SS512, SS1536

class Cai2021:
    def __init__(self):
        global group
        group = PairingGroup('128bit')
        pass

    def setup(self):
        s = group.random(ZR)
        P = group.random(G1)
        Ppub = P ** s
        params = {'P': P, 'Ppub': Ppub}
        msk = s
        return params, msk

    def KeyGen(self, IDi, msk):
        Qi = group.hash(IDi, G1)
        Di = Qi ** msk
        ski = Di
        pki = Qi
        return ski, pki


    def Sign(self, params, PK, sk_pai, m):
        length = len(PK)
        x = []
        for i in range(length):
            x.append(group.random(ZR))
        R = []
        I = []
        for i in range(length-1):
            Ri = params['Ppub'] ** x[i]
            Ii = PK[i] ** x[i]
            R.append(Ri)
            I.append(Ii)
        h = []
        for i in range(length-1):
            hi = group.hash(str(m) + str(R[i]))
            h.append(hi)
        Ra = PK[-1] ** x[-1]
        for i in range(length - 1):
            Ra = Ra / (R[i] * (PK[i] ** h[i]))
        R.append(Ra)
        ha = group.hash(str(m) + str(Ra))
        W = sk_pai ** (ha + x[-1])
        sigma = {'I': I, 'R': R, 'W': W}
        return sigma

    def Verify_Sign(self, params, PK, sigma,m):
        e1 = pair(params['P'], sigma['W'])
        h = []
        for i in range(len(PK)):
            hi = group.hash(str(m) + str(sigma['R'][i]))
            h.append(hi)
        rtotal = sigma['R'][0] * (PK[0] ** h[0])
        for i in range(1,len(PK)):
            rtotal = rtotal * sigma['R'][i] * (PK[i] ** h[i])
        e2 = pair(params['Ppub'], rtotal)
        if e2 == e1:
            return 1
        return 0