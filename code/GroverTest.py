import hashlib
from multiprocessing import Barrier
from pyqpanda import *
import numpy as np

if __name__ == "__main__":

    qvm = CPUQVM()
    qvm.init_qvm()
    qubits = qvm.qAlloc_many(3)
    cbits = qvm.cAlloc_many(3)

    # 构建量子程序
    prog = QProg()
    circuit = QCircuit()

    circuit << X(qubits[2]) \
        << H(qubits[0]) \
        << H(qubits[1]) \
        << H(qubits[2]) \

    prog << circuit << Measure(qubits[0], cbits[0])

    result = qvm.run_with_configuration(prog, cbits, 1000)

    # 打印量子态在量子程序多次运行结果中出现的次数
    per = (result['01']/1000)*100
    print(f'1:{per}%')