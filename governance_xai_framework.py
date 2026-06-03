"""
╔═════════════════════════════════════════════════════════════════════════════╗
║                FRAMEWORK DE GOVERNANÇA E EXPLICABILIDADE (XAI)          ║
║                 Componente 13: Sistema de Transparência e Auditoria      ║
╚═════════════════════════════════════════════════════════════════════════════╝
"""

import asyncio
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.inspection import permutation_importance
from sklearn.preprocessing import StandardScaler
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import json
import pickle
from collections import defaultdict, deque
import time
import hashlib
import uuid

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('GovernanceXAIFramework')

class ExplanationMethod(Enum):
    """Métodos de explicação"""
    FEATURE_IMPORTANCE = "feature_importance"
    SHAP = "shap"
    LIME = "lime"
    COUNTERFACTUAL = "counterfactual"
    ATTENTION_WEIGHTS = "attention_weights"
    GRADIENT_BASED = "gradient_based"
    PERTURBATION = "perturbation"
    PROTOTYPE = "prototype"
    RULE_BASED = "rule_based"
    SURROGATE = "surrogate"

class GovernanceType(Enum):
    """Tipos de governança"""
    MODEL_GOVERNANCE = "model_governance"
    DATA_GOVERNANCE = "data_governance"
    ALGORITHM_GOVERNANCE = "algorithm_governance"
    ETHICS_GOVERNANCE = "ethics_governance"
    COMPLIANCE_GOVERNANCE = "compliance_governance"
    RISK_GOVERNANCE = "risk_governance"
    PERFORMANCE_GOVERNANCE = "performance_governance"

class ComplianceStandard(Enum):
    """Padrões de compliance"""
    GDPR = "gdpr"
    SOX = "sox"
    PCI_DSS = "pci_dss"
    HIPAA = "hipaa"
    MiFID_II = "mifid_ii"
    BASEL_III = "basel_iii"
    ISO_27001 = "iso_27001"
    NIST = "nist"

class AuditLevel(Enum):
    """Níveis de auditoria"""
    BASIC = "basic"
    STANDARD = "standard"
    COMPREHENSIVE = "comprehensive"
    CRITICAL = "critical"

@dataclass
class Explanation:
    """Explicação de decisão do modelo"""
    id: str
    model_name: str
    input_data: Dict[str, Any]
    prediction: Any
    explanation_method: ExplanationMethod
    explanation_data: Dict[str, Any]
    confidence_score: float
    timestamp: datetime
    feature_importance: Dict[str, float] = field(default_factory=dict)
    counterfactual_examples: List[Dict[str, Any]] = field(default_factory=list)
    rule_explanations: List[str] = field(default_factory=list)
    visualization_data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'model_name': self.model_name,
            'input_data': self.input_data,
            'prediction': self.prediction,
            'explanation_method': self.explanation_method.value,
            'explanation_data': self.explanation_data,
            'confidence_score': self.confidence_score,
            'timestamp': self.timestamp.isoformat(),
            'feature_importance': self.feature_importance,
            'counterfactual_examples': self.counterfactual_examples,
            'rule_explanations': self.rule_explanations,
            'visualization_data': self.visualization_data,
            'metadata': self.metadata
        }

@dataclass
class GovernancePolicy:
    """Política de governança"""
    id: str
    name: str
    governance_type: GovernanceType
    description: str
    rules: List[Dict[str, Any]]
    compliance_standards: List[ComplianceStandard]
    enforcement_level: str  # advisory, mandatory, critical
    last_updated: datetime
    version: str
    active: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'governance_type': self.governance_type.value,
            'description': self.description,
            'rules': self.rules,
            'compliance_standards': [cs.value for cs in self.compliance_standards],
            'enforcement_level': self.enforcement_level,
            'last_updated': self.last_updated.isoformat(),
            'version': self.version,
            'active': self.active
        }

@dataclass
class AuditRecord:
    """Registro de auditoria"""
    id: str
    audit_type: str
    component: str
    timestamp: datetime
    auditor: str
    findings: List[Dict[str, Any]]
    compliance_status: str  # compliant, non_compliant, partial
    risk_level: str  # low, medium, high, critical
    recommendations: List[str]
    evidence: Dict[str, Any]
    next_audit_date: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'audit_type': self.audit_type,
            'component': self.component,
            'timestamp': self.timestamp.isoformat(),
            'auditor': self.auditor,
            'findings': self.findings,
            'compliance_status': self.compliance_status,
            'risk_level': self.risk_level,
            'recommendations': self.recommendations,
            'evidence': self.evidence,
            'next_audit_date': self.next_audit_date.isoformat() if self.next_audit_date else None
        }

