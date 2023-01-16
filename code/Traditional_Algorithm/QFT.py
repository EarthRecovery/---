from unittest import result
import numpy as np
import cirq

def main():
    qft_circuit = generate_2x2_grid_qft_circuit()
    print('Circuit:')
    print(qft_circuit)

    simulator = cirq.Simulator()
    result = simulator.simulate(qft_circuit)

    print("final result\n")
    print(np.around(result.final_state_vector, 3))

def cz_and_swap(q0,q1,rot):
    yield cirq.CZ(q0,q1)**rot
    yield cirq.SWAP(q0,q1)

def generate_2x2_grid_qft_circuit():
    a,b,c,d = [cirq.GridQubit(0,0),
              cirq.GridQubit(0,1),
              cirq.GridQubit(1,1),
              cirq.GridQubit(1,0),]

    circuit = cirq.Circuit(
        cirq.H(a),
        cz_and_swap(a,b,0.5),
        cz_and_swap(b,c,0.25),
        cz_and_swap(c,d,0.125),
        cirq.H(a),
        cz_and_swap(a,b,0.5),
        cz_and_swap(b,c,0.25),
        cirq.H(a),
        cz_and_swap(a,b,0.5),
        cirq.H(a),
        strategy = cirq.InsertStrategy.EARLIEST
    )

    return circuit

if __name__ == '__main__':
    main()