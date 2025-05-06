from timeit import default_timer as timer
from Crypto.Random import random
import CECPPA
number = 100
E = "Eabc"
m = "abc"
def Correctnesstest(Instantiation):
    # params, msk, tsk = Instantiation.setup()
    # user_number = 64
    # PK = []
    # SK = []
    # for i in range(user_number):
    #     IDi = "ID" + str(i)
    #     xi, Xi = Instantiation.Setsecval(params)
    #     pski, Ri = Instantiation.Partialkeyext(msk, IDi, params)
    #     ski = Instantiation.UserPri(xi, pski)
    #     pki = Instantiation.UserPub(Xi, Ri, IDi)
    #     PK.append(pki)
    #     SK.append(ski)
    test_usernumber = random.randint(0, user_number)
    sigma = Instantiation.Sign(params, PK[:test_usernumber], SK[test_usernumber - 1], E, m)
    if Instantiation.Verify_Sign(params, PK[:test_usernumber], sigma, E, m) == 0:
        print("Verify fails!!!")
        return None
    print("Verify successes!!!")

def Signtest(Instantiation,n):
    t = 0
    for i in range(number):
        start = timer()
        Instantiation.Sign(params, PK[:n], SK[n - 1], E, m)
        end = timer()
        t = t + end - start
    print(str(n) + "   " + str(t * 1000 / number))


def Verifytest(Instantiation, n):
    t = 0
    sigma = Instantiation.Sign(params, PK[:n], SK[n - 1], E, m)
    for i in range(number):
        start = timer()
        Instantiation.Verify_Sign(params, PK[:n], sigma, E, m)
        end = timer()
        t = t + end - start
    print(str(n) + "   " + str(t * 1000 / number))

if __name__ == '__main__':
    Instantiation = CECPPA.CECPPA()
    params, msk, tsk = Instantiation.setup()
    user_number = 1024
    PK = []
    SK = []
    for i in range(user_number):
        IDi = "ID" + str(i)
        xi, Xi = Instantiation.Setsecval(params)
        pski, Ri = Instantiation.Partialkeyext(msk, IDi, params)
        ski = Instantiation.UserPri(xi, pski)
        pki = Instantiation.UserPub(Xi, Ri, IDi)
        PK.append(pki)
        SK.append(ski)
    Correctnesstest(Instantiation)
    n = []
    for i in range(2, 11):
        n.append(2 ** i)
    print("Signtest:")
    for i in range(len(n)):
        Signtest(Instantiation,n[i])
    print("Verifytest:")
    for i in range(len(n)):
        Verifytest(Instantiation,n[i])