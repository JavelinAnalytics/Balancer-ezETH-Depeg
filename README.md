# Balancer-ezETH-Depeg
Web3 application for analyzing the differences between the ezETH depeg (April 23-24 2024) as it occurred for both Balancer liquidity pools: 
ezETH/WETH on mainnet, and ezETH/wstETH on arbitrum. Establishes connections with both liquidity pool contracts, vault contracts, as well 
as corresponing Chainlink Price Oracles, and iterates through corresponding block numbers for the depeg period, derived utlizing a Dune query,
obtaining crucial time series information including exchange rate prices, raw token balances, as well as BPT prices as plots. This program provides
a comprehensive comparison between the unfolding of the ezETH depeg between mainnet and arbitrum.
## Comprehensive Report
For a comprehensive report including charts with comparative metrics please view ezETH depeg analysis .pdf 
## Requirements
- Python >= 3.7
- Infura API Key
- Dune API Key
- To install required libraries: `pip install dune-client`
- Download all included contract ABIs
