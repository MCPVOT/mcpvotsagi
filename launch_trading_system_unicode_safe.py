#!/usr/bin/env python3
"""
Ultimate Trading System V3 - Unicode-Safe Launch Script
======================================================
🚀 Fixed launcher with Unicode-safe logging and proper error handling
"""

import asyncio
import logging
import sys
import os
import subprocess
import time
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Configure Unicode-safe logging
class UnicodeStreamHandler(logging.StreamHandler):
    """Custom stream handler that handles Unicode characters safely"""

    def emit(self, record):
        try:
            # Replace emojis with safe equivalents
            if hasattr(record, 'msg'):
                record.msg = self._make_safe(str(record.msg))
            super().emit(record)
        except UnicodeEncodeError:
            # Fallback: strip non-ASCII characters
            record.msg = self._ascii_safe(str(record.msg))
            super().emit(record)

    def _make_safe(self, text):
        """Replace emojis with safe equivalents"""
        replacements = {
            '🚀': '[ROCKET]',
            '📁': '[FOLDER]',
            '🔍': '[SEARCH]',
            '🪐': '[PLANET]',
            '✅': '[OK]',
            '❌': '[ERROR]',
            '🔧': '[TOOLS]',
            '📊': '[CHART]',
            '🧠': '[BRAIN]',
            '💰': '[MONEY]',
            '📈': '[STATS]',
            '🏥': '[HEALTH]',
            '💎': '[DIAMOND]',
            '🧪': '[TEST]',
            '🌐': '[WEB]',
            '⚡': '[BOLT]',
            '🔄': '[REFRESH]',
            '📋': '[CLIPBOARD]',
            '🔗': '[LINK]',
            '🎯': '[TARGET]',
            '🌟': '[STAR]',
            '⭐': '[STAR]',
            '🔥': '[FIRE]',
            '💪': '[STRONG]',
            '🎨': '[ART]',
            '🛠️': '[TOOLS]',
            '📡': '[ANTENNA]',
            '🌊': '[WAVE]',
            '🎉': '[PARTY]',
            '🎊': '[CONFETTI]',
            '🏆': '[TROPHY]',
            '💯': '[100]',
            '🔮': '[CRYSTAL]',
            '🌈': '[RAINBOW]',
            '⚙️': '[GEAR]',
            '🔒': '[LOCK]',
            '🔓': '[UNLOCK]',
            '🆕': '[NEW]',
            '🆙': '[UP]',
            '🔄': '[CYCLE]',
            '🌍': '[EARTH]',
            '🌎': '[GLOBE]',
            '🌏': '[ASIA]',
            '🔊': '[SOUND]',
            '🔕': '[MUTE]',
            '🔆': '[BRIGHT]',
            '🔅': '[DIM]',
            '⚡': '[LIGHTNING]',
            '🔋': '[BATTERY]',
            '🔌': '[PLUG]',
            '💻': '[LAPTOP]',
            '🖥️': '[DESKTOP]',
            '📱': '[PHONE]',
            '⌚': '[WATCH]',
            '📟': '[PAGER]',
            '☎️': '[PHONE]',
            '📞': '[HANDSET]',
            '📠': '[FAX]',
            '📺': '[TV]',
            '📻': '[RADIO]',
            '🎙️': '[MIC]',
            '🎚️': '[SLIDER]',
            '🎛️': '[CONTROL]',
            '🧭': '[COMPASS]',
            '⏰': '[ALARM]',
            '⏲️': '[TIMER]',
            '⏱️': '[STOPWATCH]',
            '⏳': '[HOURGLASS]',
            '⌛': '[SAND]',
            '📅': '[CALENDAR]',
            '📆': '[TEAR-OFF]',
            '🗓️': '[SPIRAL]',
            '📇': '[CARD]',
            '📋': '[CLIPBOARD]',
            '📌': '[PIN]',
            '📍': '[LOCATION]',
            '📎': '[CLIP]',
            '🖇️': '[PAPERCLIP]',
            '📐': '[RULER]',
            '📏': '[STRAIGHT]',
            '📖': '[BOOK]',
            '📚': '[BOOKS]',
            '📝': '[MEMO]',
            '📄': '[PAGE]',
            '📃': '[CURL]',
            '📑': '[TABS]',
            '📊': '[BAR]',
            '📈': '[TRENDING]',
            '📉': '[DECLINING]',
            '📜': '[SCROLL]',
            '📋': '[CLIPBOARD]',
            '📌': '[PIN]',
            '📍': '[ROUND]',
            '📎': '[PAPERCLIP]',
            '🖇️': '[LINKED]',
            '📐': '[TRIANGULAR]',
            '📏': '[STRAIGHT]',
            '✂️': '[SCISSORS]',
            '🗃️': '[FILING]',
            '🗂️': '[DIVIDERS]',
            '🗄️': '[CABINET]',
            '🗑️': '[TRASH]',
            '🔒': '[LOCKED]',
            '🔓': '[UNLOCKED]',
            '🔏': '[LOCKED-INK]',
            '🔐': '[LOCKED-KEY]',
            '🔑': '[KEY]',
            '🗝️': '[OLD-KEY]',
            '🔨': '[HAMMER]',
            '⛏️': '[PICKAXE]',
            '⚒️': '[HAMMER-PICK]',
            '🛠️': '[HAMMER-WRENCH]',
            '🗡️': '[DAGGER]',
            '⚔️': '[CROSSED]',
            '🏹': '[BOW]',
            '🛡️': '[SHIELD]',
            '🔧': '[WRENCH]',
            '🔩': '[NUT-BOLT]',
            '⚙️': '[GEAR]',
            '🗜️': '[CLAMP]',
            '⚖️': '[BALANCE]',
            '🔗': '[LINK]',
            '⛓️': '[CHAINS]',
            '🧰': '[TOOLBOX]',
            '🧲': '[MAGNET]',
            '⚗️': '[ALEMBIC]',
            '🧪': '[TEST-TUBE]',
            '🧫': '[PETRI]',
            '🧬': '[DNA]',
            '🔬': '[MICROSCOPE]',
            '🔭': '[TELESCOPE]',
            '📡': '[SATELLITE]',
            '💉': '[SYRINGE]',
            '💊': '[PILL]',
            '🩹': '[BANDAGE]',
            '🩺': '[STETHOSCOPE]',
            '🚪': '[DOOR]',
            '🛏️': '[BED]',
            '🛋️': '[COUCH]',
            '🪑': '[CHAIR]',
            '🚽': '[TOILET]',
            '🚿': '[SHOWER]',
            '🛁': '[BATHTUB]',
            '🧴': '[LOTION]',
            '🧷': '[SAFETY-PIN]',
            '🧹': '[BROOM]',
            '🧺': '[BASKET]',
            '🧻': '[ROLL]',
            '🧼': '[SOAP]',
            '🧽': '[SPONGE]',
            '🧯': '[EXTINGUISHER]',
            '🛒': '[CART]',
            '🚬': '[CIGARETTE]',
            '⚰️': '[COFFIN]',
            '⚱️': '[URN]',
            '🗿': '[STATUE]',
            '🔌': '[PLUG]',
            '🔋': '[BATTERY]',
            '🔆': '[BRIGHT]',
            '🔅': '[DIM]',
            '🔊': '[LOUD]',
            '🔉': '[MEDIUM]',
            '🔈': '[SOFT]',
            '🔇': '[MUTED]',
            '🔔': '[BELL]',
            '🔕': '[NO-BELL]',
            '🎶': '[NOTES]',
            '🎵': '[NOTE]',
            '🎤': '[MICROPHONE]',
            '🎧': '[HEADPHONE]',
            '📻': '[RADIO]',
            '🎷': '[SAXOPHONE]',
            '🎸': '[GUITAR]',
            '🎹': '[PIANO]',
            '🎺': '[TRUMPET]',
            '🎻': '[VIOLIN]',
            '🥁': '[DRUM]',
            '🎪': '[CIRCUS]',
            '🎨': '[PALETTE]',
            '🎬': '[CLAPPER]',
            '🎭': '[MASKS]',
            '🎪': '[TENT]',
            '🎟️': '[TICKET]',
            '🎫': '[ADMISSION]',
            '🎗️': '[RIBBON]',
            '🏆': '[TROPHY]',
            '🏅': '[MEDAL]',
            '🥇': '[GOLD]',
            '🥈': '[SILVER]',
            '🥉': '[BRONZE]',
            '⚽': '[SOCCER]',
            '🏀': '[BASKETBALL]',
            '🏈': '[FOOTBALL]',
            '⚾': '[BASEBALL]',
            '🥎': '[SOFTBALL]',
            '🎾': '[TENNIS]',
            '🏐': '[VOLLEYBALL]',
            '🏉': '[RUGBY]',
            '🎱': '[POOL]',
            '🏓': '[PING-PONG]',
            '🏸': '[BADMINTON]',
            '🥅': '[GOAL]',
            '⛳': '[GOLF]',
            '🏌️': '[GOLFER]',
            '🏌️‍♂️': '[MALE-GOLFER]',
            '🏌️‍♀️': '[FEMALE-GOLFER]',
            '🎣': '[FISHING]',
            '🎽': '[RUNNING]',
            '🎿': '[SKIS]',
            '🛷': '[SLED]',
            '🥌': '[CURLING]',
            '🎯': '[BULLSEYE]',
            '🎮': '[CONTROLLER]',
            '🕹️': '[JOYSTICK]',
            '🎰': '[SLOT]',
            '🃏': '[JOKER]',
            '🀄': '[MAHJONG]',
            '🎴': '[HANAFUDA]',
            '🎲': '[DICE]',
            '🎳': '[BOWLING]',
            '🎯': '[DART]',
            '🎺': '[TRUMPET]',
            '🎷': '[SAX]',
            '🎸': '[GUITAR]',
            '🎹': '[KEYBOARD]',
            '🎻': '[VIOLIN]',
            '🥁': '[DRUMS]',
            '🎤': '[MIC]',
            '🎧': '[HEADPHONES]',
            '📻': '[RADIO]',
            '🎼': '[SCORE]',
            '🎵': '[MUSICAL-NOTE]',
            '🎶': '[MUSICAL-NOTES]',
            '🎙️': '[STUDIO-MIC]',
            '🎚️': '[LEVEL-SLIDER]',
            '🎛️': '[CONTROL-KNOBS]',
            '🎟️': '[ADMISSION-TICKET]',
            '🎫': '[TICKET]',
            '🎗️': '[REMINDER-RIBBON]',
            '🏆': '[TROPHY]',
            '🏅': '[SPORTS-MEDAL]',
            '🥇': '[GOLD-MEDAL]',
            '🥈': '[SILVER-MEDAL]',
            '🥉': '[BRONZE-MEDAL]',
            '⚽': '[SOCCER-BALL]',
            '🏀': '[BASKETBALL]',
            '🏈': '[AMERICAN-FOOTBALL]',
            '⚾': '[BASEBALL]',
            '🥎': '[SOFTBALL]',
            '🎾': '[TENNIS]',
            '🏐': '[VOLLEYBALL]',
            '🏉': '[RUGBY-FOOTBALL]',
            '🎱': '[POOL-8-BALL]',
            '🏓': '[PING-PONG]',
            '🏸': '[BADMINTON]',
            '🥅': '[GOAL-NET]',
            '⛳': '[FLAG-IN-HOLE]',
            '🏌️': '[PERSON-GOLFING]',
            '🏌️‍♂️': '[MAN-GOLFING]',
            '🏌️‍♀️': '[WOMAN-GOLFING]',
            '🎣': '[FISHING-POLE]',
            '🎽': '[RUNNING-SHIRT]',
            '🎿': '[SKIS]',
            '🛷': '[SLED]',
            '🥌': '[CURLING-STONE]',
            '🎯': '[DIRECT-HIT]',
            '🎮': '[VIDEO-GAME]',
            '🕹️': '[JOYSTICK]',
            '🎰': '[SLOT-MACHINE]',
            '🃏': '[JOKER]',
            '🀄': '[MAHJONG-RED]',
            '🎴': '[FLOWER-CARDS]',
            '🎲': '[GAME-DIE]',
            '🎳': '[BOWLING]',
            '🎯': '[BULLSEYE]',
            '🎺': '[TRUMPET]',
            '🎷': '[SAXOPHONE]',
            '🎸': '[GUITAR]',
            '🎹': '[MUSICAL-KEYBOARD]',
            '🎻': '[VIOLIN]',
            '🥁': '[DRUM]',
            '🎤': '[MICROPHONE]',
            '🎧': '[HEADPHONE]',
            '📻': '[RADIO]',
            '🎼': '[MUSICAL-SCORE]',
            '🎵': '[MUSICAL-NOTE]',
            '🎶': '[MUSICAL-NOTES]',
            '🎙️': '[STUDIO-MICROPHONE]',
            '🎚️': '[LEVEL-SLIDER]',
            '🎛️': '[CONTROL-KNOBS]',
            '🎟️': '[ADMISSION-TICKETS]',
            '🎫': '[TICKET]',
            '🎗️': '[REMINDER-RIBBON]',
        }

        for emoji, replacement in replacements.items():
            text = text.replace(emoji, replacement)

        return text

    def _ascii_safe(self, text):
        """Remove non-ASCII characters as last resort"""
        return ''.join(char for char in text if ord(char) < 128)

