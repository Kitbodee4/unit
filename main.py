from web3 import Web3
from eth_account import Account
from loguru import logger
import json
import time
import sys
import random
from concurrent.futures import ThreadPoolExecutor, as_completed

MAX_RETRIES = 5
RETRY_DELAY = 5  # seconds
TRANSACTION_COUNT = 1000
NUM_THREADS = 8  # Adjust this according to your needs
MIN_SLEEP = 1  # Minimum sleep time in seconds
MAX_SLEEP = 5  # Maximum sleep time in seconds

# Configure Loguru with color formatting
logger.remove()
logger.add(sys.stdout, format="<white>{time:YYYY-MM-DD HH:mm:ss}</white> | <level>{level: <8}</level> | <cyan><b>{line}</b></cyan> - <white><b>{message}</b></white>")
logger = logger.opt(colors=True)

def retry(func, max_retries=MAX_RETRIES, delay=RETRY_DELAY):
    for i in range(max_retries):
        try:
            return func()
        except Exception as e:
            if i == max_retries - 1:
                raise e
            logger.warning(f"<yellow>Error occurred. Retrying... ({i + 1}/{max_retries})</yellow>")
            time.sleep(delay)

def process_wallet(private_key, wallet_index):
    web3 = Web3(Web3.HTTPProvider('https://rpc-testnet.unit0.dev'))
    account = Account.from_key(private_key)
    sender_address = account.address

    try:
        balance = retry(lambda: web3.eth.get_balance(sender_address))
        logger.info(f"Wallet {wallet_index} - Balance: {web3.from_wei(balance, 'ether')} UNIT")
    except Exception as e:
        logger.error(f"Wallet {wallet_index} - Failed to check balance for {sender_address}. Skipping to next address. Error: <red>{e}</red>")
        return

    if balance < web3.to_wei(0.00000001, 'ether'):
        logger.warning(f"Wallet {wallet_index} - <yellow>Insufficient or zero balance. Skipping to next address.</yellow>")
        return

    nonce = web3.eth.get_transaction_count(sender_address)
    for i in range(TRANSACTION_COUNT):
        receiver_account = Account.create()
        receiver_address = receiver_account.address

        amount_to_send = web3.to_wei(round(random.uniform(0.000000001, 0.00000001), 10), 'ether')
        gas_price = web3.to_wei(round(random.uniform(0.0009, 0.0015), 9), 'gwei')

        transaction = {
            'to': receiver_address,
            'value': amount_to_send,
            'gas': 21000,
            'gasPrice': gas_price,
            'nonce': nonce,
            'chainId': 88817
        }
        nonce += 1

        try:
            signed_tx = account.sign_transaction(transaction)
            tx_hash = retry(lambda: web3.eth.send_raw_transaction(signed_tx.rawTransaction))
            time.sleep(10)

            receipt = retry(lambda: web3.eth.get_transaction_receipt(tx_hash))
            if receipt:
                if receipt['status'] == 1:
                    logger.success(f"Wallet {wallet_index} - <green><b>TX Hash: {web3.to_hex(tx_hash)}</b></green>")
                else:
                    logger.error(f"Wallet {wallet_index} - <red>Transaction FAILED</red>")
            else:
                logger.warning(f"Wallet {wallet_index} - <yellow>Transaction is still pending after multiple retries.</yellow>")
        except Exception as e:
            logger.error(f"Wallet {wallet_index} - Failed to send transaction: <red>{e}</red>")

    # Introduce random sleep time between wallet processing
    sleep_time = random.uniform(MIN_SLEEP, MAX_SLEEP)
    logger.info(f"Wallet {wallet_index} - <cyan>Sleeping for {sleep_time:.2f} seconds before processing next wallet...</cyan>")
    time.sleep(sleep_time)

def main():
    try:
        with open('privateKeys.json') as file:
            private_keys = json.load(file)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON. Please check the privateKeys.json file. Error: <red>{e}</red>")
        return
    except FileNotFoundError:
        logger.error("<red>privateKeys.json file not found. Please ensure the file exists.</red>")
        return

    with ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
        futures = [executor.submit(process_wallet, pk, index + 1) for index, pk in enumerate(private_keys)]
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                logger.error(f"An error occurred: <red>{e}</red>")

if __name__ == "__main__":
    main()
