from math import log2
from time import sleep
from timeit import default_timer as timer
from charm.toolbox.ecgroup import ECGroup, elliptic_curve
from charm.toolbox.eccurve import secp256k1, secp160k1, prime256v1
from charm.core.math.elliptic_curve import G, ZR


class Guo2022:
    def __init__(self):
        global group
        group = ECGroup(secp256k1)
        pass
    def setup(self):
        a = group.random(ZR)
        P = group.random(G)
        # u = group.random(G)
        Ppub = P ** a
        k = group.random(ZR)
        Tpub = P ** k
        params = {'P': P, 'Ppub': Ppub, 'Tpub': Tpub}
        msk = a
        tsk = k
        return params, msk, tsk

    def Setsecval(self, params):
        ti = group.random(ZR)
        Ti = params['P'] ** ti
        return ti, Ti

    def Partialkeyext(self, msk, Ti, IDi, params):
        yi = group.random(ZR)
        Yi = params['P'] ** yi
        ki = group.hash(str(IDi) + str(Ti) + str(Yi) + str(params['Ppub']), ZR)
        di = yi + msk * ki
        return di, Yi

    def UserPub(self, Ti, Yi, IDi):
        pki = {'X': Ti, 'R': Yi, 'ID': IDi}
        return pki

    def UserPri(self, ti, di):
        ski = {'x': ti, 'psk': di}
        return ski

    def Sign(self, params, PK, sk_pai, m):

        #x1 = group.random(ZR)
        x2 = group.random(ZR)
        #X1 = params['P'] ** x1
        X2 = params['P'] ** x2

        length = len(PK)
        k = []
        for i in range(length):
            ki = group.hash(str(PK[i]['ID']) + str(PK[i]['X']) + str(PK[i]['R']) + str(params['Ppub']), ZR)
            k.append(ki)

        beta = group.hash(str(m) + str(X2), ZR)
        I = params['Tpub'] ** (sk_pai['psk'] + sk_pai['x'] * beta + x2)

        z = group.random(ZR)
        r = []
        c = []
        rsum = group.init(ZR, 0)
        for i in range(length - 1):
            ri = group.random(ZR)
            r.append(ri)
            c.append((PK[i]['X'] ** beta) * PK[i]['R'] * (params['Ppub'] ** k[i]) * X2)
            rsum = rsum + ri
        V = (params['Tpub'] ** z) * (I ** rsum)
        W = params['P'] ** z
        for i in range(length - 1):
            W = W * (c[i] ** r[i])
        u = group.hash(str(m) + str(I) + str(V) + str(W) + str(PK), ZR)
        r_pai = u - rsum
        r.append(r_pai)
        lambd = z - r_pai * (sk_pai['psk'] + sk_pai['x'] * beta + x2)
        sigma = {'I': I, 'X2': X2, 'r': r, 'lambd': lambd}
        return sigma

    def Verify_Sign(self, params, PK, sigma,m):
        beta = group.hash(str(m) + str(sigma['X2']), ZR)
        rsum = group.init(ZR, 0)
        for i in range(len(PK)):
            rsum = rsum + sigma['r'][i]
        V = (params['Tpub'] ** sigma['lambd']) * (sigma['I'] ** rsum)
        k = []
        c = []
        for i in range(len(PK)):
            ki = group.hash(str(PK[i]['ID']) + str(PK[i]['X']) + str(PK[i]['R']) + str(params['Ppub']), ZR)
            k.append(ki)
            c.append((PK[i]['X'] ** beta) * PK[i]['R'] * (params['Ppub'] ** k[i]) * sigma['X2'])
        W = params['P'] ** sigma['lambd']
        for i in range(len(PK)):
            W = W * (c[i] ** sigma['r'][i])
        u = group.hash(str(m) + str(sigma['I']) + str(V) + str(W) + str(PK), ZR)
        if rsum == u:
            return 1
        return 0