# Configure logging with Unicode-safe handler
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('F:/ULTIMATE_AGI_DATA/RL_TRADING/system_launcher.log', encoding='utf-8'),
        UnicodeStreamHandler()
    ]
)
logger = logging.getLogger("SystemLauncher")

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Import fixed components
try:
    from jupiter_api_wrapper_fixed import JupiterAPIWrapper
    from jupiter_rl_integration import JupiterRLIntegration
    from ultimate_trading_system_v3 import UltimateTradingSystemV3
    from ultimate_trading_dashboard_v3_fixed import UltimateTradingDashboard
    HAS_COMPONENTS = True
except ImportError as e:
    logger.error(f"Failed to import components: {e}")
    HAS_COMPONENTS = False

class FixedTradingSystemLauncher:
    """Fixed trading system launcher with Unicode-safe logging"""

    def __init__(self):
        self.f_drive_path = "F:/ULTIMATE_AGI_DATA/RL_TRADING/"
        self.workspace_path = Path(__file__).parent
        self.components = {}
        self.status = {
            "system_started": False,
            "components_status": {},
            "start_time": None,
            "errors": []
        }

        # Ensure F: drive structure
        self._ensure_f_drive_structure()

        logger.info("[ROCKET] Fixed Ultimate Trading System V3 Launcher initialized")

    def _ensure_f_drive_structure(self):
        """Ensure F: drive directory structure exists"""
        directories = [
            "F:/ULTIMATE_AGI_DATA/RL_TRADING/",
            "F:/ULTIMATE_AGI_DATA/RL_TRADING/models/",
            "F:/ULTIMATE_AGI_DATA/RL_TRADING/data/",
            "F:/ULTIMATE_AGI_DATA/RL_TRADING/logs/",
            "F:/ULTIMATE_AGI_DATA/RL_TRADING/backups/",
            "F:/ULTIMATE_AGI_DATA/RL_TRADING/dashboard_static/",
            "F:/ULTIMATE_AGI_DATA/RL_TRADING/dashboard_templates/",
            "F:/ULTIMATE_AGI_DATA/CHAT_MEMORY/",
            "F:/ULTIMATE_AGI_DATA/KNOWLEDGE_GRAPH/",
            "F:/ULTIMATE_AGI_DATA/SYSTEM_LOGS/",
            "F:/ULTIMATE_AGI_DATA/CONFIG/",
            "F:/ULTIMATE_AGI_DATA/BACKUPS/"
        ]

        for directory in directories:
            os.makedirs(directory, exist_ok=True)

        logger.info("[FOLDER] F: drive structure ensured")

    async def check_dependencies(self) -> bool:
        """Check if all required dependencies are available"""
        try:
            logger.info("[SEARCH] Checking system dependencies...")

            # Check if Jupiter API is accessible
            if HAS_COMPONENTS:
                async with JupiterAPIWrapper() as jupiter:
                    health = await jupiter.health_check()
                    logger.info(f"[PLANET] Jupiter API: {'[OK] HEALTHY' if health else '[ERROR] UNHEALTHY'}")
                    return health
            else:
                logger.error("[ERROR] Components not available")
                return False

        except Exception as e:
            logger.error(f"[ERROR] Dependency check failed: {e}")
            return False

    async def initialize_components(self) -> bool:
        """Initialize all system components"""
        try:
            logger.info("[TOOLS] Initializing system components...")

            if not HAS_COMPONENTS:
                logger.error("[ERROR] Components not available")
                return False

            # Initialize Jupiter API
            self.components["jupiter_api"] = JupiterAPIWrapper()
            logger.info("[OK] Jupiter API initialized")

            # Initialize RL Integration
            self.components["jupiter_rl"] = JupiterRLIntegration()
            logger.info("[OK] Jupiter RL initialized")

            # Initialize Trading System
            self.components["trading_system"] = UltimateTradingSystemV3()
            logger.info("[OK] Trading System initialized")

            # Initialize Dashboard
            self.components["dashboard"] = UltimateTradingDashboard()
            logger.info("[OK] Dashboard initialized")

            return True

        except Exception as e:
            logger.error(f"[ERROR] Component initialization failed: {e}")
            return False

    async def start_system(self) -> bool:
        """Start the complete trading system"""
        try:
            logger.info("[ROCKET] Starting Ultimate Trading System V3...")

            # Check dependencies
            if not await self.check_dependencies():
                logger.error("[ERROR] Dependency check failed")
                return False

            # Initialize components
            if not await self.initialize_components():
                logger.error("[ERROR] Component initialization failed")
                return False

            # Start dashboard
            if "dashboard" in self.components:
                try:
                    await self.components["dashboard"].start_server()
                    logger.info("[OK] Dashboard server started")
                except Exception as e:
                    logger.error(f"[ERROR] Dashboard startup failed: {e}")
                    return False

            # Start trading system
            if "trading_system" in self.components:
                try:
                    await self.components["trading_system"].start()
                    logger.info("[OK] Trading System started")
                except Exception as e:
                    logger.error(f"[ERROR] Trading System startup failed: {e}")
                    return False

            self.status["system_started"] = True
            self.status["start_time"] = datetime.now()
            logger.info("[OK] Ultimate Trading System V3 started successfully!")

            return True

        except Exception as e:
            logger.error(f"[ERROR] System startup failed: {e}")
            return False

    async def stop_system(self) -> bool:
        """Stop all system components"""
        try:
            logger.info("[ROCKET] Stopping Ultimate Trading System V3...")

            for name, component in self.components.items():
                try:
                    if hasattr(component, 'stop'):
                        await component.stop()
                        logger.info(f"[OK] {name} stopped")
                    elif hasattr(component, 'close'):
                        await component.close()
                        logger.info(f"[OK] {name} closed")
                except Exception as e:
                    logger.error(f"[ERROR] Failed to stop {name}: {e}")

            self.status["system_started"] = False
            logger.info("[OK] Ultimate Trading System V3 stopped")

            return True

        except Exception as e:
            logger.error(f"[ERROR] System shutdown failed: {e}")
            return False

    def get_status(self) -> Dict:
        """Get system status"""
        return {
            "system_started": self.status["system_started"],
            "start_time": self.status["start_time"].isoformat() if self.status["start_time"] else None,
            "components": list(self.components.keys()),
            "errors": self.status["errors"]
        }

    async def run(self):
        """Main run method"""
        try:
            logger.info("[ROCKET] ULTIMATE TRADING SYSTEM V3 - UNICODE-SAFE LAUNCHER")
            logger.info("=" * 60)

            if await self.start_system():
                logger.info("[OK] System started successfully!")
                logger.info("[WEB] Dashboard available at: http://localhost:8050")
                logger.info("[TARGET] Trading System active")
                logger.info("[STAR] Press Ctrl+C to stop")

                # Keep running
                try:
                    while True:
                        await asyncio.sleep(1)
                except KeyboardInterrupt:
                    logger.info("[STOP] Received stop signal")
                    await self.stop_system()
            else:
                logger.error("[ERROR] System failed to start")
                logger.error("[CLIPBOARD] Check logs for details")

        except Exception as e:
            logger.error(f"[ERROR] Launcher failed: {e}")
            await self.stop_system()

async def main():
    """Main entry point"""
    launcher = FixedTradingSystemLauncher()
    await launcher.run()

if __name__ == "__main__":
    asyncio.run(main())
