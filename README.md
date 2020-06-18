### Air Traffic and Jet Fuel Demand
Moses Rahnama

This project looks at air traffic data during COVID-19 and the impact on Jet Fuel cracks, timespreads, and Gasoil/Jet Fuel spreads.
While it is incredibly challenging to predict and model how COVID-19 will progress, I have built a model using historical numbers and future curve forecasts (third party) that predicts flight traffic.

This is a fully automated platform and within the next week or two, I expect to have completed a live platform for real time trade signals for the derivatives included in this project.

### Data Sources
1) OpenSkyNetwork for detailed air traffic data https://opensky-network.org/. This is the link for the REST API doc https://opensky-network.org/apidoc/rest.html. (Their Python API is basically dysfunctional)
2) EnergyAspects (EA) for historical data, and balances forecast. EA is exceptionally strong in the oil and products markets, particularly Jet Fuel, and their estimates often forms consensus.
3) The EIA for supply and demand data.
4) Bloomberg for historical prices.
5) NYTimes and Johns Hopkins University for COVID-19 stats.


### Derivatives
Table below provides the list of products and derivatives (with flat price ticker) used for this project.

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
