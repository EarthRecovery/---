import cirq
import random

def main():
    qubit_count = 8
    circuit_sample_count = 3
    input_qubits = [cirq.GridQubit(i,0) for i in range(qubit_count)]
    output_qubit = cirq.GridQubit(qubit_count,0)

    secret_factor_bits = [random.randint(0,1) for _ in range(qubit_count)]
    secret_bias_bit = random.randint(0,1)

    oracle = make_oracle(input_qubits, output_qubit,secret_factor_bits,secret_bias_bit)

    circuit = make_BV_circuit(input_qubits,output_qubit,oracle)

    print(circuit)

    simulator = cirq.Simulator()
    result = simulator.run(circuit,repetitions=circuit_sample_count)
    print(result)

def make_oracle(input_qubits, output_qubit,secret_factor_bits,secret_bias_bit):
    if secret_bias_bit:
        yield cirq.X(output_qubit)
    for qubit,bit in zip(input_qubits,secret_factor_bits):
        if bit:
            yield cirq.CNOT(qubit,output_qubit)

def make_BV_circuit(input_qubits,output_qubit,oracle):
    c = cirq.Circuit()

    c.append([
        cirq.X(output_qubit),
        cirq.H(output_qubit),
        cirq.H.on_each(*input_qubits)
    ])

    c.append(oracle)

    c.append([
        cirq.H.on_each(*input_qubits),
        cirq.measure(*input_qubits,key='result'),
    ])

    return c

if __name__ == '__main__':
    main()