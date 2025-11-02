"""
Example usage of the SuperProcess module.

This file demonstrates various ways to use the SuperProcess class
for autonomous process management and optimization.
"""

from super_process import SuperProcess, SuperProcessManager, ProcessState
import time
import random


def simple_task():
    """A simple task that just sleeps."""
    time.sleep(0.1)
    return "Task completed"


def data_processing_task(data):
    """A data processing task that might fail occasionally."""
    if random.random() < 0.1:  # 10% failure rate
        raise ValueError("Random processing error")
    
    # Simulate processing
    time.sleep(0.05)
    result = sum(data) if data else 0
    return result


def optimization_task(iterations=100):
    """A task that simulates optimization work."""
    result = 0
    for i in range(iterations):
        result += i ** 2
    return result


def example_basic_usage():
    """Example: Basic usage of SuperProcess."""
    print("\n=== Example 1: Basic Usage ===")
    
    # Create a super process
    process = SuperProcess(
        name="simple_process",
        process_function=simple_task,
        auto_optimize=True
    )
    
    # Execute the process
    result = process.execute()
    print(f"Result: {result}")
    print(f"Process state: {process.get_state().value}")
    print(f"Metrics: {process.get_metrics()}")


def example_with_arguments():
    """Example: Using SuperProcess with arguments."""
    print("\n=== Example 2: Process with Arguments ===")
    
    # Create a process that takes arguments
    process = SuperProcess(
        name="data_processor",
        process_function=data_processing_task,
        auto_optimize=True,
        max_retries=3
    )
    
    # Execute multiple times with different data
    for i in range(5):
        try:
            data = [random.randint(1, 100) for _ in range(10)]
            result = process.execute(data)
            print(f"Iteration {i+1}: Processed {len(data)} items, result={result}")
        except Exception as e:
            print(f"Iteration {i+1}: Failed with error: {e}")
    
    # Show metrics
    metrics = process.get_metrics()
    print(f"\nFinal metrics:")
    print(f"  Total executions: {metrics.execution_count}")
    print(f"  Success rate: {metrics.success_count}/{metrics.execution_count}")
    print(f"  Average runtime: {metrics.average_runtime:.4f}s")


def example_continuous_mode():
    """Example: Running a process continuously."""
    print("\n=== Example 3: Continuous Mode ===")
    
    # Create a process
    process = SuperProcess(
        name="continuous_optimizer",
        process_function=lambda: optimization_task(50),
        auto_optimize=True
    )
    
    # Start continuous execution
    print("Starting continuous process...")
    process.start_continuous(interval=0.5)
    
    # Let it run for a while
    time.sleep(2)
    
    # Pause it
    print("Pausing process...")
    process.pause()
    time.sleep(1)
    
    # Resume it
    print("Resuming process...")
    process.resume()
    time.sleep(1)
    
    # Stop it
    print("Stopping process...")
    process.stop()
    
    # Show final metrics
    metrics = process.get_metrics()
    print(f"\nFinal metrics:")
    print(f"  Total executions: {metrics.execution_count}")
    print(f"  Average runtime: {metrics.average_runtime:.4f}s")


def example_process_manager():
    """Example: Using SuperProcessManager for multiple processes."""
    print("\n=== Example 4: Process Manager ===")
    
    # Create a manager
    manager = SuperProcessManager()
    
    # Create and register multiple processes
    process1 = SuperProcess(
        name="processor_1",
        process_function=lambda: data_processing_task([1, 2, 3, 4, 5]),
        auto_optimize=True
    )
    
    process2 = SuperProcess(
        name="optimizer_1",
        process_function=lambda: optimization_task(100),
        auto_optimize=True
    )
    
    manager.register(process1)
    manager.register(process2)
    
    # Execute processes
    print("Executing processes...")
    for i in range(3):
        try:
            result1 = process1.execute()
            result2 = process2.execute()
            print(f"Round {i+1}: Process 1={result1}, Process 2={result2}")
        except Exception as e:
            print(f"Round {i+1}: Error: {e}")
    
    # Get summary
    summary = manager.get_summary()
    print(f"\nManager summary:")
    print(f"  Total processes: {summary['total_processes']}")
    for name, info in summary['processes'].items():
        print(f"  {name}:")
        print(f"    State: {info['state']}")
        print(f"    Executions: {info['executions']}")
        print(f"    Success rate: {info['success_rate']:.2%}")
    
    # Clean up
    manager.stop_all()


def example_error_handling():
    """Example: Error handling and retries."""
    print("\n=== Example 5: Error Handling ===")
    
    def failing_task():
        """A task that always fails."""
        raise RuntimeError("This task always fails")
    
    # Create a process with retries
    process = SuperProcess(
        name="failing_process",
        process_function=failing_task,
        auto_optimize=False,
        max_retries=3
    )
    
    # Try to execute
    try:
        process.execute()
    except Exception as e:
        print(f"Process failed as expected: {e}")
        print(f"Process state: {process.get_state().value}")
        
    metrics = process.get_metrics()
    print(f"Error count: {metrics.error_count}")


def main():
    """Run all examples."""
    print("=" * 60)
    print("SuperProcess Examples")
    print("=" * 60)
    
    example_basic_usage()
    example_with_arguments()
    example_continuous_mode()
    example_process_manager()
    example_error_handling()
    
    print("\n" + "=" * 60)
    print("All examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