class FeatureImportanceExplainer:
    """Explicador baseado em importância de features"""
    
    def __init__(self):
        self.explanations = []
        logger.info("🔍 FeatureImportanceExplainer inicializado")
    
    def explain(self, model, X: pd.DataFrame, feature_names: List[str] = None) -> Explanation:
        """Gera explicação baseada em importância de features"""
        if feature_names is None:
            feature_names = X.columns.tolist()
        
        explanation_id = f"feat_imp_{uuid.uuid4().hex[:8]}"
        timestamp = datetime.now()
        
        # Obtém importância das features
        feature_importance = self._get_feature_importance(model, X, feature_names)
        
        # Normaliza importância
        total_importance = sum(feature_importance.values())
        if total_importance > 0:
            normalized_importance = {
                k: v / total_importance for k, v in feature_importance.items()
            }
        else:
            normalized_importance = feature_importance
        
        # Gera predição para exemplo
        try:
            prediction = model.predict(X.iloc[[0]])[0]
            confidence = self._get_prediction_confidence(model, X.iloc[[0]])
        except:
            prediction = None
            confidence = 0.0
        
        explanation = Explanation(
            id=explanation_id,
            model_name=model.__class__.__name__,
            input_data=X.iloc[0].to_dict(),
            prediction=prediction,
            explanation_method=ExplanationMethod.FEATURE_IMPORTANCE,
            explanation_data={
                'method': 'feature_importance',
                'total_features': len(feature_names),
                'top_features': sorted(
                    feature_importance.items(), 
                    key=lambda x: x[1], 
                    reverse=True
                )[:10]
            },
            confidence_score=confidence,
            timestamp=timestamp,
            feature_importance=normalized_importance,
            visualization_data={
                'feature_importance_chart': self._create_importance_chart(
                    normalized_importance
                )
            }
        )
        
        self.explanations.append(explanation)
        logger.info(f"📊 Explicação de importância de features gerada: {explanation_id}")
        
        return explanation
    
    def _get_feature_importance(self, model, X: pd.DataFrame, 
                              feature_names: List[str]) -> Dict[str, float]:
        """Obtém importância das features do modelo"""
        importance = {}
        
        try:
            # Modelos sklearn
            if hasattr(model, 'feature_importances_'):
                for i, name in enumerate(feature_names):
                    if i < len(model.feature_importances_):
                        importance[name] = float(model.feature_importances_[i])
            
            # Modelos com coeficientes
            elif hasattr(model, 'coef_'):
                coef = model.coef_
                if coef.ndim > 1:
                    coef = np.mean(np.abs(coef), axis=0)
                
                for i, name in enumerate(feature_names):
                    if i < len(coef):
                        importance[name] = float(abs(coef[i]))
            
            # Permutation importance
            else:
                try:
                    perm_importance = permutation_importance(
                        model, X, np.zeros(len(X)), 
                        n_repeats=5, random_state=42
                    )
                    
                    for i, name in enumerate(feature_names):
                        if i < len(perm_importance.importances_mean):
                            importance[name] = float(perm_importance.importances_mean[i])
                            
                except:
                    # Fallback: importância igual para todas
                    for name in feature_names:
                        importance[name] = 1.0 / len(feature_names)
        
        except Exception as e:
            logger.error(f"❌ Erro ao obter importância das features: {e}")
            # Fallback
            for name in feature_names:
                importance[name] = 1.0 / len(feature_names)
        
        return importance
    
    def _get_prediction_confidence(self, model, X: pd.DataFrame) -> float:
        """Calcula confiança na predição"""
        try:
            if hasattr(model, 'predict_proba'):
                probas = model.predict_proba(X)
                return float(np.max(probas))
            elif hasattr(model, 'decision_function'):
                scores = model.decision_function(X)
                return float(abs(scores[0]))
            else:
                return 0.5  # Confiança padrão
        except:
            return 0.5
    
    def _create_importance_chart(self, importance: Dict[str, float]) -> Dict[str, Any]:
        """Cria dados para gráfico de importância"""
        # Ordena por importância
        sorted_importance = sorted(
            importance.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:20]  # Top 20
        
        return {
            'type': 'bar_chart',
            'data': {
                'features': [item[0] for item in sorted_importance],
                'importance': [item[1] for item in sorted_importance]
            },
            'layout': {
                'title': 'Importância das Features',
                'xaxis': {'title': 'Features'},
                'yaxis': {'title': 'Importância Normalizada'}
            }
        }

