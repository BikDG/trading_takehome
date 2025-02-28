# Trading Simulation Engine

## Overview

This project is a trading simulation engine that emulates a dynamic, concurrent trading environment. It features:
- **Order Matching**: Efficient matching using priority queues.
- **Auctions**: Bots can initiate auctions and buyers can place bids.
- **Asynchronous Bot Trading**: Multiple bots trade concurrently with dynamically adjusting price thresholds.
- **Trade Visualization**: Generates a graph tracking trade history for all commodities.
- **Containerized Deployment**: Easily run the simulation in a Docker container via Docker Compose.

## Features

- **Order Matching Engine**  
  Uses heaps (priority queues) for fast matching of buy and sell orders.

- **Dynamic Auctions**  
  Some seller bots initiate auctions, and buyer bots place bids on active auctions. An AuctionManager finalizes auctions when their duration expires.

- **Asynchronous Trading Bots**  
  Bots continuously trade and adjust their price thresholds if orders time out.

- **Visualization**  
  At the end of the simulation, a graph is generated (saved as `trade_history.png`) that tracks the price evolution for all commodities.

- **Dockerized**  
  The project includes a Dockerfile and docker-compose configuration to run the simulation inside a container.

## Requirements

- **Python**: Version 3.9 or higher  
- **Dependencies**:  
  - `matplotlib` (for visualization)  
  - Other standard libraries are used (e.g., `threading`, `heapq`, `time`)
- **Docker & Docker Compose** (if you prefer containerized deployment)

## Setup

### Local Development

1. **Create and Activate a Virtual Environment**  
   ```
   python3 -m venv .venv
   source .venv/bin/activate
   ``` 
2. **Install Dependencies**
   ```
   pip install -r scripts/requirements.txt
   ```
3. **Run the Simulation**
   ```
   python main.py
   ```

### Docker Deployment
1. **First Time Setup**
   ```
   chmod -R 777 output
   ```
2. **Build and Run the Container**
   ```
   docker-compose up --build
   ```

## Project Workflow
- Trading Engine (engine.py): Manages order books, order placement, matching, and trade history.
- Order Book (order_book.py): Implements matching logic using heaps.
- Auctions (auction.py): Provides classes for auctions and auction management.
- Bots (bot.py): Implements asynchronous trading bots that either place regular orders or participate in auctions.
- Utilities (utils.py): Contains helper functions for generating products and creating bots.
- Visualization (visualization.py): Generates a graph of trade history for all commodities.
- Main Entry Point (main.py): Ties everything together, starts the simulation, and manages shutdown.

## Stopping the Simulation
The simulation runs asynchronously. When the simulation duration ends, a global flag stops all bot activities immediately, and any pending orders are canceled.

## Output
Trade History Graph: At the end of the simulation, a graph (trade_history.png) is generated in the project root (or output/ directory if running in docker) showing the price history for all commodities.
