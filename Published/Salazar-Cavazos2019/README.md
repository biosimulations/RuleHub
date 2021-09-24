# Salazar-Cavazos 2019
Multisite phosphorylation of EGFR

## Abstract
The Epidermal Growth Factor Receptor (EGFR/ErbB1/HER1) plays an important role in both physiological and cancer-related processes. To study the factors that influence receptor phosphorylation, we have coupled Single Molecule Pull-down (SiMPull) measurements with rule-based modeling of EGFR signaling. Using SiMPull, we quantified the phosphorylation state of thousands of individual receptors. These measurements enabled the first direct detection of multisite phosphorylation on full-length EGFR and revealed that the extent of phosphorylation varies by tyrosine site and is dependent on the relative abundance of signaling partners that limit access by tyrosine phosphatases. We also evaluated the impact of oncogenic mutations and ligands with varying affinity on phosphorylation kinetics. Simulations highlight the importance of dimer lifetimes on EGFR phosphorylation and signaling output.

## Description
A model of EGFR signaling that was parameterized using SiMPull measurements of multisite phosphorylation dynamics.

## Keywords
* Epidermal Growth Factor Receptors
* Receptor Phosphorylation
* Single-Molecule Pull-down
* Tyrosine site
* Tyrosine phosphatases

## Thumbnails
* [Figure1.png](thumbnails/Figure1.png)

## Taxa
* [Homo sapiens](http://identifiers.org/taxonomy:9606)

## Authors
* [Emanuel Salazar-Cavazos](https://identifiers.org/orcid:0000-0003-0850-0651)
* Carolina F. Nitta
* Eshan D. Mitra
* Bridget S. Wilson
* Keith A. Lidke
* [William S. Hlavacek](https://identifiers.org/orcid:0000-0003-4383-8711)
* [Diane S. Lidke](https://identifiers.org/orcid:0000-0001-8533-6029)

## Citations
* Emanuel Salazar-Cavazos, Carolina Franco Nitta, Eshan D. Mitra, Bridget S. Wilson, Keith A. Lidke, William S. Hlavacek & Diane S. Lidkea. Multisite EGFR phosphorylation is regulated by adaptor protein abundances and dimer lifetimes. Mol Biol Cell 31, 7:695–708 (2020). DOI: [10.1091/mbc.E19-09-0548](https://identifiers.org/doi:10.1091/mbc.E19-09-0548)

<!-- Begin free-text content -->
## Files
* [190127_CHO_EGFR_best-fit.bngl](190127_CHO_EGFR_best-fit.bngl): Model of EGFR signaling in CHO cells expressing EGFR-GFP, using the parameter values for best fit obtained through PyBNF.
* [190127_HeLa.bngl](190127_HeLa.bngl),  [190127_HMEC.bngl](190127_HMEC.bngl) and [190127_MCF10A.bngl](190127_MCF10A.bngl): Models of EGFR signaling for the differents cell lines. These models use as a base the model "190127\_CHO\_EGFR\_best-fit.bngl", with protein copy numbers for EGFR, Grb2 and Shc1 specific to each cell line.
* [190127_CHO_EGFR_sensitivity.bngl](190127_CHO_EGFR_sensitivity.bngl): Modification of the model "190127\_CHO\_EGFR\_best-fit.bngl" to perform sensitity analysis by increasing each of the parameter values in the model by 1%.
* [190127_CHO_EGFR_Epigen.bngl](190127_CHO_EGFR_Epigen.bngl): Model of EGFR signaling in CHO cells expressing EGFR-GFP, but in contrast to model "190127_CHO_EGFR_best-fit.bngl", it simulates EGFR activation with 20uM Epigen instead of 25nM EGF. The parameter value for EGFR dimer off-rate was varied to find the best fit for SiMPull results with Epigen ligand.
* [190127_CHO_HA_EGFR_L858R.bngl](190127_CHO_HA_EGFR_L858R.bngl): Model of EGFR signaling in CHO cells expressing HA-EGFR. The number of EGFR per cell was set to the experimentally estimated value for this cell line. The parameter value for kinase activity (phosphorylation rate) was varied to find best fit for experimental results with L858R mutant EGFR.
* [PyBNF-fitting-setup](PyBNF-fitting-setup): Files required to run parameterization of the base model in PyBioNetFit
  * [190127_CHO_EGFR_forBNF.bngl](PyBNF-fitting-setup/190127_CHO_EGFR_forBNF.bngl): Model file with unknown parameters
  * [dose_resp.exp](PyBNF-fitting-setup/dose_resp.exp), [EGF_25nM.exp](PyBNF-fitting-setup/EGF_25nM.exp): Experimental data files
  * [fit_v1_28.conf](PyBNF-fitting-setup/fit_v1_28.conf): PyBNF configuration file to perform fitting
  * [fit_bootstrap.conf](PyBNF-fitting-setup/fit_bootstrap.conf): PyBNF configuration file to perform bootstrapping
  * [fit_pt.conf](PyBNF-fitting-setup/fit_pt.conf): PyBNF configuration file to perform Bayesian uncertainty quantification by parallel tempering
<!-- End free text content -->

## License
[MIT](http://identifiers.org/spdx:MIT)

## Curators
* [Jonathan Karr](http://identifiers.org/orcid:0000-0002-2605-5080)
* Briman Yang

## Created
2015-05-28


  
