# 11_run.py
"""
Sistema VhalinorTrade - Script de Execução
Ponto de entrada principal para iniciar o sistema
"""

import asyncio
import signal
import sys
import logging
from datetime import datetime

# Importa o orquestrador principal e a configuração global
from 09_main_system import VhalinorTrade

logger = logging.getLogger("VhalinorTrade")

# Instância global do sistema
vhalinor = None


async def main():
    """Função principal"""
    global vhalinor
    
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║         VHALINOR TRADE - SISTEMA DE TRADING IA           ║
    ║         Trading Autônomo com Deep Learning               ║
    ║                                                          ║
    ║         Versão 1.0.0                                     ║
    ║         Data: 2024                                       ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    
    print("Inicializando módulos do sistema...")
    
    # Cria instância do sistema
    vhalinor = VhalinorTrade()
    
    # Configura handlers de sinal para parada segura
    def signal_handler(sig, frame):
        logger.info("Recebido sinal de parada. Finalizando...")
        asyncio.create_task(vhalinor.stop())
        
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print("\nSistema iniciado com sucesso!")
    print("Pressione Ctrl+C para parar\n")
    
    try:
        await vhalinor.start()
    except KeyboardInterrupt:
        logger.info("Interrupção do usuário")
    except Exception as e:
        logger.error(f"Erro fatal: {e}")
    finally:
        if vhalinor:
            await vhalinor.stop()
            
    print("\nVhalinorTrade finalizado.")

if __name__ == "__main__":
    asyncio.run(main())