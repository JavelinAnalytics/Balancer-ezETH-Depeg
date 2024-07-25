# Balancer-ezETH-Depeg
Web3 application for comparing the ezETH depeg as it occurred on both Balancer liquidity pools: ezETH/WETH on mainnet, and ezETH/wstETH on arbitrum. Establishes connections with both liquidity pool contracts, vault contracts, as well as corresponding Chainlink Price Oracles, and iterates through corresponding block numbers for the duration of the depeg period - derived utilizing a Dune SQL query - obtaining crucial time series data including exchange rates, raw token balances, as well as BPT prices, all plotted. This program provides a comprehensive comparison between the unfolding of the ezETH depeg as it occurred between mainnet and arbitrum.
## Comprehensive Report
For a comprehensive report including charts with comparative metrics please view ezETH depeg analysis .pdf 
## Requirements
- Python >= 3.7
- Infura API Key
- Dune API Key
- To install required libraries: `pip install dune-client`
- Download all included contract ABIs
