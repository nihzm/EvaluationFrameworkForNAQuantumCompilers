from abc import abstractmethod
from typing import TypeAlias

from qiskit import QuantumCircuit
from qiskit.providers import Backend

from .base_estimator import BaseEstimator

Assignment: TypeAlias = tuple[QuantumCircuit, Backend]


class CircuitEstimator(BaseEstimator):
    """
    Base class for estimating job execution time using individual circuit
    execution time estimations
    """

    def estimate_execution_time(
        self,
        circuits: list[QuantumCircuit],
        backend: Backend,
        **kwargs,
    ) -> float:
        """
        Estimate the execution time of a quantum job on a specified backend
        :param circuits: Circuits in the quantum job
        :param backend: Backend to be executed on
        :param kwargs: Additional arguments, like the run configuration
        :return: Estimated execution time
        """
        execution_time = 0
        rep_delay = kwargs.get("rep_delay", backend.configuration().default_rep_delay)
        shots = min(kwargs.get("shots", 8000), backend.configuration().max_shots)
        for circuit in circuits:
            execution_time += (
                self.estimate_circuit_execution_time(circuit, backend)
                + rep_delay
            )
        execution_time *= shots

        return execution_time

    @abstractmethod
    def estimate_circuit_execution_time(
        self, circuit: QuantumCircuit, backend: Backend
    ) -> float:
        """
        Estimate the execution time of a single circuit on a backend
        :param circuit: Circuit to be estimated
        :param backend: Backend to be estimated on
        :return: Estimated execution time
        """
        ...