"""
╔═══════════════════════════════════════════════════════════════════════════╗
║                    CONFIGURAÇÃO DE HARDWARE ESPECIALIZADO               ║
║                 Componente 14: Otimização de Infraestrutura            ║
╚═══════════════════════════════════════════════════════════════════════════╝
"""

import asyncio
import numpy as np
import pandas as pd
import psutil
import platform
import subprocess
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import json
import yaml
from collections import defaultdict, deque
import time
import threading
import multiprocessing as mp

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('SpecializedHardwareConfig')

class HardwareType(Enum):
    """Tipos de hardware"""
    CPU = "cpu"
    GPU = "gpu"
    TPU = "tpu"
    FPGA = "fpga"
    ASIC = "asic"
    MEMORY = "memory"
    STORAGE = "storage"
    NETWORK = "network"
    QUANTUM = "quantum"
    NEUROMORPHIC = "neuromorphic"

class OptimizationType(Enum):
    """Tipos de otimização"""
    PERFORMANCE = "performance"
    POWER_EFFICIENCY = "power_efficiency"
    COST_OPTIMIZATION = "cost_optimization"
    LATENCY_OPTIMIZATION = "latency_optimization"
    THROUGHPUT_OPTIMIZATION = "throughput_optimization"
    MEMORY_OPTIMIZATION = "memory_optimization"
    THERMAL_OPTIMIZATION = "thermal_optimization"

class WorkloadType(Enum):
    """Tipos de workload"""
    TRAINING = "training"
    INFERENCE = "inference"
    DATA_PROCESSING = "data_processing"
    REAL_TIME = "real_time"
    BATCH = "batch"
    STREAMING = "streaming"
    HPC = "hpc"
    EDGE_COMPUTING = "edge_computing"

@dataclass
class HardwareSpec:
    """Especificações de hardware"""
    component_type: HardwareType
    vendor: str
    model: str
    architecture: str
    clock_speed_ghz: float
    cores: int
    threads: int
    cache_size_mb: float
    memory_gb: float
    bandwidth_gbps: float
    power_consumption_watts: float
    thermal_design_power_watts: float
    capabilities: List[str]
    supported_optimizations: List[OptimizationType]
    benchmark_scores: Dict[str, float] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'component_type': self.component_type.value,
            'vendor': self.vendor,
            'model': self.model,
            'architecture': self.architecture,
            'clock_speed_ghz': self.clock_speed_ghz,
            'cores': self.cores,
            'threads': self.threads,
            'cache_size_mb': self.cache_size_mb,
            'memory_gb': self.memory_gb,
            'bandwidth_gbps': self.bandwidth_gbps,
            'power_consumption_watts': self.power_consumption_watts,
            'thermal_design_power_watts': self.thermal_design_power_watts,
            'capabilities': self.capabilities,
            'supported_optimizations': [opt.value for opt in self.supported_optimizations],
            'benchmark_scores': self.benchmark_scores,
            'metadata': self.metadata
        }

@dataclass
class OptimizationProfile:
    """Perfil de otimização"""
    name: str
    workload_type: WorkloadType
    optimization_type: OptimizationType
    parameters: Dict[str, Any]
    performance_metrics: Dict[str, float]
    power_metrics: Dict[str, float]
    thermal_metrics: Dict[str, float]
    created_at: datetime
    last_updated: datetime
    active: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'workload_type': self.workload_type.value,
            'optimization_type': self.optimization_type.value,
            'parameters': self.parameters,
            'performance_metrics': self.performance_metrics,
            'power_metrics': self.power_metrics,
            'thermal_metrics': self.thermal_metrics,
            'created_at': self.created_at.isoformat(),
            'last_updated': self.last_updated.isoformat(),
            'active': self.active
        }

@dataclass
class ResourceUtilization:
    """Utilização de recursos"""
    component: HardwareType
    utilization_percent: float
    temperature_celsius: float
    power_watts: float
    frequency_ghz: float
    memory_usage_gb: float
    io_operations_per_second: float
    network_bandwidth_mbps: float
    timestamp: datetime
    alerts: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'component': self.component.value,
            'utilization_percent': self.utilization_percent,
            'temperature_celsius': self.temperature_celsius,
            'power_watts': self.power_watts,
            'frequency_ghz': self.frequency_ghz,
            'memory_usage_gb': self.memory_usage_gb,
            'io_operations_per_second': self.io_operations_per_second,
            'network_bandwidth_mbps': self.network_bandwidth_mbps,
            'timestamp': self.timestamp.isoformat(),
            'alerts': self.alerts
        }

