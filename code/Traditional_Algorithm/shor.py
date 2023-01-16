import cirq 
import numpy as np

def gcd(a,b):
    while b != 0 :
        ta = a % b
        a = b
        b = ta

    return a

