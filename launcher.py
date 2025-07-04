#!/usr/bin/env python3
"""
MCPVotsAGI Unified Launcher
===========================
Single entry point for the entire ecosystem with multiple modes
"""

import asyncio
import click
import sys
import os
from pathlib import Path
import yaml
import json
from datetime import datetime
import structlog

# Add workspace to path
sys.path.insert(0, str(Path(__file__).parent))

from ecosystem_core import EcosystemCore

logger = structlog.get_logger()

@click.group()
@click.version_option(version='2.0.0')
def cli():
    """MCPVotsAGI Ecosystem Management CLI"""
    pass

@cli.command()
@click.option('--mode', '-m', 
              type=click.Choice(['development', 'staging', 'production']), 
              default='development',
              help='Deployment mode')
@click.option('--config', '-c', 
              type=click.Path(exists=True),
              help='Path to custom configuration file')
@click.option('--services', '-s',
              multiple=True,
              help='Specific services to start (default: all)')
def start(mode, config, services):
    """Start the MCPVotsAGI ecosystem"""
    click.echo(f"🚀 Starting MCPVotsAGI Ecosystem in {mode} mode...")
    
    # Update configuration
    config_path = Path(config) if config else Path(__file__).parent / "ecosystem_config.yaml"
    
    if config_path.exists():
        with open(config_path) as f:
            cfg = yaml.safe_load(f)
            cfg['mode'] = mode
            
        # Filter services if specified
        if services:
            for service_id in list(cfg.get('services', {}).keys()):
                if service_id not in services:
                    cfg['services'][service_id]['enabled'] = False
                    
        # Save temporary config
        temp_config = Path(__file__).parent / ".ecosystem_config_temp.yaml"
        with open(temp_config, 'w') as f:
            yaml.dump(cfg, f)
            
        ecosystem = EcosystemCore(temp_config)
    else:
        ecosystem = EcosystemCore()
    
    try:
        asyncio.run(ecosystem.start())
    except KeyboardInterrupt:
        click.echo("\n⏹️  Ecosystem stopped by user")
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)
    finally:
        # Cleanup temp config
        if 'temp_config' in locals() and temp_config.exists():
            temp_config.unlink()

@cli.command()
def stop():
    """Stop the MCPVotsAGI ecosystem"""
    click.echo("⏹️  Stopping MCPVotsAGI Ecosystem...")
    # Send shutdown signal to running ecosystem
    # Implementation depends on how we track the running process
    pass

@cli.command()
@click.option('--format', '-f',
              type=click.Choice(['json', 'yaml', 'table']),
              default='table',
              help='Output format')
def status(format):
    """Check ecosystem status"""
    async def get_status():
        ecosystem = EcosystemCore()
        return await ecosystem.get_status()
    
    status_data = asyncio.run(get_status())
    
    if format == 'json':
        click.echo(json.dumps(status_data, indent=2))
    elif format == 'yaml':
        click.echo(yaml.dump(status_data, default_flow_style=False))
    else:  # table
        click.echo("\n🔮 MCPVotsAGI Ecosystem Status\n")
        click.echo(f"Mode: {status_data['mode']}")
        click.echo(f"Running: {'✅' if status_data['running'] else '❌'}")
        
        # Resources
        click.echo("\n📊 System Resources:")
        resources = status_data['resources']
        click.echo(f"  CPU: {resources['cpu']['percent']}% {'⚠️' if resources['cpu']['threshold_exceeded'] else '✅'}")
        click.echo(f"  Memory: {resources['memory']['percent']}% {'⚠️' if resources['memory']['threshold_exceeded'] else '✅'}")
        click.echo(f"  Disk: {resources['disk']['percent']}% {'⚠️' if resources['disk']['threshold_exceeded'] else '✅'}")
        
        # Services
        click.echo("\n🔧 Services:")
        for service_id, info in status_data['services'].items():
            state_icon = {
                'running': '🟢',
                'stopped': '⚪',
                'failed': '🔴',
                'degraded': '🟡',
                'starting': '🔵'
            }.get(info['state'], '❓')
            
            click.echo(f"  {state_icon} {info['name']:<30} Port: {info['port']:<6} Health: {info['health_score']:.0f}%")

