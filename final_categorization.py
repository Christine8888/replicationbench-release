"""
Categorization of 111 expert tasks into 6 categories:
1. Data Loading and Processing
2. Summary Statistics and Measurements
3. Model Fitting and Parameter Estimation
4. Bayesian Inference
5. Physical Simulations and Theoretical Calculations
6. Machine Learning Applications
"""

categorization = {
    # MUSE AGN-driven Winds Tasks (Paper 1)
    'dust_reddening': 2,  # Uses fitted params to calculate E(B-V) percentiles
    'electron_density': 2,  # Uses fitted params to calculate ne statistics
    'narrow_and_broad_line_decomposition_for_J080427': 3,  # Fitting ppxf and Gaussian line models
    'outflow_energetics': 2,  # Derives energetics from fitted params
    'voronoi_binning_for_emission_lines_J080427': 1,  # Data processing - Voronoi binning

    # Abacus N-body Force Calculations (Paper 2)
    'ewald_force_accuracy': 5,  # Physical simulation - N-body force calculation
    'ewald_force_comparison': 5,  # Physical simulation - N-body force calculation
    'lattice_force_error': 5,  # Physical simulation - N-body force calculation
    'lcdm_total_force_accuracy': 5,  # Physical simulation - N-body force calculation

    # AstroM3 Multimodal ML (Paper 3)
    'cross_modal_photometry_to_spectra_search': 6,  # ML - cross-modal similarity search with embeddings
    'modality_importance_rot_class_accuracy': 6,  # ML - CLIP classification accuracy
    'multimodal_classification_clip': 6,  # ML - fine-tuning multimodal classifier
    'photometry_classification_accuracy_no_clip': 6,  # ML - training classifier from scratch
    'photometry_classification_accuracy_with_clip': 6,  # ML - CLIP pre-trained classifier
    'spectra_classification_accuracy_limited_data_10_percent': 6,  # ML - limited data classification
    'spectral_similarity_search': 6,  # ML - spectral embedding similarity search

    # Bayesian Calibration Tasks (Paper 4)
    'cold_hot_tandem': 4,  # Bayesian inference - joint posteriors
    'cold_temp': 4,  # Bayesian inference - retrieving temperature posterior
    'evidence': 4,  # Bayesian inference - evidence calculation with increasing calibrators
    'hot_temp': 4,  # Bayesian inference - retrieving temperature posterior
    'load_cal': 4,  # Bayesian inference - full calibration
    'nwp_set': 4,  # Bayesian inference - noise wave parameter estimation

    # X-ray Transient Analysis (Paper 5)
    '2dae_embedding': 6,  # ML - autoencoder embedding
    '2dpca_embedding': 6,  # ML - PCA embedding
    'blackbody_spectral_fit': 3,  # Model fitting - blackbody spectral fit
    'powerlaw_spectral_fit': 3,  # Model fitting - powerlaw spectral fit

    # Gaia Vertical Ridges (Paper 6)
    'gaia_dr2_all': 1,  # Data loading - filtering and counting stars
    'gaia_dr2_rvs': 1,  # Data loading - filtering RVS sample
    'peak_mean_vz_all': 2,  # Summary statistics - finding peak in distribution
    'ridge_slope': 2,  # Summary statistics - measuring ridge slopes
    'ridges_in_all': 2,  # Summary statistics - counting ridge features

    # EHT M87 Reconstruction (Paper 7)
    'eht_reconstruction': 4,  # Bayesian inference - variational approximation to posterior
    'eht_ring_orientation_angle': 2,  # Summary statistics from posterior samples
    'eht_ring_size': 2,  # Summary statistics from posterior samples
    'eht_ring_width': 2,  # Summary statistics from posterior samples

    # FABLE Simulations (Paper 8)
    'comp_mps': 2,  # Computing matter power spectrum - summary statistic
    'dmo_compute_mps': 2,  # Computing matter power spectrum - summary statistic
    'fiducial2dmo_compare_mps': 2,  # Computing ratios - summary statistic
    'filtered_grafic_fiducial_halo': 1,  # Data processing - generating filtered cubes
    'grafic_cubes_gen': 1,  # Data processing - generating density cubes
    'mps_ratio2dmo_fiducial_halo': 2,  # Computing ratios - summary statistic
    'nofb2dmo_compare_mps': 2,  # Computing ratios - summary statistic
    'nofb_compute_mps': 2,  # Computing matter power spectrum - summary statistic

    # Galaxy Manifold (Paper 9)
    'data_preparation': 1,  # Data loading - downloading and filtering catalog
    'evolution_tracks': 5,  # Physical simulation - galaxy evolution model
    'gas_mass_estimation': 2,  # Summary statistics - calculating gas masses
    'manifold_plane': 2,  # Summary statistics - calculating normal plane equations
    'manifold_recovery': 6,  # ML - Extra-Trees Regressors for prediction
    'morphological_classification': 2,  # Summary statistics - determining classification boundary
    'physical_properties': 2,  # Summary statistics - mapping physical properties
    'property_prediction': 6,  # ML - Extra-Trees Regressors for prediction
    'svd_analysis': 1,  # Data processing - SVD decomposition
    'transformation_matrix': 2,  # Summary statistics - extracting transformation matrices

    # Galaxy Clustering (Paper 10)
    'bcg_identification': 6,  # ML - sOPTICS clustering algorithm
    'clustering_hyperparameter_optimization': 6,  # ML - optimizing clustering algorithms
    'fof_optimization_sdss': 6,  # ML - optimizing FoF clustering
    'millennium_data_extraction': 1,  # Data loading - SQL query extraction
    'nyu_vagc_processing': 1,  # Data loading - processing catalog
    'shi_catalog_acquisition': 1,  # Data loading - downloading catalog
    'soptics_implementation': 6,  # ML - implementing clustering algorithm
    'soptics_validation_shi': 6,  # ML - validating clustering algorithm

    # Cosmological Constraints from GW (Paper 11)
    'dark_energy': 4,  # Bayesian inference - projecting credible intervals
    'h0_scaling': 4,  # Bayesian inference - measuring constraint scaling
    'measure_combo': 4,  # Bayesian inference - fitting degeneracy, finding best-constrained combo
    'modified_gravity': 4,  # Bayesian inference - projecting credible intervals

    # Mass Gap Analysis (Paper 12)
    'default_mbh': 4,  # Bayesian inference - hierarchical inference credible interval
    'default_mtov': 4,  # Bayesian inference - hierarchical inference credible interval
    'equal_mass_slope': 4,  # Bayesian inference - hierarchical inference credible interval
    'load_data': 1,  # Data loading - loading GW data
    'mass_gap': 4,  # Bayesian inference - computing probability from posterior
    'mass_gap_constraint': 4,  # Bayesian inference - simulating measurements
    'mtov_spin': 4,  # Bayesian inference - hierarchical inference credible interval
    'mtov_spin_2': 4,  # Bayesian inference - hierarchical inference credible interval
    'spin_constraint': 4,  # Bayesian inference - hierarchical inference credible interval

    # Satellite Detection (Paper 13)
    'classifier_performance': 6,  # ML - CNN classifier performance
    'satellite_chance_post2020_acis': 6,  # ML - CNN classifier predictions
    'satellite_chance_post2020_uvis': 6,  # ML - CNN classifier predictions
    'satellite_chance_pre2020_acis': 6,  # ML - CNN classifier predictions
    'satellite_chance_pre2020_uvis': 6,  # ML - CNN classifier predictions
    'satellite_fractions': 6,  # ML - computing fractions from CNN predictions
    'satellite_fractions_increase': 6,  # ML - computing increase from CNN predictions

    # Additional Calibration Tasks (Paper 14)
    'alens': 4,  # Bayesian inference - parameter estimation
    'params': 4,  # Bayesian inference - parameter estimation
    'antenna_temp': 4,  # Bayesian inference - temperature retrieval
    'cab_temp': 4,  # Bayesian inference - temperature retrieval
    'cold_sparam': 4,  # Bayesian inference - S-parameter estimation
    'hot_temp': 4,  # Bayesian inference - temperature retrieval
    'nwp': 4,  # Bayesian inference - noise wave parameter estimation

    # Galaxy Clustering Analysis (Paper 15)
    'dbscan_optimization': 6,  # ML - DBSCAN clustering optimization
    'dbscan_test': 6,  # ML - DBSCAN clustering testing
    'best_fitting_slopes': 3,  # Model fitting - linear fits to PAH-optical correlations
    'feature_PCA': 2,  # Summary statistics - PCA variance explained
    'feature_PCA_corr_coeffs': 2,  # Summary statistics - correlation coefficients with PCs
    'identify_AGN_hosts': 1,  # Data loading - cross-matching with external catalog
    'relation_break_down': 2,  # Summary statistics - counting pixels above threshold

    # Galaxy HOD Analysis (Paper 16)
    'elg_hod_measurement_and_fitting': 3,  # Model fitting - HOD model fitting
    'elg_satellite_fraction': 2,  # Summary statistics - computing satellite fractions
    'elg_selection_count': 2,  # Summary statistics - counting selected galaxies
    'lrg_central_velocity_bias': 2,  # Summary statistics - measuring velocity bias
    'lrg_clustering_secondary_bias_ratio': 2,  # Summary statistics - computing bias ratios
    'lrg_hod_measurement_and_fitting': 3,  # Model fitting - HOD model fitting
    'lrg_satellite_fraction': 2,  # Summary statistics - computing satellite fractions
    'lrg_selection_count': 2,  # Summary statistics - counting selected galaxies

    # SMC TRGB Analysis (Paper 17)
    'aseq_bseq_trgb': 3,  # Model fitting - TRGB detection with smoothing optimization
    'fit_aseq_bseq': 3,  # Model fitting - polynomial fits to W_VI vs logP
    'gaia_synthetic_i_trgb': 3,  # Model fitting - TRGB detection with smoothing optimization
    'med_color_amp': 2,  # Summary statistics - median period and amplitude

    # Gaia Breathing Mode (Paper 18)
    'gaia_breathing_typical': 2,  # Summary statistics - mean breathing amplitude
    'gaia_rv_sample_size': 1,  # Data loading - counting stars meeting criteria
    'solar_height_from_gaia_dr2': 3,  # Model fitting - fitting symmetric density model
    'sun_height_corrected': 3,  # Model fitting - fitting asymmetry-corrected density model
}

# Verify all tasks are categorized
# Note: The JSON file has 111 entries but only 110 unique task_ids (hot_temp appears twice)
expected_unique_tasks = 110
actual_task_count = len(categorization)

if actual_task_count != expected_unique_tasks:
    print(f"WARNING: Expected {expected_unique_tasks} tasks but got {actual_task_count}")
else:
    print(f"Successfully categorized all {actual_task_count} unique tasks")

# Count tasks per category
category_counts = {}
for task_id, category in categorization.items():
    category_counts[category] = category_counts.get(category, 0) + 1

print("\nCategory Counts:")
print("1. Data Loading and Processing:", category_counts.get(1, 0))
print("2. Summary Statistics and Measurements:", category_counts.get(2, 0))
print("3. Model Fitting and Parameter Estimation:", category_counts.get(3, 0))
print("4. Bayesian Inference:", category_counts.get(4, 0))
print("5. Physical Simulations and Theoretical Calculations:", category_counts.get(5, 0))
print("6. Machine Learning Applications:", category_counts.get(6, 0))
print(f"\nTotal: {sum(category_counts.values())}")
