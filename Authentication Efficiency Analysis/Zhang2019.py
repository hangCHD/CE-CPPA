from math import log2
from time import sleep
from timeit import default_timer as timer
from charm.core.math.elliptic_curve import G, ZR
from charm.toolbox.ecgroup import ECGroup, elliptic_curve
from charm.toolbox.eccurve import secp256k1, secp160k1, prime256v1

class Zhang2019:
    def __init__(self):
        global group
        group = ECGroup(secp256k1)
        pass
    def setup(self):
        g = group.random(G)
        x_rev = group.random(ZR)
        pk_rev = g ** x_rev
        params = {'g':g,'pk_rev':pk_rev}
        return params
    def KeyGen(self,params):
        xi = group.random(ZR)
        yi = params['g']**xi
        ski = xi
        pki = yi
        return ski,pki
    def Sign(self,params,Y,sk_pai,E,m):
        h = group.hash(E,G)
        L = h ** sk_pai
        u = group.random(ZR)
        C1 = params['g']**u
        C2 = (params['pk_rev']**u)*Y[-1] # Y[-1] is the pai-th user public key
        C = {'C1':C1,'C2':C2}

        t1 = group.random(ZR)
        t2 = group.random(ZR)
        a1n_1 = params['g'] ** t1
        a2n_1 = params['pk_rev'] ** t1
        S1_1 = group.hash(str(E)+str(Y)+str(L)+str(m)+str(a1n_1)+str(a2n_1),ZR)
        Ia1n_1 = params['g'] ** t2
        Ia2n_1 = h ** t2
        S11_1 = group.hash(str(E)+str(Y)+str(L)+str(m)+str(Ia1n_1)+str(Ia2n_1),ZR)
        r1 = []
        r2 = []
        S1 = []
        S11 = []
        S1.append(S1_1)
        S11.append(S11_1)
        for i in range(len(Y)-1):
            r1i = group.random(ZR)
            r2i = group.random(ZR)
            r1.append(r1i)
            r2.append(r2i)
            a1i = (params['g'] ** r1i)*(C1**S1[i])
            a2i = (params['pk_rev'] ** r1i) * ((C2/Y[i])**S1[i])
            S1.append(group.hash(str(E)+str(Y)+str(L)+str(m)+str(a1i)+str(a2i),ZR))
            Ia1i = (params['g'] ** r2i)*(Y[i]**S11[i])
            Ia2i = (h ** r2i) * (L**S11[i])
            S11.append(group.hash(str(E) + str(Y) + str(L) +str(m)+ str(Ia1i) + str(Ia2i), ZR))
        r1n = t1 - S1[-1]* u
        r2n = t2 - S11[-1]* sk_pai
        r1.append(r1n)
        r2.append(r2n)
        sigma = {'S1':S1, 'S11':S11, 'r1':r1,'r2':r2,'L':L,'C':C}
        return sigma
    def Verify_Sign(self,params,Y,sigma,E,m):
        h = group.hash(E, G)
        sigma['S1'].append(0)
        sigma['S11'].append(0)
        for i in range(len(Y)):
            Z1_1i = (params['g']**sigma['r1'][i])*(sigma['C']['C1']**sigma['S1'][i])
            Z1_2i = (params['pk_rev'] ** sigma['r1'][i]) * ((sigma['C']['C2']/Y[i])**sigma['S1'][i])
            ##print(Z1_2i)
            sigma['S1'][i+1] = group.hash(str(E)+str(Y)+str(sigma['L'])+str(m)+str(Z1_1i)+str(Z1_2i),ZR)
            Z11_1i = (params['g'] ** sigma['r2'][i])*(Y[i]**sigma['S11'][i])
            Z11_2i = (h ** sigma['r2'][i]) * (sigma['L']**sigma['S11'][i])
            sigma['S11'][i+1] = group.hash(str(E) + str(Y) + str(sigma['L']) +str(m)+ str(Z11_1i) + str(Z11_2i), ZR)
        if sigma['S1'][0] == sigma['S1'][len(Y)]:
            if sigma['S11'][0] == sigma['S11'][len(Y)]:
                return 1
        return 0