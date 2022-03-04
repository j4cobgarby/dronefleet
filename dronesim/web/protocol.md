# Protocol for communication between the drone server and the control panel using WebSockets

The drone server shall host a websocket server at port 13254, and an arbitrary number of control panels should be able to connect to it as clients.

## Messages from server to client

### Drone translation update

This message allows the server to inform all the clients of where the drones being controlled are. For this, a JSON message of the following format is sent:

```json
{
    drones_count: <amount of drones>,
    drones: [
        {
            id: <this drone's ID>,
            pos: [<x>, <y>, <z>],
            rot: [<yaw>, <pitch>, <roll>],
        },
         . . .
    ]
}
```

## Messages from client to server

### Control Request

This message allows a client control panel to order a specific drone to a specific setpoint.

```json
{
    drone_id: <target drone ID>,
    target_pos: [<x>, <y>, <z>],
    target_rot: [<yaw>, <pitch>, <roll>]
}
```