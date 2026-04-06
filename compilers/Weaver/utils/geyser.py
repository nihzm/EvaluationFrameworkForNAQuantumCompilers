import logging
logging.disable(logging.INFO)

import numpy as np

from qiskit import Aer, execute
from qiskit import QuantumCircuit

from map_circuit import MapCircuit
from block_circuit import BlockCircuit
from compose_circuit import ComposeCircuit

ALGORITHMS = ['adder_4',
			  'vqe_4',
			  'qaoa_5',
			  'qft_5',
			  'multiplier_5',
			  'adder_9',
			  'advantage_9',
			  'qft_10',
			  'multiplier_10',
			  'heisenberg_step_100_16']

NUM_ITERATIONS = 10

def hs_distance(A, B):

	return np.sqrt(np.abs(1 - (np.abs(np.sum(np.multiply(A,np.conj(B)))) / A.shape[0])**2))

def main():

	for i in range(len(ALGORITHMS)):

		algo = ALGORITHMS[i]

		print(algo.upper())

		algo_file = '../qasm/' + algo + '_original.qasm'

		circuits = {}

		circuits['Original'] = QuantumCircuit.from_qasm_file(algo_file)

		layout = None
		blocks = None
		min_num_blocks = float('inf')

		for _ in range(NUM_ITERATIONS):

			mapper = MapCircuit(circuits['Original'])

			layout = mapper.get_layout()

			blocks = mapper.get_blocks()

			mapped = mapper.get_mapped_circuit()

			blocker = BlockCircuit(layout, blocks, mapped)

			num_blocks, blocked = blocker.get_blocked_circuit()

			if num_blocks < min_num_blocks:
				circuits['Mapped'] = mapped
				circuits['Blocked'] = blocked
				min_num_blocks = num_blocks

		with open('../qasm/' + algo + '_mapped.qasm', 'w') as f:
			f.write(circuits['Mapped'].qasm())

		print('Circuit Mapped')

		with open('../qasm/' + algo + '_blocked.qasm', 'w') as f:
			f.write(circuits['Blocked'].qasm())

		print('Circuit Blocked')

		composer = SynthesizeCircuit(algo, layout, circuits['Blocked'])

		circuits['Composed'] = composer.get_composed_circuit()

		with open('../qasm/' + algo + '_composed.qasm', 'w') as f: 
			f.write(circuits['Composed'].qasm())

		print('Circuit Composed')

		unitaries = {}
		for status, circuit in circuits.items():
			unitaries[status] = execute(circuit, Aer.get_backend('unitary_simulator')).result().get_unitary(circuit)

		for status1, unitary1 in unitaries.items():
			for status2, unitary2 in unitaries.items():
				if status1 < status2:
					print(status1, status2, 'Distance: ', hs_distance(unitary1, unitary2))

if __name__ == '__main__':

	main()