class SHAPExplainer:
    """Explicador usando SHAP (SHapley Additive exPlanations)"""
    
    def __init__(self):
        self.explanations = []
        logger.info("🧮 SHAPExplainer inicializado")
    
    def explain(self, model, X: pd.DataFrame, feature_names: List[str] = None) -> Explanation:
        """Gera explicação usando SHAP"""
        try:
            import shap
        except ImportError:
            logger.warning("⚠️ SHAP não instalado, usando fallback")
            return self._fallback_explanation(model, X, feature_names)
        
        if feature_names is None:
            feature_names = X.columns.tolist()
        
        explanation_id = f"shap_{uuid.uuid4().hex[:8]}"
        timestamp = datetime.now()
        
        try:
            # Cria explicador SHAP
            if hasattr(model, 'predict_proba'):
                # Modelo de classificação
                explainer = shap.Explainer(model, X)
            else:
                # Modelo de regressão
                explainer = shap.Explainer(model, X)
            
            # Calcula valores SHAP
            shap_values = explainer.shap_values(X)
            
            # Para classificação, pega a primeira classe
            if isinstance(shap_values, list):
                shap_values = shap_values[0]
            
            # Obtém predição e confiança
            prediction = model.predict(X.iloc[[0]])[0]
            if hasattr(model, 'predict_proba'):
                confidence = float(np.max(model.predict_proba(X.iloc[[0]])))
            else:
                confidence = 0.5
            
            # Calcula importância média
            mean_shap = np.abs(shap_values).mean(axis=0)
            feature_importance = {
                feature_names[i]: float(mean_shap[i]) 
                for i in range(len(feature_names))
            }
            
            # Normaliza importância
            total_importance = sum(feature_importance.values())
            if total_importance > 0:
                normalized_importance = {
                    k: v / total_importance for k, v in feature_importance.items()
                }
            else:
                normalized_importance = feature_importance
            
            explanation = Explanation(
                id=explanation_id,
                model_name=model.__class__.__name__,
                input_data=X.iloc[0].to_dict(),
                prediction=prediction,
                explanation_method=ExplanationMethod.SHAP,
                explanation_data={
                    'method': 'shap',
                    'shap_values': shap_values[0].tolist(),
                    'base_value': float(explainer.expected_value),
                    'feature_count': len(feature_names)
                },
                confidence_score=confidence,
                timestamp=timestamp,
                feature_importance=normalized_importance,
                visualization_data={
                    'shap_summary': self._create_shap_visualization(
                        shap_values[0], X, feature_names
                    )
                }
            )
            
            self.explanations.append(explanation)
            logger.info(f"🧮 Explicação SHAP gerada: {explanation_id}")
            
            return explanation
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar explicação SHAP: {e}")
            return self._fallback_explanation(model, X, feature_names)
    
    def _fallback_explanation(self, model, X: pd.DataFrame, 
                           feature_names: List[str]) -> Explanation:
        """Fallback quando SHAP não está disponível"""
        # Usa importância de features como fallback
        fallback_explainer = FeatureImportanceExplainer()
        explanation = fallback_explainer.explain(model, X, feature_names)
        explanation.explanation_method = ExplanationMethod.SHAP
        explanation.explanation_data['method'] = 'shap_fallback'
        
        return explanation
    
    def _create_shap_visualization(self, shap_values: np.ndarray, X: pd.DataFrame,
                                 feature_names: List[str]) -> Dict[str, Any]:
        """Cria dados para visualização SHAP"""
        return {
            'type': 'shap_plot',
            'data': {
                'shap_values': shap_values.tolist(),
                'feature_values': X.iloc[0].tolist(),
                'feature_names': feature_names
            },
            'plot_types': ['summary', 'force', 'dependence', 'waterfall']
        }

