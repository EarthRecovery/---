from turtle import circle
import cirq
import random
import matplotlib.pyplot as plt

def set_io_qubits(qubit_count):
    input_qubits = [cirq.GridQubit(i,0) for i in range(qubit_count)]
    output_qubit = cirq.GridQubit(qubit_count,0)
    return (input_qubits,output_qubit)

def make_oracle(input_qubits,output_qubit,x_bits):
    yield(cirq.X(q) for (q,bit) in zip(input_qubits,x_bits) if not bit)
    yield(cirq.TOFFOLI(input_qubits[0],input_qubits[1],output_qubit))
    yield(cirq.X(q) for (q,bit) in zip(input_qubits,x_bits) if not bit)

def make_grover_circuit(oracle,input_qubits,output_qubit,simulator):
    c = cirq.Circuit()
    c.append([
        cirq.X(output_qubit),
        cirq.H(output_qubit),
        cirq.H.on_each(*input_qubits)
    ])

    c.append(oracle)

    c.append([
        cirq.H.on_each(*input_qubits),
        cirq.X.on_each(*input_qubits),
        cirq.H(input_qubits[1]),
        cirq.CNOT(input_qubits[0],input_qubits[1]),
        cirq.H(input_qubits[1]),
        cirq.X.on_each(*input_qubits),
        cirq.H.on_each(*input_qubits)
    ])

    result = simulator.simulate(c)

    print("result:")
    print(result)

    return c

def main():
    qubit_count = 2
    circuit_sample_count = 10
    (input_qubits,output_qubit) = set_io_qubits(qubit_count)
    x_bits = [random.randint(0,1) for _ in range(qubit_count)]
    print("Secret bit sequence: {}".format(x_bits))
    
    simulator = cirq.Simulator()

    oracle = make_oracle(input_qubits,output_qubit,x_bits)

    circuit = make_grover_circuit(oracle,input_qubits,output_qubit,simulator)

    print(circuit)
    
    circuit.append([cirq.measure(*input_qubits,key='result')])
    answer = simulator.run(circuit,repetitions = 100)

    cirq.plot_state_histogram(answer, plt.subplot())
    plt.show()
    

if __name__ == '__main__':
    main()
