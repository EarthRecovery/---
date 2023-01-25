from tkinter import YView
from unittest import result
import cirq

q0,q1 = cirq.LineQubit.range(2) #生成两个量子比特

# oracle = {'0':[],
#            '1':[],
#            'x':[cirq.CNOT(q0,q1)],
#            'notx':[cirq.CNOT(q0,q1), cirq.X(q1)]}

oracle = [cirq.CNOT(q0,q1),cirq.CNOT(q0,q1), cirq.X(q1)]

def algorithm(oracle):
    yield cirq.X(q1)
    yield cirq.H(q0), cirq.H(q1)
    yield oracle
    yield cirq.H(q0)
    yield cirq.measure(q0)

circuit = cirq.Circuit()
circuit.append(algorithm(oracle))
print(circuit)

simulator = cirq.Simulator()

# for key, oracle in oracle.items():
#     result = simulator.run(
#         circuit,
#         repetitons = 10
#     )
#     print('oracle: {:<4} results: {}'.format(key,result))

for i in range(10):
    result = simulator.run(
        circuit
    )
    print(result)