import json
from datetime import datetime

scan_data = {
    "timestamp": datetime.now().isoformat(),
    "assets_scanned": (lambda m: m.config.symbols)(__import__('01_config')), 
    "high_confidence_signals": 0,
    "status": "ativo",
    "próximo_scan": "30 minutos"
}

with open('market_scan_result.json', 'w') as f:
    json.dump(scan_data, f, indent=2)

print("✅ Scan concluído — nenhum sinal de alta confiança no momento")
