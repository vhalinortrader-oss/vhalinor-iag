"""
LEXTRADER-IAG 4.0 - Integração de Sistemas Autônomos
=====================================================
Módulo de integração dos sistemas autônomos com o programa principal

Versão: 4.0.0
Data: Janeiro 2026
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class AutonomousSystemType(Enum):
    """Tipos de sistemas autônomos"""
    VALIDATION = "validation"
    SYSTEM_SERVICE = "system_service"
    TRADING_CONTROLLER = "trading_controller"
    DECISION_ENGINE = "decision_engine"
    CREATOR = "creator"
    NEURAL_CREATOR = "neural_creator"
    MANAGER = "manager"
    DASHBOARD = "dashboard"


@dataclass
class AutonomousSystemInfo:
    """Informações sobre um sistema autônomo"""
    name: str
    type: AutonomousSystemType
    status: str
    description: str
    module_path: str
    class_name: str
    is_gui: bool = False
    dependencies: List[str] = None


class AutonomousIntegrationManager:
    """Gerenciador de integração dos sistemas autônomos"""
    
    def __init__(self):
        self.systems: Dict[str, AutonomousSystemInfo] = {}
        self.loaded_systems: Dict[str, Any] = {}
        self.initialize_system_registry()
        
        logger.info("🤖 Autonomous Integration Manager inicializado")
    
    def initialize_system_registry(self):
        """Inicializa registro de sistemas disponíveis"""
        
        # Sistema de Validação Autônoma
        self.systems['validation_service'] = AutonomousSystemInfo(
            name="Autonomous Validation Service",
            type=AutonomousSystemType.VALIDATION,
            status="available",
            description="Sistema de validação autônoma com auto-recuperação",
            module_path="AutonomousValidationService",
            class_name="AutonomousValidationService",
            is_gui=False
        )
        
        self.systems['validation_dashboard'] = AutonomousSystemInfo(
            name="Autonomous Validation Dashboard",
            type=AutonomousSystemType.DASHBOARD,
            status="available",
            description="Dashboard de validação autônoma (GUI)",
            module_path="AutonomousValidationDashboard",
            class_name="AutonomousValidationDashboard",
            is_gui=True
        )
        
        # Sistema Autônomo Principal
        self.systems['system_service'] = AutonomousSystemInfo(
            name="Autonomous System Service",
            type=AutonomousSystemType.SYSTEM_SERVICE,
            status="available",
            description="Serviço principal do sistema autônomo com rede neural quântica",
            module_path="AutonomousSystemService",
            class_name="AutonomousSystemService",
            is_gui=False
        )
        
        self.systems['system_dashboard'] = AutonomousSystemInfo(
            name="Autonomous System Dashboard",
            type=AutonomousSystemType.DASHBOARD,
            status="available",
            description="Dashboard do sistema autônomo (GUI)",
            module_path="AutonomousSystemDashboard",
            class_name="AutonomousSystemDashboard",
            is_gui=True
        )
        
        # Controlador de Trading Autônomo
        self.systems['trading_controller'] = AutonomousSystemInfo(
            name="Autonomous Trading Controller",
            type=AutonomousSystemType.TRADING_CONTROLLER,
            status="available",
            description="Controlador de trading autônomo com decisões de IA",
            module_path="AutonomousTradingController",
            class_name="AutonomousTradingControllerApp",
            is_gui=True
        )
        
        # Motor de Decisões Autônomas
        self.systems['decision_engine'] = AutonomousSystemInfo(
            name="Autonomous Decision Engine",
            type=AutonomousSystemType.DECISION_ENGINE,
            status="available",
            description="Motor de decisões autônomas com indicadores técnicos",
            module_path="AutonomousDecisionEngine",
            class_name="AutonomousDecisionEngineApp",
            is_gui=True
        )
        
        # Criador Autônomo
        self.systems['creator'] = AutonomousSystemInfo(
            name="Autonomous Creator",
            type=AutonomousSystemType.CREATOR,
            status="available",
            description="Criador autônomo de técnicas com inteligência de enxame",
            module_path="AutonomousCreator",
            class_name="AutonomousCreator",
            is_gui=True
        )
        
        # Criador Neural Autônomo
        self.systems['neural_creator'] = AutonomousSystemInfo(
            name="Autonomous Neural Creator",
            type=AutonomousSystemType.NEURAL_CREATOR,
            status="available",
            description="Criador neural autônomo com evolução genética",
            module_path="AutonomousNeuralCreator",
            class_name="AutonomousNeuralCreatorApp",
            is_gui=True
        )
        
        # Gerenciador Autônomo
        self.systems['manager'] = AutonomousSystemInfo(
            name="Autonomous Manager",
            type=AutonomousSystemType.MANAGER,
            status="available",
            description="Gerenciador autônomo com memória episódica e RL profundo",
            module_path="AutonomousManager",
            class_name="LextraderAutonomousSystem",
            is_gui=False
        )
        
        # Dashboard Autônomo
        self.systems['dashboard'] = AutonomousSystemInfo(
            name="Autonomous Dashboard",
            type=AutonomousSystemType.DASHBOARD,
            status="available",
            description="Dashboard autônomo com gráficos de performance",
            module_path="AutonomousDashboard",
            class_name="AutonomousDashboard",
            is_gui=True
        )
    
    def list_systems(self, gui_only: bool = False) -> List[AutonomousSystemInfo]:
        """Lista sistemas disponíveis"""
        systems = list(self.systems.values())
        
        if gui_only:
            systems = [s for s in systems if s.is_gui]
        
        return systems
    
    def get_system_info(self, system_id: str) -> Optional[AutonomousSystemInfo]:
        """Obtém informações de um sistema"""
        return self.systems.get(system_id)
    
    async def load_system(self, system_id: str) -> Optional[Any]:
        """Carrega um sistema autônomo"""
        if system_id in self.loaded_systems:
            logger.info(f"Sistema '{system_id}' já carregado")
            return self.loaded_systems[system_id]
        
        system_info = self.systems.get(system_id)
        if not system_info:
            logger.error(f"Sistema '{system_id}' não encontrado")
            return None
        
        try:
            # Importa o módulo dinamicamente
            module = __import__(system_info.module_path)
            
            # Obtém a classe
            system_class = getattr(module, system_info.class_name)
            
            # Instancia o sistema (sem GUI para sistemas não-GUI)
            if not system_info.is_gui:
                system_instance = system_class()
                self.loaded_systems[system_id] = system_instance
                logger.info(f"✅ Sistema '{system_info.name}' carregado")
                return system_instance
            else:
                # Para sistemas GUI, retorna a classe (será instanciada com Tkinter)
                self.loaded_systems[system_id] = system_class
                logger.info(f"✅ Sistema GUI '{system_info.name}' registrado")
                return system_class
        
        except Exception as e:
            logger.error(f"❌ Erro ao carregar sistema '{system_id}': {e}")
            return None
    
    def launch_gui_system(self, system_id: str):
        """Lança um sistema GUI"""
        system_info = self.systems.get(system_id)
        if not system_info:
            logger.error(f"Sistema '{system_id}' não encontrado")
            return False
        
        if not system_info.is_gui:
            logger.error(f"Sistema '{system_id}' não é GUI")
            return False
        
        try:
            import tkinter as tk
            
            # Carrega o sistema
            system_class = asyncio.run(self.load_system(system_id))
            if not system_class:
                return False
            
            # Cria janela Tkinter
            root = tk.Tk()
            
            # Instancia o sistema GUI
            app = system_class(root)
            
            # Inicia loop
            logger.info(f"🚀 Lançando GUI '{system_info.name}'")
            root.mainloop()
            
            return True
        
        except Exception as e:
            logger.error(f"❌ Erro ao lançar GUI '{system_id}': {e}")
            return False
    
    async def get_system_status(self, system_id: str) -> Dict[str, Any]:
        """Obtém status de um sistema"""
        system_info = self.systems.get(system_id)
        if not system_info:
            return {'error': 'Sistema não encontrado'}
        
        is_loaded = system_id in self.loaded_systems
        
        status = {
            'name': system_info.name,
            'type': system_info.type.value,
            'status': system_info.status,
            'description': system_info.description,
            'is_gui': system_info.is_gui,
            'is_loaded': is_loaded,
            'timestamp': datetime.now().isoformat()
        }
        
        # Se carregado, tenta obter estatísticas
        if is_loaded and not system_info.is_gui:
            try:
                system_instance = self.loaded_systems[system_id]
                if hasattr(system_instance, 'get_statistics'):
                    status['statistics'] = system_instance.get_statistics()
            except Exception as e:
                logger.warning(f"Não foi possível obter estatísticas de '{system_id}': {e}")
        
        return status
    
    async def get_all_status(self) -> Dict[str, Any]:
        """Obtém status de todos os sistemas"""
        all_status = {}
        
        for system_id in self.systems.keys():
            all_status[system_id] = await self.get_system_status(system_id)
        
        return {
            'timestamp': datetime.now().isoformat(),
            'total_systems': len(self.systems),
            'loaded_systems': len(self.loaded_systems),
            'systems': all_status
        }
    
    def print_systems_menu(self):
        """Imprime menu de sistemas"""
        print("\n" + "=" * 80)
        print("🤖 SISTEMAS AUTÔNOMOS DISPONÍVEIS")
        print("=" * 80)
        
        # Agrupa por tipo
        by_type = {}
        for system_id, system_info in self.systems.items():
            type_name = system_info.type.value
            if type_name not in by_type:
                by_type[type_name] = []
            by_type[type_name].append((system_id, system_info))
        
        # Imprime por tipo
        for type_name, systems in sorted(by_type.items()):
            print(f"\n📁 {type_name.upper().replace('_', ' ')}")
            print("-" * 80)
            
            for system_id, system_info in systems:
                is_loaded = system_id in self.loaded_systems
                status_icon = "🟢" if is_loaded else "⚪"
                gui_icon = "🖥️" if system_info.is_gui else "⚙️"
                
                print(f"  {status_icon} {gui_icon} {system_info.name}")
                print(f"     ID: {system_id}")
                print(f"     {system_info.description}")
                print()
        
        print("=" * 80)


# Instância global
autonomous_manager = AutonomousIntegrationManager()


async def test_integration():
    """Testa integração dos sistemas autônomos"""
    print("\n🧪 Testando Integração de Sistemas Autônomos")
    print("=" * 80)
    
    # Lista sistemas
    systems = autonomous_manager.list_systems()
    print(f"✅ {len(systems)} sistemas registrados")
    
    # Testa carregamento de sistemas não-GUI
    non_gui_systems = [s for s in systems if not s.is_gui]
    print(f"\n📦 Carregando {len(non_gui_systems)} sistemas não-GUI...")
    
    for system_info in non_gui_systems:
        system_id = [k for k, v in autonomous_manager.systems.items() if v == system_info][0]
        result = await autonomous_manager.load_system(system_id)
        
        if result:
            print(f"  ✅ {system_info.name}")
        else:
            print(f"  ❌ {system_info.name}")
    
    # Status geral
    print("\n📊 Status Geral:")
    status = await autonomous_manager.get_all_status()
    print(f"  Total: {status['total_systems']}")
    print(f"  Carregados: {status['loaded_systems']}")
    
    print("\n" + "=" * 80)
    print("✅ Teste de integração concluído")


if __name__ == "__main__":
    # Teste standalone
    asyncio.run(test_integration())
