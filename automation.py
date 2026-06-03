"""
Módulo de Automação Inteligente
=================================
Implementação robusta com Selenium, PyAutoGUI e retry
"""

import asyncio
import time
import os
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import json
import threading
import queue
from pathlib import Path
from contextlib import contextmanager
import functools
import random

# Importações condicionais
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    from selenium.common.exceptions import WebDriverException, TimeoutException
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

try:
    import pyautogui
    import pyautogui.exceptions
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False

try:
    import win32gui
    import win32con
    import win32api
    import win32process
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

from config import settings
from core import get_logger, log_execution

# Conditional import for tenacity
try:
    from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
    TENACITY_AVAILABLE = True
except ImportError:
    TENACITY_AVAILABLE = False

    # Fallback retry decorator
    def retry(*args, **kwargs):
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*inner_args, **inner_kwargs):
                max_attempts = kwargs.get('stop', stop_after_attempt(3)).maximum
                for attempt in range(max_attempts):
                    try:
                        return func(*inner_args, **inner_kwargs)
                    except Exception:
                        if attempt == max_attempts - 1:
                            raise
                        time.sleep(2 ** attempt)  # Exponential backoff
                return None
            return wrapper
        return decorator


class AutomationType(str, Enum):
    """Tipos de automação disponíveis"""
    WEB_SCRAPING = "web_scraping"
    DESKTOP = "desktop"
    FILE_OPERATIONS = "file_operations"
    SYSTEM_OPERATIONS = "system_operations"
    SCHEDULED = "scheduled"


class TaskStatus(str, Enum):
    """Status das tarefas de automação"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"


class Priority(str, Enum):
    """Prioridades das tarefas"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class AutomationTask:
    """Tarefa de automação"""
    id: str
    name: str
    type: AutomationType
    status: TaskStatus
    priority: Priority
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    timeout: int = 30
    parameters: Dict[str, Any] = None
    result: Optional[Any] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        data = asdict(self)
        for field_name, field_value in data.items():
            if isinstance(field_value, datetime):
                data[field_name] = field_value.isoformat()
        return data


