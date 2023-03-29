# BioSTEAM Location-Specific Evaluation  (BLocS)

This module allows BioSTEAM users to consider the impacts of economic and environmental parameters that vary by location. Current location-specific data includes income, property, producer fuel, and sales tax rates; feedstock prices (corn, corn stover, and sugarcane); electricity prices; location capital cost factors (LCCFs), and tax incentives for all 50 states in the US.

![BLocS Logo](https://github.com/BioSTEAMDevelopmentGroup/BLocS/blob/main/BLocS_logo.tiff "BLocS Logo")

Stewart et al. [[1]](#1) is the first paper to utilize BLocS to explore the influence of policy incentives and location-specific economic parameters on the financial viability of three different biorefineries.

Follow these steps to replicate the results in [[1]](#1). Note: the authors are currently working to improve BLocS implementation. These exact methods may become deprecated, but you will still be able to achieve identical results.

After downloading BLocS, open and run evaluation.py.
```python
# This example provides the steps to replicate results for the corn stover biorefinery.
# To replicate results for the corn and sugarcane biorefineries, replace 'cornstover' in the following functions with 'corn' or 'sugarcane'.
# This code should create a results folder within your blocs installation and output the results there.

# First generate state-specific (SS) results.
>>> evaluate_SS('cornstover',10000)

# Next generate results for each incentive using median location-specific parameters.
# This will also perform a sensitivity analysis and generate Spearman's rho correlation coefficients for each metric and parameter.
>>> evaluate_IP('cornstover',10000)

# And lastly generate results across ranges of location-specific parameters. 
# Currently, this analysis requires the user to 'turn off' (by 'commenting out' using #) other location-specific parameters in create_IPs_model.
# The following code may be used to generate results across the range of state income tax rates. Be sure to 'turn off' the other location-specific parameters in lines 780-810.
>>> evaluate_incT('cornstover',5000)
```

## References
<a id="1">[1]</a>
  Stewart, D.W.; Cortés-Peña, Y.R.; Li, Y.; Stillwell, A.S.; Khanna, M.; Guest, J.S. (2023). Implications of biorefinery policy incentives and location-specific economic parameters for the financial viability of biofuels. _Environmental Science & Technology_, _57_(6), 2262–2271.
