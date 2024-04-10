# Pool Game Physics Simulator

## Description

This project simulates the physics of a pool game using a multi-language approach, incorporating **JavaScript**, **C**, and **Python**. The core physics engine is written in C for performance reasons, leveraging the speed and efficiency of compiled code. Python is used for higher-level simulation control, database interactions, and generating SVG (Scalable Vector Graphics) representations of the game state. JavaScript, along with HTML and CSS, provides a dynamic and interactive front-end, allowing users to visualize the simulation in a web browser.

## Features

- Physics simulation of pool ball dynamics, including collisions, rolling, and stopping.
- SVG generation for game state visualization.
- A web interface for interaction with the simulation.
- Database integration for storing game states and outcomes.

## Installation

### Prerequisites

- GCC (GNU Compiler Collection) for compiling C code.
- Python 3.11, along with the following packages:
  - `sqlite3` for database operations.
- swig (for converting C code for Python)
- clang (for C)
- Make (for makefile)
- A modern web browser capable of running JavaScript and displaying SVG.

### Setup

1. **Compile the Library:**

    Navigate to the directory containing the folder and compile the library:
    make
    export LD_LIBRARY_PATH=$(pwd)


3. **Run the Web Interface:**
    python3 server.py

    Open the `start.html` file in your web browser to start interacting with the simulation.
    e.g: 127.0.0.1:8085/start.html

    Zoom out on browser for best experience.

## Usage

- Use the mouse to interact with the balls on the table through the web interface.
- The simulation runs automatically upon interaction, with the current game state visualized in SVG format.


## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Credit:
Stefan Kremer (for phylib.i) swig file.
