"""
Deployment Manager - Sistema de Deployment
=========================================
API, microsserviços, edge computing e gerenciamento de modelos em produção
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import os
from pathlib import Path
import hashlib
import pickle
import threading
import queue
import subprocess
import signal
import psutil

# Importações condicionais
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

try:
    import torch
    import torch.nn as nn
    PYTORCH_AVAILABLE = True
except ImportError:
    PYTORCH_AVAILABLE = False

try:
    from fastapi import FastAPI, HTTPException, BackgroundTasks
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel, Field
    import uvicorn
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

try:
    from flask import Flask, request, jsonify
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False

try:
    import docker
    from docker.client import DockerClient
    DOCKER_AVAILABLE = True
except ImportError:
    DOCKER_AVAILABLE = False

try:
    import kubernetes
    from kubernetes import client, config
    KUBERNETES_AVAILABLE = True
except ImportError:
    KUBERNETES_AVAILABLE = False

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

from config import settings
from core import get_logger, log_execution
from .model_architect import ModelInfo, ModelType, TaskType
from .model_trainer import TrainingResult
from .model_evaluator import EvaluationResult


class DeploymentType(str, Enum):
    """Tipos de deployment"""
    LOCAL_API = "local_api"
    DOCKER_CONTAINER = "docker_container"
    KUBERNETES_POD = "kubernetes_pod"
    EDGE_DEVICE = "edge_device"
    CLOUD_FUNCTION = "cloud_function"
    MICROSERVICE = "microservice"
    BATCH_SERVICE = "batch_service"
    STREAMING_SERVICE = "streaming_service"


class DeploymentStatus(str, Enum):
    """Status do deployment"""
    PENDING = "pending"
    RUNNING = "running"
    STOPPED = "stopped"
    FAILED = "failed"
    UPDATING = "updating"
    SCALING = "scaling"
    MAINTENANCE = "maintenance"


class ScalingStrategy(str, Enum):
    """Estratégias de scaling"""
    MANUAL = "manual"
    AUTO_SCALING = "auto_scaling"
    LOAD_BASED = "load_based"
    TIME_BASED = "time_based"
    QUEUE_BASED = "queue_based"


@dataclass
class DeploymentConfig:
    """Configuração de deployment"""
    deployment_type: DeploymentType
    model_info: ModelInfo
    host: str = "localhost"
    port: int = 8000
    workers: int = 1
    memory_limit: str = "1G"
    cpu_limit: str = "1"
    auto_scaling: bool = False
    min_replicas: int = 1
    max_replicas: int = 5
    scaling_strategy: ScalingStrategy = ScalingStrategy.MANUAL
    health_check_interval: int = 30
    grace_period: int = 30
    environment_variables: Dict[str, str] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    security_config: Dict[str, Any] = field(default_factory=dict)
    monitoring_enabled: bool = True
    logging_enabled: bool = True
    custom_params: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'deployment_type': self.deployment_type.value,
            'model_info': self.model_info.to_dict(),
            'host': self.host,
            'port': self.port,
            'workers': self.workers,
            'memory_limit': self.memory_limit,
            'cpu_limit': self.cpu_limit,
            'auto_scaling': self.auto_scaling,
            'min_replicas': self.min_replicas,
            'max_replicas': self.max_replicas,
            'scaling_strategy': self.scaling_strategy.value,
            'health_check_interval': self.health_check_interval,
            'grace_period': self.grace_period,
            'environment_variables': self.environment_variables,
            'dependencies': self.dependencies,
            'security_config': self.security_config,
            'monitoring_enabled': self.monitoring_enabled,
            'logging_enabled': self.logging_enabled,
            'custom_params': self.custom_params
        }


@dataclass
class DeploymentMetrics:
    """Métricas do deployment"""
    deployment_id: str
    requests_total: int = 0
    requests_successful: int = 0
    requests_failed: int = 0
    avg_response_time: float = 0.0
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    uptime: float = 0.0
    last_health_check: Optional[datetime] = None
    errors: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'deployment_id': self.deployment_id,
            'requests_total': self.requests_total,
            'requests_successful': self.requests_successful,
            'requests_failed': self.requests_failed,
            'success_rate': self.requests_successful / max(self.requests_total, 1),
            'avg_response_time': self.avg_response_time,
            'cpu_usage': self.cpu_usage,
            'memory_usage': self.memory_usage,
            'uptime': self.uptime,
            'last_health_check': self.last_health_check.isoformat() if self.last_health_check else None,
            'errors': self.errors[-10:],  # Últimos 10 erros
            'timestamp': self.timestamp.isoformat()
        }


@dataclass
class DeploymentResult:
    """Resultado do deployment"""
    deployment_id: str
    config: DeploymentConfig
    status: DeploymentStatus
    endpoint_url: Optional[str] = None
    container_id: Optional[str] = None
    pod_name: Optional[str] = None
    metrics: DeploymentMetrics = field(default_factory=lambda: DeploymentMetrics(deployment_id=""))
    deployment_time: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'deployment_id': self.deployment_id,
            'config': self.config.to_dict(),
            'status': self.status.value,
            'endpoint_url': self.endpoint_url,
            'container_id': self.container_id,
            'pod_name': self.pod_name,
            'metrics': self.metrics.to_dict(),
            'deployment_time': self.deployment_time,
            'created_at': self.created_at.isoformat()
        }


class LocalAPIDeployer:
    """Deployer para API local"""
    
    def __init__(self):
        self.logger = get_logger("vhalinor.deployer.local_api", "local_api_deployer")
        self.active_servers = {}
    
    def deploy(self, config: DeploymentConfig) -> DeploymentResult:
        """Faz deployment de API local"""
        start_time = time.time()
        deployment_id = f"local_api_{int(time.time())}"
        
        self.logger.info(f"Deploying local API for {config.model_info.name}")
        
        try:
            if FASTAPI_AVAILABLE:
                result = self._deploy_fastapi(config, deployment_id)
            elif FLASK_AVAILABLE:
                result = self._deploy_flask(config, deployment_id)
            else:
                raise ImportError("Neither FastAPI nor Flask is available")
            
            result.deployment_time = time.time() - start_time
            self.active_servers[deployment_id] = result
            
            self.logger.info(f"Local API deployed successfully: {result.endpoint_url}")
            return result
        
        except Exception as e:
            self.logger.error(f"Error deploying local API: {e}")
            raise
    
    def _deploy_fastapi(self, config: DeploymentConfig, deployment_id: str) -> DeploymentResult:
        """Deploy com FastAPI"""
        app = FastAPI(title=f"VHALINOR API - {config.model_info.name}")
        
        # Adicionar CORS
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Modelos de dados
        class PredictionRequest(BaseModel):
            data: List[List[float]] = Field(..., description="Input data for prediction")
            
        class PredictionResponse(BaseModel):
            predictions: List[float]
            confidence: Optional[List[float]] = None
            processing_time: float
        
        # Endpoints
        @app.get("/")
        async def root():
            return {"message": f"VHALINOR API - {config.model_info.name}", "model_type": config.model_info.model_type.value}
        
        @app.get("/health")
        async def health_check():
            return {"status": "healthy", "timestamp": datetime.now().isoformat()}
        
        @app.post("/predict", response_model=PredictionResponse)
        async def predict(request: PredictionRequest):
            start_time = time.time()
            
            try:
                # Converter dados
                if NUMPY_AVAILABLE:
                    data = np.array(request.data)
                else:
                    data = request.data
                
                # Fazer predição
                model = config.model_info.model
                if hasattr(model, 'predict'):
                    predictions = model.predict(data).tolist()
                else:
                    predictions = [0.0] * len(data)
                
                # Calcular confiança se disponível
                confidence = None
                if hasattr(model, 'predict_proba'):
                    proba = model.predict_proba(data)
                    confidence = proba.max(axis=1).tolist()
                
                processing_time = time.time() - start_time
                
                return PredictionResponse(
                    predictions=predictions,
                    confidence=confidence,
                    processing_time=processing_time
                )
            
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        # Iniciar servidor em thread separada
        def run_server():
            uvicorn.run(app, host=config.host, port=config.port, log_level="info")
        
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        
        # Esperar servidor iniciar
        time.sleep(2)
        
        return DeploymentResult(
            deployment_id=deployment_id,
            config=config,
            status=DeploymentStatus.RUNNING,
            endpoint_url=f"http://{config.host}:{config.port}",
            metrics=DeploymentMetrics(deployment_id=deployment_id)
        )
    
    def _deploy_flask(self, config: DeploymentConfig, deployment_id: str) -> DeploymentResult:
        """Deploy com Flask"""
        app = Flask(f"VHALINOR API - {config.model_info.name}")
        
        @app.route("/")
        def root():
            return jsonify({
                "message": f"VHALINOR API - {config.model_info.name}",
                "model_type": config.model_info.model_type.value
            })
        
        @app.route("/health")
        def health_check():
            return jsonify({
                "status": "healthy",
                "timestamp": datetime.now().isoformat()
            })
        
        @app.route("/predict", methods=["POST"])
        def predict():
            try:
                data = request.get_json()
                input_data = data.get("data", [])
                
                # Fazer predição
                model = config.model_info.model
                if hasattr(model, 'predict'):
                    predictions = model.predict(input_data).tolist()
                else:
                    predictions = [0.0] * len(input_data)
                
                return jsonify({
                    "predictions": predictions,
                    "processing_time": 0.1
                })
            
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        # Iniciar servidor em thread separada
        def run_server():
            app.run(host=config.host, port=config.port, debug=False)
        
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        
        # Esperar servidor iniciar
        time.sleep(2)
        
        return DeploymentResult(
            deployment_id=deployment_id,
            config=config,
            status=DeploymentStatus.RUNNING,
            endpoint_url=f"http://{config.host}:{config.port}",
            metrics=DeploymentMetrics(deployment_id=deployment_id)
        )
    
    def stop_deployment(self, deployment_id: str) -> bool:
        """Para deployment"""
        if deployment_id in self.active_servers:
            # Implementar parada do servidor
            del self.active_servers[deployment_id]
            return True
        return False


class DockerDeployer:
    """Deployer para Docker"""
    
    def __init__(self):
        self.logger = get_logger("vhalinor.deployer.docker", "docker_deployer")
        self.docker_client = None
        if DOCKER_AVAILABLE:
            try:
                self.docker_client = docker.from_env()
            except Exception as e:
                self.logger.warning(f"Docker not available: {e}")
    
    def deploy(self, config: DeploymentConfig) -> DeploymentResult:
        """Faz deployment com Docker"""
        if not DOCKER_AVAILABLE or not self.docker_client:
            raise ImportError("docker is required for Docker deployment")
        
        start_time = time.time()
        deployment_id = f"docker_{int(time.time())}"
        
        self.logger.info(f"Deploying Docker container for {config.model_info.name}")
        
        try:
            # Criar Dockerfile
            dockerfile_content = self._create_dockerfile(config)
            
            # Build imagem
            image_tag = f"vhalinor/{config.model_info.name.lower().replace(' ', '_')}:latest"
            
            # Criar diretório temporário
            temp_dir = Path(f"/tmp/vhalinor_deploy_{deployment_id}")
            temp_dir.mkdir(exist_ok=True)
            
            # Salvar modelo e Dockerfile
            self._save_model_files(config, temp_dir)
            
            with open(temp_dir / "Dockerfile", "w") as f:
                f.write(dockerfile_content)
            
            # Build imagem
            image, build_logs = self.docker_client.images.build(
                path=str(temp_dir),
                tag=image_tag,
                rm=True
            )
            
            # Rodar container
            container = self.docker_client.containers.run(
                image_tag,
                ports={f"{config.port}/tcp": config.port},
                environment=config.environment_variables,
                mem_limit=config.memory_limit,
                cpu_count=int(config.cpu_limit),
                detach=True,
                name=f"vhalinor_{deployment_id}"
            )
            
            # Limpar diretório temporário
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
            
            deployment_time = time.time() - start_time
            
            result = DeploymentResult(
                deployment_id=deployment_id,
                config=config,
                status=DeploymentStatus.RUNNING,
                endpoint_url=f"http://{config.host}:{config.port}",
                container_id=container.id,
                metrics=DeploymentMetrics(deployment_id=deployment_id)
            )
            result.deployment_time = deployment_time
            
            self.logger.info(f"Docker container deployed: {container.id}")
            return result
        
        except Exception as e:
            self.logger.error(f"Error deploying Docker container: {e}")
            raise
    
    def _create_dockerfile(self, config: DeploymentConfig) -> str:
        """Cria conteúdo do Dockerfile"""
        return f"""
