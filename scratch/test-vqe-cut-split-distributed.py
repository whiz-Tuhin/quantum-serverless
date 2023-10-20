# -*- coding: utf-8 -*-
"""vqe.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1sDlUpjnsF0zYQRK5V06mhTDnvb-8nIhS
"""


import pickle
from qiskit.circuit.library import RealAmplitudes
from qiskit.algorithms.optimizers import COBYLA
# from qiskit_algorithms import COBYLA
from qiskit.providers.fake_provider import FakeKolkata
# from qiskit_aer import AerSimulator
# from qiskit_aer.noise import NoiseModel
from qiskit.result import ProbDistribution
from qiskit.opflow import I, X, Y, Z
from qiskit_ibm_runtime import Options

# relevant imports for the noise model
from qiskit import IBMQ

from circuit_knitting_toolbox.circuit_cutting.wire_cutting import cut_circuit_wires, reconstruct_full_distribution, evaluate_subcircuits

# Runtime imports
from qiskit_ibm_runtime import QiskitRuntimeService, Session


import numpy as np
from math import ceil
import time
import sys


# def save_object(obj, filename):
#     with open(filename, 'wb') as outp:
#         pickle.dump(obj, outp, pickle.HIGHEST_PROTOCOL)





# Qiskit runtime backend as a service
# qAccesKey = '<IBM QUANTUM API TOKEN>'
# service = QiskitRuntimeService(channel="ibm_quantum", token=qAccesKey)

# Tuhin's key
qAccesKey = '<IBM QUANTUM API TOKEN>'
service = QiskitRuntimeService(channel="ibm_quantum", token=qAccesKey)

# Set the Sampler and runtime options
# shots_count = int(sys.argv[1])
shots_count = 2000
# options = Options(execution={"shots": 4000})

# backends = [sys.argv[2], sys.argv[3]]
# backends = ['ibmq_qasm_simulator', 'simulator_statevector']
backends = ['ibmq_quito', 'ibmq_belem']

# [New, TK] - Session creation for persistence \
session_dict = {}
for backend in backends:
    session_dict[backend] = Session(service=service, backend=backend)
print(f"CustomDict::SessionDict::{session_dict}")

num_qubits = 6
reps = 1 # we keep this fixed to 1 for the ease of cutting
backend = None

num_vars = RealAmplitudes(num_qubits=num_qubits, reps=reps).num_parameters
init_params = np.random.randn(num_vars)


# Create the provider object - for noise model import
# IBMQ.save_account(qAccesKey)
# IBMQ.load_account() # Load account from disk
# provider = IBMQ.get_provider(hub='ibm-q-education')


# create the backend and save the object into a pickle file
# backend_quito= provider.get_backend("ibmq_quito")
# backend_manila= provider.get_backend("ibmq_manila")
# save_object(backend_quito, "backend_quito.pkl")
# save_object(backend_manila, "backend_manila.pkl")

# create the noise model objects and save into a pickle file
# noise_model_quito = NoiseModel.from_backend(backend_quito)
# noise_model_manila = NoiseModel.from_backend(backend_manila)
# save_object(noise_model_quito , f"noise_model_quito_shots_{shots_count}_with_resilience_unknown.pkl")
# save_object(noise_model_manila , f"noise_model_manila_shots_{shots_count}_with_resilience_unknown.pkl")

# create options with the noise profile
options_noise_r0_backend_1 = Options(
    simulator={
        # "noise_model": noise_model_quito,
        "seed_simulator": 1234,
        "coupling_map": backend_quito.configuration().coupling_map,
        "basis_gates": backend_quito.configuration().basis_gates
    },
    # resilience_level=0,
    execution={"shots": shots_count}
)

options_noise_r0_backend_2 = Options(
    simulator={
        # "noise_model": noise_model_manila,
        "seed_simulator": 1234,
        "coupling_map": backend_manila.configuration().coupling_map,
        "basis_gates": backend_manila.configuration().basis_gates 
    },
    # resilience_level=0,
    execution={"shots": shots_count}
)

options_list = [options_noise_r0_backend_2, options_noise_r0_backend_1]

# Logging variables
cut_timings = []
evaluate_subcircuits_timings = []
post_processing_timings = []
intermediate_energy_values = []

# def get_expval(counts: dict) -> float:
#     '''returns the expval of ZZ...Z type operator; here counts countains probability (not shots)'''
#     expval = 0
    
#     for key, val in counts.items():
#         expval += ((-1)**(key.count('1')%2))*val
    
#     return expval

# def get_expval_zz(counts: dict, i: int, j: int) -> float:
#     '''Returns the ZZ type expectation value given any locations i and j. Typically we will have j=i+1 NN interactions.
#     Here counts contains probability (not shots)'''
    
#     ## note qiskit reads from last bit to first bit. By my convention, i and j follows first to last. So we change it
#     n = len(list(counts.keys())[0]) # finds out the number of qubits
#     i, j = n-i-1, n-j-1
    
#     expval = 0
    
#     for key, val in counts.items():
#         parity = 1 if (int(key[i])+int(key[j]))%2 == 0 else -1
#         expval += parity*val
    
#     return expval

def get_expval_zz(counts: dict, i:int) -> float:
    '''returns the expval of H = Z_i Z_{i+1}'''
    # first make sure that counts contains probabilities, if not make it
    if sum(counts.values()) != 1:
        shots = sum(counts.values())
        for key in counts.keys():
            counts[key] = counts[key]/shots
    
    expval = 0
    
    for key, val in counts.items():
        parity = 1 if (int(key[i])+int(key[i+1]))%2 == 0 else -1
        expval += parity*val
    
    return expval

