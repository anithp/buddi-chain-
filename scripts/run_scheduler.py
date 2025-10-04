#!/usr/bin/env python3
"""Script to run the conversation scheduler."""

import sys
import os
import asyncio
import signal
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.scheduler import scheduler


async def main():
    """Main function to run the scheduler."""
    print("🎯 Buddi Tokenization PoC - Conversation Scheduler")
    print("=" * 60)
    print("🔄 Starting periodic conversation fetcher...")
    print("⏰ Fetch interval: 2 hours")
    print("📊 Max conversations per fetch: 50")
    print("🛑 Press Ctrl+C to stop")
    print("=" * 60)
    
    # Set up signal handler for graceful shutdown
    def signal_handler(signum, frame):
        print("\n🛑 Shutdown signal received...")
        asyncio.create_task(scheduler.stop_scheduler())
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Start the scheduler
        await scheduler.start_scheduler()
    except KeyboardInterrupt:
        print("\n🛑 Keyboard interrupt received")
    except Exception as e:
        print(f"❌ Scheduler error: {e}")
    finally:
        await scheduler.stop_scheduler()
        print("👋 Scheduler stopped")


if __name__ == "__main__":
    asyncio.run(main())
