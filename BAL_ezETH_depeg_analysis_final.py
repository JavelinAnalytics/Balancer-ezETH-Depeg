from web3 import Web3
import json
from dune_client.client import DuneClient
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
import time
import matplotlib.pyplot as plt

#INFURA_KEY = "insert infura api key here"
#API_KEY = "insert dune api key here"

def get_rate_at_block(contract, block_number):
    try:
        rate = contract.functions.getRate().call(block_identifier=int(block_number))
        return rate / 10**18 
    except Exception as e:
        print(f"Error fetching rate at block {block_number}: {e}")
        return None

def fetch_rates(contract, df):
    block_numbers = df['block_number'].tolist()
    rates = []
    with ThreadPoolExecutor(max_workers=7) as executor:
        futures = []
        for block_number in block_numbers:
            futures.append(executor.submit(get_rate_at_block, contract, block_number))
            time.sleep(0.14)
        for future in futures:
            result = future.result()
            if result is not None:
                rates.append(result)
            else:
                raise ValueError("Missing rate data")
    return rates

def get_token_balances_at_block(contract, pool_id, block_number):
    try:
        result = contract.functions.getPoolTokens(pool_id).call(block_identifier=int(block_number))
        tokens, balances, lates_block = result
        token_balances = {tokens[i]: balances[i] / 10**18 for i in range(len(tokens))}
        return token_balances
    except Exception as e:
        print(f"Error fetching token balances at block {block_number}: {e}")
        return None

def fetch_balances(contract, pool_id, df):
    block_numbers = df['block_number'].tolist()
    balances = []
    with ThreadPoolExecutor(max_workers=7) as executor:
        futures = []
        for block_number in block_numbers:
            futures.append(executor.submit(get_token_balances_at_block, contract, pool_id, block_number))
            time.sleep(0.14)
        for future in futures:
            result = future.result()
            if result is not None:
                balances.append(result)
            else:
                raise ValueError("Missing balances data")
    return balances

def get_exchange_rate_at_block(contract, block_number):
    try:
        result = contract.functions.latestRoundData().call(block_identifier=int(block_number))
        return result[1] / 10**18
    except Exception as e:
        print(f"Error fetching exchange rate at block {block_number}: {e}")
        return None

def fetch_exchange_rates(contract, df):
    block_numbers = df['block_number'].tolist()
    exchange_rates = []
    with ThreadPoolExecutor(max_workers=7) as executor:
        futures = []
        for block_number in block_numbers:
            futures.append(executor.submit(get_exchange_rate_at_block, contract, block_number))
            time.sleep(0.14)
        for future in futures:
            result = future.result()
            if result is not None:
                exchange_rates.append(result)
            else:
                raise ValueError("Missing exchange rate data")
    return exchange_rates

def get_bpt_supply_at_block(contract, block_number):
    try:
        result = contract.functions.getActualSupply().call(block_identifier=int(block_number))
        return result / 10**18 
    except Exception as e:
        print(f"Error fetching actual supply at block {block_number}: {e}")
        return None
    
def fetch_bpt_totals(contract, df):
    block_numbers = df['block_number'].tolist()
    bpt_totals = []
    with ThreadPoolExecutor(max_workers=7) as executor:
        futures = []
        for block_number in block_numbers:
            futures.append(executor.submit(get_bpt_supply_at_block, contract, block_number))
            time.sleep(0.14)
        for future in futures:
            result = future.result()
            if result is not None:
                bpt_totals.append(result)
            else:
                raise ValueError("Missing bpt supply data")
    return bpt_totals