@dataclass
class AutomationResult:
    """Resultado de tarefa de automação"""
    task_id: str
    success: bool
    result: Optional[Any] = None
    error_message: Optional[str] = None
    execution_time: float = 0.0
    screenshots_taken: List[str] = None
    logs: List[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        data = asdict(self)
        return data


class WebAutomation:
    """Automação web com Selenium - Robusta e com retry"""
    
    def __init__(self):
        self.logger = get_logger("vhalinor.automation", "automation")
        self.driver: Optional[Any] = None
        self.is_headless = getattr(settings, 'selenium_headless', True)
        self.driver_path = getattr(settings, 'selenium_driver_path', None)
        self.timeout = getattr(settings, 'selenium_timeout', 30)
        self.implicit_wait = getattr(settings, 'selenium_implicit_wait', 10)
        self.screenshot_dir = Path("logs/screenshots")
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)
        
    @contextmanager
    def driver_context(self):
        """Context manager para WebDriver com cleanup automático"""
        driver = None
        try:
            driver = self._create_driver()
            yield driver
        finally:
            if driver:
                try:
                    driver.quit()
                except Exception:
                    pass
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((WebDriverException, TimeoutException))
    )
    def _create_driver(self):
        """Cria WebDriver com configurações robustas"""
        if not SELENIUM_AVAILABLE:
            raise ImportError("Selenium not available")
        
        chrome_options = ChromeOptions()
        
        # Configurações de headless
        if self.is_headless:
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-plugins")
            chrome_options.add_argument("--disable-images")
        
        # Configurações de estabilidade
        chrome_options.add_argument("--disable-background-timer-throttling")
        chrome_options.add_argument("--disable-backgrounding-occluded-windows")
        chrome_options.add_argument("--disable-renderer-backgrounding")
        chrome_options.add_argument("--disable-features=TranslateUI")
        chrome_options.add_argument("--disable-ipc-flooding-protection")
        chrome_options.add_argument("--window-size=1920,1080")
        
        # Performance settings
        chrome_options.add_argument("--max_old_space_size=4096")
        
        # Create driver
        if self.driver_path and os.path.exists(self.driver_path):
            driver = webdriver.Chrome(
                executable_path=self.driver_path,
                options=chrome_options
            )
        else:
            driver = webdriver.Chrome(options=chrome_options)
        
        # Configure timeouts
        driver.set_page_load_timeout(self.timeout)
        driver.implicitly_wait(self.implicit_wait)
        
        return driver
    
    @log_execution(
        component="automation",
        operation="init_webdriver",
        log_exceptions=True
    )
    async def init_webdriver(self) -> bool:
        """Inicializa WebDriver com retry automático"""
        try:
            self.driver = self._create_driver()
            self.logger.info("WebDriver initialized successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize WebDriver: {e}")
            return False
    
    @log_execution(
        component="automation",
        operation="navigate_to_url",
        log_args=True,
        log_result=True
    )
    async def navigate_to_url(
        self,
        url: str,
        wait_for_element: Optional[str] = None,
        timeout: int = 10
    ) -> bool:
        """
        Navega para URL e espera elemento
        
        Args:
            url: URL para navegar
            wait_for_element: Seletor CSS para esperar
            timeout: Timeout em segundos
        
        Returns:
            True se navegação bem-sucedida
        """
        try:
            if not self.driver:
                await self.init_webdriver()
            
            # Navegar para URL
            self.driver.get(url)
            
            # Esperar elemento específico se solicitado
            if wait_for_element:
                WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, wait_for_element))
                )
            
            self.logger.info(f"Navigated to: {url}")
            return True
            
        except TimeoutException:
            self.logger.error(f"Timeout waiting for element: {wait_for_element}")
            return False
        except WebDriverException as e:
            self.logger.error(f"Navigation error: {e}")
            return False
    
    @log_execution(
        component="automation",
        operation="take_screenshot",
        log_args=True,
        log_result=True
    )
    async def take_screenshot(self, filename: Optional[str] = None) -> Optional[str]:
        """
        Tira screenshot da página atual
        
        Args:
            filename: Nome do arquivo (opcional)
        
        Returns:
            Caminho do screenshot ou None
        """
        try:
            if not self.driver:
                return None
            
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"screenshot_{timestamp}.png"
            
            # Criar diretório se não existir
            screenshot_dir = Path("screenshots")
            screenshot_dir.mkdir(exist_ok=True)
            
            # Tirar screenshot
            screenshot_path = screenshot_dir / filename
            self.driver.save_screenshot(str(screenshot_path))
            
            self.logger.info(f"Screenshot saved: {screenshot_path}")
            return str(screenshot_path)
            
        except Exception as e:
            self.logger.error(f"Screenshot error: {e}")
            return None
    
    @log_execution(
        component="automation",
        operation="extract_text",
        log_args=True,
        log_result=True
    )
    async def extract_text(
        self,
        selector: str,
        attribute: str = "text"
    ) -> Optional[str]:
        """
        Extrai texto de elemento
        
        Args:
            selector: Seletor CSS/XPath
            attribute: Atributo para extrair
        
        Returns:
            Texto extraído ou None
        """
        try:
            if not self.driver:
                return None
            
            # Encontrar elemento
            element = self.driver.find_element(By.CSS_SELECTOR, selector)
            
            # Extrair atributo
            text = getattr(element, attribute, None)
            
            if text:
                self.logger.info(f"Text extracted: {text[:100]}...")
                return text.strip()
            
            return None
            
        except Exception as e:
            self.logger.error(f"Text extraction error: {e}")
            return None
    
    @log_execution(
        component="automation",
        operation="click_element",
        log_args=True,
        log_result=True
    )
    async def click_element(
        self,
        selector: str,
        wait_time: float = 1.0
    ) -> bool:
        """
        Clica em elemento
        
        Args:
            selector: Seletor CSS/XPath
            wait_time: Tempo de espera antes do clique
        
        Returns:
            True se clique bem-sucedido
        """
        try:
            if not self.driver:
                return False
            
            # Esperar um pouco
            await asyncio.sleep(wait_time)
            
            # Encontrar e clicar
            element = self.driver.find_element(By.CSS_SELECTOR, selector)
            element.click()
            
            self.logger.info(f"Clicked element: {selector}")
            return True
            
        except Exception as e:
            self.logger.error(f"Click error: {e}")
            return False
    
    def close_webdriver(self):
        """Fecha WebDriver"""
        if self.driver:
            try:
                self.driver.quit()
                self.logger.info("WebDriver closed")
            except Exception as e:
                self.logger.error(f"Error closing WebDriver: {e}")
            finally:
                self.driver = None


