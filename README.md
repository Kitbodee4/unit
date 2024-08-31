# Unit0 Testnet Interaction Script

## Overview

This Python script interacts with the Unit0 Testnet using the Web3 library to manage multiple wallets and execute transactions. It includes features for automatic retry on failure, detailed logging with color formatting, and random sleep intervals to manage transaction rates.

## Features

- **Multi-wallet Support**: Process transactions for multiple wallets.
- **Retry Mechanism**: Automatic retry for failed operations.
- **Detailed Logging**: Color-coded logging for better visibility.
- **Randomized Sleep**: Random sleep intervals to avoid rate limits.

## Installation

### Prerequisites

- Python 3.7 or later
- `pip` (Python package installer)

### Steps

1. **Clone the Repository:**

   ```sh
   git clone https://github.com/Kitbodee4/unit.git
   cd unit
   
2. **Install Dependencies:**

   ```sh
    pip install -r requirements.txt

3. **Configuration**

   Prepare privateKeys.json:
   Create a file named privateKeys.json in the root directory with the following format:
   ```sh
   [
    "0xYourPrivateKey1",
    "0xYourPrivateKey2",
    ...
   ]


5. **Run the Script:**

    ```sh
     screen -S  unit
     python main.py