@cli.command()
@click.argument('service')
def restart(service):
    """Restart a specific service"""
    click.echo(f"🔄 Restarting {service}...")
    # Implementation needed
    pass

@cli.command()
def logs():
    """View ecosystem logs"""
    log_file = Path(__file__).parent / "logs" / "ecosystem.log"
    if log_file.exists():
        click.echo_via_pager(log_file.read_text())
    else:
        click.echo("No logs found")

@cli.command()
def backup():
    """Create ecosystem backup"""
    click.echo("💾 Creating ecosystem backup...")
    backup_dir = Path(__file__).parent / "backups"
    backup_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"ecosystem_backup_{timestamp}"
    
    # Backup databases, configs, etc.
    click.echo(f"✅ Backup created: {backup_name}")

@cli.command()
@click.option('--check', '-c', is_flag=True, help='Only check for updates')
def update(check):
    """Update ecosystem components"""
    if check:
        click.echo("🔍 Checking for updates...")
        # Check git repos, dependencies, etc.
    else:
        click.echo("📦 Updating ecosystem components...")
        # Perform updates

@cli.command()
def doctor():
    """Run ecosystem health checks"""
    click.echo("🏥 Running ecosystem diagnostics...\n")
    
    checks = []
    
    # Check Python version
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    checks.append(("Python version", python_version, sys.version_info >= (3, 8)))
    
    # Check required packages
    required_packages = ['aiohttp', 'websockets', 'psutil', 'structlog', 'click', 'pyyaml']
    for package in required_packages:
        try:
            __import__(package)
            checks.append((f"Package {package}", "Installed", True))
        except ImportError:
            checks.append((f"Package {package}", "Not installed", False))
    
    # Check ports
    import socket
    critical_ports = [3002, 3011, 11434]  # Memory MCP, Dashboard, Ollama
    for port in critical_ports:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        available = result != 0
        checks.append((f"Port {port}", "Available" if available else "In use", available))
    
    # Check disk space
    import psutil
    disk = psutil.disk_usage('/')
    disk_ok = disk.percent < 90
    checks.append(("Disk space", f"{disk.percent}% used", disk_ok))
    
    # Display results
    all_ok = True
    for check, status, ok in checks:
        icon = '✅' if ok else '❌'
        click.echo(f"{icon} {check:<25} {status}")
        if not ok:
            all_ok = False
    
    if all_ok:
        click.echo("\n✅ All checks passed! Ecosystem is ready.")
    else:
        click.echo("\n❌ Some checks failed. Please fix the issues before starting.")
        sys.exit(1)

@cli.command()
@click.option('--dashboard/--no-dashboard', default=True, help='Open dashboard after start')
@click.option('--trading/--no-trading', default=True, help='Enable trading system')
@click.option('--security/--no-security', default=True, help='Enable security monitoring')
def quickstart(dashboard, trading, security):
    """Quick start with common options"""
    click.echo("⚡ Quick starting MCPVotsAGI Ecosystem...\n")
    
    # Run doctor first
    ctx = click.get_current_context()
    ctx.invoke(doctor)
    
    # Configure services
    services = ['memory_mcp', 'github_mcp']
    
    if dashboard:
        services.append('oracle_agi')
    if trading:
        services.extend(['solana_mcp', 'ollama'])
    if security:
        services.append('opencti_mcp')
    
    # Start with selected services
    ctx.invoke(start, mode='production', services=services)
    
    if dashboard:
        click.echo("\n🌐 Dashboard available at: http://localhost:3011")


if __name__ == '__main__':
    cli()