class DesktopAutomation:
    """Automação desktop com PyAutoGUI"""
    
    def __init__(self):
        self.logger = get_logger().get_logger("vhalinor.automation", "automation")
        self.fail_safe = settings.pyautogui_fail_safe
        
        # Configurar PyAutoGUI
        if PYAUTOGUI_AVAILABLE:
            pyautogui.FAILSAFE = self.fail_safe
            pyautogui.PAUSE = 0.1
    
    @log_execution(
        component="automation",
        operation="get_screen_size",
        log_result=True
    )
    def get_screen_size(self) -> tuple:
        """Obtém tamanho da tela"""
        try:
            if PYAUTOGUI_AVAILABLE:
                width, height = pyautogui.size()
                self.logger.info(f"Screen size: {width}x{height}")
                return (width, height)
            return (0, 0)
        except Exception as e:
            self.logger.error(f"Error getting screen size: {e}")
            return (0, 0)
    
    @log_execution(
        component="automation",
        operation="take_screenshot",
        log_args=True,
        log_result=True
    )
    def take_screenshot(self, filename: Optional[str] = None) -> Optional[str]:
        """
        Tira screenshot da tela
        
        Args:
            filename: Nome do arquivo (opcional)
        
        Returns:
            Caminho do screenshot ou None
        """
        try:
            if not PYAUTOGUI_AVAILABLE:
                return None
            
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"desktop_screenshot_{timestamp}.png"
            
            # Criar diretório
            screenshot_dir = Path("screenshots")
            screenshot_dir.mkdir(exist_ok=True)
            
            # Tirar screenshot
            screenshot_path = screenshot_dir / filename
            pyautogui.screenshot(str(screenshot_path))
            
            self.logger.info(f"Desktop screenshot saved: {screenshot_path}")
            return str(screenshot_path)
            
        except Exception as e:
            self.logger.error(f"Desktop screenshot error: {e}")
            return None
    
    @log_execution(
        component="automation",
        operation="type_text",
        log_args=True,
        log_result=True
    )
    async def type_text(
        self,
        text: str,
        interval: float = 0.05
    ) -> bool:
        """
        Digita texto
        
        Args:
            text: Texto para digitar
            interval: Intervalo entre caracteres
        
        Returns:
            True se digitação bem-sucedida
        """
        try:
            if not PYAUTOGUI_AVAILABLE:
                return False
            
            pyautogui.write(text, interval=interval)
            self.logger.info(f"Typed text: {text[:50]}...")
            return True
            
        except Exception as e:
            self.logger.error(f"Text typing error: {e}")
            return False
    
    @log_execution(
        component="automation",
        operation="click_position",
        log_args=True,
        log_result=True
    )
    async def click_position(self, x: int, y: int) -> bool:
        """
        Clica em posição específica
        
        Args:
            x: Coordenada X
            y: Coordenada Y
        
        Returns:
            True se clique bem-sucedido
        """
        try:
            if not PYAUTOGUI_AVAILABLE:
                return False
            
            pyautogui.click(x, y)
            self.logger.info(f"Clicked position: ({x}, {y})")
            return True
            
        except Exception as e:
            self.logger.error(f"Position click error: {e}")
            return False
    
    @log_execution(
        component="automation",
        operation="find_image_on_screen",
        log_args=True,
        log_result=True
    )
    def find_image_on_screen(
        self,
        image_path: str,
        confidence: float = 0.8
    ) -> Optional[tuple]:
        """
        Encontra imagem na tela
        
        Args:
            image_path: Caminho da imagem
            confidence: Confiança da busca
        
        Returns:
            Coordenadas da imagem ou None
        """
        try:
            if not PYAUTOGUI_AVAILABLE:
                return None
            
            location = pyautogui.locateOnScreen(image_path, confidence=confidence)
            
            if location:
                center = pyautogui.center(location)
                self.logger.info(f"Image found at: ({center.x}, {center.y})")
                return (center.x, center.y)
            
            return None
            
        except Exception as e:
            self.logger.error(f"Image finding error: {e}")
            return None


