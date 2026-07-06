"""
Tests for system requirements: Latency, CPU Usage, RAM Usage, and Throughput.
"""
import time
import pytest
import threading
from fastapi import status
from app.core.patient_management.entities import Patient
from datetime import date

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


class TestSystemPerformance:
    """Performance tests mapped to system requirements."""

    @pytest.fixture
    def setup_data(self, stub_records):
        """Setup mock data for the performance tests."""
        stub_records.mock_patients = [
            Patient(
                id=f"pat_{i}",
                patient_name=f"Patient {i}",
                birth_date=date(1980, 1, 1),
                assigned_doc="dr_smith",
                medical_history=["None"],
                scans=[]
            ) for i in range(5)
        ]
        return stub_records

    def test_latency_requirement(self, client, setup_data):
        """System should respond to requests with minimal latency (e.g. < 500ms)."""
        start_time = time.perf_counter()
        response = client.get("/patients/records")
        end_time = time.perf_counter()
        
        latency_ms = (end_time - start_time) * 1000
        assert response.status_code == status.HTTP_200_OK

        print(
            f"PERFORMANCE_RESULT | metric=latency | value={latency_ms:.3f} | "
            "unit=ms | threshold=500.000"
        )
        
        # Requirement: Latency should be under 500 ms (adjust based on actual SRs)
        assert latency_ms < 500.0, f"Latency {latency_ms:.2f}ms exceeded the 500ms threshold."

    @pytest.mark.skipif(not PSUTIL_AVAILABLE, reason="psutil is not installed")
    def test_cpu_and_ram_usage(self, client, setup_data):
        """System overhead for a request should not spike CPU or RAM excessively."""
        process = psutil.Process()
        
        # Get baseline
        cpu_before = process.cpu_times()
        ram_before = process.memory_info().rss / (1024 * 1024)  # in MB

        # Perform the request
        start_time = time.perf_counter()
        response = client.get("/patients/records")
        elapsed = time.perf_counter() - start_time
        assert response.status_code == status.HTTP_200_OK

        # Measure after request
        cpu_after = process.cpu_times()
        cpu_seconds = (
            (cpu_after.user + cpu_after.system)
            - (cpu_before.user + cpu_before.system)
        )
        cpu_usage = (cpu_seconds / max(elapsed, 0.000001)) * 100
        ram_after = process.memory_info().rss / (1024 * 1024)

        ram_usage_spike = ram_after - ram_before

        print(
            f"PERFORMANCE_RESULT | metric=cpu_usage | value={cpu_usage:.3f} | "
            "unit=percent | threshold=300.000"
        )
        print(
            f"PERFORMANCE_RESULT | metric=ram_spike | value={ram_usage_spike:.3f} | "
            "unit=MB | threshold=50.000"
        )

        # Assertions (Example thresholds: CPU < 300% overhead, RAM spike < 50 MB)
        assert cpu_usage < 300.0, f"CPU usage spiked by {cpu_usage:.2f}%, which is too high."
        assert ram_usage_spike < 50.0, f"RAM usage spiked by {ram_usage_spike:.2f} MB, which is too high."

    def test_throughput_requirement(self, client, setup_data):
        """System should be able to handle a certain number of requests per second (throughput)."""
        start_time = time.perf_counter()
        duration = 1.0  # Run for 1 second
        requests_completed = 0

        while (time.perf_counter() - start_time) < duration:
            response = client.get("/patients/records")
            assert response.status_code == status.HTTP_200_OK
            requests_completed += 1

        elapsed = time.perf_counter() - start_time
        requests_per_second = requests_completed / elapsed

        print(
            f"PERFORMANCE_RESULT | metric=sequential_throughput | "
            f"value={requests_per_second:.3f} | unit=requests_per_second | threshold=20.000 | "
            f"requests={requests_completed} | elapsed_seconds={elapsed:.3f}"
        )

        # Example requirement: System should process at least 20 req/sec sequentially
        assert requests_completed >= 20, f"Throughput too low: only {requests_completed} req/sec."

    def test_concurrent_throughput(self, client, setup_data):
        """System should handle concurrent requests effectively."""
        num_threads = 10
        requests_per_thread = 5
        
        exceptions = []
        
        def make_requests():
            try:
                for _ in range(requests_per_thread):
                    response = client.get("/patients/records")
                    assert response.status_code == status.HTTP_200_OK
            except Exception as e:
                exceptions.append(e)

        threads = []
        start_time = time.perf_counter()
        
        for _ in range(num_threads):
            t = threading.Thread(target=make_requests)
            threads.append(t)
            t.start()
            
        for t in threads:
            t.join()
            
        end_time = time.perf_counter()
        total_time = end_time - start_time
        total_requests = num_threads * requests_per_thread
        requests_per_second = total_requests / total_time

        print(
            f"PERFORMANCE_RESULT | metric=concurrent_throughput | "
            f"value={requests_per_second:.3f} | unit=requests_per_second | "
            f"threshold_seconds=1.500 | requests={total_requests} | "
            f"elapsed_seconds={total_time:.3f} | threads={num_threads}"
        )
        
        assert len(exceptions) == 0, f"Exceptions occurred during concurrent requests: {exceptions}"
        
        # If 50 requests take less than 1.5 seconds, throughput is acceptable for concurrent load
        assert total_time < 1.5, f"Concurrent throughput too slow: took {total_time:.2f} seconds for 50 requests."
