"""
╔═══════════════════════════════════════════════════════════════════════════╗
║                MEDIDAS DE SEGURANÇA CIBERNÉTICA E COMPLIANCE         ║
║                 Componente 15: Sistema de Segurança Financeira             ║
╚═══════════════════════════════════════════════════════════════════════════╝
"""

import asyncio
import numpy as np
import pandas as pd
import hashlib
import hmac
import secrets
import ssl
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import json
import pickle
from collections import defaultdict, deque
import time
import threading
import multiprocessing as mp
from concurrent.futures import ThreadPoolExecutor
import jwt
import bcrypt
import cryptography
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import ipaddress
import re

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('CybersecurityCompliance')

class SecurityLevel(Enum):
    """Níveis de segurança"""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    SECRET = "secret"
    TOP_SECRET = "top_secret"

class ComplianceFramework(Enum):
    """Frameworks de compliance"""
    GDPR = "gdpr"
    SOX = "sox"
    PCI_DSS = "pci_dss"
    HIPAA = "hipaa"
    MiFID_II = "mifid_ii"
    BASEL_III = "basel_iii"
    ISO_27001 = "iso_27001"
    NIST = "nist"
    FINRA = "finra"
    SEC = "sec"

class ThreatType(Enum):
    """Tipos de ameaças"""
    MALWARE = "malware"
    PHISHING = "phishing"
    SQL_INJECTION = "sql_injection"
    XSS = "xss"
    DDOS = "ddos"
    INSIDER_THREAT = "insider_threat"
    DATA_BREACH = "data_breach"
    RANSOMWARE = "ransomware"
    API_ABUSE = "api_abuse"
    MAN_IN_THE_MIDDLE = "man_in_the_middle"

class SecurityControl(Enum):
    """Controles de segurança"""
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    ENCRYPTION = "encryption"
    ACCESS_CONTROL = "access_control"
    AUDIT_LOGGING = "audit_logging"
    NETWORK_SECURITY = "network_security"
    DATA_PROTECTION = "data_protection"
    VULNERABILITY_MANAGEMENT = "vulnerability_management"
    INCIDENT_RESPONSE = "incident_response"
    BUSINESS_CONTINUITY = "business_continuity"

@dataclass
class SecurityPolicy:
    """Política de segurança"""
    id: str
    name: str
    description: str
    security_level: SecurityLevel
    controls: List[SecurityControl]
    compliance_frameworks: List[ComplianceFramework]
    requirements: List[Dict[str, Any]]
    enforcement_level: str  # advisory, mandatory, critical
    last_updated: datetime
    version: str
    active: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'security_level': self.security_level.value,
            'controls': [c.value for c in self.controls],
            'compliance_frameworks': [f.value for f in self.compliance_frameworks],
            'requirements': self.requirements,
            'enforcement_level': self.enforcement_level,
            'last_updated': self.last_updated.isoformat(),
            'version': self.version,
            'active': self.active
        }

@dataclass
class SecurityIncident:
    """Incidente de segurança"""
    id: str
    threat_type: ThreatType
    severity: str  # low, medium, high, critical
    description: str
    source_ip: str
    target_system: str
    timestamp: datetime
    detected_by: str
    status: str  # open, investigating, contained, resolved
    impact_assessment: Dict[str, Any]
    mitigation_actions: List[str]
    forensics_data: Dict[str, Any]
    compliance_impact: List[ComplianceFramework]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'threat_type': self.threat_type.value,
            'severity': self.severity,
            'description': self.description,
            'source_ip': self.source_ip,
            'target_system': self.target_system,
            'timestamp': self.timestamp.isoformat(),
            'detected_by': self.detected_by,
            'status': self.status,
            'impact_assessment': self.impact_assessment,
            'mitigation_actions': self.mitigation_actions,
            'forensics_data': self.forensics_data,
            'compliance_impact': [f.value for f in self.compliance_impact]
        }

@dataclass
class ComplianceAssessment:
    """Avaliação de compliance"""
    id: str
    framework: ComplianceFramework
    scope: str
    assessment_date: datetime
    assessor: str
    controls_assessed: List[Dict[str, Any]]
    compliance_score: float
    findings: List[Dict[str, Any]]
    recommendations: List[str]
    next_assessment_date: datetime
    evidence: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'framework': self.framework.value,
            'scope': self.scope,
            'assessment_date': self.assessment_date.isoformat(),
            'assessor': self.assessor,
            'controls_assessed': self.controls_assessed,
            'compliance_score': self.compliance_score,
            'findings': self.findings,
            'recommendations': self.recommendations,
            'next_assessment_date': self.next_assessment_date.isoformat(),
            'evidence': self.evidence
        }

