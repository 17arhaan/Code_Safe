#!/usr/bin/env python3
"""
Advanced Data Processing Module
Handles large-scale data processing with various algorithms and utilities.
"""

import pandas as pd
import numpy as np
import json
import csv
import sqlite3
import logging
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass
from pathlib import Path
import asyncio
import aiofiles
import hashlib
import pickle
import gzip
import bz2
import lzma
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import multiprocessing as mp
from functools import partial, wraps
import time
import memory_profiler
import psutil
import os
import sys
from datetime import datetime, timedelta
import re
import itertools
from collections import defaultdict, Counter, deque
import heapq
import bisect
from enum import Enum
import warnings
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data_processor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ProcessingMode(Enum):
    """Enumeration for different processing modes."""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    DISTRIBUTED = "distributed"
    STREAMING = "streaming"

@dataclass
class ProcessingConfig:
    """Configuration class for data processing parameters."""
    batch_size: int = 1000
    max_workers: int = mp.cpu_count()
    memory_limit: float = 8.0  # GB
    compression: str = 'gzip'
    output_format: str = 'parquet'
    enable_caching: bool = True
    cache_size: int = 1000
    timeout: int = 300  # seconds

class DataProcessor:
    """
    Advanced data processor with support for multiple data formats,
    parallel processing, and memory optimization.
    """
    
    def __init__(self, config: ProcessingConfig = None):
        """Initialize the data processor with configuration."""
        self.config = config or ProcessingConfig()
        self.cache = {}
        self.stats = {
            'processed_records': 0,
            'processing_time': 0,
            'memory_usage': 0,
            'errors': 0
        }
        self._setup_processing_pools()
    
    def _setup_processing_pools(self):
        """Setup thread and process pools for parallel processing."""
        self.thread_pool = ThreadPoolExecutor(max_workers=self.config.max_workers)
        self.process_pool = ProcessPoolExecutor(max_workers=self.config.max_workers)
    
    def process_large_dataset(self, file_path: str, mode: ProcessingMode = ProcessingMode.PARALLEL) -> Dict[str, Any]:
        """
        Process a large dataset with the specified mode.
        
        Args:
            file_path: Path to the input file
            mode: Processing mode to use
            
        Returns:
            Dictionary containing processing results and statistics
        """
        start_time = time.time()
        logger.info(f"Starting processing of {file_path} in {mode.value} mode")
        
        try:
            if mode == ProcessingMode.STREAMING:
                result = self._process_streaming(file_path)
            elif mode == ProcessingMode.PARALLEL:
                result = self._process_parallel(file_path)
            elif mode == ProcessingMode.DISTRIBUTED:
                result = self._process_distributed(file_path)
            else:
                result = self._process_sequential(file_path)
            
            self.stats['processing_time'] = time.time() - start_time
            self.stats['memory_usage'] = psutil.Process().memory_info().rss / 1024 / 1024 / 1024  # GB
            
            logger.info(f"Processing completed in {self.stats['processing_time']:.2f} seconds")
            return result
            
        except Exception as e:
            logger.error(f"Error processing dataset: {str(e)}")
            self.stats['errors'] += 1
            raise
    
    def _process_streaming(self, file_path: str) -> Dict[str, Any]:
        """Process data in streaming mode for memory efficiency."""
        logger.info("Processing in streaming mode")
        results = []
        
        with open(file_path, 'r', encoding='utf-8') as file:
            for chunk in self._read_chunks(file, self.config.batch_size):
                processed_chunk = self._process_chunk(chunk)
                results.extend(processed_chunk)
                self.stats['processed_records'] += len(processed_chunk)
        
        return {'results': results, 'mode': 'streaming'}
    
    def _process_parallel(self, file_path: str) -> Dict[str, Any]:
        """Process data using parallel processing."""
        logger.info("Processing in parallel mode")
        
        # Read data in chunks
        chunks = self._read_data_chunks(file_path)
        
        # Process chunks in parallel
        futures = []
        for chunk in chunks:
            future = self.thread_pool.submit(self._process_chunk, chunk)
            futures.append(future)
        
        # Collect results
        results = []
        for future in futures:
            try:
                chunk_result = future.result(timeout=self.config.timeout)
                results.extend(chunk_result)
                self.stats['processed_records'] += len(chunk_result)
            except Exception as e:
                logger.error(f"Error processing chunk: {str(e)}")
                self.stats['errors'] += 1
        
        return {'results': results, 'mode': 'parallel'}
    
    def _process_distributed(self, file_path: str) -> Dict[str, Any]:
        """Process data using distributed processing across multiple processes."""
        logger.info("Processing in distributed mode")
        
        chunks = self._read_data_chunks(file_path)
        
        # Process chunks using multiple processes
        with ProcessPoolExecutor(max_workers=self.config.max_workers) as executor:
            futures = [executor.submit(self._process_chunk, chunk) for chunk in chunks]
            
            results = []
            for future in futures:
                try:
                    chunk_result = future.result(timeout=self.config.timeout)
                    results.extend(chunk_result)
                    self.stats['processed_records'] += len(chunk_result)
                except Exception as e:
                    logger.error(f"Error processing chunk: {str(e)}")
                    self.stats['errors'] += 1
        
        return {'results': results, 'mode': 'distributed'}
    
    def _process_sequential(self, file_path: str) -> Dict[str, Any]:
        """Process data sequentially."""
        logger.info("Processing in sequential mode")
        
        with open(file_path, 'r', encoding='utf-8') as file:
            data = file.readlines()
        
        results = self._process_chunk(data)
        self.stats['processed_records'] = len(results)
        
        return {'results': results, 'mode': 'sequential'}
    
    def _read_data_chunks(self, file_path: str, chunk_size: int = None) -> List[List[str]]:
        """Read data file in chunks for parallel processing."""
        chunk_size = chunk_size or self.config.batch_size
        chunks = []
        
        with open(file_path, 'r', encoding='utf-8') as file:
            chunk = []
            for line in file:
                chunk.append(line.strip())
                if len(chunk) >= chunk_size:
                    chunks.append(chunk)
                    chunk = []
            if chunk:  # Add remaining lines
                chunks.append(chunk)
        
        return chunks
    
    def _read_chunks(self, file, chunk_size: int):
        """Generator to read file in chunks."""
        chunk = []
        for line in file:
            chunk.append(line.strip())
            if len(chunk) >= chunk_size:
                yield chunk
                chunk = []
        if chunk:
            yield chunk
    
    def _process_chunk(self, chunk: List[str]) -> List[Dict[str, Any]]:
        """Process a single chunk of data."""
        results = []
        
        for line in chunk:
            try:
                # Simulate complex data processing
                processed_line = self._transform_data(line)
                results.append(processed_line)
            except Exception as e:
                logger.error(f"Error processing line: {str(e)}")
                self.stats['errors'] += 1
        
        return results
    
    def _transform_data(self, line: str) -> Dict[str, Any]:
        """Transform a single line of data."""
        # Simulate various data transformations
        data = {
            'original': line,
            'length': len(line),
            'word_count': len(line.split()),
            'hash': hashlib.md5(line.encode()).hexdigest(),
            'timestamp': datetime.now().isoformat(),
            'processed': True
        }
        
        # Add some complex processing
        if line.isdigit():
            data['is_numeric'] = True
            data['value'] = int(line)
        elif line.replace('.', '').isdigit():
            data['is_float'] = True
            data['value'] = float(line)
        else:
            data['is_text'] = True
            data['uppercase'] = line.upper()
            data['lowercase'] = line.lower()
        
        return data
    
    def save_results(self, results: List[Dict[str, Any]], output_path: str):
        """Save processing results to file."""
        logger.info(f"Saving results to {output_path}")
        
        if self.config.output_format == 'json':
            with open(output_path, 'w') as f:
                json.dump(results, f, indent=2)
        elif self.config.output_format == 'csv':
            if results:
                df = pd.DataFrame(results)
                df.to_csv(output_path, index=False)
        elif self.config.output_format == 'parquet':
            if results:
                df = pd.DataFrame(results)
                df.to_parquet(output_path, compression=self.config.compression)
        else:
            with open(output_path, 'w') as f:
                for result in results:
                    f.write(json.dumps(result) + '\n')
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get processing statistics."""
        return {
            'stats': self.stats.copy(),
            'config': {
                'batch_size': self.config.batch_size,
                'max_workers': self.config.max_workers,
                'memory_limit': self.config.memory_limit,
                'compression': self.config.compression,
                'output_format': self.config.output_format
            },
            'system_info': {
                'cpu_count': mp.cpu_count(),
                'memory_total': psutil.virtual_memory().total / 1024 / 1024 / 1024,  # GB
                'memory_available': psutil.virtual_memory().available / 1024 / 1024 / 1024,  # GB
            }
        }
    
    def cleanup(self):
        """Cleanup resources."""
        self.thread_pool.shutdown(wait=True)
        self.process_pool.shutdown(wait=True)
        logger.info("Cleanup completed")

def memory_monitor(func):
    """Decorator to monitor memory usage of functions."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        process = psutil.Process()
        memory_before = process.memory_info().rss / 1024 / 1024  # MB
        
        result = func(*args, **kwargs)
        
        memory_after = process.memory_info().rss / 1024 / 1024  # MB
        memory_used = memory_after - memory_before
        
        logger.info(f"Function {func.__name__} used {memory_used:.2f} MB of memory")
        return result
    
    return wrapper

@memory_monitor
def process_large_file(file_path: str, output_path: str, config: ProcessingConfig = None):
    """Convenience function to process a large file."""
    processor = DataProcessor(config)
    
    try:
        result = processor.process_large_dataset(file_path)
        processor.save_results(result['results'], output_path)
        stats = processor.get_statistics()
        
        logger.info(f"Processing completed successfully")
        logger.info(f"Statistics: {stats}")
        
        return stats
    finally:
        processor.cleanup()

if __name__ == "__main__":
    # Example usage
    config = ProcessingConfig(
        batch_size=5000,
        max_workers=4,
        memory_limit=16.0,
        compression='gzip',
        output_format='parquet'
    )
    
    # Process a large file
    input_file = "large_dataset.txt"
    output_file = "processed_results.parquet"
    
    if os.path.exists(input_file):
        stats = process_large_file(input_file, output_file, config)
        print(f"Processing completed with stats: {stats}")
    else:
        print(f"Input file {input_file} not found. Please create a test file first.")
