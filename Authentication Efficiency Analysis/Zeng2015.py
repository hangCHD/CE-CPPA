from time import sleep

from charm.toolbox.pairinggroup import PairingGroup, ZR, G1, GT, pair
from timeit import default_timer as timer


# from charm.toolbox.pairingcurves import SS512, SS1536


class Zeng2015:
    def __init__(self):
        global group
        group = PairingGroup('128bit')
        pass

    def setup(self):
        x = group.random(ZR)
        P = group.random(G1)
        Ppub = P ** x
        ePP = pair(P, P)
        params = {'P': P, 'Ppub': Ppub, 'ePP': ePP}
        msk = x
        return params, msk

    def KeyGen(self, params):
        xi = group.random(ZR)
        yi = params['P'] ** xi
        ski = xi
        pki = yi
        return ski, pki

    def Sign(self, params, PK, sk_pai, m):
        r0 = group.random(ZR)
        d = group.random(ZR)
        r1 = group.random(ZR)

        u0 = group.hash(str(0) + str(r0) + str(m) + str(PK), G1)
        u1 = group.hash(str(1) + str(r0) + str(m) + str(PK), G1)

        p = pair(u1, u0) ** sk_pai
        M = params['ePP'] ** d
        N = pair(u1, u0) ** d
        R1 = p ** r1

        length = len(PK)
        U = []
        h = []
        H = group.init(ZR, 0)
        for i in range(length - 1):
            U.append(group.random(G1))
            hi = group.hash(str(m) + str(M) + str(N) + str(R1) + str(p) + str(U[i]))
            h.append(hi)
            H = H + h[i]
        Uk = (PK[-1] ** r1) * (PK[-1] ** H)
        for i in range(length - 1):
            Uk = Uk / (U[i] * (PK[i] ** h[i]))
        U.append(Uk)
        hk = group.hash(str(m) + str(M) + str(N) + str(R1) + str(p) + str(Uk))
        h.append(hk)
        H = H + hk
        e = d - (H + r1) * sk_pai
        sigma = {'p': p, 'r0': r0, 'M': M, 'N': N, 'R1': R1, 'U': U, 'e': e}
        return sigma

    def Verify_Sign(self, params, PK, sigma, m):
        h = []
        H = group.init(ZR, 0)
        for i in range(len(PK)):
            hi = group.hash(str(m) + str(sigma['M']) + str(sigma['N']) + str(sigma['R1']) + str(sigma['p']) + str(sigma['U'][i]))
            h.append(hi)
            H = H + h[i]
        O = params['ePP'] ** sigma['e']
        right = sigma['U'][0] * (PK[0] ** h[0])
        for i in range(1, len(PK)):
            right = right * (sigma['U'][i] * (PK[i] ** h[i]))
        O = O * pair(params['P'], right)
        u0 = group.hash(str(0) + str(sigma['r0']) + str(m) + str(PK), G1)
        u1 = group.hash(str(1) + str(sigma['r0']) + str(m) + str(PK), G1)
        W = sigma['R1'] * (pair(u1, u0) ** sigma['e']) * (sigma['p'] ** H)
        if sigma['M'] == O and sigma['N'] == W:
            return 1
        return 0

#
# scheme = Scheme()
# params, msk = scheme.setup()
# user_number = 10
# PK = []
# SK = []
# ID = []
# for i in range(user_number):
#     ID.append(group.random(ZR))
#     ski, pki = scheme.KeyGen(params)
#     PK.append(pki)
#     SK.append(ski)
# m = 111
# sigma = scheme.Sign(params, PK, SK[-1], m)
# print(scheme.Verify_Sign(params, PK, sigma, m))
#
#
# def test(n):
#     number = 100
#     t1 = 0
#     t2 = 0
#     m = 111
#     event = 'a'
#     for i in range(number):
#         start1 = timer()
#         (M, N, R1, U, e, r0, p) = scheme.Sign(params, PK[:n], SK[n - 1], m)
#         end1 = timer()
#         t1 = t1 + end1 - start1
#         start2 = timer()
#         scheme.Verify_Sign(params, PK[:n], M, N, R1, U, e, r0, p, m)
#         end2 = timer()
#         t2 = t2 + end2 - start2
#     print("n = " + str(n))
#     print("proof :" + str(t1 * 10) + " ms")
#     print("verify :" + str(t2 * 10) + " ms")
#
#
# if __name__ == '__main__':
#     n = []
#     for i in range(2, 11):
#         n.append(2 ** i)
#     for i in range(len(n)):
#         test(n[i])