class CryptographyManager:
    """Gerenciador de criptografia"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.encryption_keys = {}
        self.key_rotation_interval = self.config.get('key_rotation_days', 90)
        self.last_key_rotation = datetime.now()
        
        logger.info("🔐 CryptographyManager inicializado")
    
    def generate_key(self, key_type: str = "AES256") -> str:
        """Gera chave criptográfica"""
        if key_type == "AES256":
            return Fernet.generate_key().decode()
        elif key_type == "RSA4096":
            # Simplificado - implementação real usaria cryptography RSA
            return secrets.token_bytes(512).hex()
        else:
            return secrets.token_bytes(32).hex()
    
    def encrypt_data(self, data: str, key: str = None) -> Dict[str, Any]:
        """Criptografa dados"""
        try:
            if key is None:
                key = self._get_or_create_key("default")
            
            f = Fernet(key.encode())
            encrypted_data = f.encrypt(data.encode())
            
            return {
                'success': True,
                'encrypted_data': encrypted_data.decode(),
                'key_id': 'default',
                'algorithm': 'AES256',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao criptografar dados: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def decrypt_data(self, encrypted_data: str, key: str = None) -> Dict[str, Any]:
        """Descriptografa dados"""
        try:
            if key is None:
                key = self._get_or_create_key("default")
            
            f = Fernet(key.encode())
            decrypted_data = f.decrypt(encrypted_data.encode())
            
            return {
                'success': True,
                'decrypted_data': decrypted_data.decode(),
                'key_id': 'default',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao descriptografar dados: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def hash_password(self, password: str) -> str:
        """Gera hash de senha"""
        try:
            salt = bcrypt.gensalt()
            hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
            return hashed.decode('utf-8')
        except Exception as e:
            logger.error(f"❌ Erro ao gerar hash de senha: {e}")
            return None
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verifica senha"""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        except Exception as e:
            logger.error(f"❌ Erro ao verificar senha: {e}")
            return False
    
    def generate_jwt(self, payload: Dict[str, Any], 
                    expires_in_hours: int = 24) -> str:
        """Gera token JWT"""
        try:
            payload['exp'] = datetime.now() + timedelta(hours=expires_in_hours)
            payload['iat'] = datetime.now()
            
            secret = self._get_or_create_key("jwt")
            token = jwt.encode(payload, secret, algorithm='HS256')
            
            return token
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar JWT: {e}")
            return None
    
    def verify_jwt(self, token: str) -> Dict[str, Any]:
        """Verifica token JWT"""
        try:
            secret = self._get_or_create_key("jwt")
            payload = jwt.decode(token, secret, algorithms=['HS256'])
            
            return {
                'valid': True,
                'payload': payload
            }
            
        except jwt.ExpiredSignatureError:
            return {
                'valid': False,
                'error': 'Token expirado'
            }
        except jwt.InvalidTokenError as e:
            return {
                'valid': False,
                'error': f'Token inválido: {str(e)}'
            }
    
    def _get_or_create_key(self, key_id: str) -> str:
        """Obtém ou cria chave"""
        if key_id not in self.encryption_keys:
            self.encryption_keys[key_id] = self.generate_key()
        
        return self.encryption_keys[key_id]
    
    def rotate_keys(self):
        """Rotaciona chaves criptográficas"""
        logger.info("🔄 Rotacionando chaves criptográficas...")
        
        for key_id in list(self.encryption_keys.keys()):
            old_key = self.encryption_keys[key_id]
            new_key = self.generate_key()
            
            # Armazena chave antiga para descriptografia de dados antigos
            self.encryption_keys[f"{key_id}_old"] = old_key
            self.encryption_keys[key_id] = new_key
        
        self.last_key_rotation = datetime.now()
        logger.info("✅ Chaves rotacionadas com sucesso")