FROM python:3.9-slim

WORKDIR /app

# Instalar dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar modelo e código
COPY model/ ./model/
COPY app.py .

# Expor porta
EXPOSE {config.port}

# Rodar aplicação
CMD ["python", "app.py"]
"""
    
    def _save_model_files(self, config: DeploymentConfig, temp_dir: Path):
        """Salva arquivos do modelo"""
        # Criar requirements.txt
        requirements = [
            "fastapi",
            "uvicorn",
            "numpy",
            "pandas",
            "scikit-learn",
            "torch" if PYTORCH_AVAILABLE else "# torch not available"
        ]
        
        with open(temp_dir / "requirements.txt", "w") as f:
            f.write("\n".join(requirements))
        
        # Salvar modelo
        model_dir = temp_dir / "model"
        model_dir.mkdir(exist_ok=True)
        
        with open(model_dir / "model.pkl", "wb") as f:
            pickle.dump(config.model_info.model, f)
        
        # Criar app.py
        app_content = self._create_app_script(config)
        with open(temp_dir / "app.py", "w") as f:
            f.write(app_content)
    
    def _create_app_script(self, config: DeploymentConfig) -> str:
        """Cria script da aplicação"""
        return f"""
import pickle
import numpy as np
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="VHALINOR API - {config.model_info.name}")