class AutomationManager:
    """
    Gerenciador de automação com retry e timeout
    """
    
    def __init__(self):
        self.logger = get_logger().get_logger("vhalinor.automation_manager", "automation_manager")
        
        # Componentes de automação
        self.web_automation = WebAutomation()
        self.desktop_automation = DesktopAutomation()
        
        # Fila de tarefas
        self.task_queue = asyncio.Queue()
        self.running_tasks: Dict[str, AutomationTask] = {}
        
        # Thread de execução
        self.execution_thread = None
        self.is_running = False
        
        # Callbacks
        self.callbacks: Dict[str, List[Callable]] = {
            "task_started": [],
            "task_completed": [],
            "task_failed": [],
            "task_retry": []
        }
        
        # Estatísticas
        self.stats = {
            "total_tasks": 0,
            "completed_tasks": 0,
            "failed_tasks": 0,
            "retry_count": 0
        }
    
    def add_callback(self, event_type: str, callback: Callable):
        """Adiciona callback para eventos"""
        if event_type in self.callbacks:
            self.callbacks[event_type].append(callback)
    
    async def _execute_callbacks(self, event_type: str, task: AutomationTask):
        """Executa callbacks de evento"""
        for callback in self.callbacks.get(event_type, []):
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(task)
                else:
                    callback(task)
            except Exception as e:
                self.logger.error(f"Callback error for {event_type}: {e}")
    
    @log_execution(
        component="automation_manager",
        operation="add_task",
        log_args=True,
        log_result=True
    )
    async def add_task(
        self,
        name: str,
        automation_type: AutomationType,
        parameters: Dict[str, Any] = None,
        priority: Priority = Priority.MEDIUM,
        timeout: int = 30,
        max_retries: int = 3
    ) -> str:
        """
        Adiciona tarefa à fila
        
        Args:
            name: Nome da tarefa
            automation_type: Tipo de automação
            parameters: Parâmetros da tarefa
            priority: Prioridade
            timeout: Timeout em segundos
            max_retries: Número máximo de retentativas
        
        Returns:
            ID da tarefa criada
        """
        task = AutomationTask(
            id=f"task_{datetime.now().timestamp()}_{name}",
            name=name,
            type=automation_type,
            status=TaskStatus.PENDING,
            priority=priority,
            created_at=datetime.now(),
            parameters=parameters or {},
            timeout=timeout,
            max_retries=max_retries
        )
        
        await self.task_queue.put(task)
        self.stats["total_tasks"] += 1
        
        self.logger.info(f"Task added: {name} ({task.id})")
        return task.id
    
    @log_execution(
        component="automation_manager",
        operation="execute_task",
        log_args=True,
        log_result=True
    )
    async def execute_task(self, task: AutomationTask) -> AutomationResult:
        """
        Executa tarefa específica
        
        Args:
            task: Tarefa para executar
        
        Returns:
            Resultado da execução
        """
        start_time = time.time()
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.now()
        
        await self._execute_callbacks("task_started", task)
        
        try:
            # Executar baseado no tipo
            if task.type == AutomationType.WEB_SCRAPING:
                result = await self._execute_web_task(task)
            elif task.type == AutomationType.DESKTOP:
                result = await self._execute_desktop_task(task)
            elif task.type == AutomationType.FILE_OPERATIONS:
                result = await self._execute_file_task(task)
            else:
                result = AutomationResult(
                    task_id=task.id,
                    success=False,
                    error_message=f"Unsupported automation type: {task.type}",
                    execution_time=time.time() - start_time
                )
            
            # Atualizar status
            task.status = TaskStatus.COMPLETED if result.success else TaskStatus.FAILED
            task.completed_at = datetime.now()
            task.result = result.result
            task.error_message = result.error_message
            
            # Atualizar estatísticas
            if result.success:
                self.stats["completed_tasks"] += 1
            else:
                self.stats["failed_tasks"] += 1
            
            await self._execute_callbacks("task_completed", task)
            
            return result
            
        except Exception as e:
            # Tratar erro
            task.status = TaskStatus.FAILED
            task.completed_at = datetime.now()
            task.error_message = str(e)
            task.retry_count += 1
            
            self.stats["failed_tasks"] += 1
            self.stats["retry_count"] += 1
            
            await self._execute_callbacks("task_failed", task)
            
            return AutomationResult(
                task_id=task.id,
                success=False,
                error_message=str(e),
                execution_time=time.time() - start_time
            )
    
    async def _execute_web_task(self, task: AutomationTask) -> AutomationResult:
        """Executa tarefa web"""
        try:
            params = task.parameters
            
            if "url" in params:
                # Navegar para URL
                success = await self.web_automation.navigate_to_url(
                    params["url"],
                    params.get("wait_for_element"),
                    task.timeout
                )
                
                if not success:
                    return AutomationResult(
                        task_id=task.id,
                        success=False,
                        error_message="Failed to navigate to URL"
                    )
                
                # Tirar screenshot se solicitado
                screenshots = []
                if params.get("take_screenshot", False):
                    screenshot_path = await self.web_automation.take_screenshot()
                    if screenshot_path:
                        screenshots.append(screenshot_path)
                
                # Extrair texto se solicitado
                text_result = None
                if "extract_text" in params:
                    text_result = await self.web_automation.extract_text(
                        params["extract_text"]
                    )
                
                # Clicar em elemento se solicitado
                if "click_element" in params:
                    await self.web_automation.click_element(params["click_element"])
                
                return AutomationResult(
                    task_id=task.id,
                    success=True,
                    result={"text": text_result},
                    screenshots_taken=screenshots
                )
            
            return AutomationResult(
                task_id=task.id,
                success=False,
                error_message="Missing URL parameter"
            )
            
        except Exception as e:
            return AutomationResult(
                task_id=task.id,
                success=False,
                error_message=str(e)
            )
    
    async def _execute_desktop_task(self, task: AutomationTask) -> AutomationResult:
        """Executa tarefa desktop"""
        try:
            params = task.parameters
            
            # Digitar texto se solicitado
            if "type_text" in params:
                await self.desktop_automation.type_text(params["type_text"])
            
            # Clicar em posição se solicitado
            if "click_position" in params:
                x, y = params["click_position"]
                await self.desktop_automation.click_position(x, y)
            
            # Tirar screenshot se solicitado
            screenshots = []
            if params.get("take_screenshot", False):
                screenshot_path = self.desktop_automation.take_screenshot()
                if screenshot_path:
                    screenshots.append(screenshot_path)
            
            # Encontrar imagem se solicitado
            image_location = None
            if "find_image" in params:
                image_location = self.desktop_automation.find_image_on_screen(
                    params["find_image"]
                )
            
            return AutomationResult(
                task_id=task.id,
                success=True,
                result={"image_location": image_location},
                screenshots_taken=screenshots
            )
            
        except Exception as e:
            return AutomationResult(
                task_id=task.id,
                success=False,
                error_message=str(e)
            )
    
    async def _execute_file_task(self, task: AutomationTask) -> AutomationResult:
        """Executa tarefa de operações de arquivo"""
        try:
            params = task.parameters
            
            # Ler arquivo
            if "read_file" in params:
                file_path = Path(params["read_file"])
                if file_path.exists():
                    content = file_path.read_text(encoding='utf-8')
                    return AutomationResult(
                        task_id=task.id,
                        success=True,
                        result={"content": content}
                    )
                else:
                    return AutomationResult(
                        task_id=task.id,
                        success=False,
                        error_message="File not found"
                    )
            
            return AutomationResult(
                task_id=task.id,
                success=False,
                error_message="Unsupported file operation"
            )
            
        except Exception as e:
            return AutomationResult(
                task_id=task.id,
                success=False,
                error_message=str(e)
            )
    
    async def _retry_task(self, task: AutomationTask) -> bool:
        """Verifica se tarefa deve ser retried"""
        return (task.retry_count < task.max_retries and 
                task.status == TaskStatus.FAILED)
    
    async def _process_task_queue(self):
        """Processa fila de tarefas"""
        while self.is_running:
            try:
                # Obter próxima tarefa com timeout
                task = await asyncio.wait_for(
                    self.task_queue.get(),
                    timeout=1.0
                )
                
                # Verificar se deve ser retried
                if await self._retry_task(task):
                    task.status = TaskStatus.RETRYING
                    await self._execute_callbacks("task_retry", task)
                
                # Executar tarefa
                result = await self.execute_task(task)
                
                # Adicionar de volta à fila se falhou e pode retry
                if not result.success and await self._retry_task(task):
                    await self.task_queue.put(task)
                
            except asyncio.TimeoutError:
                # Timeout normal, continuar loop
                continue
            except Exception as e:
                self.logger.error(f"Task queue processing error: {e}")
    
    def start(self):
        """Inicia gerenciador de automação"""
        if self.is_running:
            self.logger.warning("Automation manager already running")
            return
        
        self.is_running = True
        self.execution_thread = threading.Thread(target=self._run_execution_loop)
        self.execution_thread.daemon = True
        self.execution_thread.start()
        
        self.logger.info("Automation manager started")
    
    def _run_execution_loop(self):
        """Loop de execução em thread separada"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self._process_task_queue())
    
    def stop(self):
        """Para gerenciador de automação"""
        self.is_running = False
        
        if self.execution_thread and self.execution_thread.is_alive():
            self.execution_thread.join(timeout=5)
        
        # Limpar recursos
        self.web_automation.close_webdriver()
        
        self.logger.info("Automation manager stopped")
    
    def get_task_status(self, task_id: str) -> Optional[AutomationTask]:
        """Obtém status de tarefa específica"""
        return self.running_tasks.get(task_id)
    
    def get_queue_status(self) -> Dict[str, Any]:
        """Retorna status da fila de tarefas"""
        return {
            "is_running": self.is_running,
            "queue_size": self.task_queue.qsize(),
            "running_tasks": len(self.running_tasks),
            "stats": self.stats,
            "last_update": datetime.now().isoformat()
        }
    
    async def cancel_task(self, task_id: str) -> bool:
        """Cancela tarefa específica"""
        if task_id in self.running_tasks:
            task = self.running_tasks[task_id]
            task.status = TaskStatus.CANCELLED
            self.logger.info(f"Task cancelled: {task_id}")
            return True
        return False


# Instância global do gerenciador
_automation_manager: Optional[AutomationManager] = None


def get_automation_manager() -> AutomationManager:
    """Obtém instância global do AutomationManager"""
    global _automation_manager
    if _automation_manager is None:
        _automation_manager = AutomationManager()
    return _automation_manager


# Exportações principais
__all__ = [
    "AutomationManager",
    "AutomationTask",
    "AutomationResult",
    "WebAutomation",
    "DesktopAutomation",
    "AutomationType",
    "TaskStatus",
    "Priority",
    "get_automation_manager"
]
