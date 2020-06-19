# Air Traffic and Jet Fuel Demand
Moses Rahnama

## Overview
With the spread of COVID-19 and a sharp decline in global air travel, Jet Fuel prices and time spreads, cracks (Jet price compares to crude), regional diffs, and even Jet Fuel-Diesel (Heating Oil / “HO”/Gasoil) spreads can present significant opportunities.
An increasing number of commodity traders are actively looking at Jet Fuel to catch the inevitable recovery. While it is incredibly challenging to predict and model COVID’s future curve and governments policies on relaxing air travel, I will run a bull/bear/base analysis for Jet Fuel demand recovery and spot potential price dislocations in the following areas:
1) Cracks: Jet Fuel cracks are the most direct instrument to take a position on aviation industry’s relative fundamentals against crude, which is itself is a weighted basket of all oil products.
2) Regional diffs: New York (East Coast or PADD 1), LA (West Coast or PADD 5), and Gulf Coast (USGC or PADD 3) all have active Jet Fuel markets and very often have different fundamentals.
3) Time spreads: The futures curves for these regions can also move dramatically based on the underlying fundamentals. 
4) Jet Fuel–Diesel: These two products have a very similar cut in the distillation process and are often used for relative trades. This is a much bigger in Asia where Kerosene (lower quality JF) and diesel are used interchangeably for heating during winter. (Japan, Korea, China most) 
For this project, I have created a soon-to-be fully automated model to identify early trade signals.

## Data Sources
1) OpenSkyNetwork for detailed air traffic data https://opensky-network.org/. This is the link for the REST API doc https://opensky-network.org/apidoc/rest.html. (Their Python API is basically dysfunctional)
2) EnergyAspects (EA) for historical data, and balances forecast. EA is exceptionally strong in the oil and products markets, particularly Jet Fuel, and their estimates often forms consensus.
3) The EIA for supply and demand data.
4) Bloomberg for historical prices.
5) NYTimes and Johns Hopkins University for COVID-19 stats.


### Derivatives
Table below provides the list of products and derivatives (with flat price ticker) used for this project. (full ticker list is in the Bloomberg directory)

| Bloomberg Ticker | Description | Unit |
| :---         | :---  | :--- |
| FGJSM1 Index | USGC Jet Fuel-Nymex HO | USd/gallon |
| FLJSM1 Index | LA Jet Fuel-Nymex HO | USd/gallon |
| FNJSM1 Index | NY Jet Fuel-Nymex HO | USd/gallon |
| FSNJM1 Index | New York Jet Fuel | USd/gallon |
| FSGJM1 Index | USGC Jet Fuel | USd/gallon |
| HO1 Comdty | Generic Nymex HO | USd/gal. |
| CL1 Comdty | Generic Nymex CL | USD/bbl. |
| FSCHM1 Index |CARB (California) Diesel | USd/gallon |
| FSGCM1 Index |Gulf Coast ULSD | USd/gallon |
| FSLJM1 Index | LA Jet Fuel | USd/gallon |
