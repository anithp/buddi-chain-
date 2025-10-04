#!/usr/bin/env python3
"""Management script for the conversation scheduler."""

import sys
import os
import asyncio
import argparse
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.scheduler import scheduler


async def start_scheduler():
    """Start the scheduler."""
    print("🚀 Starting conversation scheduler...")
    await scheduler.start_scheduler()


async def stop_scheduler():
    """Stop the scheduler."""
    print("🛑 Stopping conversation scheduler...")
    await scheduler.stop_scheduler()


async def manual_fetch():
    """Run a manual fetch."""
    print("🔧 Running manual conversation fetch...")
    await scheduler.run_manual_fetch()
    print("✅ Manual fetch completed")


async def show_status():
    """Show scheduler status."""
    status = scheduler.get_status()
    print("📊 Scheduler Status:")
    print(f"   Running: {'Yes' if status['is_running'] else 'No'}")
    print(f"   Last fetch: {status['last_fetch_time'] or 'Never'}")
    print(f"   Fetch interval: {status['fetch_interval_hours']} hours")
    print(f"   Max conversations per fetch: {status['max_conversations_per_fetch']}")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Manage the conversation scheduler")
    parser.add_argument("command", choices=["start", "stop", "fetch", "status"], 
                       help="Command to execute")
    
    args = parser.parse_args()
    
    if args.command == "start":
        asyncio.run(start_scheduler())
    elif args.command == "stop":
        asyncio.run(stop_scheduler())
    elif args.command == "fetch":
        asyncio.run(manual_fetch())
    elif args.command == "status":
        asyncio.run(show_status())


if __name__ == "__main__":
    main()
