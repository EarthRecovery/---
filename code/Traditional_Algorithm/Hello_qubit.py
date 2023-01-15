# Pick a qubit.
import cirq
q = cirq.LineQubit.range(4)

ops = [cirq.H(q[0]), cirq.H(q[1]), cirq.CNOT(q[0],q[1]), cirq.CNOT(q[1],q[2])]
circuit = cirq.Circuit(ops)
print(circuit)

# # Create a circuit that applies a square root of NOT gate, then measures the qubit.
# circuit = cirq.Circuit(cirq.X(qubit) ** 0.5, cirq.measure(qubit, key='m'))
# print("Circuit:")
# print(circuit)

# # Simulate the circuit several times.
# simulator = cirq.Simulator()
# result = simulator.run(circuit, repetitions=20)
# print("Results:")
# print(result)

