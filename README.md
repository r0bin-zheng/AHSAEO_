# AHSAEO

🚧 The code is not complete.

<a href="./README.md">EN</a> | <a href="./README_zh-CN.md">中文</a>

**Adaptive Hierarchical Surrogate-Assisted Evolutionary Optimization**

This project presents an Adaptive Hierarchical Surrogate-Assisted Evolutionary Optimization Algorithm(AHSAEO), which improves upon both selection strategies and global search. In terms of selection strategy, the algorithm introduces a dynamic adjustment mechanism that modifies the search method based on search outcomes and progress information, enhancing the algorithm's ability to escape local optima. For the global search optimizer, the algorithm employs Uncertainty-assisted Firework Global Searching (UAFGS). By leveraging the uncertainty information of the Ensemble of surrogates (EoS), the algorithm can better capture regions with high data variability, thus enhancing the guiding role of the surrogate model in the search process.Experiments demonstrate that for high-dimensional and complex multimodal functions, this algorithm's search and convergence capabilities surpass those of other comparative algorithms.