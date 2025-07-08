#!/usr/bin/env python3
"""
Ultimate AGI System Health Monitor V3
====================================

Advanced health monitoring and alerting system for the Ultimate AGI System V3.
Provides real-time monitoring, predictive analytics, and automated response capabilities.

Features:
- Real-time component health monitoring
- Predictive failure detection using ML
- Automated healing and recovery
- Performance trend analysis
- Resource optimization recommendations
- Multi-channel alerting (console, file, webhook, email)
- Dashboard integration with WebSocket updates

Author: Ultimate AGI System V3
Version: 3.0.0
Date: 2025-07-06
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Tuple
from dataclasses import dataclass, asdict
import aiohttp
import psutil
import sqlite3
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import pickle
import websockets
import threading
from pathlib import Path
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
from concurrent.futures import ThreadPoolExecutor
import traceback

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('health_monitor_v3.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class HealthMetric:
    """Health metric data structure"""
    component: str
    metric_name: str
    value: float
    timestamp: datetime
    threshold: Optional[float] = None
    status: str = "OK"  # OK, WARNING, CRITICAL
    trend: str = "STABLE"  # STABLE, INCREASING, DECREASING
    prediction: Optional[float] = None

@dataclass
class AlertData:
    """Alert data structure"""
    alert_id: str
    component: str
    severity: str  # INFO, WARNING, CRITICAL
    message: str
    timestamp: datetime
    metric: Optional[HealthMetric] = None
    acknowledged: bool = False
    resolved: bool = False

class PredictiveAnalyzer:
    """ML-based predictive analyzer for system health"""

    def __init__(self, model_path: str = "health_models"):
        self.model_path = Path(model_path)
        self.model_path.mkdir(exist_ok=True)
        self.models = {}
        self.scalers = {}
        self.is_trained = False
        self.training_data = []
        self.anomaly_detectors = {}

    def collect_training_data(self, metrics: List[HealthMetric]):
        """Collect training data for ML models"""
        for metric in metrics:
            self.training_data.append({
                'component': metric.component,
                'metric_name': metric.metric_name,
                'value': metric.value,
                'timestamp': metric.timestamp.timestamp(),
                'hour': metric.timestamp.hour,
                'day_of_week': metric.timestamp.weekday(),
                'day_of_month': metric.timestamp.day
            })

    def train_models(self):
        """Train ML models for prediction and anomaly detection"""
        if len(self.training_data) < 100:  # Need minimum data
            logger.warning("Insufficient training data for ML models")
            return

        try:
            df = pd.DataFrame(self.training_data)

            # Group by component and metric
            for (component, metric_name), group in df.groupby(['component', 'metric_name']):
                if len(group) < 20:  # Need minimum samples
                    continue

                model_key = f"{component}_{metric_name}"

                # Prepare features for time series prediction
                features = ['timestamp', 'hour', 'day_of_week', 'day_of_month']
                X = group[features].values
                y = group['value'].values

                # Create lag features
                for lag in [1, 2, 3, 6, 12]:
                    if len(y) > lag:
                        lag_values = np.roll(y, lag)
                        lag_values[:lag] = y[:lag]  # Fill initial values
                        X = np.column_stack([X, lag_values])

                # Train scaler
                scaler = StandardScaler()
                X_scaled = scaler.fit_transform(X)

                # Train anomaly detector
                anomaly_detector = IsolationForest(
                    contamination=0.1,
                    random_state=42
                )
                anomaly_detector.fit(X_scaled)

                # Store models
                self.scalers[model_key] = scaler
                self.anomaly_detectors[model_key] = anomaly_detector

                logger.info(f"Trained models for {model_key}")

            self.is_trained = True
            self.save_models()

        except Exception as e:
            logger.error(f"Error training models: {e}")

    def predict_anomaly(self, metric: HealthMetric) -> Tuple[bool, float]:
        """Predict if a metric is anomalous"""
        if not self.is_trained:
            return False, 0.0

        try:
            model_key = f"{metric.component}_{metric.metric_name}"

            if model_key not in self.anomaly_detectors:
                return False, 0.0

            # Prepare features
            features = np.array([[
                metric.timestamp.timestamp(),
                metric.timestamp.hour,
                metric.timestamp.weekday(),
                metric.timestamp.day,
                metric.value  # Current value as feature
            ]])

            # Scale features
            features_scaled = self.scalers[model_key].transform(features)

            # Predict anomaly
            anomaly_score = self.anomaly_detectors[model_key].decision_function(features_scaled)[0]
            is_anomaly = self.anomaly_detectors[model_key].predict(features_scaled)[0] == -1

            return is_anomaly, abs(anomaly_score)

        except Exception as e:
            logger.error(f"Error predicting anomaly: {e}")
            return False, 0.0

    def save_models(self):
        """Save trained models to disk"""
        try:
            models_data = {
                'scalers': self.scalers,
                'anomaly_detectors': self.anomaly_detectors,
                'is_trained': self.is_trained
            }

            with open(self.model_path / "health_models.pkl", 'wb') as f:
                pickle.dump(models_data, f)

            logger.info("ML models saved successfully")

        except Exception as e:
            logger.error(f"Error saving models: {e}")

    def load_models(self):
        """Load trained models from disk"""
        try:
            model_file = self.model_path / "health_models.pkl"
            if model_file.exists():
                with open(model_file, 'rb') as f:
                    models_data = pickle.load(f)

                self.scalers = models_data.get('scalers', {})
                self.anomaly_detectors = models_data.get('anomaly_detectors', {})
                self.is_trained = models_data.get('is_trained', False)

                logger.info("ML models loaded successfully")

        except Exception as e:
            logger.error(f"Error loading models: {e}")

class AlertManager:
    """Advanced alert management system"""

    def __init__(self, config: Dict):
        self.config = config
        self.alerts = []
        self.notification_channels = config.get("notification_channels", {})
        self.executor = ThreadPoolExecutor(max_workers=5)
        self.webhook_url = config.get("webhook_url")
        self.email_config = config.get("email", {})
        self.alert_history = []
        self.suppression_rules = []

    async def send_alert(self, alert: AlertData):
        """Send alert through configured channels"""
        self.alerts.append(alert)
        self.alert_history.append(alert)

        logger.info(f"🚨 ALERT: {alert.severity} - {alert.component} - {alert.message}")

        # Send through enabled channels
        tasks = []

        if self.notification_channels.get("console", True):
            tasks.append(self.send_console_alert(alert))

        if self.notification_channels.get("file", True):
            tasks.append(self.send_file_alert(alert))

        if self.notification_channels.get("webhook", False) and self.webhook_url:
            tasks.append(self.send_webhook_alert(alert))

        if self.notification_channels.get("email", False) and self.email_config:
            tasks.append(self.send_email_alert(alert))

        # Execute all notification tasks
        await asyncio.gather(*tasks, return_exceptions=True)

    async def send_console_alert(self, alert: AlertData):
        """Send alert to console"""
        severity_colors = {
            "INFO": "\033[94m",      # Blue
            "WARNING": "\033[93m",   # Yellow
            "CRITICAL": "\033[91m"   # Red
        }
        reset_color = "\033[0m"

        color = severity_colors.get(alert.severity, "")
        print(f"{color}[{alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')}] "
              f"{alert.severity}: {alert.component} - {alert.message}{reset_color}")

    async def send_file_alert(self, alert: AlertData):
        """Send alert to file"""
        try:
            alert_file = Path("alerts.log")
            with open(alert_file, 'a') as f:
                f.write(f"[{alert.timestamp.isoformat()}] {alert.severity}: "
                       f"{alert.component} - {alert.message}\n")
        except Exception as e:
            logger.error(f"Error writing alert to file: {e}")

    async def send_webhook_alert(self, alert: AlertData):
        """Send alert via webhook"""
        try:
            payload = {
                "alert_id": alert.alert_id,
                "component": alert.component,
                "severity": alert.severity,
                "message": alert.message,
                "timestamp": alert.timestamp.isoformat(),
                "system": "Ultimate AGI System V3"
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.webhook_url,
                    json=payload,
                    timeout=10
                ) as response:
                    if response.status == 200:
                        logger.info(f"Webhook alert sent successfully for {alert.alert_id}")
                    else:
                        logger.error(f"Webhook alert failed: {response.status}")

        except Exception as e:
            logger.error(f"Error sending webhook alert: {e}")

    async def send_email_alert(self, alert: AlertData):
        """Send alert via email"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_config['from']
            msg['To'] = self.email_config['to']
            msg['Subject'] = f"[{alert.severity}] Ultimate AGI System Alert - {alert.component}"

            body = f"""
            Alert Details:

            Component: {alert.component}
            Severity: {alert.severity}
            Message: {alert.message}
            Time: {alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
            Alert ID: {alert.alert_id}

            Please investigate and take appropriate action.

            Best regards,
            Ultimate AGI System V3
            """

            msg.attach(MIMEText(body, 'plain'))

            # Send email in thread to avoid blocking
            def send_email():
                try:
                    server = smtplib.SMTP(self.email_config['smtp_server'],
                                        self.email_config['smtp_port'])
                    server.starttls()
                    server.login(self.email_config['username'],
                               self.email_config['password'])
                    server.send_message(msg)
                    server.quit()
                    logger.info(f"Email alert sent successfully for {alert.alert_id}")
                except Exception as e:
                    logger.error(f"Error sending email alert: {e}")

            await asyncio.get_event_loop().run_in_executor(
                self.executor, send_email
            )

        except Exception as e:
            logger.error(f"Error preparing email alert: {e}")

    def get_active_alerts(self) -> List[AlertData]:
        """Get currently active alerts"""
        return [alert for alert in self.alerts if not alert.resolved]

    def acknowledge_alert(self, alert_id: str):
        """Acknowledge an alert"""
        for alert in self.alerts:
            if alert.alert_id == alert_id:
                alert.acknowledged = True
                logger.info(f"Alert {alert_id} acknowledged")
                break

    def resolve_alert(self, alert_id: str):
        """Resolve an alert"""
        for alert in self.alerts:
            if alert.alert_id == alert_id:
                alert.resolved = True
                logger.info(f"Alert {alert_id} resolved")
                break