def get_expval(counts: dict) -> float:
    '''returns the expval of H = \sum_i Z_i Z_{i+1}'''
    num_qubits = len(list(counts.keys())[0])
    expval = 0
    
    for idx in range(num_qubits-1):
        expval += get_expval_zz(counts,idx)
    
    return expval

@distribute_task
def run_subcircuits(circuit):
    pass


def cut_and_evaluate_circuit(circuit, max_cuts=2, max_subcircuits=[2]):
    
    cut_start = get_current_timestamp_ms()
    cuts = cut_circuit_wires(
        circuit=circuit,
        method="automatic",
        max_subcircuit_width=ceil(circuit.depth()/2),
        max_cuts=max_cuts,
        num_subcircuits=max_subcircuits,
        verbose = False
        )
    cut_end = get_current_timestamp_ms()
    print(f"cut_and_evaluate::cut_circuit_wires::timings::{(cut_start, cut_end)}")
    cut_time_taken = cut_end - cut_start
    cut_timings.append((cut_start, cut_end, cut_time_taken))

    # subcircuit_instance_probabilities = evaluate_subcircuits(cuts)

    # Uncomment the following lines to instead use Qiskit Runtime Service as configured above.

    eval_subcircuit_start = get_current_timestamp_ms()

    # No Noise model - evaluation (optoins contains just the shot configuration)
    # subcircuit_instance_probabilities = evaluate_subcircuits(cuts,
    #                                                          service=service,
    #                                                          backend_names=backends,
    #                                                          options=options_list,
    #                                                          session_dict=session_dict
    #                                                         )
    
    subcircuit_instance_probabilities = evaluate_subcircuits(cuts,
                                                             service=service,
                                                             backend_names=backends,
                                                             options=[options_noise_r0_quito, options_noise_r0_belem]
                                                            )    

    eval_subcircuit_end = get_current_timestamp_ms()
    time_taken_eval = eval_subcircuit_end - eval_subcircuit_start
    print(f"cut_and_evaluate::evaluate_subcircuits::timings::{(eval_subcircuit_start, eval_subcircuit_end)}")
    evaluate_subcircuits_timings.append((eval_subcircuit_start, eval_subcircuit_end, time_taken_eval))

    # TODO - time it!
    # NOTE - this is the post processing
    reconstruct_start = get_current_timestamp_ms()
    reconstructed_probabilities = reconstruct_full_distribution(circuit, subcircuit_instance_probabilities, cuts)
    reconstruct_end = get_current_timestamp_ms()
    time_taken_post = reconstruct_end - reconstruct_start
    print(f"cut_and_evaluate::reconstruct::timings::{(reconstruct_start, reconstruct_end)}")
    post_processing_timings.append((reconstruct_start ,reconstruct_end, time_taken_post))


    # NOTE - post processing ends here
    reconstructed_distribution = {i: prob for i, prob in enumerate(reconstructed_probabilities)}
    
    # Represent states as bitstrings (instead of ints)
    reconstructed_dict_bitstring = ProbDistribution(data=reconstructed_distribution).binary_probabilities(num_bits=num_qubits)
    
    
    return reconstructed_dict_bitstring

def cut_objective_function(params):
    print(f"CustomLog[INFO-Params]::{params}")
    ansatz = RealAmplitudes(num_qubits=num_qubits, reps=reps).bind_parameters(params).decompose()
    
    counts = cut_and_evaluate_circuit(ansatz)
    expval = get_expval(counts)
    
    print(f"CustomeLog[INFO-Intermediate-ExpVal]::{expval}")
    intermediate_energy_values.append(expval)
    return expval

def uncut_objective_function(params,shots=2048):
    ansatz = RealAmplitudes(num_qubits=num_qubits, reps=reps).bind_parameters(params).decompose()
    ansatz.measure_all()
    
    counts = backend.run(ansatz, shots=shots).result().get_counts()
    
    for key in counts.keys():
        counts[key] = counts[key]/shots
    
    expval = get_expval(counts)
    
    return expval

optimizer = COBYLA(maxiter=120)

num_vars = RealAmplitudes(num_qubits=num_qubits, reps=reps).num_parameters
init_params = np.random.randn(num_vars)

def get_current_timestamp_ms():
    return time.time()*1000

if __name__ == "__main__":
    optimizer_start = get_current_timestamp_ms()
    mit_cut = optimizer.minimize(fun=cut_objective_function, x0=init_params)
    optimizer_end = get_current_timestamp_ms()
    # mit_uncut = optimizer.minimize(fun=uncut_objective_function, x0=init_params)

    print("Initial parameters: ",init_params)
    print("----------")
    print("energy using circuit cutting: ",mit_cut.fun)
    print("Optimized parameters via circuit cutting: ", mit_cut.x)
    print("----------")
    # print("energy via full circuit evaluation: ",mit_uncut.fun)
    # print("Optimized parameters via full circuit evaluation: ", mit_uncut.x)

    # logs
    print(f"total_optimizer_time::{optimizer_end - optimizer_start}")
    print(f"cut_timings::{cut_timings}")
    print(f"evaluate_timings::{evaluate_subcircuits_timings}")
    print(f"post_process_timings::{post_processing_timings}")
    print(f"intermediate_energy_valyes::{intermediate_energy_values}")
    print(f"Writing output to file..")
    with open("out_logs_vqe_cutqc.log", "w+") as out:
        out.write(f"cut_timings::{cut_timings}\n")
        out.write(f"evaluate_timings::{evaluate_subcircuits_timings}\n")
        out.write(f"post_process_timings::{post_processing_timings}\n")
        out.write(f"intermediate_energy_values::{intermediate_energy_values}\n")
    

