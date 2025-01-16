import asyncio
import websockets
import json


async def test_websocket():
    # Define WebSocket URL
    room_name = "1"  # Example room name
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzM0MjUwMzk3LCJpYXQiOjE3MzQyNTAwOTcsImp0aSI6ImNjZWRmZTE3NjkxMjQ1MTg4YWY1ODIyOTYxMDAyMjBjIiwidXNlcl9pZCI6Mn0.A19F4Cw81tHjdrFMZGsP0U_vFHUZluEspE8D1ar9sI0"  # Replace with your JWT token
    # websocket_url = f"ws://localhost:8000/ws/chat/?token={token}"
    websocket_url = f"ws://192.168.150.18:8000/ws/chat/?token={token}&receipent=2"

    try:
        # Connect to the WebSocket
        async with websockets.connect(websocket_url) as websocket:
            print("Connected to WebSocket")

            # Send a test message
            message = {
                "type": "chat_message",  # Ensure it matches your server's expected format
                "message": "Hello, WebSocket!",
                "attachment": None,  # Can add attachment as {"data": "...", "format": "png"}
            }
            await websocket.send(json.dumps(message))
            print(f"Sent: {message}")

            # Receive and print response
            response = await websocket.recv()
            print(f"Received: {response}")

    except websockets.exceptions.ConnectionClosedError as e:
        print(f"Connection closed with error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


# Run the test
asyncio.run(test_websocket())
