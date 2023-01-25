from pyqpanda import *
from psi4_wrapper import *
import numpy as np
from functools import partial
from math import pi
import matplotlib.pyplot as plt

def get_fermion_jordan_wigner(fermion_item):
    pauli = PauliOperator("", 1)

    for i in fermion_item:
        op_qubit = i[0]
        op_str = ""
    for j in range(op_qubit):
        op_str += "Z" + str(j) + " "

    op_str1 = op_str + "X" + str(op_qubit)
    op_str2 = op_str + "Y" + str(op_qubit)

    pauli_map = {}
    pauli_map[op_str1] = 0.5

    if i[1]:
        pauli_map[op_str2] = -0.5j
    else:
        pauli_map[op_str2] = 0.5j

    pauli *= PauliOperator(pauli_map)

    return pauli

def get_ccsd_var(qn, en, para):

    if en > qn:
        assert False    
    if en == qn:
        return VarFermionOperator()

    if get_ccsd_n_term(qn, en) != len(para):
        assert False

    cnt = 0
    var_fermion_op = VarFermionOperator()
    for i in range(en):
        for ex in range(en, qn):
            var_fermion_op += VarFermionOperator(str(ex) + "+ " + str(i), para[cnt])
            cnt += 1

    return var_fermion_op

    for i in range(en):
        for j in range(i+1, en):
            for ex1 in range(en, qn):
                for ex2 in range(ex1+1, qn):
                    fermion_op += VarFermionOperator(
                        str(ex2)+"+ "+str(ex1)+"+ "+str(j)+" "+str(i),
                        para[cnt]
                    )
                    cnt += 1

    return fermion_op

def get_ccsd_n_term(qn, en):

    if n_electron > n_qubit:
        assert False

    return int((qn - en) * en + (qn - en)* (qn -en - 1) * en * (en - 1) / 4)

def cc_to_ucc_hamiltonian_var(cc_op):

    pauli = VarPauliOperator()
    for i in cc_op.data():
        pauli += VarPauliOperator(i[0][1], complex_var(var(-2)*i[1].imag(), var(0)))

    return pauli

def JordanWignerTransformVar(var_fermion_op):
    data = var_fermion_op.data()
    var_pauli = VarPauliOperator()
    for i in data:
        one_pauli = get_fermion_jordan_wigner(i[0][0])
    for j in one_pauli.data():
        var_pauli += VarPauliOperator(j[0][1], complex_var(
            i[1].real()*j[1].real-i[1].imag()*j[1].imag,
            i[1].real()*j[1].imag+i[1].imag()*j[1].real))

    return var_pauli

def prepareInitialState(qlist, en):

    circuit = QCircuit()
    if len(qlist) < en:
        return circuit

    for i in range(en):
        circuit.insert(X(qlist[i]))

    return circuit

def simulate_one_term_var(qubit_list, hamiltonian_term, coef, t):

    vqc = VariationalQuantumCircuit()

    if len(hamiltonian_term) == 0:
        return vqc

    tmp_qlist = []
    for q, term in hamiltonian_term.items():
        if term == 'X':
            vqc.insert(H(qubit_list[q]))
        elif term == 'Y':
            vqc.insert(RX(qubit_list[q],pi/2))

    tmp_qlist.append(qubit_list[q])

    size = len(tmp_qlist)
    if size == 1:
        vqc.insert(VariationalQuantumGate_RZ(tmp_qlist[0], 2*coef*t))
    elif size > 1:
        for i in range(size - 1):
            vqc.insert(CNOT(tmp_qlist[i], tmp_qlist[size - 1]))
            vqc.insert(VariationalQuantumGate_RZ(tmp_qlist[size-1], 2*coef*t))
        for i in range(size - 1):
            vqc.insert(CNOT(tmp_qlist[i], tmp_qlist[size - 1]))

    # dagger
    for q, term in hamiltonian_term.items():
        if term == 'X':
            vqc.insert(H(qubit_list[q]))
        elif term == 'Y':
            vqc.insert(RX(qubit_list[q],-pi/2))

    return vqc

def simulate_hamiltonian_var(qubit_list,var_pauli,t,slices=3):

    vqc = VariationalQuantumCircuit()

    for i in range(slices):
        for j in var_pauli.data():
            term = j[0][0]
            vqc.insert(simulate_one_term_var(qubit_list, term, j[1].real(), t/slices))

    return vqc

def GradientDescent(mol_pauli, n_qubit, n_en, iters):
    n_para = get_ccsd_n_term(n_qubit, n_electron)

    para_vec = []
    var_para = []
    for i in range(n_para):
        var_para.append(var(0.5, True))
        para_vec.append(0.5)

    fermion_cc = get_ccsd_var(n_qubit, n_en, var_para)
    pauli_cc = JordanWignerTransformVar(fermion_cc)
    ucc = cc_to_ucc_hamiltonian_var(pauli_cc)

    machine=init_quantum_machine(QMachineType.CPU)
    qlist = machine.qAlloc_many(n_qubit)

    vqc = VariationalQuantumCircuit()
    vqc.insert(prepareInitialState(qlist, n_en))

    vqc.insert(simulate_hamiltonian_var(qlist, ucc, 1.0, 3))

    loss = qop(vqc, mol_pauli, machine, qlist)
    gd_optimizer = MomentumOptimizer.minimize(loss, 0.1, 0.9)
    leaves = gd_optimizer.get_variables()

    min_energy=float('inf')
    for i in range(iters):
        gd_optimizer.run(leaves, 0)
        loss_value = gd_optimizer.get_loss()

        print(loss_value)
        if loss_value < min_energy:
            min_energy = loss_value
            for m,n in enumerate(var_para):
                para_vec[m] = eval(n, True)[0][0]   

    return min_energy

def getAtomElectronNum(atom):
    atom_electron_map = {
    'H':1, 'He':2, 'Li':3, 'Be':4, 'B':5, 'C':6, 'N':7, 'O':8, 'F':9, 'Ne':10,
    'Na':11, 'Mg':12, 'Al':13, 'Si':14, 'P':15, 'S':16, 'Cl':17, 'Ar':18
    }

    if (not atom_electron_map.__contains__(atom)):
        return 0

    return atom_electron_map[atom]

if __name__=="__main__":
    distances = [x * 0.1 for x in range(2, 25)]
    molecule = "H 0 0 0\nH 0 0 {0}"

    molecules = []
    for d in distances:
        molecules.append(molecule.format(d))

    chemistry_dict = {
    "mol":"",
    "multiplicity":1,
    "charge":0,
    "basis":"sto-3g",
    }

    energies = []

    for d in distances:
        mol = molecule.format(d)

        chemistry_dict["mol"] = molecule.format(d)
        data = run_psi4(chemistry_dict)
        #get molecule electron number
        n_electron = 0
        mol_splits = mol.split()
        cnt = 0
        while (cnt < len(mol_splits)):
            n_electron += getAtomElectronNum(mol_splits[cnt])
            cnt += 4

        fermion_op = parsePsi4DataToFermion(data[1])
        pauli_op = JordanWignerTransform(fermion_op)

        n_qubit = pauli_op.getMaxIndex()

        energies.append(GradientDescent(pauli_op, n_qubit, n_electron, 30))

    plt.plot(distances , energies, 'r')
    plt.xlabel('distance')
    plt.ylabel('energy')
    plt.title('VQE PLOT')
    plt.show()