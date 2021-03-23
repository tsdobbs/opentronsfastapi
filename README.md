# bot-host
Bot-Host is a hosting tool that allows parameterized job execution commands to be sent directly to an Opentrons OT2 liquid handling robot over HTTP via an API. Execution of the job begins immediately, allowing the OT2 to work as part of a larger automated lab management system, or simply allowing the user to build a user interface that suits their needs better than the stock options Opentrons provides.

If the components of a robot procedure being executed in a bio-foundry are as follows:  
1. A job queue that lists the tasks to be done
2. A system-level execution manager that decides what job to do next and passes the job to an appropriate robot
3. A client on the robot that receives job requests and, if accepted, initiates execution on the robot
4. A low-level layer that converts job instructions to the actuation of motors
Bot-Host is #3

## Features
Bot-Host:
- Exposes an API for passing parameters to a defined robot procedure, which is then executed (e.g. "Pipette 100ul from Well A1 to Well _X_", where _X_ is passed as a parameter)
- Manages robot state - if the robot is busy, then job requests are refused until the robot work is complete, and an error code is returned to the requestor
- Can report the state of the robot to a requestor, via API endpoint
- Can report the protocol version the robot will use, in the form of a unique hash, via an API endpoint
- Allows the API to be accessed by any arbitrary tool, as long as POST requests are sent in the right format
- Can be deployed on stock OT2's without special tools
- Works at the level of a single robot, and is naive of other robots. However, it can be deployed on multiple robots, which can then be managed by a supervisor.

## Use
The user is required to write their own procedures in the ```procedures.py``` file. These procedures should accept parameters, which will be passed in by Bot-Host. The entire repository contents should then be copied onto the Raspberry Pi that runs the OT2. This will allow the server to accept requests over HTTP.

// Console-based installation instructions, details about file structure and server TK