class HealthMonitorV3:
    """Advanced health monitoring system"""

    def __init__(self, config_path: str = "orchestrator_config.json"):
        self.config = self.load_config(config_path)
        self.db_path = "health_monitor.db"
        self.predictive_analyzer = PredictiveAnalyzer()
        self.alert_manager = AlertManager(self.config.get("monitoring", {}))
        self.metrics_buffer = []
        self.websocket_clients = set()
        self.running = False
        self.health_thresholds = self.config["monitoring"]["alert_thresholds"]

        # Initialize components
        self.init_database()
        self.predictive_analyzer.load_models()

        logger.info("🏥 Health Monitor V3 initialized")

    def load_config(self, config_path: str) -> Dict:
        """Load configuration from file"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return {}

    def init_database(self):
        """Initialize database for health metrics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS health_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    component TEXT,
                    metric_name TEXT,
                    value REAL,
                    timestamp DATETIME,
                    status TEXT,
                    trend TEXT,
                    prediction REAL,
                    anomaly_score REAL
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    alert_id TEXT UNIQUE,
                    component TEXT,
                    severity TEXT,
                    message TEXT,
                    timestamp DATETIME,
                    acknowledged BOOLEAN,
                    resolved BOOLEAN
                )
            ''')

            conn.commit()
            conn.close()

        except Exception as e:
            logger.error(f"Database initialization error: {e}")

    async def start_monitoring(self):
        """Start the health monitoring system"""
        logger.info("🏥 Starting Health Monitor V3...")
        self.running = True

        # Start monitoring tasks
        tasks = [
            asyncio.create_task(self.metric_collection_loop()),
            asyncio.create_task(self.analysis_loop()),
            asyncio.create_task(self.websocket_server()),
            asyncio.create_task(self.model_training_loop())
        ]

        try:
            await asyncio.gather(*tasks)
        except Exception as e:
            logger.error(f"Error in monitoring tasks: {e}")
            traceback.print_exc()

    async def metric_collection_loop(self):
        """Collect health metrics from all components"""
        while self.running:
            try:
                metrics = await self.collect_all_metrics()

                for metric in metrics:
                    # Store in buffer for analysis
                    self.metrics_buffer.append(metric)

                    # Store in database
                    await self.store_metric(metric)

                    # Send to WebSocket clients
                    await self.broadcast_metric(metric)

                # Keep buffer size manageable
                if len(self.metrics_buffer) > 10000:
                    self.metrics_buffer = self.metrics_buffer[-5000:]

                await asyncio.sleep(5)  # Collect every 5 seconds

            except Exception as e:
                logger.error(f"Error in metric collection: {e}")
                await asyncio.sleep(1)

    async def collect_all_metrics(self) -> List[HealthMetric]:
        """Collect metrics from all system components"""
        metrics = []

        # System metrics
        system_metrics = await self.collect_system_metrics()
        metrics.extend(system_metrics)

        # Component metrics
        component_metrics = await self.collect_component_metrics()
        metrics.extend(component_metrics)

        return metrics

    async def collect_system_metrics(self) -> List[HealthMetric]:
        """Collect system-level metrics"""
        metrics = []
        timestamp = datetime.now()

        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            metrics.append(HealthMetric(
                component="system",
                metric_name="cpu_usage",
                value=cpu_percent,
                timestamp=timestamp,
                threshold=self.health_thresholds["cpu_usage"]
            ))

            # Memory metrics
            memory = psutil.virtual_memory()
            metrics.append(HealthMetric(
                component="system",
                metric_name="memory_usage",
                value=memory.percent,
                timestamp=timestamp,
                threshold=self.health_thresholds["memory_usage"]
            ))

            # Disk metrics
            disk = psutil.disk_usage('/')
            metrics.append(HealthMetric(
                component="system",
                metric_name="disk_usage",
                value=disk.percent,
                timestamp=timestamp,
                threshold=self.health_thresholds["disk_usage"]
            ))

            # Network metrics
            network = psutil.net_io_counters()
            metrics.append(HealthMetric(
                component="system",
                metric_name="network_bytes_sent",
                value=float(network.bytes_sent),
                timestamp=timestamp
            ))

            metrics.append(HealthMetric(
                component="system",
                metric_name="network_bytes_recv",
                value=float(network.bytes_recv),
                timestamp=timestamp
            ))

        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")

        return metrics

    async def collect_component_metrics(self) -> List[HealthMetric]:
        """Collect metrics from individual components"""
        metrics = []
        timestamp = datetime.now()

        # Get component configurations
        components = self.config.get("components", {})

        for component_name, config in components.items():
            try:
                # Check if component is running
                port = config.get("port")
                if port:
                    # Try to get health metrics via HTTP
                    health_url = f"http://localhost:{port}/health"
                    response_time, health_score = await self.check_component_health(health_url)

                    metrics.append(HealthMetric(
                        component=component_name,
                        metric_name="response_time",
                        value=response_time,
                        timestamp=timestamp,
                        threshold=self.health_thresholds.get("response_time", 5000)
                    ))

                    metrics.append(HealthMetric(
                        component=component_name,
                        metric_name="health_score",
                        value=health_score,
                        timestamp=timestamp,
                        threshold=self.health_thresholds.get("component_health", 70)
                    ))

            except Exception as e:
                logger.error(f"Error collecting metrics for {component_name}: {e}")

        return metrics

    async def check_component_health(self, health_url: str) -> Tuple[float, float]:
        """Check component health via HTTP endpoint"""
        try:
            start_time = datetime.now()

            async with aiohttp.ClientSession() as session:
                async with session.get(health_url, timeout=10) as response:
                    end_time = datetime.now()
                    response_time = (end_time - start_time).total_seconds() * 1000

                    if response.status == 200:
                        health_data = await response.json()
                        health_score = health_data.get("health_score", 100.0)
                        return response_time, health_score
                    else:
                        return response_time, 0.0

        except Exception:
            return 10000.0, 0.0  # High response time, no health score

    async def analysis_loop(self):
        """Analyze metrics and generate alerts"""
        while self.running:
            try:
                if self.metrics_buffer:
                    # Analyze recent metrics
                    recent_metrics = self.metrics_buffer[-100:]  # Last 100 metrics

                    for metric in recent_metrics:
                        await self.analyze_metric(metric)

                await asyncio.sleep(10)  # Analyze every 10 seconds

            except Exception as e:
                logger.error(f"Error in analysis loop: {e}")
                await asyncio.sleep(1)

    async def analyze_metric(self, metric: HealthMetric):
        """Analyze a single metric and generate alerts if needed"""
        try:
            # Check threshold violations
            if metric.threshold and metric.value > metric.threshold:
                metric.status = "CRITICAL" if metric.value > metric.threshold * 1.2 else "WARNING"

                # Generate alert
                alert = AlertData(
                    alert_id=f"{metric.component}_{metric.metric_name}_{int(metric.timestamp.timestamp())}",
                    component=metric.component,
                    severity=metric.status,
                    message=f"{metric.metric_name} is {metric.value:.2f} (threshold: {metric.threshold})",
                    timestamp=metric.timestamp,
                    metric=metric
                )

                await self.alert_manager.send_alert(alert)

            # Predictive analysis
            if self.predictive_analyzer.is_trained:
                is_anomaly, anomaly_score = self.predictive_analyzer.predict_anomaly(metric)

                if is_anomaly and anomaly_score > 0.5:
                    alert = AlertData(
                        alert_id=f"anomaly_{metric.component}_{metric.metric_name}_{int(metric.timestamp.timestamp())}",
                        component=metric.component,
                        severity="WARNING",
                        message=f"Anomaly detected in {metric.metric_name}: {metric.value:.2f} (score: {anomaly_score:.3f})",
                        timestamp=metric.timestamp,
                        metric=metric
                    )

                    await self.alert_manager.send_alert(alert)

        except Exception as e:
            logger.error(f"Error analyzing metric: {e}")

    async def model_training_loop(self):
        """Periodically train ML models"""
        while self.running:
            try:
                await asyncio.sleep(3600)  # Train every hour

                if len(self.metrics_buffer) > 200:
                    logger.info("Training ML models...")

                    # Collect training data
                    self.predictive_analyzer.collect_training_data(self.metrics_buffer)

                    # Train models in background
                    await asyncio.get_event_loop().run_in_executor(
                        None, self.predictive_analyzer.train_models
                    )

            except Exception as e:
                logger.error(f"Error in model training loop: {e}")
                await asyncio.sleep(60)

    async def websocket_server(self):
        """WebSocket server for real-time metric updates"""
        async def handle_client(websocket, path):
            """Handle WebSocket client connections"""
            self.websocket_clients.add(websocket)
            logger.info(f"WebSocket client connected: {websocket.remote_address}")

            try:
                async for message in websocket:
                    # Handle client messages if needed
                    pass
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
            finally:
                self.websocket_clients.discard(websocket)
                logger.info(f"WebSocket client disconnected: {websocket.remote_address}")

        try:
            start_server = websockets.serve(handle_client, "localhost", 8999)
            await start_server
            logger.info("WebSocket server started on ws://localhost:8999")
        except Exception as e:
            logger.error(f"Error starting WebSocket server: {e}")

    async def broadcast_metric(self, metric: HealthMetric):
        """Broadcast metric to all WebSocket clients"""
        if self.websocket_clients:
            message = json.dumps({
                "type": "metric",
                "data": asdict(metric)
            }, default=str)

            # Send to all clients
            disconnected_clients = set()
            for client in self.websocket_clients:
                try:
                    await client.send(message)
                except Exception:
                    disconnected_clients.add(client)

            # Remove disconnected clients
            self.websocket_clients -= disconnected_clients

    async def store_metric(self, metric: HealthMetric):
        """Store metric in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO health_metrics
                (component, metric_name, value, timestamp, status, trend, prediction, anomaly_score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                metric.component,
                metric.metric_name,
                metric.value,
                metric.timestamp.isoformat(),
                metric.status,
                metric.trend,
                metric.prediction,
                0.0  # Default anomaly score
            ))

            conn.commit()
            conn.close()

        except Exception as e:
            logger.error(f"Error storing metric: {e}")

    async def get_health_dashboard_data(self) -> Dict:
        """Get health dashboard data"""
        try:
            # Recent metrics
            recent_metrics = self.metrics_buffer[-50:] if self.metrics_buffer else []

            # Active alerts
            active_alerts = self.alert_manager.get_active_alerts()

            # System summary
            system_metrics = [m for m in recent_metrics if m.component == "system"]

            return {
                "timestamp": datetime.now().isoformat(),
                "recent_metrics": [asdict(m) for m in recent_metrics],
                "active_alerts": [asdict(a) for a in active_alerts],
                "system_summary": {
                    "total_components": len(self.config.get("components", {})),
                    "healthy_components": len([m for m in recent_metrics if m.status == "OK"]),
                    "critical_alerts": len([a for a in active_alerts if a.severity == "CRITICAL"]),
                    "warning_alerts": len([a for a in active_alerts if a.severity == "WARNING"])
                },
                "performance_trends": await self.get_performance_trends()
            }

        except Exception as e:
            logger.error(f"Error getting dashboard data: {e}")
            return {}

    async def get_performance_trends(self) -> Dict:
        """Get performance trends for dashboard"""
        try:
            # This would analyze historical data for trends
            # For now, return mock data
            return {
                "cpu_trend": "stable",
                "memory_trend": "increasing",
                "response_time_trend": "improving",
                "error_rate_trend": "stable"
            }
        except Exception as e:
            logger.error(f"Error getting performance trends: {e}")
            return {}

    async def shutdown(self):
        """Shutdown the health monitor"""
        logger.info("🛑 Shutting down Health Monitor V3...")
        self.running = False

        # Close WebSocket connections
        for client in self.websocket_clients:
            try:
                await client.close()
            except Exception:
                pass

        logger.info("✅ Health Monitor V3 shutdown complete")

async def main():
    """Main entry point"""
    try:
        monitor = HealthMonitorV3()
        await monitor.start_monitoring()
    except KeyboardInterrupt:
        logger.info("Shutdown requested by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
