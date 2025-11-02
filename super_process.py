"""
Super Process - An advanced process management and optimization module.

This module provides a SuperProcess class for managing and optimizing
autonomous processes with built-in monitoring, optimization, and control features.
"""

import time
import threading
import logging
from typing import Callable, Optional, Dict, Any, List
from dataclasses import dataclass, field
from enum import Enum

# Configure logger for the module
logger = logging.getLogger(__name__)


class ProcessState(Enum):
    """Enumeration of process states."""
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    OPTIMIZING = "optimizing"
    ERROR = "error"


@dataclass
class ProcessMetrics:
    """Metrics tracked for a super process."""
    execution_count: int = 0
    total_runtime: float = 0.0
    average_runtime: float = 0.0
    success_count: int = 0
    error_count: int = 0
    optimization_level: float = 1.0
    last_execution_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def update_execution(self, runtime: float, success: bool = True):
        """Update metrics after an execution."""
        self.execution_count += 1
        self.total_runtime += runtime
        self.average_runtime = self.total_runtime / self.execution_count
        self.last_execution_time = runtime
        if success:
            self.success_count += 1
        else:
            self.error_count += 1


class SuperProcess:
    """
    SuperProcess - An advanced process management class.
    
    This class provides comprehensive process management with features like:
    - Autonomous execution with monitoring
    - Performance optimization
    - State management
    - Metric collection
    - Error handling and recovery
    """

    def __init__(
        self,
        name: str,
        process_function: Callable,
        auto_optimize: bool = True,
        max_retries: int = 3,
        optimization_threshold: float = 0.8
    ):
        """
        Initialize a SuperProcess.

        Args:
            name: Name of the process
            process_function: The function to execute
            auto_optimize: Enable automatic optimization
            max_retries: Maximum number of retries on failure
            optimization_threshold: Threshold for triggering optimization
        """
        self.name = name
        self.process_function = process_function
        self.auto_optimize = auto_optimize
        self.max_retries = max_retries
        self.optimization_threshold = optimization_threshold

        self.state = ProcessState.IDLE
        self.metrics = ProcessMetrics()
        self._lock = threading.Lock()
        self._stop_flag = threading.Event()
        self._pause_flag = threading.Event()
        self._thread: Optional[threading.Thread] = None

    def execute(self, *args, **kwargs) -> Any:
        """
        Execute the process function with monitoring and optimization.

        Args:
            *args: Positional arguments for the process function
            **kwargs: Keyword arguments for the process function

        Returns:
            Result from the process function

        Raises:
            Exception: If execution fails after all retries
        """
        with self._lock:
            self.state = ProcessState.RUNNING

        retries = 0
        last_error = None

        while retries < self.max_retries:
            try:
                # Check if optimization is needed
                if self.auto_optimize and self._should_optimize():
                    self._optimize()

                # Execute the process function and measure only its execution time
                func_start_time = time.time()
                result = self.process_function(*args, **kwargs)
                func_runtime = time.time() - func_start_time
                
                # Update metrics on success
                self.metrics.update_execution(func_runtime, success=True)
                
                with self._lock:
                    self.state = ProcessState.IDLE
                
                return result

            except Exception as e:
                last_error = e
                retries += 1
                if retries < self.max_retries:
                    time.sleep(0.1 * retries)  # Exponential backoff

        # All retries exhausted, update metrics and raise error
        if last_error:
            # Measure approximate runtime for failed execution
            self.metrics.update_execution(0.0, success=False)
            with self._lock:
                self.state = ProcessState.ERROR
            raise last_error

    def start_continuous(self, interval: float = 1.0, *args, **kwargs):
        """
        Start the process in continuous mode.

        Args:
            interval: Time interval between executions in seconds
            *args: Positional arguments for the process function
            **kwargs: Keyword arguments for the process function
        """
        if self._thread and self._thread.is_alive():
            raise RuntimeError(f"Process {self.name} is already running")

        self._stop_flag.clear()
        self._pause_flag.clear()

        def _run_continuous():
            while not self._stop_flag.is_set():
                if not self._pause_flag.is_set():
                    try:
                        self.execute(*args, **kwargs)
                    except Exception as e:
                        logger.error(f"Error in continuous process {self.name}: {e}")
                
                time.sleep(interval)

        self._thread = threading.Thread(target=_run_continuous, daemon=True)
        self._thread.start()

    def pause(self):
        """Pause the continuous execution."""
        self._pause_flag.set()
        with self._lock:
            self.state = ProcessState.PAUSED

    def resume(self):
        """Resume the continuous execution."""
        self._pause_flag.clear()
        with self._lock:
            self.state = ProcessState.RUNNING

    def stop(self):
        """Stop the continuous execution."""
        self._stop_flag.set()
        if self._thread:
            self._thread.join(timeout=5.0)
        with self._lock:
            self.state = ProcessState.STOPPED

    def get_metrics(self) -> ProcessMetrics:
        """Get current process metrics."""
        return self.metrics

    def get_state(self) -> ProcessState:
        """Get current process state."""
        with self._lock:
            return self.state

    def reset_metrics(self):
        """Reset all metrics to initial values."""
        self.metrics = ProcessMetrics()

    def _should_optimize(self) -> bool:
        """Check if optimization should be triggered."""
        if self.metrics.execution_count < 10:
            return False
        
        success_rate = self.metrics.success_count / self.metrics.execution_count
        return success_rate < self.optimization_threshold

    def _optimize(self):
        """Perform optimization on the process."""
        with self._lock:
            previous_state = self.state
            self.state = ProcessState.OPTIMIZING

        # Placeholder for optimization logic
        # In a real implementation, this could adjust parameters,
        # allocate resources, or tune execution strategies
        self.metrics.optimization_level += 0.1
        
        with self._lock:
            self.state = previous_state

    def __repr__(self) -> str:
        """String representation of the SuperProcess."""
        current_state = self.get_state()
        return (
            f"SuperProcess(name='{self.name}', state={current_state.value}, "
            f"executions={self.metrics.execution_count}, "
            f"success_rate={self.metrics.success_count}/{self.metrics.execution_count})"
        )


