"""
Tests for the SuperProcess module.

Simple tests to validate core functionality.
"""

from super_process import SuperProcess, SuperProcessManager, ProcessState
import time


def test_basic_execution():
    """Test basic process execution."""
    print("Test 1: Basic execution... ", end="")
    
    def simple_func():
        return 42
    
    process = SuperProcess(
        name="test_process",
        process_function=simple_func
    )
    
    result = process.execute()
    assert result == 42, "Expected result to be 42"
    assert process.metrics.execution_count == 1, "Expected 1 execution"
    assert process.metrics.success_count == 1, "Expected 1 success"
    assert process.get_state() == ProcessState.IDLE, "Expected IDLE state"
    
    print("PASSED")


def test_execution_with_args():
    """Test process execution with arguments."""
    print("Test 2: Execution with arguments... ", end="")
    
    def add_numbers(a, b):
        return a + b
    
    process = SuperProcess(
        name="add_process",
        process_function=add_numbers
    )
    
    result = process.execute(5, 10)
    assert result == 15, f"Expected 15, got {result}"
    
    result = process.execute(a=3, b=7)
    assert result == 10, f"Expected 10, got {result}"
    
    assert process.metrics.execution_count == 2, "Expected 2 executions"
    
    print("PASSED")


def test_retry_mechanism():
    """Test retry mechanism on failures."""
    print("Test 3: Retry mechanism... ", end="")
    
    attempt_count = 0
    
    def failing_func():
        nonlocal attempt_count
        attempt_count += 1
        if attempt_count < 3:
            raise ValueError("Simulated failure")
        return "success"
    
    process = SuperProcess(
        name="retry_process",
        process_function=failing_func,
        max_retries=3
    )
    
    result = process.execute()
    assert result == "success", "Expected successful result after retries"
    assert attempt_count == 3, f"Expected 3 attempts, got {attempt_count}"
    
    print("PASSED")


def test_metrics_tracking():
    """Test metrics collection."""
    print("Test 4: Metrics tracking... ", end="")
    
    def timed_func():
        time.sleep(0.01)
        return "done"
    
    process = SuperProcess(
        name="metrics_process",
        process_function=timed_func
    )
    
    # Execute multiple times
    for _ in range(5):
        process.execute()
    
    metrics = process.get_metrics()
    assert metrics.execution_count == 5, "Expected 5 executions"
    assert metrics.success_count == 5, "Expected 5 successes"
    assert metrics.error_count == 0, "Expected 0 errors"
    assert metrics.total_runtime > 0, "Expected positive total runtime"
    assert metrics.average_runtime > 0, "Expected positive average runtime"
    
    print("PASSED")


def test_continuous_mode():
    """Test continuous execution mode."""
    print("Test 5: Continuous mode... ", end="")
    
    execution_count = 0
    
    def counting_func():
        nonlocal execution_count
        execution_count += 1
        return execution_count
    
    process = SuperProcess(
        name="continuous_process",
        process_function=counting_func
    )
    
    # Start continuous mode
    process.start_continuous(interval=0.1)
    time.sleep(0.5)
    
    # Should have executed multiple times
    current_count = execution_count
    assert current_count >= 3, f"Expected at least 3 executions, got {current_count}"
    
    # Stop and verify it stops
    process.stop()
    time.sleep(0.3)
    final_count = execution_count
    
    # Count should not have increased significantly after stop
    assert final_count - current_count <= 2, "Process should have stopped"
    
    print("PASSED")


def test_pause_resume():
    """Test pause and resume functionality."""
    print("Test 6: Pause and resume... ", end="")
    
    execution_count = 0
    
    def counting_func():
        nonlocal execution_count
        execution_count += 1
    
    process = SuperProcess(
        name="pause_process",
        process_function=counting_func
    )
    
    # Start continuous mode
    process.start_continuous(interval=0.1)
    time.sleep(0.3)
    
    # Pause and check count doesn't increase much
    count_before_pause = execution_count
    process.pause()
    assert process.get_state() == ProcessState.PAUSED, "Expected PAUSED state"
    time.sleep(0.3)
    count_during_pause = execution_count
    
    # Should not have increased much during pause
    assert count_during_pause - count_before_pause <= 1, "Should not execute much while paused"
    
    # Resume and check it continues
    process.resume()
    time.sleep(0.3)
    count_after_resume = execution_count
    assert count_after_resume > count_during_pause, "Should resume execution"
    
    process.stop()
    
    print("PASSED")


def test_process_manager():
    """Test SuperProcessManager."""
    print("Test 7: Process manager... ", end="")
    
    manager = SuperProcessManager()
    
    process1 = SuperProcess("proc1", lambda: 1)
    process2 = SuperProcess("proc2", lambda: 2)
    
    manager.register(process1)
    manager.register(process2)
    
    # Test retrieval
    assert manager.get_process("proc1") == process1
    assert manager.get_process("proc2") == process2
    assert manager.get_process("nonexistent") is None
    
    # Execute processes
    process1.execute()
    process2.execute()
    process2.execute()
    
    # Get summary
    summary = manager.get_summary()
    assert summary["total_processes"] == 2
    assert summary["processes"]["proc1"]["executions"] == 1
    assert summary["processes"]["proc2"]["executions"] == 2
    
    # Unregister
    manager.unregister("proc1")
    assert manager.get_process("proc1") is None
    
    # Stop all
    manager.stop_all()
    
    print("PASSED")


def test_error_handling():
    """Test error handling."""
    print("Test 8: Error handling... ", end="")
    
    def always_fails():
        raise RuntimeError("Always fails")
    
    process = SuperProcess(
        name="error_process",
        process_function=always_fails,
        max_retries=2
    )
    
    try:
        process.execute()
        assert False, "Should have raised an exception"
    except RuntimeError as e:
        assert str(e) == "Always fails"
        assert process.get_state() == ProcessState.ERROR
        assert process.metrics.error_count == 1
        assert process.metrics.success_count == 0
    
    print("PASSED")


def run_all_tests():
    """Run all tests."""
    print("=" * 60)
    print("Running SuperProcess Tests")
    print("=" * 60)
    print()
    
    tests = [
        test_basic_execution,
        test_execution_with_args,
        test_retry_mechanism,
        test_metrics_tracking,
        test_continuous_mode,
        test_pause_resume,
        test_process_manager,
        test_error_handling,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"ERROR: {e}")
            failed += 1
    
    print()
    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
