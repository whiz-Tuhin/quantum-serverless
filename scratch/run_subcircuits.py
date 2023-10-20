from quantum_serverless import get_arguments, save_result, distribute_task

from qiskit_ibm_runtime import QiskitRuntimeService, Session, Sampler
from qiskit import QuantumCircuit
from qiskit_ibm_runtime import Options

import os
import json
os.system("pip install circuit-knitting-toolbox")


from circuit_knitting_toolbox.circuit_cutting.cutqc import cut_circuit_wires, reconstruct_full_distribution, evaluate_subcircuits

# @distribute_task()
def distributed_sample(circuit: QuantumCircuit, session, options):
    """Distributed task that returns quasi distribution for given circuit."""
    dists = Sampler(session=session, options=options).run(circuit).result().quasi_dists[0]
    print(dists)

qAccesKey = '<IBM QUANTUM API TOKEN>'
service = QiskitRuntimeService(channel="ibm_quantum", token=qAccesKey)
shots_count = 2000
backends = ['ibmq_qasm_simulator', 'simulator_statevector']
session_list = []
for backend in backends:
    session_list.append(Session(service=service, backend=backend))
print(f"CustomDict::SessionList::{session_list}")

# create options with the noise profile
options_noise_r0_backend_1 = Options(
    simulator={
        "seed_simulator": 1234,
    },
    # resilience_level=0,
    execution={"shots": shots_count}
)

options_noise_r0_backend_2 = Options(
    simulator={
        "seed_simulator": 1234,
    },
    # resilience_level=0,
    execution={"shots": shots_count}
)

options_list = [options_noise_r0_backend_2, options_noise_r0_backend_1]

# get all arguments passed to this program
arguments = get_arguments()

cuts = arguments.get("subcircuits")

subcircuit_instance_probabilities = evaluate_subcircuits(cuts,
                                                         service=service,
                                                         backend_names=backends,
                                                         options=options_list
                                                         )    

# # get specific argument that we are interested in
# # subcircuits = arguments.get("subcircuits")

# # run parallely the subcircuits on the simulators
# for idx, circuit in enumerate(subcircuits):
#     distributed_sample(circuit, session_list[idx], options_list[idx])

# sampler1 = Sampler(session=session_list[0])

# quasi_dists = sampler.run(circuit).result().quasi_dists

# print(f"Quasi distribution: {quasi_dists[0]}")

# # saving results of a program
# save_result({
#     "quasi_dists": quasi_dists[0]
# })
