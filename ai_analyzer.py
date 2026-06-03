"""
Módulo de Análise de IA Avançada
=================================
Pipeline completo com spaCy, Transformers e análise cognitiva
"""

import asyncio
import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
import json
import re
import math
from collections import defaultdict
import hashlib

# Importações condicionais
try:
    import spacy
    from spacy.lang.en import English
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False

try:
    from transformers import (
        AutoTokenizer, AutoModel, AutoModelForSequenceClassification,
        pipeline, TextClassificationPipeline, BertModel, GPT2Model,
        T5ForConditionalGeneration, T5Tokenizer
    )
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

try:
    import chromadb
    from chromadb.config import Settings as ChromaSettings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    from sklearn.cluster import KMeans
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

from config import settings
from core import get_logger, log_execution


class AnalysisType(str, Enum):
    """Tipos de análise disponíveis"""
    SENTIMENT = "sentiment"
    ENTITY = "entity"
    TOPIC = "topic"
    KEYWORD = "keyword"
    SUMMARIZATION = "summarization"
    CLASSIFICATION = "classification"
    EMBEDDING = "embedding"
    RAG = "rag"


@dataclass
class AnalysisResult:
    """Resultado de análise de IA"""
    text: str
    analysis_type: AnalysisType
    confidence: float
    result: Dict[str, Any]
    timestamp: datetime
    model_used: str
    processing_time: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data


@dataclass
class Entity:
    """Entidade extraída do texto"""
    text: str
    label: str
    start: int
    end: int
    confidence: float


@dataclass
class SentimentScore:
    """Score de sentimento"""
    label: str  # positive, negative, neutral
    score: float
    confidence: float