class CounterfactualExplainer:
    """Explicador baseado em exemplos contrafactuais"""
    
    def __init__(self):
        self.explanations = []
        logger.info("🔄 CounterfactualExplainer inicializado")
    
    def explain(self, model, X: pd.DataFrame, feature_names: List[str] = None,
               target_class: Any = None, max_examples: int = 5) -> Explanation:
        """Gera explicação usando exemplos contrafactuais"""
        if feature_names is None:
            feature_names = X.columns.tolist()
        
        explanation_id = f"cf_{uuid.uuid4().hex[:8]}"
        timestamp = datetime.now()
        
        # Obtém predição original
        original_prediction = model.predict(X.iloc[[0]])[0]
        
        # Gera exemplos contrafactuais
        counterfactuals = self._generate_counterfactuals(
            model, X.iloc[0], feature_names, target_class, max_examples
        )
        
        # Calcula confiança
        if hasattr(model, 'predict_proba'):
            confidence = float(np.max(model.predict_proba(X.iloc[[0]])))
        else:
            confidence = 0.5
        
        explanation = Explanation(
            id=explanation_id,
            model_name=model.__class__.__name__,
            input_data=X.iloc[0].to_dict(),
            prediction=original_prediction,
            explanation_method=ExplanationMethod.COUNTERFACTUAL,
            explanation_data={
                'method': 'counterfactual',
                'target_class': target_class,
                'generated_examples': len(counterfactuals),
                'search_strategy': 'genetic_algorithm'
            },
            confidence_score=confidence,
            timestamp=timestamp,
            counterfactual_examples=counterfactuals,
            visualization_data={
                'counterfactual_plot': self._create_counterfactual_visualization(
                    X.iloc[0], counterfactuals, feature_names
                )
            }
        )
        
        self.explanations.append(explanation)
        logger.info(f"🔄 Explicação contrafactual gerada: {explanation_id}")
        
        return explanation
    
    def _generate_counterfactuals(self, model, original_input: pd.Series,
                                feature_names: List[str], target_class: Any,
                                max_examples: int) -> List[Dict[str, Any]]:
        """Gera exemplos contrafactuais"""
        counterfactuals = []
        
        try:
            # Estratégia simples: perturba features uma por uma
            original_pred = model.predict(original_input.values.reshape(1, -1))[0]
            
            for feature_name in feature_names:
                if feature_name not in original_input.index:
                    continue
                
                # Cria variações da feature
                original_value = original_input[feature_name]
                
                # Para features numéricas
                if isinstance(original_value, (int, float)):
                    variations = [
                        original_value * 0.8,
                        original_value * 1.2,
                        original_value - abs(original_value) * 0.1,
                        original_value + abs(original_value) * 0.1
                    ]
                else:
                    # Para features categóricas
                    variations = [original_value]  # Simplificado
                
                # Testa variações
                for variation in variations:
                    modified_input = original_input.copy()
                    modified_input[feature_name] = variation
                    
                    try:
                        new_pred = model.predict(modified_input.values.reshape(1, -1))[0]
                        
                        # Se a predição mudou, é um contrafactual
                        if new_pred != original_pred:
                            counterfactuals.append({
                                'modified_feature': feature_name,
                                'original_value': original_value,
                                'new_value': variation,
                                'original_prediction': original_pred,
                                'new_prediction': new_pred,
                                'distance': abs(variation - original_value) / (abs(original_value) + 1e-6)
                            })
                            
                            if len(counterfactuals) >= max_examples:
                                break
                    except:
                        continue
                
                if len(counterfactuals) >= max_examples:
                    break
            
            # Ordena por distância (menor mudança primeiro)
            counterfactuals.sort(key=lambda x: x['distance'])
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar contrafactuais: {e}")
        
        return counterfactuals[:max_examples]
    
    def _create_counterfactual_visualization(self, original_input: pd.Series,
                                         counterfactuals: List[Dict[str, Any]],
                                         feature_names: List[str]) -> Dict[str, Any]:
        """Cria dados para visualização contrafactual"""
        return {
            'type': 'counterfactual_plot',
            'data': {
                'original_input': original_input.to_dict(),
                'counterfactuals': counterfactuals,
                'feature_names': feature_names
            },
            'plot_types': ['feature_changes', 'prediction_changes']
        }

