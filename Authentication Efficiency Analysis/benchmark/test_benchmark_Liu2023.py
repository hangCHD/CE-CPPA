from timeit import default_timer as timer
from Crypto.Random import random
import Liu2023
number = 100
m = "abc"
def Correctnesstest(Instantiation):
    test_usernumber = 16
    sigma = Instantiation.Sign(params, PK[:test_usernumber], SK[test_usernumber - 1],m)
    if Instantiation.Verify_Sign(params, PK[:test_usernumber], sigma, m) == 0:
        print("Verify fails!!!")
        return None
    print("Verify successes!!!")

def Signtest(Instantiation,n):
    t = 0
    for i in range(number):
        start = timer()
        Instantiation.Sign(params, PK[:n], SK[n - 1], m)
        end = timer()
        t = t + end - start
    print(str(n) + "   " + str(t * 1000 / number))


def Verifytest(Instantiation, n):
    t = 0
    sigma = Instantiation.Sign(params, PK[:n], SK[n - 1], m)
    for i in range(number):
        start = timer()
        Instantiation.Verify_Sign(params, PK[:n], sigma, m)
        end = timer()
        t = t + end - start
    print(str(n) + "   " + str(t * 1000 / number))

if __name__ == '__main__':
    Instantiation = Liu2023.Liu2023()
    params = Instantiation.setup()
    user_number = 1024
    PK = []
    SK = []
    for i in range(user_number):
        ski, pki = Instantiation.KeyGen(params)
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