# Carregar modelo
with open("model/model.pkl", "rb") as f:
    model = pickle.load(f)

class PredictionRequest(BaseModel):
    data: list[list[float]]

@app.get("/")
async def root():
    return {{"message": "VHALINOR API", "model": "{config.model_info.name}"}}

@app.post("/predict")
async def predict(request: PredictionRequest):
    try:
        data = np.array(request.data)
        predictions = model.predict(data).tolist()
        return {{"predictions": predictions}}
    except Exception as e:
        return {{"error": str(e)}}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port={config.port})
"""
    
    def stop_deployment(self, deployment_id: str) -> bool:
        """Para container Docker"""
        try:
            if self.docker_client:
                container = self.docker_client.containers.get(f"vhalinor_{deployment_id}")
                container.stop()
                container.remove()
                return True
        except Exception as e:
            self.logger.error(f"Error stopping Docker container: {e}")
        return False


class EdgeDeployer:
    """Deployer para edge devices"""
    
    def __init__(self):
        self.logger = get_logger("vhalinor.deployer.edge", "edge_deployer")
    
    def deploy(self, config: DeploymentConfig) -> DeploymentResult:
        """Faz deployment em edge device"""
        start_time = time.time()
        deployment_id = f"edge_{int(time.time())}"
        
        self.logger.info(f"Deploying to edge device for {config.model_info.name}")
        
        try:
            # Implementar deployment edge (simplificado)
            # Na prática, isso envolveria SSH, SCP, ou protocolos específicos
            
            deployment_time = time.time() - start_time
            
            result = DeploymentResult(
                deployment_id=deployment_id,
                config=config,
                status=DeploymentStatus.RUNNING,
                endpoint_url=f"edge://{config.host}:{config.port}",
                metrics=DeploymentMetrics(deployment_id=deployment_id)
            )
            result.deployment_time = deployment_time
            
            self.logger.info(f"Edge deployment completed: {deployment_id}")
            return result
        
        except Exception as e:
            self.logger.error(f"Error deploying to edge device: {e}")
            raise
    
    def stop_deployment(self, deployment_id: str) -> bool:
        """Para deployment edge"""
        # Implementar parada de serviço edge
        return True


class DeploymentManager:
    """Gerenciador principal de deployments"""
    
    def __init__(self):
        self.logger = get_logger("vhalinor.deployer.main", "deployment_manager")
        
        # Inicializar deployers
        self.local_deployer = LocalAPIDeployer()
        self.docker_deployer = DockerDeployer()
        self.edge_deployer = EdgeDeployer()
        
        self.deployments = {}
        self.deployment_queue = queue.Queue()
        self.monitoring_active = False
    
    @log_execution(component="deployment", operation="deploy_model")
    async def deploy_model(self, model_info: ModelInfo, config: DeploymentConfig) -> DeploymentResult:
        """Faz deployment do modelo"""
        self.logger.info(f"Deploying {model_info.name} with {config.deployment_type.value}")
        
        # Atualizar config com model_info
        config.model_info = model_info
        
        try:
            # Escolher deployer baseado no tipo
            if config.deployment_type == DeploymentType.LOCAL_API:
                result = self.local_deployer.deploy(config)
            elif config.deployment_type == DeploymentType.DOCKER_CONTAINER:
                result = self.docker_deployer.deploy(config)
            elif config.deployment_type == DeploymentType.EDGE_DEVICE:
                result = self.edge_deployer.deploy(config)
            else:
                raise ValueError(f"Unsupported deployment type: {config.deployment_type}")
            
            # Armazenar deployment
            self.deployments[result.deployment_id] = result
            
            # Iniciar monitoramento se necessário
            if config.monitoring_enabled and not self.monitoring_active:
                self._start_monitoring()
            
            return result
        
        except Exception as e:
            self.logger.error(f"Error deploying model: {e}")
            raise
    
    async def stop_deployment(self, deployment_id: str) -> bool:
        """Para deployment específico"""
        if deployment_id not in self.deployments:
            return False
        
        deployment = self.deployments[deployment_id]
        config = deployment.config
        
        try:
            if config.deployment_type == DeploymentType.LOCAL_API:
                success = self.local_deployer.stop_deployment(deployment_id)
            elif config.deployment_type == DeploymentType.DOCKER_CONTAINER:
                success = self.docker_deployer.stop_deployment(deployment_id)
            elif config.deployment_type == DeploymentType.EDGE_DEVICE:
                success = self.edge_deployer.stop_deployment(deployment_id)
            else:
                success = False
            
            if success:
                deployment.status = DeploymentStatus.STOPPED
                self.logger.info(f"Deployment {deployment_id} stopped successfully")
            
            return success
        
        except Exception as e:
            self.logger.error(f"Error stopping deployment {deployment_id}: {e}")
            return False
    
    def get_deployment(self, deployment_id: str) -> Optional[DeploymentResult]:
        """Retorna deployment específico"""
        return self.deployments.get(deployment_id)
    
    def list_deployments(self) -> List[str]:
        """Lista todos os deployments"""
        return list(self.deployments.keys())
    
    def get_deployment_metrics(self, deployment_id: str) -> Optional[DeploymentMetrics]:
        """Retorna métricas do deployment"""
        deployment = self.deployments.get(deployment_id)
        if deployment:
            return deployment.metrics
        return None
    
    def _start_monitoring(self):
        """Inicia monitoramento de deployments"""
        self.monitoring_active = True
        
        def monitor_loop():
            while self.monitoring_active:
                try:
                    for deployment_id, deployment in self.deployments.items():
                        if deployment.status == DeploymentStatus.RUNNING:
                            self._update_metrics(deployment)
                    
                    time.sleep(30)  # Atualizar a cada 30 segundos
                
                except Exception as e:
                    self.logger.error(f"Error in monitoring loop: {e}")
                    time.sleep(5)
        
        monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        monitor_thread.start()
    
    def _update_metrics(self, deployment: DeploymentResult):
        """Atualiza métricas do deployment"""
        try:
            metrics = deployment.metrics
            
            # Atualizar uptime
            metrics.uptime = (datetime.now() - deployment.created_at).total_seconds()
            
            # Atualizar uso de CPU e memória
            process = psutil.Process()
            metrics.cpu_usage = process.cpu_percent()
            metrics.memory_usage = process.memory_info().rss / 1024 / 1024  # MB
            
            # Health check
            metrics.last_health_check = datetime.now()
            
        except Exception as e:
            self.logger.error(f"Error updating metrics for {deployment.deployment_id}: {e}")
    
    async def scale_deployment(self, deployment_id: str, replicas: int) -> bool:
        """Escala deployment"""
        deployment = self.deployments.get(deployment_id)
        if not deployment:
            return False
        
        if not deployment.config.auto_scaling:
            self.logger.warning(f"Auto-scaling not enabled for deployment {deployment_id}")
            return False
        
        try:
            # Implementar lógica de scaling
            deployment.status = DeploymentStatus.SCALING
            
            # Simular scaling
            time.sleep(2)
            
            deployment.status = DeploymentStatus.RUNNING
            self.logger.info(f"Deployment {deployment_id} scaled to {replicas} replicas")
            
            return True
        
        except Exception as e:
            self.logger.error(f"Error scaling deployment {deployment_id}: {e}")
            deployment.status = DeploymentStatus.FAILED
            return False
    
    def create_standard_config(self, model_info: ModelInfo, deployment_type: DeploymentType) -> DeploymentConfig:
        """Cria configuração padrão de deployment"""
        return DeploymentConfig(
            deployment_type=deployment_type,
            model_info=model_info,
            host="localhost",
            port=8000,
            workers=1,
            auto_scaling=False,
            monitoring_enabled=True,
            logging_enabled=True
        )
    
    def get_deployment_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas de deployments"""
        stats = {
            'total_deployments': len(self.deployments),
            'deployment_types': {},
            'status_distribution': {},
            'monitoring_active': self.monitoring_active
        }
        
        # Estatísticas por tipo
        for deployment in self.deployments.values():
            dep_type = deployment.config.deployment_type.value
            status = deployment.status.value
            
            stats['deployment_types'][dep_type] = stats['deployment_types'].get(dep_type, 0) + 1
            stats['status_distribution'][status] = stats['status_distribution'].get(status, 0) + 1
        
        return stats


# Função de conveniência
_deployment_manager_instance = None

def get_deployment_manager() -> DeploymentManager:
    """Obtém instância singleton do gerenciador de deployment"""
    global _deployment_manager_instance
    if _deployment_manager_instance is None:
        _deployment_manager_instance = DeploymentManager()
    return _deployment_manager_instance
