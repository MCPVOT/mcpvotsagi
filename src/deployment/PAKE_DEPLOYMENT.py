#!/usr/bin/env python3
"""
Pake Deployment Module for ULTIMATE AGI SYSTEM
==============================================
Package AGI interfaces as lightweight desktop applications
"""

import os
import sys
import json
import subprocess
import platform
from pathlib import Path
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class PakeDeployment:
    """Deploy AGI interfaces as desktop apps using Pake"""
    
    def __init__(self):
        self.pake_path = Path(__file__).parent.parent.parent / "tools" / "Pake"
        self.apps_dir = Path(__file__).parent.parent.parent / "desktop_apps"
        self.apps_dir.mkdir(exist_ok=True)
        
        # Pake configuration templates
        self.app_configs = {
            'ultimate_agi': {
                'name': 'UltimateAGI',
                'url': 'http://localhost:8888',
                'identifier': 'com.mcpvots.ultimateagi',
                'icon': 'icons/agi.png',
                'width': 1200,
                'height': 800,
                'resizable': True,
                'fullscreen': True
            },
            'trading_dashboard': {
                'name': 'AGITrading',
                'url': 'http://localhost:8888/trading',
                'identifier': 'com.mcpvots.trading',
                'icon': 'icons/trading.png',
                'width': 1400,
                'height': 900,
                'resizable': True
            },
            'memory_explorer': {
                'name': 'AGIMemory',
                'url': 'http://localhost:8888/memory',
                'identifier': 'com.mcpvots.memory',
                'icon': 'icons/memory.png',
                'width': 1000,
                'height': 700,
                'resizable': True
            },
            'agent_monitor': {
                'name': 'AGIMonitor',
                'url': 'http://localhost:8888/agents',
                'identifier': 'com.mcpvots.monitor',
                'icon': 'icons/monitor.png',
                'width': 1200,
                'height': 800,
                'resizable': True
            }
        }
    
    def check_pake_installation(self) -> bool:
        """Check if Pake is properly installed"""
        try:
            # Check if pake-cli is available
            result = subprocess.run(
                ['pake', '--version'],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                logger.info(f"✅ Pake installed: {result.stdout.strip()}")
                return True
        except FileNotFoundError:
            pass
        
        # Check local installation
        if (self.pake_path / 'package.json').exists():
            logger.info(f"✅ Pake found at: {self.pake_path}")
            return True
        
        logger.warning("⚠️ Pake not found. Install with: npm install -g pake-cli")
        return False
    
    def create_app_config(self, app_name: str, custom_config: Dict = None) -> Dict:
        """Create Pake configuration for an app"""
        base_config = self.app_configs.get(app_name, {})
        
        if custom_config:
            base_config.update(custom_config)
        
        # Platform-specific adjustments
        if platform.system() == 'Darwin':  # macOS
            base_config['platform'] = 'macos'
            base_config['targets'] = 'dmg'
        elif platform.system() == 'Windows':
            base_config['platform'] = 'windows'
            base_config['targets'] = 'nsis'
        else:  # Linux
            base_config['platform'] = 'linux'
            base_config['targets'] = 'deb'
        
        return base_config
    
    def build_desktop_app(self, app_name: str, config: Dict = None) -> Dict:
        """Build a desktop app using Pake"""
        if not self.check_pake_installation():
            return {'error': 'Pake not installed'}
        
        app_config = self.create_app_config(app_name, config)
        output_dir = self.apps_dir / app_name
        output_dir.mkdir(exist_ok=True)
        
        # Build command
        cmd = [
            'pake',
            app_config['url'],
            '--name', app_config['name'],
            '--icon', str(self._get_icon_path(app_config['icon'])),
            '--width', str(app_config['width']),
            '--height', str(app_config['height']),
            '--targets', app_config['targets']
        ]
        
        if app_config.get('resizable'):
            cmd.append('--resizable')
        
        if app_config.get('fullscreen'):
            cmd.append('--fullscreen')
        
        # Add output directory
        cmd.extend(['--out', str(output_dir)])
        
        logger.info(f"Building {app_name} desktop app...")
        logger.info(f"Command: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=str(self.pake_path)
            )
            
            if result.returncode == 0:
                logger.info(f"✅ Successfully built {app_name}")
                return {
                    'status': 'success',
                    'app_name': app_name,
                    'output_dir': str(output_dir),
                    'platform': app_config['platform']
                }
            else:
                logger.error(f"Build failed: {result.stderr}")
                return {
                    'error': 'Build failed',
                    'stderr': result.stderr
                }
        
        except Exception as e:
            logger.error(f"Build error: {e}")
            return {'error': str(e)}
    
    def _get_icon_path(self, icon_name: str) -> Path:
        """Get or create icon path"""
        icons_dir = self.apps_dir / 'icons'
        icons_dir.mkdir(exist_ok=True)
        
        icon_path = icons_dir / icon_name
        
        # Create default icon if doesn't exist
        if not icon_path.exists():
            self._create_default_icon(icon_path)
        
        return icon_path
    
    def _create_default_icon(self, icon_path: Path):
        """Create a default icon (placeholder)"""
        # In a real implementation, generate or copy a default icon
        # For now, create a simple PNG placeholder
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            # Create a simple icon
            img = Image.new('RGBA', (512, 512), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            # Draw a circle
            draw.ellipse([50, 50, 462, 462], fill=(0, 150, 255, 255))
            
            # Add text
            try:
                font = ImageFont.truetype("arial.ttf", 120)
            except:
                font = None
            
            draw.text((256, 256), "AGI", fill=(255, 255, 255, 255), 
                     font=font, anchor="mm")
            
            img.save(icon_path)
            logger.info(f"Created default icon: {icon_path}")
        
        except ImportError:
            # If PIL not available, create empty file
            icon_path.write_text("")
            logger.warning("PIL not available, created empty icon file")
    
    def create_launcher_script(self, app_name: str) -> Path:
        """Create a launcher script for the app"""
        launcher_dir = self.apps_dir / 'launchers'
        launcher_dir.mkdir(exist_ok=True)
        
        if platform.system() == 'Windows':
            launcher_path = launcher_dir / f'{app_name}.bat'
            script_content = f"""@echo off
echo Starting {app_name}...
cd /d "{self.apps_dir / app_name}"
start {self.app_configs[app_name]['name']}.exe
"""
        else:
            launcher_path = launcher_dir / f'{app_name}.sh'
            script_content = f"""#!/bin/bash
echo "Starting {app_name}..."
cd "{self.apps_dir / app_name}"
./{self.app_configs[app_name]['name']}
"""
        
        launcher_path.write_text(script_content)
        
        if platform.system() != 'Windows':
            os.chmod(launcher_path, 0o755)
        
        return launcher_path
    
    def build_all_apps(self) -> List[Dict]:
        """Build all configured desktop apps"""
        results = []
        
        for app_name in self.app_configs:
            logger.info(f"\nBuilding {app_name}...")
            result = self.build_desktop_app(app_name)
            results.append(result)
            
            if result.get('status') == 'success':
                launcher = self.create_launcher_script(app_name)
                result['launcher'] = str(launcher)
        
        return results
    
    def create_web_wrapper(self, name: str, url: str, **kwargs) -> Dict:
        """Create a custom web wrapper app"""
        custom_config = {
            'name': name,
            'url': url,
            'identifier': f'com.mcpvots.{name.lower()}',
            **kwargs
        }
        
        # Save to app configs
        self.app_configs[name.lower()] = custom_config
        
        # Build the app
        return self.build_desktop_app(name.lower())


class DesktopAppManager:
    """Manage deployed desktop applications"""
    
    def __init__(self, deployment: PakeDeployment):
        self.deployment = deployment
        self.installed_apps = {}
        self._scan_installed_apps()
    
    def _scan_installed_apps(self):
        """Scan for installed desktop apps"""
        if self.deployment.apps_dir.exists():
            for app_dir in self.deployment.apps_dir.iterdir():
                if app_dir.is_dir() and app_dir.name != 'icons':
                    self.installed_apps[app_dir.name] = {
                        'path': str(app_dir),
                        'launcher': str(self.deployment.apps_dir / 'launchers' / f'{app_dir.name}.sh')
                    }
    
    def launch_app(self, app_name: str) -> bool:
        """Launch a desktop app"""
        if app_name not in self.installed_apps:
            logger.error(f"App not found: {app_name}")
            return False
        
        launcher = self.installed_apps[app_name]['launcher']
        
        try:
            if platform.system() == 'Windows':
                subprocess.Popen(launcher, shell=True)
            else:
                subprocess.Popen([launcher])
            
            logger.info(f"✅ Launched {app_name}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to launch {app_name}: {e}")
            return False
    
    def list_apps(self) -> List[Dict]:
        """List all installed desktop apps"""
        return [
            {
                'name': name,
                'path': info['path'],
                'launcher': info['launcher']
            }
            for name, info in self.installed_apps.items()
        ]


# Deployment presets for common use cases
class DeploymentPresets:
    """Pre-configured deployment templates"""
    
    @staticmethod
    def create_ai_chat_app(base_url: str) -> Dict:
        """Create an AI chat interface app"""
        return {
            'name': 'AIChat',
            'url': f'{base_url}/chat',
            'width': 800,
            'height': 600,
            'resizable': True,
            'always_on_top': False
        }
    
    @staticmethod
    def create_dashboard_app(base_url: str) -> Dict:
        """Create a monitoring dashboard app"""
        return {
            'name': 'AGIDashboard',
            'url': base_url,
            'width': 1400,
            'height': 900,
            'resizable': True,
            'fullscreen': True
        }
    
    @staticmethod
    def create_code_assistant_app(base_url: str) -> Dict:
        """Create a code assistant app"""
        return {
            'name': 'CodeAssistant',
            'url': f'{base_url}/code',
            'width': 1200,
            'height': 800,
            'resizable': True,
            'developer_tools': True
        }


# Integration function for ULTIMATE AGI SYSTEM
def create_pake_deployment() -> PakeDeployment:
    """Create Pake deployment instance"""
    deployment = PakeDeployment()
    
    if deployment.check_pake_installation():
        logger.info("✅ Pake deployment ready")
    else:
        logger.warning("⚠️ Pake not installed - desktop app creation disabled")
    
    return deployment


# Test deployment
def test_pake_deployment():
    """Test Pake deployment"""
    print("Testing Pake Deployment...")
    
    deployment = create_pake_deployment()
    
    # Check installation
    if deployment.check_pake_installation():
        print("✅ Pake is installed")
        
        # Create a test app config
        test_config = deployment.create_app_config('ultimate_agi')
        print(f"App config: {json.dumps(test_config, indent=2)}")
        
        # List app configurations
        print(f"\nAvailable apps: {list(deployment.app_configs.keys())}")
        
        # Create launcher script
        launcher = deployment.create_launcher_script('ultimate_agi')
        print(f"Launcher created: {launcher}")
    else:
        print("⚠️ Pake not installed - skipping build tests")
    
    print("\n✅ Pake Deployment Test Complete!")


if __name__ == "__main__":
    test_pake_deployment()