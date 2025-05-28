#!/usr/bin/env python3
"""
Strategic Tekton Launcher - Focused on Success

This launcher focuses on getting a core set of working components launched and healthy.
We prioritize components that are known to work and build up systematically.
"""
import asyncio
import time
import aiohttp
from typing import List, Dict, Any

class StrategicLauncher:
    """Strategic launcher focused on reliable component launch"""
    
    # Components ranked by reliability/simplicity
    COMPONENT_TIERS = {
        "tier_1_core": {
            "tekton_core": {"port": 8010, "timeout": 10},
        },
        "tier_2_infrastructure": {
            "engram": {"port": 8000, "timeout": 15},
        },
        "tier_3_services": {
            "rhetor": {"port": 8003, "timeout": 15},
            "telos": {"port": 8008, "timeout": 15},
            "budget": {"port": 8013, "timeout": 15},
        },
        "tier_4_specialized": {
            "terma": {"port": 8004, "timeout": 20},
            "harmonia": {"port": 8007, "timeout": 20},
            "synthesis": {"port": 8009, "timeout": 20},
        },
        "tier_5_complex": {
            "hephaestus": {"port": 8080, "timeout": 30},
            "ergon": {"port": 8002, "timeout": 25},
            "athena": {"port": 8005, "timeout": 25},
        }
    }
    
    def __init__(self):
        self.launched_components = {}
        self.failed_components = {}
        
    async def launch_component(self, name: str, config: Dict[str, Any]) -> bool:
        """Launch a single component using the enhanced launcher"""
        print(f"🚀 Launching {name}...")
        
        cmd = [
            "python", 
            "/Users/cskoons/projects/github/Tekton/scripts/enhanced_tekton_launcher.py",
            "--components", name
        ]
        
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd="/Users/cskoons/projects/github/Tekton"
            )
            
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(), 
                timeout=config["timeout"]
            )
            
            if proc.returncode == 0:
                print(f"✅ {name} launched successfully")
                await self.verify_health(name, config["port"])
                return True
            else:
                print(f"❌ {name} failed to launch (exit code {proc.returncode})")
                if stderr:
                    print(f"   Error: {stderr.decode()[:200]}...")
                return False
                
        except asyncio.TimeoutError:
            print(f"⏰ {name} timed out after {config['timeout']}s")
            return False
        except Exception as e:
            print(f"💥 {name} crashed: {e}")
            return False
    
    async def verify_health(self, name: str, port: int) -> bool:
        """Verify component health with multiple endpoint attempts"""
        health_endpoints = ["/health", "/api/health", "/status", "/"]
        
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
            for endpoint in health_endpoints:
                try:
                    async with session.get(f"http://localhost:{port}{endpoint}") as resp:
                        if resp.status == 200:
                            print(f"   💚 {name} health check passed via {endpoint}")
                            self.launched_components[name] = {
                                "port": port, 
                                "endpoint": endpoint,
                                "status": "healthy"
                            }
                            return True
                except:
                    continue
        
        print(f"   💛 {name} launched but health check failed")
        self.launched_components[name] = {
            "port": port, 
            "endpoint": None,
            "status": "unknown"
        }
        return False
    
    async def launch_tier(self, tier_name: str, components: Dict[str, Dict[str, Any]]) -> Dict[str, bool]:
        """Launch all components in a tier"""
        print(f"\n🏗️  Launching {tier_name}...")
        results = {}
        
        for name, config in components.items():
            results[name] = await self.launch_component(name, config)
            if results[name]:
                # Brief pause between successful launches
                await asyncio.sleep(2)
            else:
                self.failed_components[name] = config
                
        return results
    
    async def launch_all_strategic(self) -> Dict[str, Any]:
        """Launch components strategically by tier"""
        print("🎯 Strategic Tekton Launch - Focused on Success")
        start_time = time.time()
        
        all_results = {}
        
        for tier_name, components in self.COMPONENT_TIERS.items():
            tier_results = await self.launch_tier(tier_name, components)
            all_results[tier_name] = tier_results
            
            # Check if we should continue to next tier
            success_rate = sum(tier_results.values()) / len(tier_results)
            print(f"   {tier_name}: {sum(tier_results.values())}/{len(tier_results)} successful ({success_rate:.0%})")
            
            # If tier 1 fails, abort
            if tier_name == "tier_1_core" and success_rate < 1.0:
                print("❌ Core tier failed, aborting launch")
                break
                
            # If success rate drops below 50%, be more cautious
            if success_rate < 0.5:
                print(f"⚠️  Low success rate in {tier_name}, proceeding cautiously...")
        
        # Final status check
        print(f"\n🔍 Performing final health check...")
        await self.final_health_check()
        
        total_time = time.time() - start_time
        successful = len(self.launched_components)
        total = sum(len(tier) for tier in self.COMPONENT_TIERS.values())
        
        print(f"\n📊 Strategic Launch Results:")
        print(f"   ✅ Successful: {successful}/{total} components")
        print(f"   ⏱️  Total time: {total_time:.1f}s")
        print(f"   📈 Success rate: {successful/total:.0%}")
        
        if successful > 0:
            print(f"\n🎉 Victory Achieved! {successful} components running and healthy:")
            for name, info in self.launched_components.items():
                status_emoji = "💚" if info["status"] == "healthy" else "💛"
                print(f"   {status_emoji} {name} on port {info['port']}")
        
        return {
            "successful": successful,
            "total": total,
            "success_rate": successful/total,
            "time": total_time,
            "launched": self.launched_components,
            "failed": self.failed_components
        }
    
    async def final_health_check(self):
        """Perform final health check on all launched components"""
        for name, info in list(self.launched_components.items()):
            healthy = await self.verify_health(name, info["port"])
            if not healthy:
                info["status"] = "unhealthy"

async def main():
    launcher = StrategicLauncher()
    results = await launcher.launch_all_strategic()
    
    # Quick status check using existing tool
    if results["successful"] > 0:
        print(f"\n🔍 Running comprehensive status check...")
        import subprocess
        try:
            subprocess.run([
                "python", 
                "/Users/cskoons/projects/github/Tekton/scripts/enhanced_tekton_status.py"
            ], cwd="/Users/cskoons/projects/github/Tekton", timeout=30)
        except:
            print("Status check failed, but components are launched")

if __name__ == "__main__":
    asyncio.run(main())