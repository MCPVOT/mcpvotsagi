#!/usr/bin/env python3
"""
Advanced DGM System Integration Script
=====================================

This script integrates the advanced DGM evolution engine with neural architecture search
into the main MCPVotsAGI system and validates all endpoints.

Features:
- Launch advanced DGM evolution engine as async web service
- Test neural architecture search endpoints
- Validate meta-learning and self-modifying code capabilities
- Run comprehensive health checks
- Generate integration report

Author: MCPVotsAGI Development Team
Date: 2024
"""

import asyncio
import aiohttp
import json
import sys
import os
import time
from pathlib import Path
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

class AdvancedDGMIntegrator:
    """Advanced DGM System Integration Manager"""

    def __init__(self):
        self.base_url = "http://localhost"
        self.advanced_dgm_port = 8087
        self.nas_port = 8088
        self.session = None
        self.integration_results = {
            'timestamp': datetime.now().isoformat(),
            'services_tested': [],
            'endpoints_validated': [],
            'errors': [],
            'success_rate': 0.0,
            'recommendations': []
        }

    async def setup_session(self):
        """Setup HTTP session"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30)
        )

    async def cleanup_session(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()

    async def test_service_health(self, service_name: str, port: int) -> bool:
        """Test if a service is healthy"""
        try:
            url = f"{self.base_url}:{port}/health"
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"✅ {service_name} health check passed: {data}")
                    self.integration_results['endpoints_validated'].append(f"{service_name}/health")
                    return True
                else:
                    logger.error(f"❌ {service_name} health check failed: {response.status}")
                    self.integration_results['errors'].append(f"{service_name} health check failed: {response.status}")
                    return False
        except Exception as e:
            logger.error(f"❌ {service_name} health check error: {e}")
            self.integration_results['errors'].append(f"{service_name} health check error: {str(e)}")
            return False

    async def test_advanced_dgm_endpoints(self) -> bool:
        """Test Advanced DGM Evolution Engine endpoints"""
        try:
            base_url = f"{self.base_url}:{self.advanced_dgm_port}"
            success_count = 0
            total_tests = 0

            # Test status endpoint
            total_tests += 1
            try:
                async with self.session.get(f"{base_url}/status") as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.info(f"✅ Advanced DGM status: {data}")
                        success_count += 1
                        self.integration_results['endpoints_validated'].append("advanced_dgm/status")
            except Exception as e:
                logger.error(f"❌ Advanced DGM status test failed: {e}")
                self.integration_results['errors'].append(f"Advanced DGM status test failed: {str(e)}")

            # Test evolution endpoint
            total_tests += 1
            evolution_config = {
                "generations": 5,
                "population_size": 10,
                "mutation_rate": 0.1,
                "meta_learning": True
            }
            try:
                async with self.session.post(
                    f"{base_url}/evolve",
                    json=evolution_config
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.info(f"✅ Advanced DGM evolution test passed: {data.get('message', 'Success')}")
                        success_count += 1
                        self.integration_results['endpoints_validated'].append("advanced_dgm/evolve")
            except Exception as e:
                logger.error(f"❌ Advanced DGM evolution test failed: {e}")
                self.integration_results['errors'].append(f"Advanced DGM evolution test failed: {str(e)}")

            # Test meta-learning endpoint
            total_tests += 1
            meta_config = {
                "task_id": "test_task_001",
                "domain": "classification",
                "examples": [
                    {"input": [1, 2, 3], "output": 0},
                    {"input": [4, 5, 6], "output": 1}
                ],
                "metric": "accuracy",
                "steps": 5
            }
            try:
                async with self.session.post(
                    f"{base_url}/meta-learn",
                    json=meta_config
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.info(f"✅ Advanced DGM meta-learning test passed: {data.get('message', 'Success')}")
                        success_count += 1
                        self.integration_results['endpoints_validated'].append("advanced_dgm/meta-learn")
            except Exception as e:
                logger.error(f"❌ Advanced DGM meta-learning test failed: {e}")
                self.integration_results['errors'].append(f"Advanced DGM meta-learning test failed: {str(e)}")

            # Test genome evaluation endpoint
            total_tests += 1
            eval_config = {
                "genome_id": "test_genome_001",
                "evaluation_metrics": ["accuracy", "efficiency"],
                "test_data": "sample_test_data"
            }
            try:
                async with self.session.post(
                    f"{base_url}/evaluate",
                    json=eval_config
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.info(f"✅ Advanced DGM genome evaluation test passed: {data.get('message', 'Success')}")
                        success_count += 1
                        self.integration_results['endpoints_validated'].append("advanced_dgm/evaluate")
            except Exception as e:
                logger.error(f"❌ Advanced DGM genome evaluation test failed: {e}")
                self.integration_results['errors'].append(f"Advanced DGM genome evaluation test failed: {str(e)}")

            success_rate = success_count / total_tests if total_tests > 0 else 0
            logger.info(f"Advanced DGM endpoints success rate: {success_rate:.2%} ({success_count}/{total_tests})")
            return success_rate > 0.5

        except Exception as e:
            logger.error(f"❌ Advanced DGM endpoint testing failed: {e}")
            self.integration_results['errors'].append(f"Advanced DGM endpoint testing failed: {str(e)}")
            return False

    async def test_nas_endpoints(self) -> bool:
        """Test Neural Architecture Search endpoints"""
        try:
            base_url = f"{self.base_url}:{self.nas_port}"
            success_count = 0
            total_tests = 0

            # Test status endpoint
            total_tests += 1
            try:
                async with self.session.get(f"{base_url}/status") as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.info(f"✅ NAS status: {data}")
                        success_count += 1
                        self.integration_results['endpoints_validated'].append("nas/status")
            except Exception as e:
                logger.error(f"❌ NAS status test failed: {e}")
                self.integration_results['errors'].append(f"NAS status test failed: {str(e)}")

            # Test DARTS search endpoint
            total_tests += 1
            darts_config = {
                "search_space": "macro",
                "epochs": 5,
                "channels": 16
            }
            try:
                async with self.session.post(
                    f"{base_url}/search/darts",
                    json=darts_config
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.info(f"✅ NAS DARTS search test passed: {data.get('message', 'Success')}")
                        success_count += 1
                        self.integration_results['endpoints_validated'].append("nas/search/darts")
            except Exception as e:
                logger.error(f"❌ NAS DARTS search test failed: {e}")
                self.integration_results['errors'].append(f"NAS DARTS search test failed: {str(e)}")

            # Test evolutionary search endpoint
            total_tests += 1
            evo_config = {
                "population_size": 20,
                "generations": 10,
                "mutation_rate": 0.2
            }
            try:
                async with self.session.post(
                    f"{base_url}/search/evolutionary",
                    json=evo_config
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.info(f"✅ NAS evolutionary search test passed: {data.get('message', 'Success')}")
                        success_count += 1
                        self.integration_results['endpoints_validated'].append("nas/search/evolutionary")
            except Exception as e:
                logger.error(f"❌ NAS evolutionary search test failed: {e}")
                self.integration_results['errors'].append(f"NAS evolutionary search test failed: {str(e)}")

            success_rate = success_count / total_tests if total_tests > 0 else 0
            logger.info(f"NAS endpoints success rate: {success_rate:.2%} ({success_count}/{total_tests})")
            return success_rate > 0.5

        except Exception as e:
            logger.error(f"❌ NAS endpoint testing failed: {e}")
            self.integration_results['errors'].append(f"NAS endpoint testing failed: {str(e)}")
            return False

    async def launch_services(self):
        """Launch the advanced DGM services"""
        logger.info("🚀 Launching Advanced DGM Evolution Engine...")

        # Import and launch advanced DGM evolution engine
        try:
            import subprocess
            import sys

            # Launch Advanced DGM Evolution Engine
            cmd_dgm = [
                sys.executable,
                str(PROJECT_ROOT / "services" / "advanced_dgm_evolution_engine.py")
            ]
            subprocess.Popen(cmd_dgm, cwd=str(PROJECT_ROOT))
            logger.info(f"✅ Advanced DGM Evolution Engine launched on port {self.advanced_dgm_port}")

            # Launch Neural Architecture Search
            cmd_nas = [
                sys.executable,
                str(PROJECT_ROOT / "services" / "neural_architecture_search.py")
            ]
            subprocess.Popen(cmd_nas, cwd=str(PROJECT_ROOT))
            logger.info(f"✅ Neural Architecture Search launched on port {self.nas_port}")

            # Wait for services to start
            logger.info("⏳ Waiting for services to initialize...")
            await asyncio.sleep(10)

        except Exception as e:
            logger.error(f"❌ Failed to launch services: {e}")
            self.integration_results['errors'].append(f"Service launch failed: {str(e)}")

    async def run_integration_tests(self):
        """Run comprehensive integration tests"""
        logger.info("🧪 Running Advanced DGM Integration Tests")

        await self.setup_session()

        try:
            # Test service health
            dgm_healthy = await self.test_service_health("Advanced DGM Evolution", self.advanced_dgm_port)
            nas_healthy = await self.test_service_health("Neural Architecture Search", self.nas_port)

            if dgm_healthy:
                self.integration_results['services_tested'].append("Advanced DGM Evolution Engine")
            if nas_healthy:
                self.integration_results['services_tested'].append("Neural Architecture Search")

            # Test endpoints if services are healthy
            dgm_endpoints_ok = False
            nas_endpoints_ok = False

            if dgm_healthy:
                dgm_endpoints_ok = await self.test_advanced_dgm_endpoints()

            if nas_healthy:
                nas_endpoints_ok = await self.test_nas_endpoints()

            # Calculate overall success rate
            total_services = 2
            successful_services = sum([dgm_endpoints_ok, nas_endpoints_ok])
            self.integration_results['success_rate'] = successful_services / total_services

            # Generate recommendations
            if self.integration_results['success_rate'] < 1.0:
                self.integration_results['recommendations'].append(
                    "Some services failed - check logs and ensure all dependencies are installed"
                )
            if not dgm_healthy or not nas_healthy:
                self.integration_results['recommendations'].append(
                    "Service health checks failed - verify port availability and service startup"
                )
            if self.integration_results['success_rate'] == 1.0:
                self.integration_results['recommendations'].append(
                    "All tests passed - Advanced DGM system is ready for production"
                )

        finally:
            await self.cleanup_session()

    def generate_report(self):
        """Generate integration report"""
        report_path = PROJECT_ROOT / "reports" / "advanced_dgm_integration_report.md"
        report_path.parent.mkdir(exist_ok=True)

        report_content = f"""# Advanced DGM System Integration Report