class AIAnalyzer:
    """
    Analisador de IA com múltiplos modelos e técnicas
    """
    
    def __init__(self):
        self.logger = get_logger().get_logger("vhalinor.ai_analyzer", "ai_analyzer")
        
        # Modelos spaCy
        self.nlp_models: Dict[str, Any] = {}
        self._load_spacy_models()
        
        # Modelos Transformers
        self.transformer_models: Dict[str, Any] = {}
        self.transformer_tokenizers: Dict[str, Any] = {}
        self._load_transformer_models()
        
        # Sentence Transformers para embeddings
        self.sentence_transformer: Optional[Any] = None
        self._load_sentence_transformer()
        
        # Vector store para RAG
        self.vector_store: Optional[Any] = None
        self._init_vector_store()
        
        # Cache de análises
        self.analysis_cache: Dict[str, AnalysisResult] = {}
        
        # Configurações
        self.max_text_length = settings.nlp_max_length
        self.batch_size = settings.nlp_batch_size
    
    @log_execution(
        component="ai_analyzer",
        operation="load_spacy_models",
        log_exceptions=True
    )
    def _load_spacy_models(self):
        """Carrega modelos spaCy"""
        if not SPACY_AVAILABLE:
            self.logger.warning("spaCy not available")
            return
        
        try:
            # Carregar modelo principal
            self.nlp_models["en_core_web_sm"] = spacy.load("en_core_web_sm")
            self.nlp_models["en_core_web_md"] = spacy.load("en_core_web_md")
            self.nlp_models["en_core_web_lg"] = spacy.load("en_core_web_lg")
            
            self.logger.info("spaCy models loaded successfully")
        except Exception as e:
            self.logger.error(f"Failed to load spaCy models: {e}")
    
    @log_execution(
        component="ai_analyzer",
        operation="load_transformer_models",
        log_exceptions=True
    )
    def _load_transformer_models(self):
        """Carrega modelos Transformers"""
        if not TRANSFORMERS_AVAILABLE:
            self.logger.warning("Transformers not available")
            return
        
        try:
            # Modelo de sentimento
            sentiment_model_name = "cardiffnlp/twitter-roberta-base-sentiment-latest"
            self.transformer_models["sentiment"] = AutoModelForSequenceClassification.from_pretrained(
                sentiment_model_name
            )
            self.transformer_tokenizers["sentiment"] = AutoTokenizer.from_pretrained(
                sentiment_model_name
            )
            
            # Modelo de classificação
            classification_model_name = "microsoft/DialoGPT-medium"
            self.transformer_models["classification"] = AutoModel.from_pretrained(
                classification_model_name
            )
            self.transformer_tokenizers["classification"] = AutoTokenizer.from_pretrained(
                classification_model_name
            )
            
            # Pipeline de sumarização
            self.transformer_models["summarization"] = pipeline(
                "summarization",
                model="facebook/bart-large-cnn"
            )
            
            self.logger.info("Transformer models loaded successfully")
        except Exception as e:
            self.logger.error(f"Failed to load Transformer models: {e}")
    
    @log_execution(
        component="ai_analyzer",
        operation="load_sentence_transformer",
        log_exceptions=True
    )
    def _load_sentence_transformer(self):
        """Carrega Sentence Transformer para embeddings"""
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            self.logger.warning("Sentence Transformers not available")
            return
        
        try:
            self.sentence_transformer = SentenceTransformer(
                'all-MiniLM-L6-v2'
            )
            self.logger.info("Sentence Transformer loaded successfully")
        except Exception as e:
            self.logger.error(f"Failed to load Sentence Transformer: {e}")
    
    @log_execution(
        component="ai_analyzer",
        operation="init_vector_store",
        log_exceptions=True
    )
    def _init_vector_store(self):
        """Inicializa vector store para RAG"""
        if not CHROMADB_AVAILABLE:
            self.logger.warning("ChromaDB not available")
            return
        
        try:
            self.vector_store = chromadb.Client()
            self.vector_store.get_or_create_collection(
                name="vhalinor_knowledge",
                metadata={"description": "Knowledge base for RAG"}
            )
            self.logger.info("Vector store initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize vector store: {e}")
    
    @log_execution(
        component="ai_analyzer",
        operation="analyze_sentiment",
        log_args=True,
        log_result=True
    )
    async def analyze_sentiment(self, text: str) -> Optional[SentimentScore]:
        """
        Analisa sentimento do texto
        
        Args:
            text: Texto para analisar
        
        Returns:
            Score de sentimento ou None
        """
        try:
            # Verificar cache
            cache_key = f"sentiment_{hash(text)}"
            if cache_key in self.analysis_cache:
                return self.analysis_cache[cache_key].result.get("sentiment")
            
            # Truncar texto se necessário
            if len(text) > self.max_text_length:
                text = text[:self.max_text_length]
            
            # Usar modelo Transformers
            if "sentiment" in self.transformer_models:
                tokenizer = self.transformer_tokenizers["sentiment"]
                model = self.transformer_models["sentiment"]
                
                inputs = tokenizer(
                    text,
                    return_tensors="pt",
                    truncation=True,
                    max_length=self.max_text_length
                )
                
                with torch.no_grad():
                    outputs = model(**inputs)
                    predictions = torch.nn.functional.softmax(
                        outputs.logits, dim=-1
                    )
                    sentiment_idx = torch.argmax(predictions).item()
                    confidence = predictions[0][sentiment_idx].item()
                
                # Mapear labels
                labels = ["negative", "neutral", "positive"]
                sentiment_label = labels[sentiment_idx]
                
                result = SentimentScore(
                    label=sentiment_label,
                    score=confidence,
                    confidence=confidence
                )
                
                # Salvar no cache
                analysis_result = AnalysisResult(
                    text=text,
                    analysis_type=AnalysisType.SENTIMENT,
                    confidence=confidence,
                    result={"sentiment": asdict(result)},
                    timestamp=datetime.now(),
                    model_used="cardiffnlp/twitter-roberta-base-sentiment",
                    processing_time=0.0
                )
                self.analysis_cache[cache_key] = analysis_result
                
                return result
            
            return None
            
        except Exception as e:
            self.logger.error(f"Sentiment analysis error: {e}")
            return None
    
    @log_execution(
        component="ai_analyzer",
        operation="extract_entities",
        log_args=True,
        log_result=True
    )
    async def extract_entities(self, text: str) -> List[Entity]:
        """
        Extrai entidades do texto usando spaCy
        
        Args:
            text: Texto para analisar
        
        Returns:
            Lista de entidades encontradas
        """
        try:
            # Verificar cache
            cache_key = f"entities_{hash(text)}"
            if cache_key in self.analysis_cache:
                return self.analysis_cache[cache_key].result.get("entities")
            
            # Usar spaCy
            if "en_core_web_md" in self.nlp_models:
                nlp = self.nlp_models["en_core_web_md"]
                doc = nlp(text)
                
                entities = []
                for ent in doc.ents:
                    entity = Entity(
                        text=ent.text,
                        label=ent.label_,
                        start=ent.start_char,
                        end=ent.end_char,
                        confidence=ent.kb_id_ / 100.0 if ent.kb_id_ else 0.8
                    )
                    entities.append(entity)
                
                # Salvar no cache
                analysis_result = AnalysisResult(
                    text=text,
                    analysis_type=AnalysisType.ENTITY,
                    confidence=0.8,
                    result={"entities": [asdict(e) for e in entities]},
                    timestamp=datetime.now(),
                    model_used="spaCy en_core_web_md",
                    processing_time=0.0
                )
                self.analysis_cache[cache_key] = analysis_result
                
                self.logger.info(f"Extracted {len(entities)} entities")
                return entities
            
            return []
            
        except Exception as e:
            self.logger.error(f"Entity extraction error: {e}")
            return []
    
    @log_execution(
        component="ai_analyzer",
        operation="generate_embedding",
        log_args=True,
        log_result=True
    )
    async def generate_embedding(self, text: str) -> Optional[np.ndarray]:
        """
        Gera embedding do texto
        
        Args:
            text: Texto para gerar embedding
        
        Returns:
            Vetor de embedding ou None
        """
        try:
            # Verificar cache
            cache_key = f"embedding_{hash(text)}"
            if cache_key in self.analysis_cache:
                return self.analysis_cache[cache_key].result.get("embedding")
            
            # Usar Sentence Transformer
            if self.sentence_transformer:
                embedding = self.sentence_transformer.encode(text)
                
                # Salvar no cache
                analysis_result = AnalysisResult(
                    text=text,
                    analysis_type=AnalysisType.EMBEDDING,
                    confidence=1.0,
                    result={"embedding": embedding.tolist()},
                    timestamp=datetime.now(),
                    model_used="all-MiniLM-L6-v2",
                    processing_time=0.0
                )
                self.analysis_cache[cache_key] = analysis_result
                
                return embedding
            
            return None
            
        except Exception as e:
            self.logger.error(f"Embedding generation error: {e}")
            return None
    
    @log_execution(
        component="ai_analyzer",
        operation="summarize_text",
        log_args=True,
        log_result=True
    )
    async def summarize_text(self, text: str, max_length: int = 150) -> Optional[str]:
        """
        Gera resumo do texto
        
        Args:
            text: Texto para resumir
            max_length: Comprimento máximo do resumo
        
        Returns:
            Resumo do texto ou None
        """
        try:
            # Verificar cache
            cache_key = f"summary_{hash(text)}"
            if cache_key in self.analysis_cache:
                return self.analysis_cache[cache_key].result.get("summary")
            
            # Usar pipeline de sumarização
            if "summarization" in self.transformer_models:
                summarizer = self.transformer_models["summarization"]
                
                summary = summarizer(
                    text,
                    max_length=max_length,
                    min_length=30,
                    do_sample=False
                )[0]['summary_text']
                
                # Salvar no cache
                analysis_result = AnalysisResult(
                    text=text,
                    analysis_type=AnalysisType.SUMMARIZATION,
                    confidence=0.8,
                    result={"summary": summary},
                    timestamp=datetime.now(),
                    model_used="facebook/bart-large-cnn",
                    processing_time=0.0
                )
                self.analysis_cache[cache_key] = analysis_result
                
                self.logger.info(f"Generated summary with {len(summary)} characters")
                return summary
            
            return None
            
        except Exception as e:
            self.logger.error(f"Text summarization error: {e}")
            return None
    
    @log_execution(
        component="ai_analyzer",
        operation="add_to_knowledge_base",
        log_args=True,
        log_result=True
    )
    async def add_to_knowledge_base(
        self,
        text: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Adiciona texto à base de conhecimento para RAG
        
        Args:
            text: Texto para adicionar
            metadata: Metadados adicionais
        
        Returns:
            ID do documento adicionado ou None
        """
        try:
            if not self.vector_store:
                self.logger.error("Vector store not initialized")
                return None
            
            # Gerar embedding
            embedding = await self.generate_embedding(text)
            if embedding is None:
                return None
            
            # Adicionar à coleção
            collection = self.vector_store.get_collection("vhalinor_knowledge")
            
            document_data = {
                "text": text,
                "embedding": embedding.tolist(),
                "metadata": metadata or {},
                "timestamp": datetime.now().isoformat()
            }
            
            result = collection.add(
                documents=[text],
                embeddings=[embedding],
                metadatas=[metadata or {}],
                ids=[f"doc_{hash(text)}_{datetime.now().timestamp()}"]
            )
            
            doc_id = result['ids'][0]
            self.logger.info(f"Added document to knowledge base: {doc_id}")
            
            return doc_id
            
        except Exception as e:
            self.logger.error(f"Failed to add to knowledge base: {e}")
            return None
    
    @log_execution(
        component="ai_analyzer",
        operation="search_knowledge_base",
        log_args=True,
        log_result=True
    )
    async def search_knowledge_base(
        self,
        query: str,
        n_results: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Busca na base de conhecimento usando RAG
        
        Args:
            query: Query de busca
            n_results: Número de resultados
        
        Returns:
            Lista de documentos relevantes
        """
        try:
            if not self.vector_store:
                self.logger.error("Vector store not initialized")
                return []
            
            # Gerar embedding da query
            query_embedding = await self.generate_embedding(query)
            if query_embedding is None:
                return []
            
            # Buscar na coleção
            collection = self.vector_store.get_collection("vhalinor_knowledge")
            
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results
            )
            
            # Processar resultados
            documents = []
            for i, doc in enumerate(results['documents'][0]):
                documents.append({
                    "text": doc,
                    "metadata": results['metadatas'][0][i],
                    "distance": results['distances'][0][i],
                    "id": results['ids'][0][i]
                })
            
            self.logger.info(f"Found {len(documents)} documents in knowledge base")
            return documents
            
        except Exception as e:
            self.logger.error(f"Knowledge base search error: {e}")
            return []
    
    @log_execution(
        component="ai_analyzer",
        operation="comprehensive_analysis",
        log_args=True,
        log_result=True
    )
    async def comprehensive_analysis(
        self,
        text: str,
        analyses: List[AnalysisType] = None
    ) -> Dict[str, Any]:
        """
        Realiza análise completa do texto
        
        Args:
            text: Texto para analisar
            analyses: Tipos de análise desejadas
        
        Returns:
            Dicionário com todos os resultados
        """
        if analyses is None:
            analyses = [
                AnalysisType.SENTIMENT,
                AnalysisType.ENTITY,
                AnalysisType.EMBEDDING
            ]
        
        results = {}
        
        # Análise de sentimento
        if AnalysisType.SENTIMENT in analyses:
            sentiment = await self.analyze_sentiment(text)
            results["sentiment"] = sentiment
        
        # Extração de entidades
        if AnalysisType.ENTITY in analyses:
            entities = await self.extract_entities(text)
            results["entities"] = entities
        
        # Geração de embedding
        if AnalysisType.EMBEDDING in analyses:
            embedding = await self.generate_embedding(text)
            results["embedding"] = embedding.tolist() if embedding is not None else None
        
        # Sumarização (se texto longo)
        if AnalysisType.SUMMARIZATION in analyses and len(text) > 500:
            summary = await self.summarize_text(text)
            results["summary"] = summary
        
        # Adicionar metadados
        results["metadata"] = {
            "text_length": len(text),
            "word_count": len(text.split()),
            "analysis_timestamp": datetime.now().isoformat(),
            "analyses_performed": [a.value for a in analyses]
        }
        
        self.logger.info(f"Comprehensive analysis completed: {list(analyses)}")
        return results
    
    def get_model_info(self) -> Dict[str, Any]:
        """Retorna informações sobre os modelos carregados"""
        return {
            "spacy_models": list(self.nlp_models.keys()),
            "transformer_models": list(self.transformer_models.keys()),
            "sentence_transformer": self.sentence_transformer is not None,
            "vector_store": self.vector_store is not None,
            "cache_size": len(self.analysis_cache),
            "max_text_length": self.max_text_length,
            "batch_size": self.batch_size
        }
    
    def clear_cache(self):
        """Limpa cache de análises"""
        self.analysis_cache.clear()
        self.logger.info("Analysis cache cleared")
    
    def get_status(self) -> Dict[str, Any]:
        """Retorna status do analisador"""
        return {
            "models_loaded": {
                "spacy": len(self.nlp_models) > 0,
                "transformers": len(self.transformer_models) > 0,
                "sentence_transformer": self.sentence_transformer is not None,
                "vector_store": self.vector_store is not None
            },
            "cache_size": len(self.analysis_cache),
            "max_text_length": self.max_text_length,
            "batch_size": self.batch_size,
            "last_update": datetime.now().isoformat()
        }


# Instância global do analisador
_ai_analyzer: Optional[AIAnalyzer] = None


def get_ai_analyzer() -> AIAnalyzer:
    """Obtém instância global do AIAnalyzer"""
    global _ai_analyzer
    if _ai_analyzer is None:
        _ai_analyzer = AIAnalyzer()
    return _ai_analyzer


# Exportações principais
__all__ = [
    "AIAnalyzer",
    "AnalysisResult",
    "Entity",
    "SentimentScore",
    "AnalysisType",
    "get_ai_analyzer"
]