if __name__ == "__main__":
    
    #Establish connection between remote mainnet & arbitrum nodes with liquidity pool contracts
    w3_mainnet = Web3(Web3.HTTPProvider(f"https://mainnet.infura.io/v3/{INFURA_KEY}"))    
    w3_arbitrum = Web3(Web3.HTTPProvider(f"https://arbitrum-mainnet.infura.io/v3/{INFURA_KEY}"))   
    
    mainnet_pool_address = "0x596192bB6e41802428Ac943D2f1476C1Af25CC0E"
    arbitrum_pool_address = "0xB61371Ab661B1ACec81C699854D2f911070C059E"

    with open(r"BALezETHWETHstablepoolABI.json", 'r') as mainnet_abi_file:    #replace filepath here if needed for the ezETH/WETH mainnet contract ABI
        mainnet_pool_abi = json.load(mainnet_abi_file)
    with open(r"BALezETHwstETHstablepoolABI.json", 'r') as arbitrum_abi_file:    #replace filepath here if needed for the ezETH/wstETH arbitrum contract ABI
        arbitrum_pool_abi = json.load(arbitrum_abi_file)

    mainnet_pool_contract = w3_mainnet.eth.contract(address=mainnet_pool_address, abi=mainnet_pool_abi)
    arbitrum_pool_contract = w3_arbitrum.eth.contract(address=arbitrum_pool_address, abi=arbitrum_pool_abi)
    
    #List corresponding 5 minute interval blocknumbers on mainnet & arbitrum, corresponding to the ezETH depeg period 
    dune = DuneClient(API_KEY)     #replace api_key with your dune key
    dune_query = dune.get_latest_result_dataframe(3841843)
    arbitrum_df = dune_query[dune_query['blockchain'] == 'arbitrum'].reset_index(drop=True)
    ethereum_df = dune_query[dune_query['blockchain'] == 'ethereum'].reset_index(drop=True)
    
    #Approach 1: Retrieve historical BPI prices denominated in the pools base token by calling pool.getRates on historical blockchain states through Web3
    ethereum_df['BPTPrice_called'] = fetch_rates(mainnet_pool_contract, ethereum_df)
    arbitrum_df['BPTPrice_called'] = fetch_rates(arbitrum_pool_contract, arbitrum_df)
    
    #Approach 2: Retrieve historical token balances by calling vault.getPoolTokens on historical blockchain states through Web3
    mainnet_vault_address = "0xBA12222222228d8Ba445958a75a0704d566BF2C8"
    arbitrum_vault_address = "0xBA12222222228d8Ba445958a75a0704d566BF2C8"

    with open(r"BALmainnetvaultABI.json", 'r') as mainnet_abi_file:    #replace filepath here if needed for the mainnet vault contract ABI
        mainnet_vault_abi = json.load(mainnet_abi_file)
    with open(r"BALarbitrumvaultABI.json", 'r') as arbitrum_abi_file:    #replace filepath here if needed for the arbitrum vault contract ABI
        arbitrum_vault_abi = json.load(arbitrum_abi_file)
    
    mainnet_vault_contract = w3_mainnet.eth.contract(address=mainnet_vault_address, abi=mainnet_vault_abi)
    arbitrum_vault_contract = w3_arbitrum.eth.contract(address=arbitrum_vault_address, abi=arbitrum_vault_abi)
    
    mainnet_pool_id = mainnet_pool_contract.functions.getPoolId().call()
    arbitrum_pool_id = arbitrum_pool_contract.functions.getPoolId().call()
    
    mainnet_balances = fetch_balances(mainnet_vault_contract, mainnet_pool_id, ethereum_df)
    arbitrum_balances = fetch_balances(arbitrum_vault_contract, arbitrum_pool_id, arbitrum_df)
    
    ezETH_mainnet_token_address = '0xbf5495Efe5DB9ce00f80364C8B423567e58d2110'
    WETH_mainnet_token_address = '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2'
    ezETH_arbitrum_token_address = '0x2416092f143378750bb29b79eD961ab195CcEea5'
    wstETH_arbitrum_token_address = '0x5979D7b546E38E414F7E9822514be443A4800529'
    
    ezETH_rawbalances_arbitrum = []
    wstETH_rawbalances_arbitrum = []
    ezETH_rawbalances_mainnet = []
    WETH_rawbalances_mainnet = []
    
    for balance_dict in mainnet_balances:
        if balance_dict is not None:
            ezETH_balance = balance_dict.get(ezETH_mainnet_token_address, None)
            WETH_balance = balance_dict.get(WETH_mainnet_token_address, None)
            if ezETH_balance is None or WETH_balance is None:
                raise ValueError("Missing balance data")
            ezETH_rawbalances_mainnet.append(ezETH_balance)
            WETH_rawbalances_mainnet.append(WETH_balance)
        else:
            raise ValueError("Missing balance data")

    assert len(ezETH_rawbalances_mainnet) == len(ethereum_df)
    assert len(WETH_rawbalances_mainnet) == len(ethereum_df)

    ethereum_df['ezETH_rawbalances'] = ezETH_rawbalances_mainnet
    ethereum_df['WETH_rawbalances'] = WETH_rawbalances_mainnet
    
    for balance_dict in arbitrum_balances:
        if balance_dict is not None:
            ezETH_balance = balance_dict.get(ezETH_arbitrum_token_address, None)
            wstETH_balance = balance_dict.get(wstETH_arbitrum_token_address, None)
            if ezETH_balance is None or wstETH_balance is None:
                raise ValueError("Missing balance data")
            ezETH_rawbalances_arbitrum.append(ezETH_balance)
            wstETH_rawbalances_arbitrum.append(wstETH_balance)
        else:
            raise ValueError("Missing balance data")

    assert len(ezETH_rawbalances_arbitrum) == len(arbitrum_df)
    assert len(wstETH_rawbalances_arbitrum) == len(arbitrum_df)

    arbitrum_df['ezETH_rawbalances'] = ezETH_rawbalances_arbitrum
    arbitrum_df['wstETH_rawbalances'] = wstETH_rawbalances_arbitrum
    
    #Approach 2: Retrieve historical exchange rates by calling oracle.latestRoundData() on historical blockchain states through Web3
    ezETH_ETH_mainnet_oracle_address = '0x636A000262F6aA9e1F094ABF0aD8f645C44f641C'
    ezETH_ETH_arbitrum_oracle_address = '0x989a480b6054389075CBCdC385C18CfB6FC08186'
    wstETH_ETH_arbitrum_oracle_address = '0xb523AE262D20A936BC152e6023996e46FDC2A95D'

    with open(r"ChainlinkoracleABIezETHmainnet.json", 'r') as mainnet_abi_file:    #replace filepath here if needed for the ezETH/ETH mainnet chainlink ABI
        ezETH_ETH_mainnet_oracle_abi = json.load(mainnet_abi_file)
    with open(r"ChainlinkoracleABIezETHarbitrum.json", 'r') as arbitrum_abi_file:    #replace filepath here if needed for the ezETH/ETH arbitrum chainlink ABI
        ezETH_ETH_arbitrum_oracle_abi = json.load(arbitrum_abi_file)
    with open(r"ChainlinkoracleABIwstETHarbitrum.json", 'r') as arbitrum_abi_file:    #replace filepath here if needed for the wstETH/ETH arbitrum chainlink ABI
        wstETH_ETH_arbitrum_oracle_abi = json.load(arbitrum_abi_file)
    
    ezETH_ETH_mainnet_oracle_contract = w3_mainnet.eth.contract(address=ezETH_ETH_mainnet_oracle_address, abi=ezETH_ETH_mainnet_oracle_abi)
    ezETH_ETH_arbitrum_oracle_contract = w3_arbitrum.eth.contract(address=ezETH_ETH_arbitrum_oracle_address, abi=ezETH_ETH_arbitrum_oracle_abi)
    wstETH_ETH_arbitrum_oracle_contract = w3_arbitrum.eth.contract(address=wstETH_ETH_arbitrum_oracle_address, abi=wstETH_ETH_arbitrum_oracle_abi)
    
    ezETH_ETH_mainnet_exchange_rates = fetch_exchange_rates(ezETH_ETH_mainnet_oracle_contract, ethereum_df)
    ezETH_ETH_arbitrum_exchange_rates = fetch_exchange_rates(ezETH_ETH_arbitrum_oracle_contract, arbitrum_df)
    wstETH_ETH_arbitrum_exchange_rates = fetch_exchange_rates(wstETH_ETH_arbitrum_oracle_contract, arbitrum_df)

    ethereum_df['ezETH/ETH'] = ezETH_ETH_mainnet_exchange_rates
    arbitrum_df['ezETH/ETH'] = ezETH_ETH_arbitrum_exchange_rates
    arbitrum_df['wstETH/ETH'] = wstETH_ETH_arbitrum_exchange_rates
    arbitrum_df['ezETH/wstETH'] = arbitrum_df['ezETH/ETH'] / arbitrum_df['wstETH/ETH']
    arbitrum_df.drop(['ezETH/ETH', 'wstETH/ETH'], axis=1, inplace=True)
    
    #Approach 2: Retrieve historical BPT token supplies by calling pool.getActualSupply() on historical blockchain states through Web3
    mainnet_bpt_totals = fetch_bpt_totals(mainnet_pool_contract, ethereum_df)
    arbitrum_bpt_totals = fetch_bpt_totals(arbitrum_pool_contract, arbitrum_df)

    ethereum_df['BPT supply'] = mainnet_bpt_totals
    arbitrum_df['BPT supply'] = arbitrum_bpt_totals
    
    #Approach 2: Combining obtained parameters, manually compute the BPT price through the formula BPTprice = TVL denominated in base token / BPT supply
    ethereum_df['TVL_in_ETH'] = ((ethereum_df['ezETH_rawbalances'] * ethereum_df['ezETH/ETH']) + ethereum_df['WETH_rawbalances']) 
    ethereum_df['BPTprice_calculated'] = ethereum_df['TVL_in_ETH'] / ethereum_df['BPT supply']
    arbitrum_df['TVL_in_wstETH'] = ((arbitrum_df['ezETH_rawbalances'] * arbitrum_df['ezETH/wstETH']) + arbitrum_df['wstETH_rawbalances'])
    arbitrum_df['BPTPrice_calculated'] = arbitrum_df['TVL_in_wstETH'] / arbitrum_df['BPT supply']
    
    #Plot the results
    ethereum_df['interval_time'] = pd.to_datetime(ethereum_df['interval_time'])
    arbitrum_df['interval_time'] = pd.to_datetime(arbitrum_df['interval_time'])

    fig, axes = plt.subplots(nrows=4, ncols=1, figsize=(12, 25))
    fig.suptitle('Mainnet Pool Analysis')

    axes[0].plot(ethereum_df['interval_time'], ethereum_df['BPTPrice_called'], label='BPTPrice_called')
    axes[0].set_xlabel('Interval Time')
    axes[0].set_ylabel('BPTPrice_called')
    axes[0].legend()
    axes[0].tick_params(axis='x', rotation=45)

    axes[1].plot(ethereum_df['interval_time'], ethereum_df['BPTprice_calculated'], label='BPTprice_calculated')
    axes[1].set_xlabel('Interval Time')
    axes[1].set_ylabel('BPTprice_calculated')
    axes[1].legend()
    axes[1].tick_params(axis='x', rotation=45)

    axes[2].plot(ethereum_df['interval_time'], ethereum_df['ezETH/ETH'], label='ezETH/ETH')
    axes[2].set_xlabel('Interval Time')
    axes[2].set_ylabel('ezETH/ETH')
    axes[2].legend()
    axes[2].tick_params(axis='x', rotation=45)

    axes[3].plot(ethereum_df['interval_time'], ethereum_df['ezETH_rawbalances'], label='ezETH_rawbalances')
    axes[3].plot(ethereum_df['interval_time'], ethereum_df['WETH_rawbalances'], label='WETH_rawbalances')
    axes[3].set_xlabel('Interval Time')
    axes[3].set_ylabel('Token Balances')
    axes[3].legend()
    axes[3].tick_params(axis='x', rotation=45)

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.show()

    fig, axes = plt.subplots(nrows=4, ncols=1, figsize=(12, 25))
    fig.suptitle('Arbitrum Pool Analysis')

    axes[0].plot(arbitrum_df['interval_time'], arbitrum_df['BPTPrice_called'], label='BPTPrice_called')
    axes[0].set_xlabel('Interval Time')
    axes[0].set_ylabel('BPTPrice_called')
    axes[0].legend()
    axes[0].tick_params(axis='x', rotation=45)
    
    axes[1].plot(arbitrum_df['interval_time'], arbitrum_df['BPTPrice_calculated'], label='BPTPrice_calculated')
    axes[1].set_xlabel('Interval Time')
    axes[1].set_ylabel('BPTPrice_calculated')
    axes[1].legend()
    axes[1].tick_params(axis='x', rotation=45)

    axes[2].plot(arbitrum_df['interval_time'], arbitrum_df['ezETH/wstETH'], label='ezETH/wstETH')
    axes[2].set_xlabel('Interval Time')
    axes[2].set_ylabel('ezETH/wstETH')
    axes[2].legend()
    axes[2].tick_params(axis='x', rotation=45)

    axes[3].plot(arbitrum_df['interval_time'], arbitrum_df['ezETH_rawbalances'], label='ezETH_rawbalances')
    axes[3].plot(arbitrum_df['interval_time'], arbitrum_df['wstETH_rawbalances'], label='wstETH_rawbalances')
    axes[3].set_xlabel('Interval Time')
    axes[3].set_ylabel('Token Balances')
    axes[3].legend()
    axes[3].tick_params(axis='x', rotation=45)

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.show()