class AccessControlManager:
    """Gerenciador de controle de acesso"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.users = {}
        self.roles = {}
        self.permissions = {}
        self.sessions = {}
        self.failed_attempts = defaultdict(int)
        self.max_failed_attempts = self.config.get('max_failed_attempts', 5)
        self.lockout_duration_minutes = self.config.get('lockout_minutes', 30)
        
        logger.info("🛡️ AccessControlManager inicializado")
    
    def create_user(self, username: str, email: str, 
                   password: str, role: str) -> Dict[str, Any]:
        """Cria novo usuário"""
        try:
            if username in self.users:
                return {
                    'success': False,
                    'error': 'Usuário já existe'
                }
            
            crypto_manager = CryptographyManager()
            hashed_password = crypto_manager.hash_password(password)
            
            user = {
                'username': username,
                'email': email,
                'password_hash': hashed_password,
                'role': role,
                'created_at': datetime.now(),
                'last_login': None,
                'active': True,
                'permissions': self._get_role_permissions(role)
            }
            
            self.users[username] = user
            
            logger.info(f"👤 Usuário criado: {username}")
            
            return {
                'success': True,
                'user_id': username,
                'message': 'Usuário criado com sucesso'
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao criar usuário: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def authenticate_user(self, username: str, password: str, 
                         ip_address: str = None) -> Dict[str, Any]:
        """Autentica usuário"""
        try:
            # Verifica lockout
            if self._is_account_locked(username):
                return {
                    'success': False,
                    'error': 'Conta bloqueada. Tente novamente mais tarde.'
                }
            
            user = self.users.get(username)
            if not user:
                self.failed_attempts[username] += 1
                return {
                    'success': False,
                    'error': 'Usuário ou senha inválidos'
                }
            
            if not user['active']:
                return {
                    'success': False,
                    'error': 'Conta desativada'
                }
            
            crypto_manager = CryptographyManager()
            if not crypto_manager.verify_password(password, user['password_hash']):
                self.failed_attempts[username] += 1
                
                if self.failed_attempts[username] >= self.max_failed_attempts:
                    self._lock_account(username)
                
                return {
                    'success': False,
                    'error': 'Usuário ou senha inválidos'
                }
            
            # Reseta tentativas falhas
            self.failed_attempts[username] = 0
            
            # Cria sessão
            session_id = secrets.token_urlsafe(32)
            session = {
                'session_id': session_id,
                'username': username,
                'role': user['role'],
                'permissions': user['permissions'],
                'ip_address': ip_address,
                'created_at': datetime.now(),
                'last_activity': datetime.now(),
                'expires_at': datetime.now() + timedelta(hours=8)
            }
            
            self.sessions[session_id] = session
            user['last_login'] = datetime.now()
            
            logger.info(f"✅ Usuário autenticado: {username}")
            
            return {
                'success': True,
                'session_id': session_id,
                'user_info': {
                    'username': username,
                    'role': user['role'],
                    'permissions': user['permissions']
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Erro na autenticação: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def verify_session(self, session_id: str, 
                      required_permission: str = None) -> Dict[str, Any]:
        """Verifica sessão de usuário"""
        try:
            session = self.sessions.get(session_id)
            
            if not session:
                return {
                    'valid': False,
                    'error': 'Sessão inválida'
                }
            
            if datetime.now() > session['expires_at']:
                del self.sessions[session_id]
                return {
                    'valid': False,
                    'error': 'Sessão expirada'
                }
            
            # Atualiza última atividade
            session['last_activity'] = datetime.now()
            
            # Verifica permissão
            if required_permission:
                user_permissions = session.get('permissions', [])
                if required_permission not in user_permissions:
                    return {
                        'valid': False,
                        'error': 'Permissão insuficiente'
                    }
            
            return {
                'valid': True,
                'user_info': {
                    'username': session['username'],
                    'role': session['role'],
                    'permissions': session['permissions']
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Erro na verificação de sessão: {e}")
            return {
                'valid': False,
                'error': str(e)
            }
    
    def revoke_session(self, session_id: str) -> bool:
        """Revoga sessão"""
        try:
            if session_id in self.sessions:
                del self.sessions[session_id]
                logger.info(f"🚫 Sessão revogada: {session_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"❌ Erro ao revogar sessão: {e}")
            return False
    
    def _get_role_permissions(self, role: str) -> List[str]:
        """Obtém permissões baseado no papel"""
        role_permissions = {
            'admin': [
                'read', 'write', 'delete', 'admin', 'audit',
                'trading', 'risk_management', 'system_config'
            ],
            'trader': [
                'read', 'write', 'trading', 'risk_view'
            ],
            'analyst': [
                'read', 'write', 'analysis', 'risk_view'
            ],
            'viewer': [
                'read', 'view'
            ]
        }
        
        return role_permissions.get(role, [])
    
    def _is_account_locked(self, username: str) -> bool:
        """Verifica se conta está bloqueada"""
        return self.failed_attempts.get(username, 0) >= self.max_failed_attempts
    
    def _lock_account(self, username: str):
        """Bloqueia conta"""
        logger.warning(f"🔒 Conta bloqueada: {username}")
        
        # Agenda desbloqueio
        unlock_time = datetime.now() + timedelta(minutes=self.lockout_duration_minutes)
        
        # Simplificado - implementação real usaria scheduler
        def unlock_account():
            time.sleep(self.lockout_duration_minutes * 60)
            if self.failed_attempts.get(username, 0) >= self.max_failed_attempts:
                self.failed_attempts[username] = 0
                logger.info(f"🔓 Conta desbloqueada: {username}")
        
        threading.Thread(target=unlock_account, daemon=True).start()

class ThreatDetectionEngine:
    """Motor de detecção de ameaças"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.threat_patterns = {}
        self.anomaly_thresholds = {}
        self.detected_threats = deque(maxlen=1000)
        self.monitoring_active = False
        
        logger.info("🚨 ThreatDetectionEngine inicializado")
    
    def load_threat_patterns(self):
        """Carrega padrões de ameaças"""
        self.threat_patterns = {
            'sql_injection': [
                r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER)\b)",
                r"(\b(UNION|OR|AND)\b.*\b(SELECT|INSERT|UPDATE|DELETE)\b)",
                r"(--|#|/\*|\*/|;)"
            ],
            'xss': [
                r"(<script|<iframe|<object|<embed)",
                r"(javascript:|vbscript:|onload=|onerror=)",
                r"(\b(COOKIE|DOCUMENT|WINDOW|LOCATION)\b)"
            ],
            'path_traversal': [
                r"(\.\./|\.\.\\)",
                r"(/etc/passwd|/proc/|/sys/)",
                r"(\\windows\\system32|c:\\windows\\)"
            ],
            'command_injection': [
                r"(;|\||&|&&)",
                r"(\b(curl|wget|nc|netcat|telnet|ssh)\b)",
                r"(\b(rm|del|format|fdisk)\b)"
            ]
        }
        
        logger.info("📋 Padrões de ameaças carregados")
    
    def analyze_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analisa requisição em busca de ameaças"""
        threats_detected = []
        
        try:
            # Análise de SQL Injection
            sql_threats = self._detect_sql_injection(request_data)
            threats_detected.extend(sql_threats)
            
            # Análise de XSS
            xss_threats = self._detect_xss(request_data)
            threats_detected.extend(xss_threats)
            
            # Análise de Path Traversal
            path_threats = self._detect_path_traversal(request_data)
            threats_detected.extend(path_threats)
            
            # Análise de Command Injection
            cmd_threats = self._detect_command_injection(request_data)
            threats_detected.extend(cmd_threats)
            
            # Análise de anomalias
            anomalies = self._detect_anomalies(request_data)
            threats_detected.extend(anomalies)
            
            # Classifica severidade
            max_severity = 'low'
            if threats_detected:
                severities = [t['severity'] for t in threats_detected]
                severity_order = ['low', 'medium', 'high', 'critical']
                max_severity = max(severities, key=lambda x: severity_order.index(x))
            
            result = {
                'threats_detected': threats_detected,
                'risk_score': self._calculate_risk_score(threats_detected),
                'max_severity': max_severity,
                'recommendations': self._generate_recommendations(threats_detected),
                'timestamp': datetime.now().isoformat()
            }
            
            # Se detectou ameaças, registra
            if threats_detected:
                self._log_threat_detection(request_data, result)
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Erro na análise de ameaças: {e}")
            return {
                'threats_detected': [],
                'error': str(e)
            }
    
    def _detect_sql_injection(self, request_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detecta SQL Injection"""
        threats = []
        patterns = self.threat_patterns.get('sql_injection', [])
        
        for key, value in request_data.items():
            if isinstance(value, str):
                for pattern in patterns:
                    if re.search(pattern, value, re.IGNORECASE):
                        threats.append({
                            'type': 'sql_injection',
                            'field': key,
                            'pattern': pattern,
                            'value': value[:100],  # Primeiros 100 caracteres
                            'severity': 'high'
                        })
                        break
        
        return threats
    
    def _detect_xss(self, request_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detecta XSS"""
        threats = []
        patterns = self.threat_patterns.get('xss', [])
        
        for key, value in request_data.items():
            if isinstance(value, str):
                for pattern in patterns:
                    if re.search(pattern, value, re.IGNORECASE):
                        threats.append({
                            'type': 'xss',
                            'field': key,
                            'pattern': pattern,
                            'value': value[:100],
                            'severity': 'medium'
                        })
                        break
        
        return threats
    
    def _detect_path_traversal(self, request_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detecta Path Traversal"""
        threats = []
        patterns = self.threat_patterns.get('path_traversal', [])
        
        for key, value in request_data.items():
            if isinstance(value, str):
                for pattern in patterns:
                    if re.search(pattern, value, re.IGNORECASE):
                        threats.append({
                            'type': 'path_traversal',
                            'field': key,
                            'pattern': pattern,
                            'value': value[:100],
                            'severity': 'high'
                        })
                        break
        
        return threats
    
    def _detect_command_injection(self, request_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detecta Command Injection"""
        threats = []
        patterns = self.threat_patterns.get('command_injection', [])
        
        for key, value in request_data.items():
            if isinstance(value, str):
                for pattern in patterns:
                    if re.search(pattern, value, re.IGNORECASE):
                        threats.append({
                            'type': 'command_injection',
                            'field': key,
                            'pattern': pattern,
                            'value': value[:100],
                            'severity': 'critical'
                        })
                        break
        
        return threats
    
    def _detect_anomalies(self, request_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detecta anomalias"""
        threats = []
        
        # Verifica tamanho dos dados
        for key, value in request_data.items():
            if isinstance(value, str):
                if len(value) > 10000:  # Dados muito grandes
                    threats.append({
                        'type': 'large_payload',
                        'field': key,
                        'size': len(value),
                        'severity': 'medium'
                    })
                
                # Verifica caracteres suspeitos
                suspicious_chars = len(re.findall(r'[^\w\s\-\.@]', value))
                if suspicious_chars > len(value) * 0.3:  # >30% caracteres especiais
                    threats.append({
                        'type': 'suspicious_chars',
                        'field': key,
                        'suspicious_ratio': suspicious_chars / len(value),
                        'severity': 'low'
                    })
        
        # Verifica IP de origem
        if 'ip_address' in request_data:
            ip = request_data['ip_address']
            if self._is_suspicious_ip(ip):
                threats.append({
                    'type': 'suspicious_ip',
                    'ip_address': ip,
                    'severity': 'medium'
                })
        
        return threats
    
    def _is_suspicious_ip(self, ip: str) -> bool:
        """Verifica se IP é suspeito"""
        try:
            ip_obj = ipaddress.ip_address(ip)
            
            # Verifica se é IP privado
            if ip_obj.is_private:
                return False
            
            # Verifica ranges conhecidos maliciosos (simplificado)
            malicious_ranges = [
                '0.0.0.0/8',      # Reservado
                '169.254.0.0/16',  # Link-local
                '224.0.0.0/4'      # Multicast
            ]
            
            for range_str in malicious_ranges:
                if ip_obj in ipaddress.ip_network(range_str):
                    return True
            
            return False
            
        except:
            return True  # Se não conseguir analisar, considera suspeito
    
    def _calculate_risk_score(self, threats: List[Dict[str, Any]]) -> float:
        """Calcula score de risco"""
        if not threats:
            return 0.0
        
        severity_weights = {
            'low': 1.0,
            'medium': 2.5,
            'high': 5.0,
            'critical': 10.0
        }
        
        total_score = sum(severity_weights[t['severity']] for t in threats)
        
        # Normaliza para 0-100
        max_possible_score = len(threats) * 10.0
        normalized_score = (total_score / max_possible_score) * 100
        
        return min(normalized_score, 100.0)
    
    def _generate_recommendations(self, threats: List[Dict[str, Any]]) -> List[str]:
        """Gera recomendações baseadas nas ameaças detectadas"""
        recommendations = []
        
        threat_types = set(t['type'] for t in threats)
        
        if 'sql_injection' in threat_types:
            recommendations.append("Implementar prepared statements e parameterized queries")
            recommendations.append("Usar ORM com proteção contra SQL injection")
        
        if 'xss' in threat_types:
            recommendations.append("Implementar sanitização de entrada e saída de dados")
            recommendations.append("Usar Content Security Policy (CSP)")
        
        if 'path_traversal' in threat_types:
            recommendations.append("Validar e sanitizar paths de arquivo")
            recommendations.append("Usar chaves numéricas em vez de paths")
        
        if 'command_injection' in threat_types:
            recommendations.append("Evitar executar comandos do sistema com input do usuário")
            recommendations.append("Usar APIs seguras em vez de chamadas de sistema")
        
        if 'suspicious_ip' in threat_types:
            recommendations.append("Implementar lista de bloqueio de IPs suspeitos")
            recommendations.append("Monitorar tentativas de acesso de IPs maliciosos")
        
        return recommendations
    
    def _log_threat_detection(self, request_data: Dict[str, Any], 
                             analysis_result: Dict[str, Any]):
        """Registra detecção de ameaça"""
        threat_log = {
            'timestamp': datetime.now(),
            'request_data': request_data,
            'analysis_result': analysis_result,
            'source_ip': request_data.get('ip_address', 'unknown')
        }
        
        self.detected_threats.append(threat_log)
        
        # Log de segurança
        logger.warning(f"🚨 Ameaça detectada: {analysis_result['max_severity']} - "
                      f"Score: {analysis_result['risk_score']:.1f}")
        
        # Se risco alto, gera alerta imediato
        if analysis_result['risk_score'] > 70:
            self._generate_security_alert(threat_log)
    
    def _generate_security_alert(self, threat_log: Dict[str, Any]):
        """Gera alerta de segurança"""
        alert_data = {
            'alert_type': 'threat_detected',
            'severity': 'high',
            'timestamp': threat_log['timestamp'],
            'source_ip': threat_log['source_ip'],
            'risk_score': threat_log['analysis_result']['risk_score'],
            'threats': threat_log['analysis_result']['threats_detected']
        }
        
        # Aqui seria integrado com sistema de alertas
        logger.critical(f"🚨 ALERTA DE SEGURANÇA: {alert_data}")

class ComplianceManager:
    """Gerenciador de compliance"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.security_policies = {}
        self.compliance_assessments = []
        self.audit_trail = deque(maxlen=10000)
        
        logger.info("📋 ComplianceManager inicializado")
    
    def create_security_policy(self, policy: SecurityPolicy):
        """Cria política de segurança"""
        self.security_policies[policy.id] = policy
        logger.info(f"📋 Política criada: {policy.name}")
    
    def assess_compliance(self, framework: ComplianceFramework, 
                        scope: str = "full_system") -> ComplianceAssessment:
        """Avalia compliance com framework especificado"""
        assessment_id = f"assessment_{int(time.time())}"
        
        # Obtém controles relevantes
        controls = self._get_framework_controls(framework)
        
        # Avalia cada controle
        controls_assessed = []
        findings = []
        
        for control in controls:
            result = self._assess_control(control, scope)
            controls_assessed.append(result)
            
            if not result['compliant']:
                findings.append({
                    'control_id': control['id'],
                    'requirement': control['requirement'],
                    'finding': result['finding'],
                    'severity': result['severity']
                })
        
        # Calcula score de compliance
        compliant_controls = len([c for c in controls_assessed if c['compliant']])
        compliance_score = (compliant_controls / len(controls_assessed)) * 100
        
        # Gera recomendações
        recommendations = self._generate_compliance_recommendations(findings, framework)
        
        assessment = ComplianceAssessment(
            id=assessment_id,
            framework=framework,
            scope=scope,
            assessment_date=datetime.now(),
            assessor="system",
            controls_assessed=controls_assessed,
            compliance_score=compliance_score,
            findings=findings,
            recommendations=recommendations,
            next_assessment_date=datetime.now() + timedelta(days=365),
            evidence={'assessment_data': 'collected'}
        )
        
        self.compliance_assessments.append(assessment)
        
        logger.info(f"📊 Avaliação de compliance concluída: {framework.value} - "
                    f"Score: {compliance_score:.1f}%")
        
        return assessment
    
    def _get_framework_controls(self, framework: ComplianceFramework) -> List[Dict[str, Any]]:
        """Obtém controles do framework"""
        controls_map = {
            ComplianceFramework.GDPR: [
                {
                    'id': 'GDPR_ART_32',
                    'requirement': 'Security of processing',
                    'description': 'Implement appropriate technical and organizational measures'
                },
                {
                    'id': 'GDPR_ART_25',
                    'requirement': 'Data protection by design and by default',
                    'description': 'Implement data protection measures'
                }
            ],
            ComplianceFramework.PCI_DSS: [
                {
                    'id': 'PCI_REQ_3',
                    'requirement': 'Protect stored cardholder data',
                    'description': 'Encrypt cardholder data'
                },
                {
                    'id': 'PCI_REQ_4',
                    'requirement': 'Encrypt transmission of cardholder data',
                    'description': 'Use strong cryptography'
                }
            ],
            ComplianceFramework.ISO_27001: [
                {
                    'id': 'ISO_A9',
                    'requirement': 'Access control',
                    'description': 'Control access to information'
                },
                {
                    'id': 'ISO_A12',
                    'requirement': 'Operations security',
                    'description': 'Ensure correct and secure operations'
                }
            ]
        }
        
        return controls_map.get(framework, [])
    
    def _assess_control(self, control: Dict[str, Any], 
                       scope: str) -> Dict[str, Any]:
        """Avalia controle específico"""
        # Simplificado - implementação real faria verificações detalhadas
        control_id = control['id']
        
        # Simula avaliação baseada em políticas existentes
        compliant = True
        finding = "Control implemented and effective"
        severity = "low"
        
        # Verifica se há políticas relacionadas
        related_policies = [
            p for p in self.security_policies.values()
            if any(req in control['requirement'].lower() 
                  for req in p.description.lower().split())
        ]
        
        if not related_policies:
            compliant = False
            finding = f"No security policy found for {control['requirement']}"
            severity = "high"
        
        return {
            'control_id': control_id,
            'requirement': control['requirement'],
            'compliant': compliant,
            'finding': finding,
            'severity': severity,
            'related_policies': [p.id for p in related_policies]
        }
    
    def _generate_compliance_recommendations(self, findings: List[Dict[str, Any]], 
                                         framework: ComplianceFramework) -> List[str]:
        """Gera recomendações de compliance"""
        recommendations = []
        
        if not findings:
            recommendations.append("System is fully compliant with current assessment")
            return recommendations
        
        # Agrupa findings por severidade
        high_severity = [f for f in findings if f['severity'] == 'high']
        medium_severity = [f for f in findings if f['severity'] == 'medium']
        
        if high_severity:
            recommendations.append(
                f"URGENT: Address {len(high_severity)} high severity findings for {framework.value}"
            )
        
        if medium_severity:
            recommendations.append(
                f"Address {len(medium_severity)} medium severity findings within 30 days"
            )
        
        # Recomendações específicas por framework
        if framework == ComplianceFramework.GDPR:
            recommendations.extend([
                "Implement data protection impact assessments (DPIAs)",
                "Ensure data subject rights are implemented",
                "Maintain records of processing activities"
            ])
        elif framework == ComplianceFramework.PCI_DSS:
            recommendations.extend([
                "Implement tokenization for card data",
                "Ensure network segmentation",
                "Regular vulnerability scanning"
            ])
        elif framework == ComplianceFramework.ISO_27001:
            recommendations.extend([
                "Develop comprehensive risk assessment methodology",
                "Implement incident management process",
                "Regular internal audits"
            ])
        
        return recommendations
    
    def log_security_event(self, event_type: str, description: str, 
                          user: str = None, ip_address: str = None):
        """Registra evento de segurança"""
        event = {
            'timestamp': datetime.now(),
            'event_type': event_type,
            'description': description,
            'user': user,
            'ip_address': ip_address,
            'event_id': secrets.token_urlsafe(16)
        }
        
        self.audit_trail.append(event)
        
        # Log de segurança
        security_level = 'INFO'
        if any(keyword in description.lower() 
               for keyword in ['failed', 'denied', 'blocked', 'threat']):
            security_level = 'WARNING'
        
        logger.log(
            getattr(logging, security_level),
            f"🔒 Security Event: {event_type} - {description}"
        )
    
    def generate_compliance_report(self, framework: ComplianceFramework = None) -> Dict[str, Any]:
        """Gera relatório de compliance"""
        if framework:
            assessments = [a for a in self.compliance_assessments if a.framework == framework]
        else:
            assessments = self.compliance_assessments
        
        if not assessments:
            return {'message': 'No compliance assessments found'}
        
        # Estatísticas gerais
        latest_assessments = {}
        for f in ComplianceFramework:
            framework_assessments = [a for a in assessments if a.framework == f]
            if framework_assessments:
                latest_assessments[f] = max(framework_assessments, key=lambda x: x.assessment_date)
        
        # Scores médios por framework
        framework_scores = defaultdict(list)
        for assessment in assessments:
            framework_scores[assessment.framework].append(assessment.compliance_score)
        
        average_scores = {
            f.value: np.mean(scores) if scores else 0
            for f, scores in framework_scores.items()
        }
        
        # Findings recentes
        recent_findings = []
        for assessment in assessments:
            if assessment.assessment_date >= datetime.now() - timedelta(days=30):
                recent_findings.extend(assessment.findings)
        
        return {
            'summary': {
                'total_assessments': len(assessments),
                'frameworks_assessed': list(set(a.framework for a in assessments)),
                'latest_assessments': {
                    f.value: a.to_dict() for f, a in latest_assessments.items()
                }
            },
            'compliance_scores': average_scores,
            'recent_findings': recent_findings,
            'security_policies_count': len(self.security_policies),
            'audit_trail_entries': len(self.audit_trail),
            'recommendations': self._get_overall_recommendations(assessments)
        }
    
    def _get_overall_recommendations(self, assessments: List[ComplianceAssessment]) -> List[str]:
        """Obtém recomendações gerais"""
        recommendations = []
        
        # Analisa scores médios
        if assessments:
            avg_score = np.mean([a.compliance_score for a in assessments])
            
            if avg_score < 70:
                recommendations.append("Overall compliance score is below 70%. Immediate action required.")
            elif avg_score < 85:
                recommendations.append("Compliance score needs improvement. Focus on high-severity findings.")
            else:
                recommendations.append("Good compliance score. Maintain current controls.")
        
        # Recomendações baseadas em findings
        all_findings = []
        for assessment in assessments:
            all_findings.extend(assessment.findings)
        
        if all_findings:
            severity_counts = defaultdict(int)
            for finding in all_findings:
                severity_counts[finding['severity']] += 1
            
            if severity_counts['high'] > 0:
                recommendations.append(f"Address {severity_counts['high']} high-severity findings immediately.")
            
            if severity_counts['medium'] > 5:
                recommendations.append("Multiple medium-severity findings require attention.")
        
        return recommendations

class CybersecurityComplianceSystem:
    """Sistema integrado de segurança e compliance"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        
        # Componentes
        self.crypto_manager = CryptographyManager(self.config.get('cryptography', {}))
        self.access_control = AccessControlManager(self.config.get('access_control', {}))
        self.threat_detector = ThreatDetectionEngine(self.config.get('threat_detection', {}))
        self.compliance_manager = ComplianceManager(self.config.get('compliance', {}))
        
        # Estado
        self.security_incidents = []
        self.monitoring_active = False
        
        logger.info("🛡️ CybersecurityComplianceSystem inicializado")
    
    def initialize_system(self):
        """Inicializa sistema de segurança"""
        logger.info("🚀 Inicializando sistema de segurança e compliance...")
        
        # Carrega padrões de ameaças
        self.threat_detector.load_threat_patterns()
        
        # Cria políticas de segurança padrão
        self._create_default_security_policies()
        
        logger.info("✅ Sistema de segurança inicializado")
    
    def _create_default_security_policies(self):
        """Cria políticas de segurança padrão"""
        # Política de autenticação
        auth_policy = SecurityPolicy(
            id="auth_policy",
            name="Política de Autenticação",
            description="Requisitos para autenticação de usuários",
            security_level=SecurityLevel.CONFIDENTIAL,
            controls=[SecurityControl.AUTHENTICATION, SecurityControl.AUDIT_LOGGING],
            compliance_frameworks=[ComplianceFramework.GDPR, ComplianceFramework.ISO_27001],
            requirements=[
                {
                    'requirement': 'Autenticação multifator obrigatória',
                    'details': 'Todos os usuários devem usar MFA'
                },
                {
                    'requirement': 'Política de senhas fortes',
                    'details': 'Mínimo 8 caracteres, incluindo números e símbolos'
                }
            ],
            enforcement_level="mandatory",
            last_updated=datetime.now(),
            version="1.0"
        )
        
        # Política de criptografia
        crypto_policy = SecurityPolicy(
            id="crypto_policy",
            name="Política de Criptografia",
            description="Requisitos para criptografia de dados",
            security_level=SecurityLevel.SECRET,
            controls=[SecurityControl.ENCRYPTION, SecurityControl.DATA_PROTECTION],
            compliance_frameworks=[ComplianceFramework.GDPR, ComplianceFramework.PCI_DSS],
            requirements=[
                {
                    'requirement': 'Criptografia de dados sensíveis',
                    'details': 'Todos os dados PII devem ser criptografados'
                },
                {
                    'requirement': 'Criptografia em trânsito',
                    'details': 'TLS 1.2+ obrigatório para todas as conexões'
                }
            ],
            enforcement_level="mandatory",
            last_updated=datetime.now(),
            version="1.0"
        )
        
        # Política de acesso
        access_policy = SecurityPolicy(
            id="access_policy",
            name="Política de Controle de Acesso",
            description="Requisitos para controle de acesso",
            security_level=SecurityLevel.CONFIDENTIAL,
            controls=[SecurityControl.ACCESS_CONTROL, SecurityControl.AUTHORIZATION],
            compliance_frameworks=[ComplianceFramework.ISO_27001, ComplianceFramework.SOX],
            requirements=[
                {
                    'requirement': 'Princípio do menor privilégio',
                    'details': 'Usuários devem ter acesso mínimo necessário'
                },
                {
                    'requirement': 'Revisão periódica de acessos',
                    'details': 'Acessos devem ser revisados trimestralmente'
                }
            ],
            enforcement_level="mandatory",
            last_updated=datetime.now(),
            version="1.0"
        )
        
        self.compliance_manager.create_security_policy(auth_policy)
        self.compliance_manager.create_security_policy(crypto_policy)
        self.compliance_manager.create_security_policy(access_policy)
        
        logger.info("📋 Políticas de segurança padrão criadas")
    
    def process_secure_request(self, request_data: Dict[str, Any], 
                            session_id: str = None) -> Dict[str, Any]:
        """Processa requisição com segurança"""
        try:
            # Análise de ameaças
            threat_analysis = self.threat_detector.analyze_request(request_data)
            
            # Verifica de autenticação
            auth_result = {'authenticated': False}
            if session_id:
                auth_result = self.access_control.verify_session(session_id)
            
            # Registra evento
            self.compliance_manager.log_security_event(
                event_type="request_processed",
                description=f"Request processed - Threat score: {threat_analysis['risk_score']:.1f}",
                user=auth_result.get('user_info', {}).get('username') if auth_result['authenticated'] else None,
                ip_address=request_data.get('ip_address')
            )
            
            # Determina se requisição deve ser bloqueada
            should_block = (
                threat_analysis['risk_score'] > 70 or
                threat_analysis['max_severity'] in ['high', 'critical'] or
                not auth_result['authenticated']
            )
            
            result = {
                'allowed': not should_block,
                'threat_analysis': threat_analysis,
                'authentication': auth_result,
                'recommendations': threat_analysis.get('recommendations', []),
                'timestamp': datetime.now().isoformat()
            }
            
            if should_block:
                result['block_reason'] = self._get_block_reason(threat_analysis, auth_result)
                logger.warning(f"🚫 Requisição bloqueada: {result['block_reason']}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Erro ao processar requisição segura: {e}")
            return {
                'allowed': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _get_block_reason(self, threat_analysis: Dict[str, Any], 
                         auth_result: Dict[str, Any]) -> str:
        """Determina motivo do bloqueio"""
        if not auth_result.get('authenticated', False):
            return "Não autenticado"
        
        if threat_analysis['max_severity'] == 'critical':
            return "Ameaça crítica detectada"
        
        if threat_analysis['max_severity'] == 'high':
            return "Ameaça de alta severidade detectada"
        
        if threat_analysis['risk_score'] > 70:
            return f"Score de risco alto: {threat_analysis['risk_score']:.1f}"
        
        return "Política de segurança violada"
    
    def create_security_incident(self, incident_data: Dict[str, Any]) -> SecurityIncident:
        """Cria registro de incidente de segurança"""
        incident = SecurityIncident(
            id=f"incident_{int(time.time())}",
            threat_type=ThreatType(incident_data.get('threat_type', 'data_breach')),
            severity=incident_data.get('severity', 'medium'),
            description=incident_data.get('description', ''),
            source_ip=incident_data.get('source_ip', 'unknown'),
            target_system=incident_data.get('target_system', 'unknown'),
            timestamp=datetime.now(),
            detected_by=incident_data.get('detected_by', 'system'),
            status=incident_data.get('status', 'open'),
            impact_assessment=incident_data.get('impact_assessment', {}),
            mitigation_actions=incident_data.get('mitigation_actions', []),
            forensics_data=incident_data.get('forensics_data', {}),
            compliance_impact=[
                ComplianceFramework(f) for f in incident_data.get('compliance_impact', [])
            ]
        )
        
        self.security_incidents.append(incident)
        
        # Registra evento
        self.compliance_manager.log_security_event(
            event_type="security_incident",
            description=f"Security incident: {incident.threat_type.value} - {incident.severity}",
            ip_address=incident.source_ip
        )
        
        logger.critical(f"🚨 Incidente de segurança criado: {incident.id}")
        
        return incident
    
    def run_compliance_assessment(self, framework: ComplianceFramework) -> ComplianceAssessment:
        """Executa avaliação de compliance"""
        return self.compliance_manager.assess_compliance(framework)
    
    def generate_security_report(self) -> Dict[str, Any]:
        """Gera relatório completo de segurança"""
        return {
            'system_status': {
                'monitoring_active': self.monitoring_active,
                'security_incidents_count': len(self.security_incidents),
                'active_sessions': len(self.access_control.sessions),
                'security_policies_count': len(self.compliance_manager.security_policies)
            },
            'compliance_summary': self.compliance_manager.generate_compliance_report(),
            'recent_incidents': [i.to_dict() for i in self.security_incidents[-10:]],
            'threat_detection_stats': {
                'total_threats_detected': len(self.threat_detector.detected_threats),
                'high_risk_requests': len([
                    t for t in self.threat_detector.detected_threats
                    if t['analysis_result']['risk_score'] > 70
                ])
            },
            'security_recommendations': self._get_security_recommendations()
        }
    
    def _get_security_recommendations(self) -> List[str]:
        """Obtém recomendações de segurança"""
        recommendations = []
        
        # Análise de incidentes
        if self.security_incidents:
            recent_incidents = [
                i for i in self.security_incidents
                if i.timestamp >= datetime.now() - timedelta(days=30)
            ]
            
            if len(recent_incidents) > 5:
                recommendations.append("Alto número de incidentes recentes. Revisar controles de segurança.")
            
            critical_incidents = [i for i in recent_incidents if i.severity == 'critical']
            if critical_incidents:
                recommendations.append("Incidentes críticos detectados. Ação imediata necessária.")
        
        # Análise de ameaças
        if self.threat_detector.detected_threats:
            high_risk_threats = [
                t for t in self.threat_detector.detected_threats
                if t['analysis_result']['risk_score'] > 70
            ]
            
            if len(high_risk_threats) > 10:
                recommendations.append("Múltiplas ameaças de alto risco detectadas. Fortalecer defesas.")
        
        # Recomendações gerais
        recommendations.extend([
            "Realizar treinamento regular de conscientização em segurança",
            "Implementar monitoramento contínuo de segurança",
            "Manter sistemas atualizados com patches de segurança",
            "Realizar testes de penetração periódicos"
        ])
        
        return recommendations
    
    def save_security_data(self, filepath: str):
        """Salva dados de segurança"""
        data = {
            'timestamp': datetime.now().isoformat(),
            'security_incidents': [i.to_dict() for i in self.security_incidents],
            'compliance_assessments': [a.to_dict() for a in self.compliance_manager.compliance_assessments],
            'security_policies': {
                pid: policy.to_dict() 
                for pid, policy in self.compliance_manager.security_policies.items()
            },
            'audit_trail': list(self.compliance_manager.audit_trail)[-1000:],  # Últimos 1000
            'threat_detection_data': list(self.threat_detector.detected_threats)[-500],  # Últimos 500
            'system_config': self.config
        }
        
        # Criptografa dados sensíveis
        crypto_result = self.crypto_manager.encrypt_data(json.dumps(data))
        
        if crypto_result['success']:
            with open(filepath, 'w') as f:
                json.dump(crypto_result, f, indent=2)
        
        logger.info(f"💾 Dados de segurança salvos em {filepath}")

# Configuração padrão
DEFAULT_SECURITY_CONFIG = {
    'cryptography': {
        'key_rotation_days': 90,
        'encryption_algorithm': 'AES256',
        'jwt_expiry_hours': 24
    },
    'access_control': {
        'max_failed_attempts': 5,
        'lockout_minutes': 30,
        'session_timeout_hours': 8
    },
    'threat_detection': {
        'anomaly_threshold': 0.7,
        'monitor suspicious_ips': True,
        'real_time_analysis': True
    },
    'compliance': {
        'auto_assessment': True,
        'assessment_frequency_days': 90,
        'required_frameworks': ['GDPR', 'ISO_27001']
    }
}

if __name__ == "__main__":
    # Exemplo de uso
    def test_cybersecurity_system():
        """Testa sistema de segurança e compliance"""
        print("🛡️ Iniciando Teste do Sistema de Segurança e Compliance")
        print("=" * 70)
        
        # Cria sistema
        security_system = CybersecurityComplianceSystem(DEFAULT_SECURITY_CONFIG)
        
        # Inicializa sistema
        security_system.initialize_system()
        
        # Teste de gerenciamento de usuários
        print("\n👤 Teste de Gerenciamento de Usuários:")
        print("-" * 40)
        
        # Cria usuário
        user_result = security_system.access_control.create_user(
            username="trader1",
            email="trader1@company.com",
            password="SecurePass123!",
            role="trader"
        )
        print(f"Criação de usuário: {'✅ Sucesso' if user_result['success'] else '❌ Falha'}")
        
        # Autentica usuário
        auth_result = security_system.access_control.authenticate_user(
            username="trader1",
            password="SecurePass123!",
            ip_address="192.168.1.100"
        )
        print(f"Autenticação: {'✅ Sucesso' if auth_result['success'] else '❌ Falha'}")
        
        session_id = auth_result.get('session_id') if auth_result['success'] else None
        
        # Teste de criptografia
        print("\n🔐 Teste de Criptografia:")
        print("-" * 40)
        
        test_data = "Informação financeira sensível"
        encrypt_result = security_system.crypto_manager.encrypt_data(test_data)
        print(f"Criptografia: {'✅ Sucesso' if encrypt_result['success'] else '❌ Falha'}")
        
        if encrypt_result['success']:
            decrypt_result = security_system.crypto_manager.decrypt_data(encrypt_result['encrypted_data'])
            print(f"Descriptografia: {'✅ Sucesso' if decrypt_result['success'] else '❌ Falha'}")
            
            if decrypt_result['success']:
                print(f"Dados originais: {decrypt_result['decrypted_data']}")
        
        # Teste de detecção de ameaças
        print("\n🚨 Teste de Detecção de Ameaças:")
        print("-" * 40)
        
        # Requisição normal
        normal_request = {
            'action': 'get_portfolio',
            'portfolio_id': '12345',
            'ip_address': '192.168.1.100'
        }
        
        normal_analysis = security_system.threat_detector.analyze_request(normal_request)
        print(f"Requisição normal - Score: {normal_analysis['risk_score']:.1f}")
        
        # Requisição maliciosa
        malicious_request = {
            'action': 'get_portfolio',
            'portfolio_id': "12345'; DROP TABLE users; --",
            'ip_address': '10.0.0.1'
        }
        
        malicious_analysis = security_system.threat_detector.analyze_request(malicious_request)
        print(f"Requisição maliciosa - Score: {malicious_analysis['risk_score']:.1f}")
        print(f"Ameaças detectadas: {len(malicious_analysis['threats_detected'])}")
        
        # Teste de processamento de requisição segura
        print("\n🔒 Teste de Processamento Seguro:")
        print("-" * 40)
        
        if session_id:
            secure_result = security_system.process_secure_request(
                normal_request, session_id
            )
            print(f"Requisição segura: {'✅ Permitida' if secure_result['allowed'] else '❌ Bloqueada'}")
        
        # Teste de compliance
        print("\n📋 Teste de Compliance:")
        print("-" * 40)
        
        gdpr_assessment = security_system.run_compliance_assessment(
            ComplianceFramework.GDPR
        )
        print(f"GDPR Assessment - Score: {gdpr_assessment.compliance_score:.1f}%")
        print(f"Findings: {len(gdpr_assessment.findings)}")
        
        iso_assessment = security_system.run_compliance_assessment(
            ComplianceFramework.ISO_27001
        )
        print(f"ISO 27001 Assessment - Score: {iso_assessment.compliance_score:.1f}%")
        print(f"Findings: {len(iso_assessment.findings)}")
        
        # Gera relatório de segurança
        print("\n📊 Relatório de Segurança:")
        print("-" * 40)
        
        security_report = security_system.generate_security_report()
        
        print(f"Status do Sistema: {'Ativo' if security_report['system_status']['monitoring_active'] else 'Inativo'}")
        print(f"Incidentes de Segurança: {security_report['system_status']['security_incidents_count']}")
        print(f"Sessões Ativas: {security_report['system_status']['active_sessions']}")
        print(f"Políticas de Segurança: {security_report['system_status']['security_policies_count']}")
        
        # Salva dados de segurança
        security_system.save_security_data('security_data.json')
        
        print("\n💾 Dados de segurança salvos")
        print("✅ Teste do sistema de segurança concluído com sucesso!")
        
        return security_system
    
    # Executa teste
    security_system = test_cybersecurity_system()
