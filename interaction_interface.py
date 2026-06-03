"""
Interaction Interface - Sistema de Interface de Interação
=====================================================
Chatbot, dashboard e feedback para interação com o sistema de IA
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
import uuid
from collections import defaultdict, deque

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
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False

try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

try:
    import dash
    from dash import dcc, html, Input, Output, State, callback_context
    import dash_bootstrap_components as dbc
    DASH_AVAILABLE = True
except ImportError:
    DASH_AVAILABLE = False

try:
    from flask import Flask, render_template, request, jsonify, session
    from flask_socketio import SocketIO, emit
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False

from config import settings
from core import get_logger, log_execution
from .model_architect import ModelInfo, ModelType, TaskType
from .model_trainer import TrainingResult
from .model_evaluator import EvaluationResult
from .deployment_manager import DeploymentResult
from .model_monitor import MonitoringMetrics, DriftAlert


class InteractionType(str, Enum):
    """Tipos de interação"""
    CHATBOT = "chatbot"
    DASHBOARD = "dashboard"
    WEB_INTERFACE = "web_interface"
    API_INTERFACE = "api_interface"
    COMMAND_LINE = "command_line"
    VOICE_INTERFACE = "voice_interface"
    CUSTOM = "custom"


class MessageType(str, Enum):
    """Tipos de mensagens"""
    USER_QUERY = "user_query"
    SYSTEM_RESPONSE = "system_response"
    ERROR_MESSAGE = "error_message"
    NOTIFICATION = "notification"
    FEEDBACK = "feedback"
    STATUS_UPDATE = "status_update"


class FeedbackType(str, Enum):
    """Tipos de feedback"""
    THUMBS_UP_DOWN = "thumbs_up_down"
    STAR_RATING = "star_rating"
    TEXT_FEEDBACK = "text_feedback"
    DETAILED_FEEDBACK = "detailed_feedback"
    CORRECTION = "correction"


@dataclass
class ChatMessage:
    """Mensagem do chat"""
    message_id: str
    user_id: str
    message_type: MessageType
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    response_to: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'message_id': self.message_id,
            'user_id': self.user_id,
            'message_type': self.message_type.value,
            'content': self.content,
            'timestamp': self.timestamp.isoformat(),
            'metadata': self.metadata,
            'response_to': self.response_to
        }


@dataclass
class UserFeedback:
    """Feedback do usuário"""
    feedback_id: str
    user_id: str
    interaction_id: str
    feedback_type: FeedbackType
    rating: Optional[Union[int, float]] = None
    comment: Optional[str] = None
    categories: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'feedback_id': self.feedback_id,
            'user_id': self.user_id,
            'interaction_id': self.interaction_id,
            'feedback_type': self.feedback_type.value,
            'rating': self.rating,
            'comment': self.comment,
            'categories': self.categories,
            'timestamp': self.timestamp.isoformat()
        }


@dataclass
class InterfaceConfig:
    """Configuração da interface"""
    interaction_type: InteractionType
    title: str = "VHALINOR AI System"
    theme: str = "default"
    language: str = "en"
    enable_chat: bool = True
    enable_dashboard: bool = True
    enable_feedback: bool = True
    enable_notifications: bool = True
    auto_save: bool = True
    session_timeout: int = 3600  # segundos
    max_message_history: int = 100
    custom_components: List[str] = field(default_factory=list)
    styling: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'interaction_type': self.interaction_type.value,
            'title': self.title,
            'theme': self.theme,
            'language': self.language,
            'enable_chat': self.enable_chat,
            'enable_dashboard': self.enable_dashboard,
            'enable_feedback': self.enable_feedback,
            'enable_notifications': self.enable_notifications,
            'auto_save': self.auto_save,
            'session_timeout': self.session_timeout,
            'max_message_history': self.max_message_history,
            'custom_components': self.custom_components,
            'styling': self.styling
        }


class ChatbotInterface:
    """Interface de chatbot"""
    
    def __init__(self):
        self.logger = get_logger("vhalinor.interface.chatbot", "chatbot_interface")
        self.conversations = defaultdict(lambda: deque(maxlen=100))
        self.user_sessions = {}
        self.response_handlers = []
    
    def create_session(self, user_id: str) -> str:
        """Cria sessão de chat"""
        session_id = str(uuid.uuid4())
        self.user_sessions[session_id] = {
            'user_id': user_id,
            'created_at': datetime.now(),
            'last_activity': datetime.now(),
            'message_count': 0
        }
        return session_id
    
    def send_message(self, session_id: str, content: str) -> ChatMessage:
        """Envia mensagem do usuário"""
        if session_id not in self.user_sessions:
            raise ValueError("Invalid session ID")
        
        session = self.user_sessions[session_id]
        user_id = session['user_id']
        
        message = ChatMessage(
            message_id=str(uuid.uuid4()),
            user_id=user_id,
            message_type=MessageType.USER_QUERY,
            content=content
        )
        
        self.conversations[session_id].append(message)
        session['last_activity'] = datetime.now()
        session['message_count'] += 1
        
        # Gerar resposta
        response = self._generate_response(message)
        self.conversations[session_id].append(response)
        
        return response
    
    def _generate_response(self, user_message: ChatMessage) -> ChatMessage:
        """Gera resposta do sistema"""
        # Simular processamento de IA
        time.sleep(0.5)
        
        # Respostas simples baseadas em padrões
        content_lower = user_message.content.lower()
        
        if "hello" in content_lower or "hi" in content_lower:
            response_content = "Hello! I'm VHALINOR AI. How can I help you today?"
        elif "how are you" in content_lower:
            response_content = "I'm functioning optimally and ready to assist you with AI tasks!"
        elif "model" in content_lower and "train" in content_lower:
            response_content = "I can help you train models using various algorithms. What type of model would you like to train?"
        elif "data" in content_lower and "collect" in content_lower:
            response_content = "I can assist with data collection from various sources including text, images, audio, and sensors."
        elif "deploy" in content_lower:
            response_content = "I support deployment through APIs, Docker containers, Kubernetes, and edge devices."
        elif "monitor" in content_lower:
            response_content = "I provide comprehensive model monitoring including drift detection and automatic retraining."
        elif "help" in content_lower:
            response_content = """I can help you with:
            - Data collection and preprocessing
            - Feature engineering and selection
            - Model training and evaluation
            - Hyperparameter optimization
            - Model deployment
            - Monitoring and maintenance
            What would you like to know more about?"""
        else:
            response_content = f"I understand you're asking about: '{user_message.content}'. I'm here to help with your AI pipeline needs. Could you provide more details about what you'd like to accomplish?"
        
        return ChatMessage(
            message_id=str(uuid.uuid4()),
            user_id="system",
            message_type=MessageType.SYSTEM_RESPONSE,
            content=response_content,
            response_to=user_message.message_id
        )
    
    def get_conversation(self, session_id: str, limit: int = 50) -> List[ChatMessage]:
        """Retorna conversa"""
        if session_id not in self.conversations:
            return []
        
        messages = list(self.conversations[session_id])
        return messages[-limit:]
    
    def add_response_handler(self, handler: Callable[[ChatMessage], str]):
        """Adiciona handler de respostas customizadas"""
        self.response_handlers.append(handler)


class DashboardInterface:
    """Interface de dashboard"""
    
    def __init__(self):
        self.logger = get_logger("vhalinor.interface.dashboard", "dashboard_interface")
        self.dashboard_data = {}
        self.widgets = {}
        self.refresh_interval = 30
    
    def create_dashboard(self, config: InterfaceConfig) -> Dict[str, Any]:
        """Cria estrutura do dashboard"""
        dashboard = {
            'title': config.title,
            'layout': self._create_layout(),
            'widgets': self._create_widgets(),
            'theme': config.theme,
            'auto_refresh': True,
            'refresh_interval': self.refresh_interval
        }
        
        self.dashboard_data[config.title] = dashboard
        return dashboard
    
    def _create_layout(self) -> Dict[str, Any]:
        """Cria layout do dashboard"""
        return {
            'header': {
                'title': 'VHALINOR AI System',
                'subtitle': 'Intelligent Pipeline Management',
                'actions': ['refresh', 'settings', 'export']
            },
            'sidebar': {
                'navigation': [
                    {'name': 'Overview', 'icon': 'dashboard'},
                    {'name': 'Models', 'icon': 'model'},
                    {'name': 'Data', 'icon': 'data'},
                    {'name': 'Training', 'icon': 'training'},
                    {'name': 'Deployment', 'icon': 'deployment'},
                    {'name': 'Monitoring', 'icon': 'monitor'}
                ]
            },
            'main': {
                'sections': [
                    {'id': 'overview', 'title': 'System Overview'},
                    {'id': 'models', 'title': 'Model Management'},
                    {'id': 'metrics', 'title': 'Performance Metrics'},
                    {'id': 'alerts', 'title': 'Alerts & Notifications'}
                ]
            }
        }
    
    def _create_widgets(self) -> Dict[str, Any]:
        """Cria widgets do dashboard"""
        return {
            'system_stats': {
                'type': 'metric_cards',
                'metrics': [
                    {'name': 'Active Models', 'value': 0, 'unit': 'models'},
                    {'name': 'Total Predictions', 'value': 0, 'unit': 'predictions'},
                    {'name': 'System Uptime', 'value': '0h 0m', 'unit': 'time'},
                    {'name': 'Success Rate', 'value': 0, 'unit': '%'}
                ]
            },
            'model_performance': {
                'type': 'line_chart',
                'title': 'Model Performance Over Time',
                'data': []
            },
            'drift_alerts': {
                'type': 'alert_table',
                'title': 'Recent Drift Alerts',
                'columns': ['Model', 'Type', 'Severity', 'Time'],
                'data': []
            },
            'training_progress': {
                'type': 'progress_bar',
                'title': 'Active Training Jobs',
                'jobs': []
            }
        }
    
    def update_widget_data(self, widget_id: str, data: Any):
        """Atualiza dados do widget"""
        if widget_id in self.widgets:
            self.widgets[widget_id]['data'] = data
    
    def get_dashboard_data(self, dashboard_name: str) -> Optional[Dict[str, Any]]:
        """Retorna dados do dashboard"""
        return self.dashboard_data.get(dashboard_name)


class WebInterface:
    """Interface web completa"""
    
    def __init__(self):
        self.logger = get_logger("vhalinor.interface.web", "web_interface")
        self.app = None
        self.socketio = None
        self.routes = {}
        self.templates = {}
    
    def create_flask_app(self, config: InterfaceConfig) -> Flask:
        """Cria aplicação Flask"""
        if not FLASK_AVAILABLE:
            raise ImportError("Flask is required for web interface")
        
        app = Flask(__name__)
        app.config['SECRET_KEY'] = 'vhalinor-secret-key'
        
        # Configurar SocketIO
        self.socketio = SocketIO(app, cors_allowed_origins="*")
        
        # Rotas principais
        @app.route('/')
        def index():
            return render_template('index.html', title=config.title)
        
        @app.route('/dashboard')
        def dashboard():
            return render_template('dashboard.html', title=f"{config.title} - Dashboard")
        
        @app.route('/chat')
        def chat():
            return render_template('chat.html', title=f"{config.title} - Chat")
        
        # API endpoints
        @app.route('/api/models')
        def get_models():
            return jsonify({'models': []})  # Implementar com dados reais
        
        @app.route('/api/metrics')
        def get_metrics():
            return jsonify({'metrics': {}})  # Implementar com dados reais
        
        # WebSocket events
        @self.socketio.on('connect')
        def handle_connect():
            emit('status', {'message': 'Connected to VHALINOR AI System'})
        
        @self.socketio.on('chat_message')
        def handle_chat_message(data):
            # Processar mensagem e retornar resposta
            response = self._process_chat_message(data)
            emit('chat_response', response)
        
        self.app = app
        return app
    
    def _process_chat_message(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Processa mensagem do chat"""
        # Implementar lógica de processamento
        return {
            'response': 'This is a placeholder response',
            'timestamp': datetime.now().isoformat()
        }
    
    def run(self, host: str = 'localhost', port: int = 5000, debug: bool = False):
        """Inicia servidor web"""
        if self.app and self.socketio:
            self.socketio.run(self.app, host=host, port=port, debug=debug)


