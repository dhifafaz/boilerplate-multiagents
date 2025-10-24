"""
Unit tests for utility functions.
"""
import pytest
import asyncio
import time
from unittest.mock import Mock, patch

from source.utils.telemetry import logging


class TestLoggingDecorator:
    """Test suite for logging decorator."""
    
    def test_sync_function_logging(self):
        """Test logging decorator on synchronous function."""
        
        @logging
        def test_func(x, y):
            return x + y
        
        with patch('source.utils.telemetry.logger') as mock_logger:
            result = test_func(2, 3)
            
            assert result == 5
            assert mock_logger.info.call_count >= 2  # Entry and exit logs
    
    @pytest.mark.asyncio
    async def test_async_function_logging(self):
        """Test logging decorator on asynchronous function."""
        
        @logging
        async def test_async_func(x, y):
            await asyncio.sleep(0.01)
            return x + y
        
        with patch('source.utils.telemetry.logger') as mock_logger:
            result = await test_async_func(2, 3)
            
            assert result == 5
            assert mock_logger.info.call_count >= 2  # Entry and exit logs
    
    def test_sync_function_error_logging(self):
        """Test logging decorator handles errors in synchronous function."""
        
        @logging
        def test_func_error():
            raise ValueError("Test error")
        
        with patch('source.utils.telemetry.logger') as mock_logger:
            with pytest.raises(ValueError):
                test_func_error()
            
            # Should log the error
            assert any("failed" in str(call) for call in mock_logger.error.call_args_list)
    
    @pytest.mark.asyncio
    async def test_async_function_error_logging(self):
        """Test logging decorator handles errors in asynchronous function."""
        
        @logging
        async def test_async_func_error():
            await asyncio.sleep(0.01)
            raise ValueError("Test error")
        
        with patch('source.utils.telemetry.logger') as mock_logger:
            with pytest.raises(ValueError):
                await test_async_func_error()
            
            # Should log the error
            assert any("failed" in str(call) for call in mock_logger.error.call_args_list)
    
    def test_class_method_logging(self):
        """Test logging decorator on class methods."""
        
        class TestClass:
            @logging
            def test_method(self, x):
                return x * 2
        
        obj = TestClass()
        
        with patch('source.utils.telemetry.logger') as mock_logger:
            result = obj.test_method(5)
            
            assert result == 10
            # Should include class name in logs
            assert any("TestClass" in str(call) for call in mock_logger.info.call_args_list)
    
    @pytest.mark.asyncio
    async def test_async_class_method_logging(self):
        """Test logging decorator on async class methods."""
        
        class TestClass:
            @logging
            async def test_async_method(self, x):
                await asyncio.sleep(0.01)
                return x * 2
        
        obj = TestClass()
        
        with patch('source.utils.telemetry.logger') as mock_logger:
            result = await obj.test_async_method(5)
            
            assert result == 10
            # Should include class name in logs
            assert any("TestClass" in str(call) for call in mock_logger.info.call_args_list)
    
    def test_execution_time_logging(self):
        """Test that execution time is logged."""
        
        @logging
        def slow_func():
            time.sleep(0.1)
            return "done"
        
        with patch('source.utils.telemetry.logger') as mock_logger:
            result = slow_func()
            
            assert result == "done"
            # Should log execution time
            assert any("execution time" in str(call).lower() for call in mock_logger.info.call_args_list)