class HardwareDetector:
    """Detetor de hardware especializado"""
    
    def __init__(self):
        self.detected_hardware = {}
        self.system_info = {}
        logger.info("🔍 HardwareDetector inicializado")
    
    def detect_all_hardware(self) -> Dict[str, HardwareSpec]:
        """Detecta todo o hardware disponível"""
        hardware_specs = {}
        
        # Detecta CPU
        cpu_spec = self._detect_cpu()
        if cpu_spec:
            hardware_specs['cpu'] = cpu_spec
        
        # Detecta GPUs
        gpu_specs = self._detect_gpus()
        if gpu_specs:
            hardware_specs['gpus'] = gpu_specs
        
        # Detecta memória
        memory_spec = self._detect_memory()
        if memory_spec:
            hardware_specs['memory'] = memory_spec
        
        # Detecta storage
        storage_specs = self._detect_storage()
        if storage_specs:
            hardware_specs['storage'] = storage_specs
        
        # Detecta rede
        network_spec = self._detect_network()
        if network_spec:
            hardware_specs['network'] = network_spec
        
        self.detected_hardware = hardware_specs
        
        logger.info(f"🖥️ Hardware detectado: {len(hardware_specs)} componentes")
        
        return hardware_specs
    
    def _detect_cpu(self) -> Optional[HardwareSpec]:
        """Detecta especificações da CPU"""
        try:
            # Informações básicas
            cpu_info = platform.processor()
            machine = platform.machine()
            
            # Informações detalhadas
            cpu_count = psutil.cpu_count(logical=False)
            cpu_count_logical = psutil.cpu_count(logical=True)
            
            # Frequência
            cpu_freq = psutil.cpu_freq()
            current_freq = cpu_freq.current if cpu_freq else 0
            
            # Cache (simplificado)
            cache_size = self._get_cpu_cache_size()
            
            # Memória
            memory = psutil.virtual_memory()
            
            # Arquitetura
            architecture = platform.architecture()[0]
            
            # Vendor
            vendor = self._get_cpu_vendor()
            
            spec = HardwareSpec(
                component_type=HardwareType.CPU,
                vendor=vendor,
                model=cpu_info,
                architecture=architecture,
                clock_speed_ghz=current_freq / 1000 if current_freq > 0 else 0,
                cores=cpu_count,
                threads=cpu_count_logical,
                cache_size_mb=cache_size,
                memory_gb=memory.total / (1024**3),
                bandwidth_gbps=self._estimate_memory_bandwidth(),
                power_consumption_watts=self._estimate_cpu_power(),
                thermal_design_power_watts=self._estimate_cpu_tdp(),
                capabilities=self._get_cpu_capabilities(),
                supported_optimizations=[
                    OptimizationType.PERFORMANCE,
                    OptimizationType.POWER_EFFICIENCY,
                    OptimizationType.THERMAL_OPTIMIZATION
                ],
                benchmark_scores=self._run_cpu_benchmarks()
            )
            
            return spec
            
        except Exception as e:
            logger.error(f"❌ Erro ao detectar CPU: {e}")
            return None
    
    def _detect_gpus(self) -> List[HardwareSpec]:
        """Detecta GPUs disponíveis"""
        gpu_specs = []
        
        try:
            # Tenta detectar NVIDIA GPUs
            nvidia_gpus = self._detect_nvidia_gpus()
            gpu_specs.extend(nvidia_gpus)
            
            # Tenta detectar AMD GPUs
            amd_gpus = self._detect_amd_gpus()
            gpu_specs.extend(amd_gpus)
            
            # Tenta detectar Intel GPUs
            intel_gpus = self._detect_intel_gpus()
            gpu_specs.extend(intel_gpus)
            
        except Exception as e:
            logger.error(f"❌ Erro ao detectar GPUs: {e}")
        
        return gpu_specs
    
    def _detect_nvidia_gpus(self) -> List[HardwareSpec]:
        """Detecta GPUs NVIDIA"""
        gpu_specs = []
        
        try:
            # Usa nvidia-smi se disponível
            result = subprocess.run(
                ['nvidia-smi', '--query-gpu=name,driver_version,memory.total,temperature.gpu,power.draw,clocks.sm', '--format=csv,noheader,nounits'],
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                
                for i, line in enumerate(lines):
                    if line.strip():
                        parts = [p.strip() for p in line.split(',')]
                        if len(parts) >= 6:
                            spec = HardwareSpec(
                                component_type=HardwareType.GPU,
                                vendor="NVIDIA",
                                model=parts[0],
                                architecture="CUDA",
                                clock_speed_ghz=float(parts[5]) / 1000 if parts[5] else 0,
                                cores=1,  # Simplificado
                                threads=1,
                                cache_size_mb=0,  # Não disponível via nvidia-smi
                                memory_gb=float(parts[2]) / 1024,
                                bandwidth_gbps=self._estimate_gpu_bandwidth(parts[0]),
                                power_consumption_watts=float(parts[4]) if parts[4] else 0,
                                thermal_design_power_watts=self._estimate_gpu_tdp(parts[0]),
                                capabilities=self._get_gpu_capabilities("nvidia"),
                                supported_optimizations=[
                                    OptimizationType.PERFORMANCE,
                                    OptimizationType.THROUGHPUT_OPTIMIZATION,
                                    OptimizationType.MEMORY_OPTIMIZATION
                                ],
                                benchmark_scores=self._run_gpu_benchmarks(i)
                            )
                            gpu_specs.append(spec)
            
        except Exception as e:
            logger.debug(f"NVIDIA GPU detection failed: {e}")
        
        return gpu_specs
    
    def _detect_amd_gpus(self) -> List[HardwareSpec]:
        """Detecta GPUs AMD"""
        gpu_specs = []
        
        try:
            # Usa rocm-smi se disponível
            result = subprocess.run(
                ['rocm-smi', '--showproductname', '--showmeminfo', '--showtemp', '--format=csv'],
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                
                for line in lines:
                    if 'GPU' in line:
                        # Simplificado - parsing real seria mais complexo
                        spec = HardwareSpec(
                            component_type=HardwareType.GPU,
                            vendor="AMD",
                            model=line.strip(),
                            architecture="ROCm",
                            clock_speed_ghz=1.5,  # Estimado
                            cores=1,
                            threads=1,
                            cache_size_mb=0,
                            memory_gb=8.0,  # Estimado
                            bandwidth_gbps=512.0,  # Estimado
                            power_consumption_watts=250.0,  # Estimado
                            thermal_design_power_watts=300.0,  # Estimado
                            capabilities=self._get_gpu_capabilities("amd"),
                            supported_optimizations=[
                                OptimizationType.PERFORMANCE,
                                OptimizationType.THROUGHPUT_OPTIMIZATION
                            ],
                            benchmark_scores={}
                        )
                        gpu_specs.append(spec)
            
        except Exception as e:
            logger.debug(f"AMD GPU detection failed: {e}")
        
        return gpu_specs
    
    def _detect_intel_gpus(self) -> List[HardwareSpec]:
        """Detecta GPUs Intel"""
        gpu_specs = []
        
        try:
            # Usa intel_gpu_tools se disponível
            result = subprocess.run(
                ['intel_gpu_top', '--version'],
                capture_output=True, text=True, timeout=5
            )
            
            if result.returncode == 0:
                # Simplificado - parsing real seria mais complexo
                spec = HardwareSpec(
                    component_type=HardwareType.GPU,
                    vendor="Intel",
                    model="Intel Integrated GPU",
                    architecture="Intel",
                    clock_speed_ghz=1.2,  # Estimado
                    cores=1,
                    threads=1,
                    cache_size_mb=0,
                    memory_gb=2.0,  # Compartilhada
                    bandwidth_gbps=64.0,  # Estimado
                    power_consumption_watts=65.0,  # Estimado
                    thermal_design_power_watts=95.0,  # Estimado
                    capabilities=self._get_gpu_capabilities("intel"),
                    supported_optimizations=[
                        OptimizationType.POWER_EFFICIENCY,
                        OptimizationType.LATENCY_OPTIMIZATION
                    ],
                    benchmark_scores={}
                )
                gpu_specs.append(spec)
            
        except Exception as e:
            logger.debug(f"Intel GPU detection failed: {e}")
        
        return gpu_specs
    
    def _detect_memory(self) -> Optional[HardwareSpec]:
        """Detecta especificações de memória"""
        try:
            memory = psutil.virtual_memory()
            
            spec = HardwareSpec(
                component_type=HardwareType.MEMORY,
                vendor="Unknown",
                model="System Memory",
                architecture=platform.architecture()[0],
                clock_speed_ghz=self._estimate_memory_speed(),
                cores=1,
                threads=1,
                cache_size_mb=0,
                memory_gb=memory.total / (1024**3),
                bandwidth_gbps=self._estimate_memory_bandwidth(),
                power_consumption_watts=memory.total / (1024**3) * 3,  # Estimado
                thermal_design_power_watts=0,
                capabilities=self._get_memory_capabilities(),
                supported_optimizations=[
                    OptimizationType.MEMORY_OPTIMIZATION,
                    OptimizationType.PERFORMANCE
                ],
                benchmark_scores=self._run_memory_benchmarks()
            )
            
            return spec
            
        except Exception as e:
            logger.error(f"❌ Erro ao detectar memória: {e}")
            return None
    
    def _detect_storage(self) -> List[HardwareSpec]:
        """Detecta dispositivos de armazenamento"""
        storage_specs = []
        
        try:
            disk_partitions = psutil.disk_partitions()
            
            for partition in disk_partitions:
                try:
                    disk_usage = psutil.disk_usage(partition.mountpoint)
                    
                    # Determina tipo de storage
                    if 'ssd' in partition.device.lower() or 'nvme' in partition.device.lower():
                        storage_type = "SSD"
                        bandwidth = 500.0  # Estimado para SSD
                    else:
                        storage_type = "HDD"
                        bandwidth = 150.0  # Estimado para HDD
                    
                    spec = HardwareSpec(
                        component_type=HardwareType.STORAGE,
                        vendor="Unknown",
                        model=partition.device,
                        architecture=storage_type,
                        clock_speed_ghz=0,
                        cores=1,
                        threads=1,
                        cache_size_mb=self._estimate_disk_cache(),
                        memory_gb=disk_usage.total / (1024**3),
                        bandwidth_gbps=bandwidth,
                        power_consumption_watts=self._estimate_storage_power(storage_type),
                        thermal_design_power_watts=0,
                        capabilities=self._get_storage_capabilities(storage_type),
                        supported_optimizations=[
                            OptimizationType.THROUGHPUT_OPTIMIZATION,
                            OptimizationType.LATENCY_OPTIMIZATION
                        ],
                        benchmark_scores=self._run_storage_benchmarks(partition.device)
                    )
                    
                    storage_specs.append(spec)
                    
                except Exception as e:
                    logger.debug(f"Erro ao analisar partição {partition.device}: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"❌ Erro ao detectar storage: {e}")
        
        return storage_specs
    
    def _detect_network(self) -> Optional[HardwareSpec]:
        """Detecta interfaces de rede"""
        try:
            network_io = psutil.net_io_counters()
            
            spec = HardwareSpec(
                component_type=HardwareType.NETWORK,
                vendor="Unknown",
                model="Network Interface",
                architecture="Ethernet/WiFi",
                clock_speed_ghz=0,
                cores=1,
                threads=1,
                cache_size_mb=0,
                memory_gb=0,
                bandwidth_gbps=self._estimate_network_bandwidth(),
                power_consumption_watts=10.0,  # Estimado
                thermal_design_power_watts=0,
                capabilities=self._get_network_capabilities(),
                supported_optimizations=[
                    OptimizationType.LATENCY_OPTIMIZATION,
                    OptimizationType.THROUGHPUT_OPTIMIZATION
                ],
                benchmark_scores=self._run_network_benchmarks()
            )
            
            return spec
            
        except Exception as e:
            logger.error(f"❌ Erro ao detectar rede: {e}")
            return None
    
    def _get_cpu_vendor(self) -> str:
        """Obtém vendor da CPU"""
        try:
            with open('/proc/cpuinfo', 'r') as f:
                for line in f:
                    if line.startswith('vendor_id'):
                        if 'Intel' in line:
                            return 'Intel'
                        elif 'AMD' in line:
                            return 'AMD'
                        elif 'ARM' in line:
                            return 'ARM'
        except:
            pass
        
        return 'Unknown'
    
    def _get_cpu_cache_size(self) -> float:
        """Obtém tamanho do cache da CPU"""
        try:
            cache_size = 0
            with open('/proc/cpuinfo', 'r') as f:
                for line in f:
                    if 'cache size' in line:
                        size_str = line.split(':')[1].strip()
                        if 'KB' in size_str:
                            cache_size = float(size_str.replace('KB', '').strip()) / 1024
                        elif 'MB' in size_str:
                            cache_size = float(size_str.replace('MB', '').strip())
                        break
            return cache_size
        except:
            return 0
    
    def _estimate_memory_bandwidth(self) -> float:
        """Estima largura de banda da memória"""
        try:
            # Tenta obter informações do sistema
            if platform.system() == 'Linux':
                result = subprocess.run(
                    ['lscpu | grep "Memory bandwidth"'],
                    shell=True, capture_output=True, text=True, timeout=5
                )
                if result.returncode == 0:
                    bandwidth_str = result.stdout.split(':')[1].strip()
                    if 'GB/s' in bandwidth_str:
                        return float(bandwidth_str.replace('GB/s', '').strip())
        except:
            pass
        
        # Estimado baseado no tipo de memória
        return 25.6  # DDR4-2133 padrão
    
    def _estimate_memory_speed(self) -> float:
        """Estima velocidade da memória"""
        try:
            if platform.system() == 'Linux':
                result = subprocess.run(
                    ['lscpu | grep "max MHz"'],
                    shell=True, capture_output=True, text=True, timeout=5
                )
                if result.returncode == 0:
                    freq_str = result.stdout.split(':')[1].strip()
                    return float(freq_str) / 1000
        except:
            pass
        
        return 2.4  # DDR4-2400 padrão
    
    def _get_cpu_capabilities(self) -> List[str]:
        """Obtém capacidades da CPU"""
        capabilities = []
        
        # Capacidades básicas
        capabilities.extend(['x86_64', '64-bit'])
        
        # Verifica suporte a extensões
        try:
            if platform.system() == 'Linux':
                result = subprocess.run(
                    ['lscpu | grep "Flags"'],
                    shell=True, capture_output=True, text=True, timeout=5
                )
                if result.returncode == 0:
                    flags = result.stdout.split(':')[1].strip().split()
                    
                    if 'sse' in flags:
                        capabilities.append('SSE')
                    if 'sse2' in flags:
                        capabilities.append('SSE2')
                    if 'sse4_1' in flags:
                        capabilities.append('SSE4.1')
                    if 'sse4_2' in flags:
                        capabilities.append('SSE4.2')
                    if 'avx' in flags:
                        capabilities.append('AVX')
                    if 'avx2' in flags:
                        capabilities.append('AVX2')
                    if 'fma' in flags:
                        capabilities.append('FMA')
        except:
            pass
        
        return capabilities
    
    def _get_gpu_capabilities(self, vendor: str) -> List[str]:
        """Obtém capacidades da GPU"""
        capabilities = []
        
        if vendor == "nvidia":
            capabilities.extend(['CUDA', 'cuBLAS', 'cuDNN', 'TensorRT'])
        elif vendor == "amd":
            capabilities.extend(['ROCm', 'OpenCL', 'Vulkan'])
        elif vendor == "intel":
            capabilities.extend(['OpenCL', 'Vulkan', 'QuickSync'])
        
        capabilities.extend(['OpenGL', 'DirectX'])
        
        return capabilities
    
    def _get_memory_capabilities(self) -> List[str]:
        """Obtém capacidades da memória"""
        capabilities = ['DDR4', 'ECC']
        
        # Verifica suporte a NUMA
        try:
            if platform.system() == 'Linux':
                result = subprocess.run(['numactl', '--hardware'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    capabilities.append('NUMA')
        except:
            pass
        
        return capabilities
    
    def _get_storage_capabilities(self, storage_type: str) -> List[str]:
        """Obtém capacidades do storage"""
        capabilities = [storage_type]
        
        if storage_type == "SSD":
            capabilities.extend(['TRIM', 'SMART', 'NVMe'])
        
        capabilities.extend(['SATA', 'PCIe'])
        
        return capabilities
    
    def _get_network_capabilities(self) -> List[str]:
        """Obtém capacidades de rede"""
        capabilities = ['TCP/IP', 'UDP', 'Ethernet']
        
        # Verifica Wi-Fi
        try:
            result = subprocess.run(['iwconfig'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                capabilities.append('Wi-Fi')
        except:
            pass
        
        return capabilities
    
    def _estimate_cpu_power(self) -> float:
        """Estima consumo de energia da CPU"""
        try:
            # Tenta obter do sistema
            if platform.system() == 'Linux':
                result = subprocess.run(
                    ['cat', '/sys/class/power_supply/intel_pstate/RAPL_PP0/current_power_uw'],
                    capture_output=True, text=True, timeout=5
                )
                if result.returncode == 0:
                    return float(result.stdout.strip()) / 1000000
        except:
            pass
        
        # Estimado baseado no número de cores
        cpu_count = psutil.cpu_count()
        return cpu_count * 15  # 15W por core estimado
    
    def _estimate_cpu_tdp(self) -> float:
        """Estima TDP da CPU"""
        try:
            if platform.system() == 'Linux':
                result = subprocess.run(
                    ['cat', '/sys/class/thermal/thermal_zone0/trip_point_0_temp'],
                    capture_output=True, text=True, timeout=5
                )
                if result.returncode == 0:
                    # Simplificado - TDP real seria mais complexo de obter
                    return 95.0
        except:
            pass
        
        return 95.0  # Estimado para CPU moderna
    
    def _estimate_gpu_bandwidth(self, model: str) -> float:
        """Estima largura de banda da GPU"""
        # Estimado baseado no modelo
        if 'RTX' in model or 'GTX' in model:
            return 512.0  # RTX 3080+
        elif 'RX' in model:
            return 512.0  # RX 6000+
        else:
            return 256.0  # GPU integrada ou mais antiga
    
    def _estimate_gpu_tdp(self, model: str) -> float:
        """Estima TDP da GPU"""
        if 'RTX' in model:
            return 320.0  # RTX 3080
        elif 'GTX' in model:
            return 200.0  # GTX 1660
        elif 'RX' in model:
            return 250.0  # RX 6700 XT
        else:
            return 150.0  # GPU integrada
    
    def _estimate_storage_power(self, storage_type: str) -> float:
        """Estima consumo de storage"""
        if storage_type == "SSD":
            return 5.0
        else:
            return 8.0
    
    def _estimate_disk_cache(self) -> float:
        """Estima cache do disco"""
        return 64.0  # Cache padrão
    
    def _estimate_network_bandwidth(self) -> float:
        """Estima largura de banda da rede"""
        return 1.0  # 1 Gbps estimado
    
    def _run_cpu_benchmarks(self) -> Dict[str, float]:
        """Executa benchmarks da CPU"""
        scores = {}
        
        try:
            # Benchmark de performance simples
            start_time = time.time()
            
            # Teste matemático intensivo
            result = 0
            for i in range(1000000):
                result += np.sqrt(i)
            
            elapsed_time = time.time() - start_time
            scores['math_performance'] = 1000000 / elapsed_time
            
            # Benchmark de memória
            start_time = time.time()
            large_array = np.random.random(1000000)
            result = np.sum(large_array)
            elapsed_time = time.time() - start_time
            scores['memory_bandwidth'] = 1000000 / elapsed_time
            
        except Exception as e:
            logger.error(f"❌ Erro no benchmark da CPU: {e}")
        
        return scores
    
    def _run_gpu_benchmarks(self, gpu_id: int) -> Dict[str, float]:
        """Executa benchmarks da GPU"""
        scores = {}
        
        try:
            # Simplificado - benchmark real usaria CUDA/OpenCL
            start_time = time.time()
            
            # Operação de matriz
            matrix_a = np.random.random((1000, 1000))
            matrix_b = np.random.random((1000, 1000))
            result = np.dot(matrix_a, matrix_b)
            
            elapsed_time = time.time() - start_time
            scores['matrix_performance'] = 1000 / elapsed_time
            
        except Exception as e:
            logger.error(f"❌ Erro no benchmark da GPU: {e}")
        
        return scores
    
    def _run_memory_benchmarks(self) -> Dict[str, float]:
        """Executa benchmarks de memória"""
        scores = {}
        
        try:
            # Teste de largura de banda
            start_time = time.time()
            
            # Operação intensiva de memória
            data = []
            for i in range(1000):
                data.append(np.random.random(10000))
            
            result = sum(np.sum(d) for d in data)
            
            elapsed_time = time.time() - start_time
            scores['bandwidth_test'] = 10000 / elapsed_time
            
        except Exception as e:
            logger.error(f"❌ Erro no benchmark de memória: {e}")
        
        return scores
    
    def _run_storage_benchmarks(self, device: str) -> Dict[str, float]:
        """Executa benchmarks de storage"""
        scores = {}
        
        try:
            # Teste de I/O
            start_time = time.time()
            
            # Escrita de teste
            test_data = b'A' * 1024 * 1024  # 1MB
            with open('/tmp/benchmark_test', 'wb') as f:
                f.write(test_data)
            
            # Leitura de teste
            with open('/tmp/benchmark_test', 'rb') as f:
                data = f.read()
            
            elapsed_time = time.time() - start_time
            scores['io_performance'] = 1.0 / elapsed_time
            
            # Limpa
            import os
            os.remove('/tmp/benchmark_test')
            
        except Exception as e:
            logger.error(f"❌ Erro no benchmark de storage: {e}")
        
        return scores
    
    def _run_network_benchmarks(self) -> Dict[str, float]:
        """Executa benchmarks de rede"""
        scores = {}
        
        try:
            # Teste de latência
            start_time = time.time()
            
            # Ping para localhost
            result = subprocess.run(
                ['ping', '-c', '1', '127.0.0.1'],
                capture_output=True, text=True, timeout=5
            )
            
            elapsed_time = time.time() - start_time
            scores['latency'] = elapsed_time
            
        except Exception as e:
            logger.error(f"❌ Erro no benchmark de rede: {e}")
        
        return scores

class PerformanceOptimizer:
    """Otimizador de performance de hardware"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.profiles = {}
        self.active_profile = None
        self.monitoring_active = False
        self.optimization_history = []
        
        logger.info("⚡ PerformanceOptimizer inicializado")
    
    def create_optimization_profile(self, name: str, workload_type: WorkloadType,
                                   hardware_specs: Dict[str, HardwareSpec],
                                   optimization_type: OptimizationType) -> OptimizationProfile:
        """Cria perfil de otimização"""
        parameters = self._generate_optimization_parameters(
            workload_type, hardware_specs, optimization_type
        )
        
        profile = OptimizationProfile(
            name=name,
            workload_type=workload_type,
            optimization_type=optimization_type,
            parameters=parameters,
            performance_metrics={},
            power_metrics={},
            thermal_metrics={},
            created_at=datetime.now(),
            last_updated=datetime.now()
        )
        
        self.profiles[name] = profile
        
        logger.info(f"📋 Perfil de otimização criado: {name}")
        
        return profile
    
    def _generate_optimization_parameters(self, workload_type: WorkloadType,
                                       hardware_specs: Dict[str, HardwareSpec],
                                       optimization_type: OptimizationType) -> Dict[str, Any]:
        """Gera parâmetros de otimização"""
        parameters = {}
        
        if optimization_type == OptimizationType.PERFORMANCE:
            parameters.update(self._get_performance_parameters(workload_type, hardware_specs))
        elif optimization_type == OptimizationType.POWER_EFFICIENCY:
            parameters.update(self._get_power_efficiency_parameters(workload_type, hardware_specs))
        elif optimization_type == OptimizationType.LATENCY_OPTIMIZATION:
            parameters.update(self._get_latency_parameters(workload_type, hardware_specs))
        elif optimization_type == OptimizationType.THROUGHPUT_OPTIMIZATION:
            parameters.update(self._get_throughput_parameters(workload_type, hardware_specs))
        elif optimization_type == OptimizationType.MEMORY_OPTIMIZATION:
            parameters.update(self._get_memory_parameters(workload_type, hardware_specs))
        
        return parameters
    
    def _get_performance_parameters(self, workload_type: WorkloadType,
                                   hardware_specs: Dict[str, HardwareSpec]) -> Dict[str, Any]:
        """Obtém parâmetros de performance"""
        params = {
            'cpu_governor': 'performance',
            'cpu_scaling_governor': 'performance',
            'disable_cpu_idle': True,
            'cpu_min_frequency': 'maximum',
            'turbo_boost': True,
            'hyperthreading': True,
            'cpu_affinity': 'auto',
            'power_save': False
        }
        
        # GPU parameters
        if 'gpus' in hardware_specs:
            params.update({
                'gpu_power_limit': 'maximum',
                'gpu_performance_mode': 'performance',
                'gpu_clock_offset': '+100',
                'memory_clock_offset': '+500',
                'disable_power_limits': True
            })
        
        # Memory parameters
        if 'memory' in hardware_specs:
            params.update({
                'memory_overcommit': True,
                'swap_usage': 'minimal',
                'memory_pressure': 'disabled'
            })
        
        # Workload-specific parameters
        if workload_type == WorkloadType.TRAINING:
            params.update({
                'batch_size_optimization': True,
                'data_loading_workers': 'maximum',
                'mixed_precision': True,
                'gradient_checkpointing': False
            })
        elif workload_type == WorkloadType.INFERENCE:
            params.update({
                'batch_size_optimization': True,
                'tensorrt_optimization': True,
                'model_quantization': False,
                'dynamic_batching': True
            })
        
        return params
    
    def _get_power_efficiency_parameters(self, workload_type: WorkloadType,
                                          hardware_specs: Dict[str, HardwareSpec]) -> Dict[str, Any]:
        """Obtém parâmetros de eficiência energética"""
        params = {
            'cpu_governor': 'powersave',
            'cpu_scaling_governor': 'powersave',
            'enable_cpu_idle': True,
            'cpu_min_frequency': 'minimum',
            'turbo_boost': False,
            'hyperthreading': False,
            'cpu_affinity': 'balanced',
            'power_save': True
        }
        
        # GPU parameters
        if 'gpus' in hardware_specs:
            params.update({
                'gpu_power_limit': 'minimum',
                'gpu_performance_mode': 'power_saver',
                'gpu_clock_offset': '-200',
                'memory_clock_offset': '-1000',
                'enable_power_limits': True
            })
        
        # Memory parameters
        if 'memory' in hardware_specs:
            params.update({
                'memory_overcommit': False,
                'swap_usage': 'aggressive',
                'memory_pressure': 'enabled'
            })
        
        return params
    
    def _get_latency_parameters(self, workload_type: WorkloadType,
                                   hardware_specs: Dict[str, HardwareSpec]) -> Dict[str, Any]:
        """Obtém parâmetros de otimização de latência"""
        params = {
            'cpu_governor': 'performance',
            'cpu_isolation': True,
            'cpu_affinity': 'dedicated',
            'disable_cpu_idle': True,
            'realtime_priority': True,
            'interrupt_affinity': True,
            'numa_balancing': 'local'
        }
        
        # GPU parameters
        if 'gpus' in hardware_specs:
            params.update({
                'gpu_power_preference': 'performance',
                'gpu_clock_max': True,
                'memory_clock_max': True,
                'persistence_mode': True,
                'compute_mode': 'exclusive'
            })
        
        # Network parameters
        if 'network' in hardware_specs:
            params.update({
                'network_interrupt_affinity': True,
                'tcp_nodelay': True,
                'network_buffer_optimization': True,
                'irq_balancing': 'disabled'
            })
        
        return params
    
    def _get_throughput_parameters(self, workload_type: WorkloadType,
                                        hardware_specs: Dict[str, HardwareSpec]) -> Dict[str, Any]:
        """Obtém parâmetros de otimização de throughput"""
        params = {
            'cpu_governor': 'performance',
            'cpu_scaling_governor': 'performance',
            'hyperthreading': True,
            'cpu_affinity': 'spread',
            'load_balancing': 'enabled',
            'parallel_processing': 'maximum'
        }
        
        # GPU parameters
        if 'gpus' in hardware_specs:
            params.update({
                'gpu_multi_stream': True,
                'gpu_concurrent_kernels': True,
                'memory_pinned': True,
                'data_pipeline': 'optimized'
            })
        
        # Storage parameters
        if 'storage' in hardware_specs:
            params.update({
                'io_scheduler': 'deadline',
                'read_ahead': 'maximum',
                'write_back': 'aggressive',
                'file_system_optimization': True
            })
        
        return params
    
    def _get_memory_parameters(self, workload_type: WorkloadType,
                                    hardware_specs: Dict[str, HardwareSpec]) -> Dict[str, Any]:
        """Obtém parâmetros de otimização de memória"""
        params = {
            'memory_compaction': 'enabled',
            'memory_defragmentation': 'enabled',
            'huge_pages': 'enabled',
            'memory_overcommit': 'controlled',
            'swap_usage': 'minimal'
        }
        
        # Workload-specific
        if workload_type == WorkloadType.TRAINING:
            params.update({
                'gradient_checkpointing': True,
                'mixed_precision': True,
                'memory_efficient_attention': True
            })
        elif workload_type == WorkloadType.INFERENCE:
            params.update({
                'model_quantization': True,
                'dynamic_batching': True,
                'memory_pool': 'enabled'
            })
        
        return params
    
    def apply_optimization_profile(self, profile_name: str) -> bool:
        """Aplica perfil de otimização"""
        if profile_name not in self.profiles:
            logger.error(f"❌ Perfil não encontrado: {profile_name}")
            return False
        
        profile = self.profiles[profile_name]
        
        try:
            # Aplica otimizações de CPU
            self._apply_cpu_optimizations(profile.parameters)
            
            # Aplica otimizações de GPU
            self._apply_gpu_optimizations(profile.parameters)
            
            # Aplica otimizações de memória
            self._apply_memory_optimizations(profile.parameters)
            
            # Aplica otimizações de storage
            self._apply_storage_optimizations(profile.parameters)
            
            self.active_profile = profile_name
            profile.last_updated = datetime.now()
            
            logger.info(f"✅ Perfil de otimização aplicado: {profile_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao aplicar perfil {profile_name}: {e}")
            return False
    
    def _apply_cpu_optimizations(self, parameters: Dict[str, Any]):
        """Aplica otimizações de CPU"""
        try:
            if platform.system() == 'Linux':
                # CPU governor
                governor = parameters.get('cpu_governor', 'performance')
                subprocess.run(['cpupower', 'frequency-set', '-g', governor], 
                              capture_output=True, timeout=10)
                
                # CPU affinity
                cpu_affinity = parameters.get('cpu_affinity', 'auto')
                if cpu_affinity != 'auto':
                    # Implementar affinity específica
                    pass
                
        except Exception as e:
            logger.error(f"❌ Erro ao otimizar CPU: {e}")
    
    def _apply_gpu_optimizations(self, parameters: Dict[str, Any]):
        """Aplica otimizações de GPU"""
        try:
            # NVIDIA GPU optimizations
            if parameters.get('gpu_power_limit') == 'maximum':
                subprocess.run(['nvidia-smi', '-i', '0', '-pl', 'max'], 
                              capture_output=True, timeout=10)
            
            # Performance mode
            if parameters.get('gpu_performance_mode') == 'performance':
                subprocess.run(['nvidia-smi', '-i', '0', '-pm', '1'], 
                              capture_output=True, timeout=10)
            
        except Exception as e:
            logger.error(f"❌ Erro ao otimizar GPU: {e}")
    
    def _apply_memory_optimizations(self, parameters: Dict[str, Any]):
        """Aplica otimizações de memória"""
        try:
            if platform.system() == 'Linux':
                # Swap settings
                if parameters.get('swap_usage') == 'minimal':
                    subprocess.run(['echo', 'vm.swappiness=10', '>', '/proc/sys/vm/swappiness'], 
                                  shell=True, capture_output=True, timeout=5)
                
                # Memory overcommit
                if not parameters.get('memory_overcommit', False):
                    subprocess.run(['echo', 'vm.overcommit_memory=0', '>', '/proc/sys/vm/overcommit_memory'], 
                                  shell=True, capture_output=True, timeout=5)
            
        except Exception as e:
            logger.error(f"❌ Erro ao otimizar memória: {e}")
    
    def _apply_storage_optimizations(self, parameters: Dict[str, Any]):
        """Aplica otimizações de storage"""
        try:
            if platform.system() == 'Linux':
                # I/O scheduler
                scheduler = parameters.get('io_scheduler', 'deadline')
                subprocess.run(['echo', scheduler, '>', '/sys/block/sda/queue/scheduler'], 
                              shell=True, capture_output=True, timeout=5)
                
                # Read-ahead
                readahead = parameters.get('read_ahead', 'maximum')
                if readahead == 'maximum':
                    subprocess.run(['blockdev', '--setra', '256', '/dev/sda'], 
                                  capture_output=True, timeout=5)
            
        except Exception as e:
            logger.error(f"❌ Erro ao otimizar storage: {e}")
    
    def monitor_optimization_performance(self, profile_name: str, 
                                      duration_minutes: int = 10) -> Dict[str, Any]:
        """Monitora performance da otimização"""
        if profile_name not in self.profiles:
            return {'error': 'Perfil não encontrado'}
        
        profile = self.profiles[profile_name]
        monitoring_data = {
            'profile_name': profile_name,
            'start_time': datetime.now(),
            'duration_minutes': duration_minutes,
            'metrics': [],
            'alerts': []
        }
        
        # Coleta métricas durante o período
        start_time = time.time()
        
        while time.time() - start_time < duration_minutes * 60:
            try:
                # Coleta métricas do sistema
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                disk_io = psutil.disk_io_counters()
                network_io = psutil.net_io_counters()
                
                metric = {
                    'timestamp': datetime.now(),
                    'cpu_utilization': cpu_percent,
                    'memory_utilization': memory.percent,
                    'memory_available_gb': memory.available / (1024**3),
                    'disk_read_mb_s': disk_io.read_bytes / (1024*1024) if disk_io else 0,
                    'disk_write_mb_s': disk_io.write_bytes / (1024*1024) if disk_io else 0,
                    'network_recv_mb_s': network_io.bytes_recv / (1024*1024) if network_io else 0,
                    'network_sent_mb_s': network_io.bytes_sent / (1024*1024) if network_io else 0
                }
                
                monitoring_data['metrics'].append(metric)
                
                # Verifica alertas
                if cpu_percent > 90:
                    monitoring_data['alerts'].append({
                        'timestamp': datetime.now(),
                        'type': 'cpu_high',
                        'message': f'CPU utilization high: {cpu_percent}%'
                    })
                
                if memory.percent > 90:
                    monitoring_data['alerts'].append({
                        'timestamp': datetime.now(),
                        'type': 'memory_high',
                        'message': f'Memory utilization high: {memory.percent}%'
                    })
                
                time.sleep(5)  # Coleta a cada 5 segundos
                
            except Exception as e:
                logger.error(f"❌ Erro no monitoramento: {e}")
                time.sleep(5)
        
        # Calcula estatísticas
        if monitoring_data['metrics']:
            cpu_values = [m['cpu_utilization'] for m in monitoring_data['metrics']]
            memory_values = [m['memory_utilization'] for m in monitoring_data['metrics']]
            
            monitoring_data['statistics'] = {
                'avg_cpu_utilization': np.mean(cpu_values),
                'max_cpu_utilization': np.max(cpu_values),
                'avg_memory_utilization': np.mean(memory_values),
                'max_memory_utilization': np.max(memory_values),
                'total_alerts': len(monitoring_data['alerts'])
            }
        
        return monitoring_data

class SpecializedHardwareConfig:
    """Sistema de configuração de hardware especializado"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        
        # Componentes
        self.hardware_detector = HardwareDetector()
        self.performance_optimizer = PerformanceOptimizer(self.config.get('optimizer', {}))
        
        # Estado
        self.detected_hardware = {}
        self.optimization_profiles = {}
        self.monitoring_data = {}
        
        logger.info("🖥️ SpecializedHardwareConfig inicializado")
    
    def detect_and_configure_hardware(self) -> Dict[str, Any]:
        """Detecta e configura hardware especializado"""
        logger.info("🔍 Detectando hardware especializado...")
        
        # Detecta hardware
        self.detected_hardware = self.hardware_detector.detect_all_hardware()
        
        # Cria perfis de otimização automáticos
        self._create_automatic_profiles()
        
        # Gera recomendações
        recommendations = self._generate_hardware_recommendations()
        
        result = {
            'detected_hardware': {
                component: spec.to_dict() 
                for component, spec in self.detected_hardware.items()
            },
            'optimization_profiles': {
                name: profile.to_dict() 
                for name, profile in self.optimization_profiles.items()
            },
            'recommendations': recommendations,
            'system_summary': self._get_system_summary()
        }
        
        logger.info("✅ Hardware detectado e configurado")
        
        return result
    
    def _create_automatic_profiles(self):
        """Cria perfis de otimização automáticos"""
        hardware_specs = self.detected_hardware
        
        # Perfil de performance máxima
        self.performance_optimizer.create_optimization_profile(
            name="maximum_performance",
            workload_type=WorkloadType.TRAINING,
            hardware_specs=hardware_specs,
            optimization_type=OptimizationType.PERFORMANCE
        )
        
        # Perfil de eficiência energética
        self.performance_optimizer.create_optimization_profile(
            name="power_efficiency",
            workload_type=WorkloadType.INFERENCE,
            hardware_specs=hardware_specs,
            optimization_type=OptimizationType.POWER_EFFICIENCY
        )
        
        # Perfil de baixa latência
        self.performance_optimizer.create_optimization_profile(
            name="low_latency",
            workload_type=WorkloadType.REAL_TIME,
            hardware_specs=hardware_specs,
            optimization_type=OptimizationType.LATENCY_OPTIMIZATION
        )
        
        # Perfil de alto throughput
        self.performance_optimizer.create_optimization_profile(
            name="high_throughput",
            workload_type=WorkloadType.BATCH,
            hardware_specs=hardware_specs,
            optimization_type=OptimizationType.THROUGHPUT_OPTIMIZATION
        )
        
        self.optimization_profiles = self.performance_optimizer.profiles
        
        logger.info("📋 Perfis de otimização automáticos criados")
    
    def _generate_hardware_recommendations(self) -> List[str]:
        """Gera recomendações de hardware"""
        recommendations = []
        
        # Analisa CPU
        if 'cpu' in self.detected_hardware:
            cpu = self.detected_hardware['cpu']
            if cpu.cores < 8:
                recommendations.append(
                    f"Considerar upgrade da CPU: {cpu.vendor} {cpu.model} tem apenas {cpu.cores} cores"
                )
            if cpu.clock_speed_ghz < 3.0:
                recommendations.append(
                    f"CPU com clock baixo: {cpu.clock_speed_ghz:.1f}GHz. Considerar upgrade para melhor performance"
                )
        
        # Analisa GPU
        if 'gpus' in self.detected_hardware:
            for i, gpu in enumerate(self.detected_hardware['gpus']):
                if gpu.memory_gb < 8:
                    recommendations.append(
                        f"GPU {i+1} com pouca memória: {gpu.memory_gb:.1f}GB. Considerar GPU com mais VRAM"
                    )
                if gpu.bandwidth_gbps < 256:
                    recommendations.append(
                        f"GPU {i+1} com baixa largura de banda: {gpu.bandwidth_gbps:.0f}GB/s"
                    )
        else:
            recommendations.append(
                "Nenhuma GPU detectada. Considerar adicionar GPU para acelerar workloads de ML"
            )
        
        # Analisa memória
        if 'memory' in self.detected_hardware:
            memory = self.detected_hardware['memory']
            if memory.memory_gb < 16:
                recommendations.append(
                    f"Memória RAM insuficiente: {memory.memory_gb:.1f}GB. Considerar upgrade para 32GB+"
                )
            if memory.bandwidth_gbps < 25:
                recommendations.append(
                    f"Memória com baixa largura de banda: {memory.bandwidth_gbps:.1f}GB/s"
                )
        
        # Analisa storage
        if 'storage' in self.detected_hardware:
            for i, storage in enumerate(self.detected_hardware['storage']):
                if storage.architecture == 'HDD':
                    recommendations.append(
                        f"Storage {i+1} é HDD. Considerar upgrade para SSD para melhor performance"
                    )
        
        if not recommendations:
            recommendations.append("Hardware configurado adequadamente para workloads modernos")
        
        return recommendations
    
    def _get_system_summary(self) -> Dict[str, Any]:
        """Obtém resumo do sistema"""
        summary = {
            'platform': platform.platform(),
            'architecture': platform.architecture()[0],
            'processor': platform.processor(),
            'total_cores': psutil.cpu_count(),
            'logical_cores': psutil.cpu_count(logical=True),
            'total_memory_gb': psutil.virtual_memory().total / (1024**3),
            'detected_components': len(self.detected_hardware),
            'optimization_profiles': len(self.optimization_profiles)
        }
        
        # Adiciona informações específicas
        if 'cpu' in self.detected_hardware:
            summary['cpu_details'] = {
                'vendor': self.detected_hardware['cpu'].vendor,
                'model': self.detected_hardware['cpu'].model,
                'clock_speed': self.detected_hardware['cpu'].clock_speed_ghz
            }
        
        if 'gpus' in self.detected_hardware:
            summary['gpu_count'] = len(self.detected_hardware['gpus'])
            summary['total_gpu_memory_gb'] = sum(
                gpu.memory_gb for gpu in self.detected_hardware['gpus']
            )
        
        return summary
    
    def apply_optimization_profile(self, profile_name: str) -> bool:
        """Aplica perfil de otimização"""
        return self.performance_optimizer.apply_optimization_profile(profile_name)
    
    def monitor_performance(self, profile_name: str, 
                           duration_minutes: int = 10) -> Dict[str, Any]:
        """Monitora performance da otimização"""
        return self.performance_optimizer.monitor_optimization_performance(
            profile_name, duration_minutes
        )
    
    def save_configuration(self, filepath: str):
        """Salva configuração de hardware"""
        config_data = {
            'timestamp': datetime.now().isoformat(),
            'detected_hardware': {
                component: spec.to_dict() 
                for component, spec in self.detected_hardware.items()
            },
            'optimization_profiles': {
                name: profile.to_dict() 
                for name, profile in self.optimization_profiles.items()
            },
            'config': self.config,
            'system_info': self._get_system_summary()
        }
        
        with open(filepath, 'w') as f:
            json.dump(config_data, f, indent=2, default=str)
        
        logger.info(f"💾 Configuração salva em {filepath}")
    
    def load_configuration(self, filepath: str):
        """Carrega configuração de hardware"""
        try:
            with open(filepath, 'r') as f:
                config_data = json.load(f)
            
            self.detected_hardware = config_data.get('detected_hardware', {})
            self.config = config_data.get('config', {})
            
            logger.info(f"📂 Configuração carregada de {filepath}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao carregar configuração: {e}")

# Configuração padrão
DEFAULT_HARDWARE_CONFIG = {
    'auto_detect': True,
    'auto_optimize': True,
    'monitoring_interval': 60,
    'optimization_profiles': {
        'training': 'maximum_performance',
        'inference': 'power_efficiency',
        'real_time': 'low_latency',
        'batch': 'high_throughput'
    },
    'thresholds': {
        'cpu_warning': 80,
        'cpu_critical': 95,
        'memory_warning': 85,
        'memory_critical': 95,
        'gpu_warning': 85,
        'gpu_critical': 95
    }
}

if __name__ == "__main__":
    # Exemplo de uso
    def test_hardware_config():
        """Testa sistema de configuração de hardware"""
        print("🖥️ Iniciando Teste do Sistema de Configuração de Hardware")
        print("=" * 70)
        
        # Cria sistema
        hardware_config = SpecializedHardwareConfig(DEFAULT_HARDWARE_CONFIG)
        
        # Detecta e configura hardware
        print("\n🔍 Detectando e configurando hardware...")
        configuration = hardware_config.detect_and_configure_hardware()
        
        # Mostra hardware detectado
        print(f"\n💻 HARDWARE DETECTADO:")
        print("=" * 40)
        
        system_summary = configuration['system_summary']
        print(f"Plataforma: {system_summary['platform']}")
        print(f"Arquitetura: {system_summary['architecture']}")
        print(f"Processador: {system_summary['processor']}")
        print(f"Núcleos (físicos/lógicos): {system_summary['total_cores']}/{system_summary['logical_cores']}")
        print(f"Memória Total: {system_summary['total_memory_gb']:.1f} GB")
        print(f"Componentes Detectados: {system_summary['detected_components']}")
        
        if 'gpu_count' in system_summary:
            print(f"GPUs: {system_summary['gpu_count']}")
            print(f"Memória GPU Total: {system_summary.get('total_gpu_memory_gb', 0):.1f} GB")
        
        # Detalhes da CPU
        if 'cpu_details' in system_summary:
            cpu = system_summary['cpu_details']
            print(f"\n🖥️ CPU:")
            print(f"  Vendor: {cpu['vendor']}")
            print(f"  Modelo: {cpu['model']}")
            print(f"  Clock: {cpu['clock_speed']:.1f} GHz")
        
        # Perfis de otimização
        print(f"\n⚡ PERFIS DE OTIMIZAÇÃO:")
        print("=" * 40)
        
        for name, profile in configuration['optimization_profiles'].items():
            print(f"  • {name}")
            print(f"    Workload: {profile['workload_type']}")
            print(f"    Otimização: {profile['optimization_type']}")
            print(f"    Parâmetros: {len(profile['parameters'])} configurados")
        
        # Recomendações
        print(f"\n💡 RECOMENDAÇÕES:")
        print("=" * 40)
        
        for i, rec in enumerate(configuration['recommendations'], 1):
            print(f"  {i}. {rec}")
        
        # Testa aplicação de perfil
        print(f"\n🔧 TESTANDO APLICAÇÃO DE PERFIL:")
        print("=" * 40)
        
        profile_name = "maximum_performance"
        if profile_name in configuration['optimization_profiles']:
            success = hardware_config.apply_optimization_profile(profile_name)
            print(f"  Perfil '{profile_name}': {'✅ Sucesso' if success else '❌ Falha'}")
        
        # Monitoramento de performance
        print(f"\n📊 MONITORAMENTO DE PERFORMANCE (10s):")
        print("=" * 40)
        
        monitoring_data = hardware_config.monitor_performance(
            profile_name, duration_minutes=0.17  # ~10 segundos
        )
        
        if 'statistics' in monitoring_data:
            stats = monitoring_data['statistics']
            print(f"  CPU Médio: {stats['avg_cpu_utilization']:.1f}%")
            print(f"  CPU Máximo: {stats['max_cpu_utilization']:.1f}%")
            print(f"  Memória Média: {stats['avg_memory_utilization']:.1f}%")
            print(f"  Memória Máxima: {stats['max_memory_utilization']:.1f}%")
            print(f"  Alertas: {stats['total_alerts']}")
        
        # Salva configuração
        hardware_config.save_configuration('hardware_config.json')
        
        print(f"\n💾 Configuração salva em hardware_config.json")
        print("✅ Teste do sistema de hardware concluído com sucesso!")
        
        return hardware_config, configuration
    
    # Executa teste
    hardware_config, config_data = test_hardware_config()