class StreamlitInterface:
    """Interface Streamlit"""
    
    def __init__(self):
        self.logger = get_logger("vhalinor.interface.streamlit", "streamlit_interface")
        self.page_config = {
            'page_title': 'VHALINOR AI System',
            'page_icon': ':robot:',
            'layout': 'wide',
            'initial_sidebar_state': 'expanded'
        }
    
    def create_app(self) -> None:
        """Cria aplicação Streamlit"""
        if not STREAMLIT_AVAILABLE:
            raise ImportError("Streamlit is required for Streamlit interface")
        
        # Configurar página
        st.set_page_config(**self.page_config)
        
        # Sidebar
        self._render_sidebar()
        
        # Main content based on selection
        page = st.sidebar.selectbox(
            'Select Page',
            ['Overview', 'Models', 'Data Pipeline', 'Training', 'Deployment', 'Monitoring', 'Chat']
        )
        
        if page == 'Overview':
            self._render_overview()
        elif page == 'Models':
            self._render_models()
        elif page == 'Data Pipeline':
            self._render_data_pipeline()
        elif page == 'Training':
            self._render_training()
        elif page == 'Deployment':
            self._render_deployment()
        elif page == 'Monitoring':
            self._render_monitoring()
        elif page == 'Chat':
            self._render_chat()
    
    def _render_sidebar(self):
        """Renderiza sidebar"""
        st.sidebar.title('VHALINOR AI')
        st.sidebar.image('https://via.placeholder.com/300x100?text=VHALINOR+AI', use_column_width=True)
        
        # System status
        st.sidebar.subheader('System Status')
        status_color = 'green' if True else 'red'  # Simular status
        st.sidebar.markdown(f"**:green[{status_color}]** System Operational")
        
        # Quick stats
        st.sidebar.subheader('Quick Stats')
        st.sidebar.metric('Active Models', '5')
        st.sidebar.metric('Total Predictions', '1.2M')
        st.sidebar.metric('Success Rate', '98.5%')
    
    def _render_overview(self):
        """Renderiza página de overview"""
        st.title('System Overview')
        
        # Metrics cards
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric('Active Models', '5', '+2')
        
        with col2:
            st.metric('Predictions Today', '12,543', '+15%')
        
        with col3:
            st.metric('Success Rate', '98.5%', '+0.3%')
        
        with col4:
            st.metric('System Uptime', '7d 14h 32m')
        
        # Charts
        st.subheader('Performance Trends')
        if PLOTLY_AVAILABLE:
            # Simular gráfico de performance
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=list(range(24)),
                y=[0.95 + 0.02 * np.sin(i/2) for i in range(24)],
                mode='lines',
                name='Accuracy'
            ))
            fig.update_layout(title='Model Accuracy (Last 24 Hours)')
            st.plotly_chart(fig, use_container_width=True)
        
        # Recent activity
        st.subheader('Recent Activity')
        activity_data = [
            {'Time': '10:30', 'Activity': 'Model trained', 'Status': 'Success'},
            {'Time': '09:45', 'Activity': 'Data collected', 'Status': 'Success'},
            {'Time': '08:15', 'Activity': 'Deployment updated', 'Status': 'Success'},
        ]
        
        df_activity = pd.DataFrame(activity_data) if PANDAS_AVAILABLE else activity_data
        st.dataframe(df_activity)
    
    def _render_models(self):
        """Renderiza página de modelos"""
        st.title('Model Management')
        
        # Model list
        st.subheader('Active Models')
        
        models_data = [
            {'Name': 'Classification Model v1.2', 'Type': 'Random Forest', 'Accuracy': '95.2%', 'Status': 'Active'},
            {'Name': 'Regression Model v2.1', 'Type': 'Neural Network', 'RMSE': '0.123', 'Status': 'Active'},
            {'Name': 'NLP Model v1.0', 'Type': 'Transformer', 'F1-Score': '0.89', 'Status': 'Training'},
        ]
        
        df_models = pd.DataFrame(models_data) if PANDAS_AVAILABLE else models_data
        st.dataframe(df_models, use_container_width=True)
        
        # Model actions
        st.subheader('Model Actions')
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button('Train New Model', use_container_width=True):
                st.info('Model training initiated')
        
        with col2:
            if st.button('Deploy Model', use_container_width=True):
                st.info('Deployment wizard opened')
        
        with col3:
            if st.button('Evaluate Model', use_container_width=True):
                st.info('Model evaluation started')
    
    def _render_data_pipeline(self):
        """Renderiza página de pipeline de dados"""
        st.title('Data Pipeline')
        
        # Pipeline stages
        st.subheader('Pipeline Stages')
        
        stages = [
            {'Stage': 'Data Collection', 'Status': 'Active', 'Records': '1.2M'},
            {'Stage': 'Preprocessing', 'Status': 'Active', 'Records': '1.1M'},
            {'Stage': 'Feature Engineering', 'Status': 'Active', 'Features': '256'},
            {'Stage': 'Storage', 'Status': 'Active', 'Size': '2.3GB'},
        ]
        
        df_stages = pd.DataFrame(stages) if PANDAS_AVAILABLE else stages
        st.dataframe(df_stages, use_container_width=True)
    
    def _render_training(self):
        """Renderiza página de treinamento"""
        st.title('Model Training')
        
        # Active training jobs
        st.subheader('Active Training Jobs')
        
        jobs_data = [
            {'Model': 'NLP Model v1.0', 'Progress': 75, 'ETA': '15 min', 'Loss': '0.123'},
            {'Model': 'CNN Model v3.2', 'Progress': 45, 'ETA': '32 min', 'Loss': '0.089'},
        ]
        
        df_jobs = pd.DataFrame(jobs_data) if PANDAS_AVAILABLE else jobs_data
        
        for _, job in df_jobs.iterrows() if PANDAS_AVAILABLE else jobs_data:
            with st.expander(f"Training: {job['Model']}"):
                st.progress(job['Progress'] / 100)
                st.write(f"ETA: {job['ETA']}")
                st.write(f"Current Loss: {job['Loss']}")
    
    def _render_deployment(self):
        """Renderiza página de deployment"""
        st.title('Model Deployment')
        
        # Active deployments
        st.subheader('Active Deployments')
        
        deployments_data = [
            {'Model': 'Classification API', 'Type': 'REST API', 'Status': 'Running', 'Requests': '1.2K/hour'},
            {'Model': 'Edge Model', 'Type': 'Edge Device', 'Status': 'Running', 'Latency': '12ms'},
        ]
        
        df_deployments = pd.DataFrame(deployments_data) if PANDAS_AVAILABLE else deployments_data
        st.dataframe(df_deployments, use_container_width=True)
    
    def _render_monitoring(self):
        """Renderiza página de monitoramento"""
        st.title('Model Monitoring')
        
        # Drift alerts
        st.subheader('Drift Alerts')
        
        alerts_data = [
            {'Model': 'Classification Model', 'Type': 'Data Drift', 'Severity': 'Medium', 'Time': '2 hours ago'},
            {'Model': 'Regression Model', 'Type': 'Performance Drift', 'Severity': 'Low', 'Time': '5 hours ago'},
        ]
        
        df_alerts = pd.DataFrame(alerts_data) if PANDAS_AVAILABLE else alerts_data
        st.dataframe(df_alerts, use_container_width=True)
        
        # Performance metrics
        st.subheader('Performance Metrics')
        if PLOTLY_AVAILABLE:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=list(range(48)),
                y=[0.92 + 0.05 * np.random.random() for _ in range(48)],
                mode='lines',
                name='Model Accuracy'
            ))
            fig.update_layout(title='Model Performance (Last 48 Hours)')
            st.plotly_chart(fig, use_container_width=True)
    
    def _render_chat(self):
        """Renderiza página de chat"""
        st.title('AI Assistant Chat')
        
        # Chat interface
        if 'chat_messages' not in st.session_state:
            st.session_state.chat_messages = []
        
        # Display chat messages
        for message in st.session_state.chat_messages:
            if message['role'] == 'user':
                st.chat_message("user").write(message['content'])
            else:
                st.chat_message("assistant").write(message['content'])
        
        # Chat input
        user_input = st.chat_input("Ask me anything about the AI system...")
        
        if user_input:
            # Add user message
            st.session_state.chat_messages.append({'role': 'user', 'content': user_input})
            st.chat_message("user").write(user_input)
            
            # Generate response
            response = self._generate_chat_response(user_input)
            st.session_state.chat_messages.append({'role': 'assistant', 'content': response})
            st.chat_message("assistant").write(response)
    
    def _generate_chat_response(self, user_input: str) -> str:
        """Gera resposta do chat"""
        # Simular respostas inteligentes
        input_lower = user_input.lower()
        
        if "model" in input_lower and "performance" in input_lower:
            return "Based on current metrics, your models are performing well with an average accuracy of 95.2%. The classification model shows the best performance at 97.8% accuracy."
        elif "drift" in input_lower:
            return "I've detected 2 drift alerts in the last 24 hours. One medium-severity data drift in the classification model and one low-severity performance drift in the regression model. Both are within acceptable thresholds."
        elif "deploy" in input_lower:
            return "You have 2 active deployments: a REST API for the classification model handling 1.2K requests per hour, and an edge deployment with 12ms latency. Both are running smoothly."
        elif "train" in input_lower:
            return "Currently 2 models are training: NLP Model v1.0 (75% complete, ETA 15 min) and CNN Model v3.2 (45% complete, ETA 32 min). Both are progressing normally."
        else:
            return f"I understand you're asking about: '{user_input}'. I'm here to help you manage your AI pipeline. You can ask me about model performance, drift detection, deployments, training progress, or any other aspect of the system."