class GovernanceEngine:
    """Motor de governança do sistema"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.policies = {}
        self.audit_records = []
        self.compliance_checks = {}
        
        logger.info("⚖️ GovernanceEngine inicializado")
    
    def add_policy(self, policy: GovernancePolicy):
        """Adiciona política de governança"""
        self.policies[policy.id] = policy
        logger.info(f"📋 Política adicionada: {policy.name}")
    
    def check_compliance(self, component: str, data: Dict[str, Any],
                      policy_id: str = None) -> Dict[str, Any]:
        """Verifica compliance de componente"""
        compliance_result = {
            'component': component,
            'timestamp': datetime.now().isoformat(),
            'compliant': True,
            'violations': [],
            'warnings': [],
            'recommendations': []
        }
        
        if policy_id and policy_id in self.policies:
            policy = self.policies[policy_id]
            violations = self._check_policy_compliance(policy, component, data)
            
            compliance_result['violations'] = violations
            compliance_result['compliant'] = len(violations) == 0
            
            if violations:
                compliance_result['recommendations'] = [
                    f"Corrigir violação da política {policy.name}: {v}"
                    for v in violations
                ]
        else:
            # Verifica todas as políticas aplicáveis
            for policy in self.policies.values():
                if not policy.active:
                    continue
                
                violations = self._check_policy_compliance(policy, component, data)
                if violations:
                    compliance_result['violations'].extend([
                        f"{policy.name}: {v}" for v in violations
                    ])
                    compliance_result['compliant'] = False
        
        return compliance_result
    
    def _check_policy_compliance(self, policy: GovernancePolicy, component: str,
                                data: Dict[str, Any]) -> List[str]:
        """Verifica compliance de uma política específica"""
        violations = []
        
        for rule in policy.rules:
            rule_type = rule.get('type')
            
            if rule_type == 'model_validation':
                if not self._check_model_validation(data, rule):
                    violations.append(rule.get('description', 'Regra de validação de modelo'))
            
            elif rule_type == 'data_quality':
                if not self._check_data_quality(data, rule):
                    violations.append(rule.get('description', 'Regra de qualidade de dados'))
            
            elif rule_type == 'performance_threshold':
                if not self._check_performance_threshold(data, rule):
                    violations.append(rule.get('description', 'Regra de performance'))
            
            elif rule_type == 'security_requirement':
                if not self._check_security_requirement(data, rule):
                    violations.append(rule.get('description', 'Regra de segurança'))
        
        return violations
    
    def _check_model_validation(self, data: Dict[str, Any], 
                              rule: Dict[str, Any]) -> bool:
        """Verifica validação de modelo"""
        required_metrics = rule.get('required_metrics', [])
        model_metrics = data.get('model_metrics', {})
        
        for metric in required_metrics:
            if metric not in model_metrics:
                return False
            
            threshold = rule.get('thresholds', {}).get(metric)
            if threshold and model_metrics[metric] < threshold:
                return False
        
        return True
    
    def _check_data_quality(self, data: Dict[str, Any], 
                          rule: Dict[str, Any]) -> bool:
        """Verifica qualidade de dados"""
        quality_metrics = data.get('data_quality', {})
        
        min_completeness = rule.get('min_completeness', 0.9)
        if quality_metrics.get('completeness', 0) < min_completeness:
            return False
        
        max_missing_rate = rule.get('max_missing_rate', 0.05)
        if quality_metrics.get('missing_rate', 0) > max_missing_rate:
            return False
        
        return True
    
    def _check_performance_threshold(self, data: Dict[str, Any], 
                                  rule: Dict[str, Any]) -> bool:
        """Verifica threshold de performance"""
        performance_metrics = data.get('performance_metrics', {})
        
        min_accuracy = rule.get('min_accuracy', 0.8)
        if performance_metrics.get('accuracy', 0) < min_accuracy:
            return False
        
        max_latency = rule.get('max_latency_ms', 1000)
        if performance_metrics.get('latency_ms', 0) > max_latency:
            return False
        
        return True
    
    def _check_security_requirement(self, data: Dict[str, Any], 
                                   rule: Dict[str, Any]) -> bool:
        """Verifica requisito de segurança"""
        security_metrics = data.get('security_metrics', {})
        
        required_encryption = rule.get('require_encryption', False)
        if required_encryption and not security_metrics.get('encrypted', False):
            return False
        
        required_authentication = rule.get('require_authentication', False)
        if required_authentication and not security_metrics.get('authenticated', False):
            return False
        
        return True
    
    def create_audit_record(self, component: str, audit_type: str,
                          findings: List[Dict[str, Any]], auditor: str) -> AuditRecord:
        """Cria registro de auditoria"""
        audit_id = f"audit_{uuid.uuid4().hex[:8]}"
        
        # Determina status de compliance
        has_violations = any(f.get('severity') == 'high' for f in findings)
        has_warnings = any(f.get('severity') == 'medium' for f in findings)
        
        if has_violations:
            compliance_status = 'non_compliant'
            risk_level = 'high'
        elif has_warnings:
            compliance_status = 'partial'
            risk_level = 'medium'
        else:
            compliance_status = 'compliant'
            risk_level = 'low'
        
        # Gera recomendações
        recommendations = []
        for finding in findings:
            if finding.get('recommendation'):
                recommendations.append(finding['recommendation'])
        
        # Calcula próxima data de auditoria
        if risk_level == 'high':
            next_audit = datetime.now() + timedelta(days=30)
        elif risk_level == 'medium':
            next_audit = datetime.now() + timedelta(days=90)
        else:
            next_audit = datetime.now() + timedelta(days=180)
        
        audit_record = AuditRecord(
            id=audit_id,
            audit_type=audit_type,
            component=component,
            timestamp=datetime.now(),
            auditor=auditor,
            findings=findings,
            compliance_status=compliance_status,
            risk_level=risk_level,
            recommendations=recommendations,
            evidence={'audit_data': 'collected'},
            next_audit_date=next_audit
        )
        
        self.audit_records.append(audit_record)
        logger.info(f"📋 Registro de auditoria criado: {audit_id}")
        
        return audit_record
    
    def get_compliance_report(self, component: str = None) -> Dict[str, Any]:
        """Gera relatório de compliance"""
        records = self.audit_records
        
        if component:
            records = [r for r in records if r.component == component]
        
        if not records:
            return {'message': 'Nenhum registro de auditoria encontrado'}
        
        # Estatísticas gerais
        total_audits = len(records)
        compliant_audits = len([r for r in records if r.compliance_status == 'compliant'])
        non_compliant_audits = len([r for r in records if r.compliance_status == 'non_compliant'])
        
        # Por risco
        risk_distribution = defaultdict(int)
        for record in records:
            risk_distribution[record.risk_level] += 1
        
        # Recomendações mais comuns
        all_recommendations = []
        for record in records:
            all_recommendations.extend(record.recommendations)
        
        recommendation_counts = defaultdict(int)
        for rec in all_recommendations:
            recommendation_counts[rec] += 1
        
        top_recommendations = sorted(
            recommendation_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        return {
            'summary': {
                'total_audits': total_audits,
                'compliant_audits': compliant_audits,
                'non_compliant_audits': non_compliant_audits,
                'compliance_rate': compliant_audits / total_audits if total_audits > 0 else 0
            },
            'risk_distribution': dict(risk_distribution),
            'top_recommendations': top_recommendations,
            'recent_audits': [r.to_dict() for r in records[-5:]],
            'upcoming_audits': [
                r.to_dict() for r in records 
                if r.next_audit_date and r.next_audit_date > datetime.now()
            ]
        }

class XAIFramework:
    """Framework principal de XAI e Governança"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        
        # Componentes de explicação
        self.feature_explainer = FeatureImportanceExplainer()
        self.shap_explainer = SHAPExplainer()
        self.counterfactual_explainer = CounterfactualExplainer()
        
        # Motor de governança
        self.governance_engine = GovernanceEngine(self.config.get('governance', {}))
        
        # Histórico
        self.explanation_history = []
        self.audit_history = []
        
        # Configurações
        self.default_explanation_methods = [
            ExplanationMethod.FEATURE_IMPORTANCE,
            ExplanationMethod.SHAP,
            ExplanationMethod.COUNTERFACTUAL
        ]
        
        logger.info("🧠 XAIFramework inicializado")
    
    def explain_model_decision(self, model, X: pd.DataFrame, 
                             method: ExplanationMethod = None,
                             feature_names: List[str] = None) -> Explanation:
        """Explica decisão do modelo usando método especificado"""
        if method is None:
            method = self.default_explanation_methods[0]
        
        if feature_names is None:
            feature_names = X.columns.tolist()
        
        # Seleciona explicador
        if method == ExplanationMethod.FEATURE_IMPORTANCE:
            explanation = self.feature_explainer.explain(model, X, feature_names)
        elif method == ExplanationMethod.SHAP:
            explanation = self.shap_explainer.explain(model, X, feature_names)
        elif method == ExplanationMethod.COUNTERFACTUAL:
            explanation = self.counterfactual_explainer.explain(model, X, feature_names)
        else:
            raise ValueError(f"Método de explicação não suportado: {method}")
        
        self.explanation_history.append(explanation)
        
        # Verifica governança após explicação
        self._check_explanation_governance(explanation)
        
        return explanation
    
    def explain_multiple_methods(self, model, X: pd.DataFrame,
                              feature_names: List[str] = None) -> List[Explanation]:
        """Gera explicações usando múltiplos métodos"""
        explanations = []
        
        for method in self.default_explanation_methods:
            try:
                explanation = self.explain_model_decision(
                    model, X, method, feature_names
                )
                explanations.append(explanation)
            except Exception as e:
                logger.error(f"❌ Erro no método {method}: {e}")
        
        return explanations
    
    def _check_explanation_governance(self, explanation: Explanation):
        """Verifica governança da explicação"""
        # Política de transparência
        transparency_policy = GovernancePolicy(
            id="xai_transparency",
            name="Política de Transparência XAI",
            governance_type=GovernanceType.ETHICS_GOVERNANCE,
            description="Garante que explicações sejam transparentes e compreensíveis",
            rules=[
                {
                    'type': 'explanation_quality',
                    'description': 'Explicação deve ter confiança mínima',
                    'min_confidence': 0.7
                },
                {
                    'type': 'feature_coverage',
                    'description': 'Explicação deve cobrir features principais',
                    'min_features': 3
                }
            ],
            compliance_standards=[ComplianceStandard.GDPR],
            enforcement_level="mandatory",
            last_updated=datetime.now(),
            version="1.0"
        )
        
        # Verifica compliance
        explanation_data = {
            'explanation_confidence': explanation.confidence_score,
            'feature_count': len(explanation.feature_importance),
            'explanation_method': explanation.explanation_method.value
        }
        
        compliance_result = self.governance_engine.check_compliance(
            "xai_explanation", explanation_data, "xai_transparency"
        )
        
        if not compliance_result['compliant']:
            logger.warning(f"⚠️ Explicação não compliant: {compliance_result['violations']}")
    
    def audit_model_component(self, model_name: str, model_data: Dict[str, Any],
                           auditor: str = "system") -> AuditRecord:
        """Audita componente do modelo"""
        findings = []
        
        # Verifica performance
        performance_metrics = model_data.get('performance_metrics', {})
        if performance_metrics.get('accuracy', 0) < 0.8:
            findings.append({
                'severity': 'high',
                'description': 'Acurácia do modelo abaixo do threshold',
                'recommendation': 'Retreinar modelo com mais dados'
            })
        
        # Verifica drift
        if model_data.get('drift_detected', False):
            findings.append({
                'severity': 'medium',
                'description': 'Drift de dados detectado',
                'recommendation': 'Atualizar modelo com dados recentes'
            })
        
        # Verifica bias
        bias_metrics = model_data.get('bias_metrics', {})
        if bias_metrics.get('demographic_parity_difference', 0) > 0.1:
            findings.append({
                'severity': 'high',
                'description': 'Bias demográfico detectado',
                'recommendation': 'Aplicar técnicas de mitigação de bias'
            })
        
        # Cria registro de auditoria
        audit_record = self.governance_engine.create_audit_record(
            component=model_name,
            audit_type="model_governance",
            findings=findings,
            auditor=auditor
        )
        
        self.audit_history.append(audit_record)
        
        return audit_record
    
    def generate_xai_report(self, model_name: str = None) -> Dict[str, Any]:
        """Gera relatório completo de XAI"""
        explanations = self.explanation_history
        
        if model_name:
            explanations = [e for e in explanations if e.model_name == model_name]
        
        if not explanations:
            return {'message': 'Nenhuma explicação encontrada'}
        
        # Estatísticas das explicações
        method_counts = defaultdict(int)
        confidence_scores = []
        
        for exp in explanations:
            method_counts[exp.explanation_method.value] += 1
            confidence_scores.append(exp.confidence_score)
        
        # Features mais importantes
        all_feature_importance = defaultdict(float)
        for exp in explanations:
            for feature, importance in exp.feature_importance.items():
                all_feature_importance[feature] += importance
        
        top_features = sorted(
            all_feature_importance.items(),
            key=lambda x: x[1],
            reverse=True
        )[:20]
        
        return {
            'summary': {
                'total_explanations': len(explanations),
                'average_confidence': np.mean(confidence_scores),
                'method_distribution': dict(method_counts),
                'date_range': {
                    'first': min(e.timestamp for e in explanations).isoformat(),
                    'last': max(e.timestamp for e in explanations).isoformat()
                }
            },
            'top_features': top_features,
            'recent_explanations': [e.to_dict() for e in explanations[-10:]],
            'governance_summary': self.governance_engine.get_compliance_report(),
            'recommendations': self._generate_xai_recommendations(explanations)
        }
    
    def _generate_xai_recommendations(self, explanations: List[Explanation]) -> List[str]:
        """Gera recomendações baseadas nas explicações"""
        recommendations = []
        
        # Analisa confiança das explicações
        confidence_scores = [e.confidence_score for e in explanations]
        avg_confidence = np.mean(confidence_scores)
        
        if avg_confidence < 0.7:
            recommendations.append(
                "Baixa confiança média nas explicações. Considerar melhorar o modelo ou usar métodos de explicação mais robustos."
            )
        
        # Analisa métodos usados
        methods = [e.explanation_method for e in explanations]
        method_counts = defaultdict(int)
        for method in methods:
            method_counts[method] += 1
        
        if len(method_counts) < 3:
            recommendations.append(
                "Usar múltiplos métodos de explicação para obter visão mais completa das decisões do modelo."
            )
        
        # Analisa features
        all_features = set()
        for exp in explanations:
            all_features.update(exp.feature_importance.keys())
        
        if len(all_features) < 5:
            recommendations.append(
                "Poucas features sendo explicadas. Considerar aumentar a diversidade de features no modelo."
            )
        
        return recommendations
    
    def save_framework_data(self, filepath: str):
        """Salva dados do framework XAI"""
        data = {
            'timestamp': datetime.now().isoformat(),
            'explanations': [e.to_dict() for e in self.explanation_history],
            'audit_records': [a.to_dict() for a in self.audit_history],
            'governance_policies': {
                pid: policy.to_dict() 
                for pid, policy in self.governance_engine.policies.items()
            },
            'config': self.config
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        
        logger.info(f"💾 Dados do framework XAI salvos em {filepath}")
    
    def load_framework_data(self, filepath: str):
        """Carrega dados do framework XAI"""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            # Carrega explicações (simplificado)
            self.explanation_history = []
            
            # Carrega políticas
            for pid, policy_data in data.get('governance_policies', {}).items():
                policy = GovernancePolicy(
                    id=policy_data['id'],
                    name=policy_data['name'],
                    governance_type=GovernanceType(policy_data['governance_type']),
                    description=policy_data['description'],
                    rules=policy_data['rules'],
                    compliance_standards=[
                        ComplianceStandard(cs) for cs in policy_data['compliance_standards']
                    ],
                    enforcement_level=policy_data['enforcement_level'],
                    last_updated=datetime.fromisoformat(policy_data['last_updated']),
                    version=policy_data['version'],
                    active=policy_data['active']
                )
                self.governance_engine.add_policy(policy)
            
            logger.info(f"📂 Dados do framework XAI carregados de {filepath}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao carregar dados: {e}")

# Configuração padrão
DEFAULT_XAI_CONFIG = {
    'explanation_methods': [
        'feature_importance',
        'shap',
        'counterfactual'
    ],
    'governance': {
        'auto_audit': True,
        'audit_interval_days': 30,
        'compliance_threshold': 0.8
    },
    'visualization': {
        'enable_charts': True,
        'chart_format': 'json',
        'save_plots': True
    }
}

if __name__ == "__main__":
    # Exemplo de uso
    def create_sample_model():
        """Cria modelo de exemplo"""
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.datasets import make_classification
        
        # Gera dados de exemplo
        X, y = make_classification(
            n_samples=1000, n_features=10, n_informative=5, 
            n_redundant=2, random_state=42
        )
        
        feature_names = [f'feature_{i}' for i in range(X.shape[1])]
        
        # Cria e treina modelo
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X, y)
        
        return model, X, feature_names, y
    
    def test_xai_framework():
        """Testa framework XAI"""
        print("🧠 Iniciando Teste do Framework XAI e Governança")
        print("=" * 60)
        
        # Cria modelo e dados
        model, X, feature_names, y = create_sample_model()
        
        # Cria framework XAI
        xai_framework = XAIFramework(DEFAULT_XAI_CONFIG)
        
        # Testa diferentes métodos de explicação
        print("\n🔍 Testando Métodos de Explicação:")
        print("-" * 40)
        
        # Explicação por importância de features
        print("1. Importância de Features:")
        feat_exp = xai_framework.explain_model_decision(
            model, pd.DataFrame(X[:1], columns=feature_names),
            ExplanationMethod.FEATURE_IMPORTANCE,
            feature_names
        )
        print(f"   ID: {feat_exp.id}")
        print(f"   Confiança: {feat_exp.confidence_score:.3f}")
        print(f"   Top 3 Features: {list(feat_exp.feature_importance.keys())[:3]}")
        
        # Explicação SHAP
        print("\n2. SHAP:")
        try:
            shap_exp = xai_framework.explain_model_decision(
                model, pd.DataFrame(X[:1], columns=feature_names),
                ExplanationMethod.SHAP,
                feature_names
            )
            print(f"   ID: {shap_exp.id}")
            print(f"   Confiança: {shap_exp.confidence_score:.3f}")
            print(f"   Método: {shap_exp.explanation_method.value}")
        except Exception as e:
            print(f"   Erro: {e}")
        
        # Explicação Contrafactual
        print("\n3. Contrafactual:")
        cf_exp = xai_framework.explain_model_decision(
            model, pd.DataFrame(X[:1], columns=feature_names),
            ExplanationMethod.COUNTERFACTUAL,
            feature_names
        )
        print(f"   ID: {cf_exp.id}")
        print(f"   Confiança: {cf_exp.confidence_score:.3f}")
        print(f"   Exemplos Contrafactuais: {len(cf_exp.counterfactual_examples)}")
        
        # Testa múltiplos métodos
        print("\n🔄 Testando Múltiplos Métodos:")
        multi_exps = xai_framework.explain_multiple_methods(
            model, pd.DataFrame(X[:1], columns=feature_names),
            feature_names
        )
        print(f"   Total de explicações: {len(multi_exps)}")
        
        # Testa governança
        print("\n⚖️ Testando Governança:")
        print("-" * 40)
        
        # Cria política de exemplo
        policy = GovernancePolicy(
            id="model_quality",
            name="Política de Qualidade de Modelo",
            governance_type=GovernanceType.MODEL_GOVERNANCE,
            description="Garante qualidade mínima do modelo",
            rules=[
                {
                    'type': 'model_validation',
                    'description': 'Acurácia mínima',
                    'required_metrics': ['accuracy'],
                    'thresholds': {'accuracy': 0.8}
                }
            ],
            compliance_standards=[ComplianceStandard.GDPR],
            enforcement_level="mandatory",
            last_updated=datetime.now(),
            version="1.0"
        )
        
        xai_framework.governance_engine.add_policy(policy)
        
        # Simula dados do modelo para auditoria
        model_data = {
            'performance_metrics': {
                'accuracy': 0.85,
                'precision': 0.82,
                'recall': 0.88,
                'latency_ms': 150
            },
            'bias_metrics': {
                'demographic_parity_difference': 0.05
            },
            'drift_detected': False
        }
        
        # Verifica compliance
        compliance_result = xai_framework.governance_engine.check_compliance(
            "test_model", model_data, "model_quality"
        )
        
        print(f"   Compliance: {compliance_result['compliant']}")
        print(f"   Violações: {len(compliance_result['violations'])}")
        if compliance_result['violations']:
            for violation in compliance_result['violations']:
                print(f"     • {violation}")
        
        # Cria auditoria
        audit_record = xai_framework.audit_model_component(
            "test_model", model_data, "system_test"
        )
        
        print(f"\n📋 Auditoria Criada:")
        print(f"   ID: {audit_record.id}")
        print(f"   Status: {audit_record.compliance_status}")
        print(f"   Risco: {audit_record.risk_level}")
        print(f"   Recomendações: {len(audit_record.recommendations)}")
        
        # Gera relatório XAI
        print("\n📊 Gerando Relatório XAI:")
        xai_report = xai_framework.generate_xai_report()
        
        print(f"   Total de Explicações: {xai_report['summary']['total_explanations']}")
        print(f"   Confiança Média: {xai_report['summary']['average_confidence']:.3f}")
        print(f"   Métodos Usados: {list(xai_report['summary']['method_distribution'].keys())}")
        print(f"   Top Features: {len(xai_report['top_features'])}")
        
        # Salva dados
        xai_framework.save_framework_data('xai_framework_data.json')
        
        print("\n💾 Dados salvos em xai_framework_data.json")
        print("✅ Teste do Framework XAI concluído com sucesso!")
        
        return xai_framework
    
    # Executa teste
    xai_framework = test_xai_framework()
