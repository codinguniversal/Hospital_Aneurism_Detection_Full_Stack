import asyncio
from app.dependencies import build_notification_service

async def main():
    print("Firing real HTTP API email via dynamic factory...")
    
    # This uses your reflection mechanism perfectly
    service = build_notification_service() 
    
    success = await service.send_urgent_alert(scan_id="scan_DYNAMIC_123", probability=0.94)
    print(f"Execution finished! Status: {'Success' if success else 'Failed'}")

if __name__ == "__main__":
    asyncio.run(main())