class FeedbackManager:
    """Gerenciador de feedback"""
    
    def __init__(self):
        self.logger = get_logger("vhalinor.interface.feedback", "feedback_manager")
        self.feedback_data = defaultdict(list)
        self.feedback_analytics = {}
    
    def submit_feedback(self, user_id: str, interaction_id: str, feedback_type: FeedbackType, 
                      rating: Optional[Union[int, float]] = None, comment: Optional[str] = None,
                      categories: List[str] = None) -> str:
        """Submete feedback"""
        feedback_id = str(uuid.uuid4())
        
        feedback = UserFeedback(
            feedback_id=feedback_id,
            user_id=user_id,
            interaction_id=interaction_id,
            feedback_type=feedback_type,
            rating=rating,
            comment=comment,
            categories=categories or []
        )
        
        self.feedback_data[feedback_type].append(feedback)
        
        self.logger.info(f"Feedback submitted: {feedback_id} - {feedback_type.value}")
        return feedback_id
    
    def get_feedback_analytics(self, feedback_type: FeedbackType = None, days: int = 30) -> Dict[str, Any]:
        """Retorna analytics de feedback"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        if feedback_type:
            feedback_list = [f for f in self.feedback_data[feedback_type] if f.timestamp >= cutoff_date]
        else:
            feedback_list = []
            for fb_list in self.feedback_data.values():
                feedback_list.extend([f for f in fb_list if f.timestamp >= cutoff_date])
        
        if not feedback_list:
            return {'total_feedback': 0}
        
        # Calcular estatísticas
        ratings = [f.rating for f in feedback_list if f.rating is not None]
        avg_rating = sum(ratings) / len(ratings) if ratings else None
        
        # Categorização
        category_counts = defaultdict(int)
        for f in feedback_list:
            for category in f.categories:
                category_counts[category] += 1
        
        return {
            'total_feedback': len(feedback_list),
            'average_rating': avg_rating,
            'rating_distribution': self._get_rating_distribution(ratings),
            'category_counts': dict(category_counts),
            'feedback_by_type': {ft.value: len(self.feedback_data[ft]) for ft in FeedbackType}
        }
    
    def _get_rating_distribution(self, ratings: List[Union[int, float]]) -> Dict[str, int]:
        """Calcula distribuição de ratings"""
        if not ratings:
            return {}
        
        distribution = defaultdict(int)
        for rating in ratings:
            if isinstance(rating, (int, float)):
                if rating <= 1:
                    distribution['1_star'] += 1
                elif rating <= 2:
                    distribution['2_star'] += 1
                elif rating <= 3:
                    distribution['3_star'] += 1
                elif rating <= 4:
                    distribution['4_star'] += 1
                else:
                    distribution['5_star'] += 1
        
        return dict(distribution)


class InteractionManager:
    """Gerenciador principal de interação"""
    
    def __init__(self):
        self.logger = get_logger("vhalinor.interface.main", "interaction_manager")
        
        # Inicializar interfaces
        self.chatbot = ChatbotInterface()
        self.dashboard = DashboardInterface()
        self.web_interface = WebInterface()
        self.streamlit_interface = StreamlitInterface()
        self.feedback_manager = FeedbackManager()
        
        self.active_interfaces = {}
        self.interface_configs = {}
    
    @log_execution(component="interface", operation="create_interface")
    async def create_interface(self, config: InterfaceConfig) -> Dict[str, Any]:
        """Cria interface baseada na configuração"""
        self.logger.info(f"Creating {config.interaction_type.value} interface")
        
        try:
            if config.interaction_type == InteractionType.CHATBOT:
                interface_data = {'type': 'chatbot', 'session_handler': self.chatbot}
            
            elif config.interaction_type == InteractionType.DASHBOARD:
                interface_data = self.dashboard.create_dashboard(config)
            
            elif config.interaction_type == InteractionType.WEB_INTERFACE:
                app = self.web_interface.create_flask_app(config)
                interface_data = {'type': 'web', 'app': app, 'socketio': self.web_interface.socketio}
            
            elif config.interaction_type == InteractionType.STREAMLIT:
                # Streamlit é executado diretamente, não retorna objeto
                interface_data = {'type': 'streamlit', 'config': config}
            
            else:
                raise ValueError(f"Unsupported interface type: {config.interaction_type}")
            
            # Armazenar interface
            interface_id = f"{config.interaction_type.value}_{int(time.time())}"
            self.active_interfaces[interface_id] = interface_data
            self.interface_configs[interface_id] = config
            
            self.logger.info(f"Interface created: {interface_id}")
            return {'interface_id': interface_id, 'data': interface_data}
        
        except Exception as e:
            self.logger.error(f"Error creating interface: {e}")
            raise
    
    def get_interface(self, interface_id: str) -> Optional[Dict[str, Any]]:
        """Retorna interface específica"""
        return self.active_interfaces.get(interface_id)
    
    def submit_feedback(self, interface_id: str, user_id: str, feedback_type: FeedbackType,
                       rating: Optional[Union[int, float]] = None, comment: Optional[str] = None,
                       categories: List[str] = None) -> str:
        """Submete feedback para interface"""
        feedback_id = self.feedback_manager.submit_feedback(
            user_id=user_id,
            interaction_id=interface_id,
            feedback_type=feedback_type,
            rating=rating,
            comment=comment,
            categories=categories
        )
        
        return feedback_id
    
    def get_interface_analytics(self, interface_id: str = None) -> Dict[str, Any]:
        """Retorna analytics das interfaces"""
        analytics = {
            'active_interfaces': len(self.active_interfaces),
            'interface_types': {},
            'feedback_analytics': self.feedback_manager.get_feedback_analytics(),
            'chatbot_sessions': len(self.chatbot.user_sessions),
            'dashboard_widgets': len(self.dashboard.widgets)
        }
        
        # Contar por tipo
        for interface_data in self.active_interfaces.values():
            interface_type = interface_data.get('type', 'unknown')
            analytics['interface_types'][interface_type] = analytics['interface_types'].get(interface_type, 0) + 1
        
        return analytics
    
    def create_standard_config(self, interaction_type: InteractionType) -> InterfaceConfig:
        """Cria configuração padrão de interface"""
        return InterfaceConfig(
            interaction_type=interaction_type,
            title="VHALINOR AI System",
            theme="default",
            language="en",
            enable_chat=True,
            enable_dashboard=True,
            enable_feedback=True,
            enable_notifications=True
        )
    
    def get_interface_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas das interfaces"""
        return {
            'total_interfaces': len(self.active_interfaces),
            'available_types': [itype.value for itype in InteractionType],
            'message_types': [mtype.value for mtype in MessageType],
            'feedback_types': [ftype.value for ftype in FeedbackType],
            'chatbot_sessions': len(self.chatbot.user_sessions),
            'feedback_submissions': sum(len(feedbacks) for feedbacks in self.feedback_manager.feedback_data.values())
        }


# Função de conveniência
_interface_manager_instance = None

def get_interaction_manager() -> InteractionManager:
    """Obtém instância singleton do gerenciador de interação"""
    global _interface_manager_instance
    if _interface_manager_instance is None:
        _interface_manager_instance = InteractionManager()
    return _interface_manager_instance