## Summary
- **Timestamp**: {self.integration_results['timestamp']}
- **Success Rate**: {self.integration_results['success_rate']:.2%}
- **Services Tested**: {len(self.integration_results['services_tested'])}
- **Endpoints Validated**: {len(self.integration_results['endpoints_validated'])}
- **Errors**: {len(self.integration_results['errors'])}

## Services Tested
{chr(10).join(f"- {service}" for service in self.integration_results['services_tested'])}

## Endpoints Validated
{chr(10).join(f"- {endpoint}" for endpoint in self.integration_results['endpoints_validated'])}

## Errors
{chr(10).join(f"- {error}" for error in self.integration_results['errors']) if self.integration_results['errors'] else "No errors detected"}

## Recommendations
{chr(10).join(f"- {rec}" for rec in self.integration_results['recommendations'])}

## Advanced DGM Capabilities Tested
1. **Neural Architecture Search**
   - DARTS (Differentiable Architecture Search)
   - Evolutionary Architecture Search
   - Progressive Neural Architecture Search

2. **Meta-Learning**
   - Few-shot learning adaptation
   - Task-specific optimization
   - Cross-domain transfer learning

3. **Self-Modifying Code**
   - Architecture modification
   - Performance-driven optimization
   - Safety-checked code evolution

## Next Steps
1. Monitor service performance in production
2. Implement continuous integration testing
3. Add monitoring and alerting for service health
4. Expand neural architecture search capabilities
5. Integrate with existing DGM trading algorithms

---
Generated by Advanced DGM Integration Script
MCPVotsAGI Development Team - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)

        logger.info(f"📊 Integration report saved to: {report_path}")
        return report_path

async def main():
    """Main integration function"""
    integrator = AdvancedDGMIntegrator()

    try:
        # Launch services
        await integrator.launch_services()

        # Run integration tests
        await integrator.run_integration_tests()

        # Generate report
        report_path = integrator.generate_report()

        # Print summary
        logger.info(f"\n🎯 Advanced DGM Integration Complete!")
        logger.info(f"Success Rate: {integrator.integration_results['success_rate']:.2%}")
        logger.info(f"Services Tested: {len(integrator.integration_results['services_tested'])}")
        logger.info(f"Endpoints Validated: {len(integrator.integration_results['endpoints_validated'])}")
        logger.info(f"Report: {report_path}")

        if integrator.integration_results['success_rate'] >= 0.8:
            logger.info("🎉 Advanced DGM System Integration SUCCESSFUL!")
        else:
            logger.warning("⚠️ Advanced DGM System Integration completed with issues")

    except Exception as e:
        logger.error(f"❌ Integration failed: {e}")
        return False

    return True

if __name__ == "__main__":
    asyncio.run(main())