class SuperProcessManager:
    """
    Manager for multiple SuperProcess instances.
    
    Provides centralized management, coordination, and monitoring
    of multiple processes.
    """

    def __init__(self):
        """Initialize the SuperProcessManager."""
        self.processes: Dict[str, SuperProcess] = {}
        self._lock = threading.Lock()

    def register(self, process: SuperProcess):
        """
        Register a SuperProcess with the manager.

        Args:
            process: SuperProcess instance to register
        """
        with self._lock:
            if process.name in self.processes:
                raise ValueError(f"Process {process.name} already registered")
            self.processes[process.name] = process

    def unregister(self, name: str):
        """
        Unregister a process from the manager.

        Args:
            name: Name of the process to unregister
        """
        with self._lock:
            if name in self.processes:
                self.processes[name].stop()
                del self.processes[name]

    def get_process(self, name: str) -> Optional[SuperProcess]:
        """
        Get a process by name.

        Args:
            name: Name of the process

        Returns:
            SuperProcess instance or None if not found
        """
        with self._lock:
            return self.processes.get(name)

    def get_all_metrics(self) -> Dict[str, ProcessMetrics]:
        """
        Get metrics for all registered processes.

        Returns:
            Dictionary mapping process names to their metrics
        """
        with self._lock:
            return {name: proc.get_metrics() for name, proc in self.processes.items()}

    def stop_all(self):
        """Stop all registered processes."""
        with self._lock:
            for process in self.processes.values():
                process.stop()

    def get_summary(self) -> Dict[str, Any]:
        """
        Get a summary of all processes.

        Returns:
            Dictionary with summary information
        """
        with self._lock:
            return {
                "total_processes": len(self.processes),
                "processes": {
                    name: {
                        "state": proc.get_state().value,
                        "executions": proc.metrics.execution_count,
                        "success_rate": (
                            proc.metrics.success_count / proc.metrics.execution_count
                            if proc.metrics.execution_count > 0 else 0
                        )
                    }
                    for name, proc in self.processes.items()
                }
            }

    def __repr__(self) -> str:
        """String representation of the manager."""
        return f"SuperProcessManager(processes={len(self.processes)})"
