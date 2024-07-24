# Balancer-ezETH-Depeg
Web3 application for analyzing the differences between the ezETH depeg (April 23-24 2024) as it occurred for both Balancer liquidity pools: 
ezETH/WETH on mainnet, and ezETH/wstETH on arbitrum. Establishes connections with both liquidity pool contracts, vault contracts, as well 
as corresponing Chainlink Price Oracles, and iterates through corresponding block numbers for the depeg period, derived utlizing a Dune query,
obtaining crucial time series information including exchange rate prices, raw token balances, as well as BPT prices as plots. This program provides
a comprehensive review between the unfolding of the ezETH depeg between mainnet and arbitrum.
## Comprehensive Report
During the ezETH depeg (April 23rd-24th) 340 million dollars of ezETH collateral was liquidated across lending protocols deployed mainly across Ethereum mainnet and L2s. The liquidations included 115 credit accounts accounting for 10650 ezETH being sold on Balancer alone. Below, we will analyze the event as it occurred on Balancer, comparing the overall resilience of arbitrum pools with the clear de peg on ethereum pools.
 
 As already evident from the token balances charts, the main pre existing problem that enabled the depeg to occur was low liquidity in terms of the base token (WETH and wstETH in our example). The underlying concern that lead to lower liquidity across DEX ezETH pools was the inability for ezETH holders to make staking withdrawals on their staked/restaked ETH, thus the only option for ezETH holders to redeem their locked value being - to sell their ezETH on DEXs. This constant selling pressure surely causes an environment of higher ezETH token balances and lower base token balances in liquidity pools.
 
 The general formula for spot price of a weighted liquidity pool, is given as Spot Price y/x (y in terms of x) = (Total Balance token x / weight of token x) / (Total Balance token y / weight of token y). From this relationship, if we take the Spot Price ezETH/ETH into consideration, we can infer the downwards pressure on price that continuously upwards shifting ezETH token balances bring, given continuously downwards shifting base token balances. As evident from the token balances below, we can see this trend of selling pressure leading up to the depeg event.
  
  On April 23rd, following a series of unfair announcements on tokenomics and rewards, ezETH holders began to dump, this downwards pressure triggered many liquidations across ezETH collateralized borrowings across lending protocols, as the value of collateral posted fell below the borrowed values. This greatly exacerbated the selling pressure, as gearbox alone liquidated 10650 ezETH, selling all of it on Balancer, culminating in 340 million dollars in liquidations mainly on ethereum mainnet.
 
 As seen in both price feeds below, the de peg was felt across both chains ethereum mainnet and arbitrum, however at an incredibly lesser degree on arbitrum. The negative sentiment and FUD was felt across both chains on Balancer, however it was precisely the massive liquidations that cascaded the ezETH/ETH price on ethereum mainnet. On the other hand, only dealing with FUD and arbitrageur selling pressure, as well as benefiting from a lack of leverage farming liquidations, the ezETH/wstETH price on arbitrum was able to stay in tact. 
 
 Fortunately, for all ezETH holders (stakers, restakers, liquidity providers) combined efforts between arbitrageurs sweeping in and Renzo making timely corrective announcements beneficial to its community as well as the announced enablement of withdrawals in Q2 2024, helped settle the smoke.
## Requirements
- Python >= 3.7
- Infura API Key
- Dune API Key
- To install required libraries: 'pip install dune-client'
- Download all included contract ABIs
