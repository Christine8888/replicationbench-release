"""Categorize all expert tasks."""
from src.dataset.dataloader import Dataloader
from collections import defaultdict

# Load only expert tasks
loader = Dataloader(filters={"source": "expert"}, load_text=False)

# Collect all tasks with paper context
all_tasks = []
for paper_id, paper in sorted(loader.papers.items()):
    for task_id, task in sorted(paper.tasks.items()):
        all_tasks.append({
            'paper_id': paper_id,
            'task_id': task_id,
            'task': task,
            'paper_title': paper.title
        })

print(f"Total expert tasks: {len(all_tasks)}\n")

# Manual categorization based on descriptions
categorization = {
    # MUSE paper
    'dust_reddening': 2,  # Deriving dust reddening - measurement
    'electron_density': 2,  # Deriving electron density - measurement
    'narrow_and_broad_line_decomposition_for_J080427': 3,  # Emission line fitting - model fitting
    'outflow_energetics': 2,  # Deriving energetics - measurement
    'voronoi_binning_for_emission_lines_J080427': 1,  # Binning data - data processing

    # ABACUS paper
    'ewald_force_accuracy': 5,  # Force error calculation - physical simulation
    'ewald_force_comparison': 5,  # Force solver comparison - physical simulation
    'lattice_force_error': 5,  # Force error on lattice - physical simulation
    'lcdm_total_force_accuracy': 5,  # Cosmological force accuracy - physical simulation

    # AstroM3 paper
    'cross_modal_photometry_to_spectra_search': 6,  # Cross-modal similarity search - ML
    'modality_importance_rot_class_accuracy': 6,  # Classification accuracy - ML
    'multimodal_classification_clip': 6,  # Fine-tuning classifier - ML
    'photometry_classification_accuracy_no_clip': 6,  # Classification without pretraining - ML
    'photometry_classification_accuracy_with_clip': 6,  # Classification with pretraining - ML
    'spectra_classification_accuracy_limited_data_10_percent': 6,  # Classification with limited data - ML
    'spectral_similarity_search': 6,  # Similarity search with embeddings - ML

    # Bayesian noise wave calibration paper
    'cold_hot_tandem': 4,  # Joint posteriors - Bayesian inference
    'cold_temp': 3,  # Retrieving temperature - model fitting/parameter estimation
    'evidence': 4,  # Evaluating evidence - Bayesian inference
    'hot_temp': 3,  # Retrieving temperature - model fitting/parameter estimation
    'load_cal': 3,  # Full calibration - model fitting/parameter estimation
    'nwp_set': 3,  # Calculating noise wave parameters - model fitting/parameter estimation

    # Fast X-ray transient paper
    '2dae_embedding': 6,  # Autoencoder embedding - ML
    '2dpca_embedding': 1,  # PCA embedding - data processing
    'blackbody_spectral_fit': 3,  # Fitting blackbody model - model fitting
    'powerlaw_spectral_fit': 3,  # Fitting powerlaw model - model fitting

    # Gaia DR2 paper
    # 'figure2_rvs': 1,  # REMOVED - Creating density map - data processing
    'gaia_dr2_all': 1,  # Counting stars - data loading
    'gaia_dr2_rvs': 1,  # Selecting and counting - data loading/filtering
    'peak_mean_vz_all': 2,  # Finding peak velocity - summary statistic
    'ridge_slope': 2,  # Measuring slope - summary statistic
    'ridges_in_all': 2,  # Counting features - summary statistic

    # EHT M87 paper
    'eht_reconstruction': 4,  # Bayesian variational approximation - Bayesian inference
    'eht_ring_orientation_angle': 2,  # Posterior mean and uncertainty - summary statistic
    'eht_ring_size': 2,  # Posterior mean and uncertainty - summary statistic
    'eht_ring_width': 2,  # Posterior mean and uncertainty - summary statistic

    # FABLE simulations paper
    'comp_mps': 2,  # Computing power spectrum - summary statistic/measurement
    'dmo_compute_mps': 2,  # Computing power spectrum - summary statistic/measurement
    'fiducial2dmo_compare_mps': 2,  # Computing ratio - summary statistic
    'filtered_grafic_fiducial_halo': 1,  # Filtering particles - data processing
    'grafic_cubes_gen': 1,  # Generating cubes - data processing
    'mps_ratio2dmo_fiducial_halo': 2,  # Computing ratio - summary statistic
    'nofb2dmo_compare_mps': 2,  # Computing ratio - summary statistic
    'nofb_compute_mps': 2,  # Computing power spectrum - summary statistic/measurement

    # Galaxy Manifold paper
    'data_preparation': 1,  # Downloading and preparing data - data loading/processing
    'evolution_tracks': 5,  # Calculating evolution tracks - theoretical calculation
    'gas_mass_estimation': 2,  # Estimating masses - measurement
    'manifold_plane': 2,  # Calculating normal plane - measurement
    'manifold_recovery': 6,  # Training models to recover coordinates - ML
    'morphological_classification': 2,  # Determining boundary - summary statistic
    'physical_properties': 1,  # Mapping properties - data processing
    'property_prediction': 6,  # Predicting properties with trained models - ML
    'svd_analysis': 1,  # Applying SVD - data processing
    'transformation_matrix': 2,  # Calculating transformation matrix - measurement

    # sOPTICS paper
    'bcg_identification': 6,  # Clustering algorithm application - ML
    'clustering_hyperparameter_optimization': 6,  # Optimizing clustering - ML
    'fof_optimization_sdss': 6,  # Optimizing FoF algorithm - ML
    'millennium_data_extraction': 1,  # SQL extraction - data loading
    'nyu_vagc_processing': 1,  # Processing catalog - data loading/processing
    'shi_catalog_acquisition': 1,  # Downloading catalog - data loading/processing
    'soptics_implementation': 6,  # Implementing clustering algorithm - ML
    'soptics_validation_shi': 6,  # Validating clustering - ML

    # Standard Sirens paper
    'dark_energy': 4,  # Predicting constraints on w_0 - Bayesian inference
    'h0_scaling': 2,  # Measuring scaling - summary statistic
    'measure_combo': 3,  # Fitting degeneracy - model fitting
    'modified_gravity': 4,  # Predicting constraints on c_M - Bayesian inference

    # Neutron star maximum mass paper
    'default_mbh': 4,  # Credible interval - Bayesian inference
    'default_mtov': 4,  # Credible interval - Bayesian inference
    'equal_mass_slope': 4,  # Credible interval - Bayesian inference
    'load_data': 1,  # Data loading check - data loading
    'mass_gap': 4,  # Computing probability - Bayesian inference
    'mass_gap_constraint': 4,  # Simulating measurement - Bayesian inference
    'mtov_spin': 4,  # Modal value and limits - Bayesian inference
    'mtov_spin_2': 4,  # Credible interval - Bayesian inference
    'spin_constraint': 4,  # Simulating constraints - Bayesian inference

    # HST satellite trails paper
    'classifier_performance': 6,  # Training classifier - ML
    'satellite_chance_post2020_acis': 2,  # Computing chance - summary statistic
    'satellite_chance_post2020_uvis': 2,  # Computing chance - summary statistic
    'satellite_chance_pre2020_acis': 2,  # Computing chance - summary statistic
    'satellite_chance_pre2020_uvis': 2,  # Computing chance - summary statistic
    'satellite_fractions': 2,  # Computing fraction of trails - summary statistic
    'satellite_fractions_increase': 2,  # Computing fraction increase - summary statistic

    # ACT DR6 lensing paper
    'alens': 3,  # Fitting lensing amplitude - model fitting
    'params': 4,  # Likelihood evaluation for structure growth - Bayesian inference

    # Additional noise wave calibration tasks
    'antenna_temp': 2,  # Calculation of calibrated temperature - measurement
    'cab_temp': 2,  # Temperature gradients - measurement
    'cold_sparam': 1,  # Retrieving S-parameters - data retrieval
    'nwp': 3,  # Deriving noise wave parameters - parameter estimation

    # Additional sOPTICS tasks
    'dbscan_optimization': 6,  # DBSCAN hyperparameter optimization - ML
    'dbscan_test': 6,  # DBSCAN testing - ML

    # PAH optical line paper
    # 'PAH_optical_line_relation_correlation_AGN_hosts': 2,  # REMOVED - Examining relation - summary statistic
    'best_fitting_slopes': 3,  # Estimating slopes of correlation - model fitting
    'feature_PCA': 1,  # Applying PCA on features - data processing
    'feature_PCA_corr_coeffs': 2,  # Correlation coefficients - summary statistic
    'identify_AGN_hosts': 1,  # Identifying AGN hosts from catalog - data processing
    'relation_break_down': 2,  # Identifying breakdown - summary statistic

    # IllustrisTNG DESI paper
    'elg_hod_measurement_and_fitting': 3,  # HOD model fitting - model fitting
    'elg_satellite_fraction': 2,  # Calculating satellite fraction - summary statistic
    'elg_selection_count': 1,  # Counting selected galaxies - data processing
    'lrg_central_velocity_bias': 2,  # Calculating velocity bias - summary statistic
    'lrg_clustering_secondary_bias_ratio': 2,  # Calculating ratio - summary statistic
    'lrg_hod_measurement_and_fitting': 3,  # HOD model fitting - model fitting
    'lrg_satellite_fraction': 2,  # Calculating satellite fraction - summary statistic
    'lrg_selection_count': 1,  # Counting selected galaxies - data processing

    # SMC TRGB paper
    'aseq_bseq_trgb': 2,  # Measuring TRGB magnitude - measurement
    'fit_aseq_bseq': 3,  # Fitting polynomials - model fitting
    'gaia_synthetic_i_trgb': 2,  # Measuring TRGB magnitude - measurement
    'med_color_amp': 2,  # Calculating median values - summary statistic

    # Gaia vertical distribution paper
    # 'gaia_asymmetry_plot': 1,  # REMOVED - Plotting number counts - data processing/visualization
    'gaia_breathing_typical': 2,  # Calculating amplitude - summary statistic
    'gaia_rv_sample_size': 1,  # Counting stars - data loading
    'solar_height_from_gaia_dr2': 3,  # Fitting density model - model fitting
    'sun_height_corrected': 2,  # Determining offset after correction - summary statistic
}

# Check for uncategorized tasks
for item in all_tasks:
    task = item['task']
    task_id = task.task_id

    # Categorize remaining tasks
    if task_id not in categorization:
        # I'll need to see these to categorize them
        print(f"Need to categorize: {task_id}")
        print(f"  Description: {task.description}")
        print()

# Count by category
categories = {
    1: "Data Loading and Processing",
    2: "Summary Statistics and Measurements",
    3: "Model Fitting and Parameter Estimation",
    4: "Bayesian Inference",
    5: "Physical Simulations and Theoretical Calculations",
    6: "Machine Learning Applications"
}

tally = defaultdict(list)
for item in all_tasks:
    task_id = item['task'].task_id
    if task_id in categorization:
        cat = categorization[task_id]
        tally[cat].append(task_id)

# Print results
print("\n" + "="*80)
print("CATEGORIZATION RESULTS")
print("="*80 + "\n")

for cat_num in sorted(categories.keys()):
    count = len(tally[cat_num])
    print(f"{cat_num}. {categories[cat_num]}: {count}")

print(f"\nTotal categorized: {sum(len(tasks) for tasks in tally.values())}")
print(f"Total tasks: {len(all_tasks)}")
print(f"Uncategorized: {len(all_tasks) - sum(len(tasks) for tasks in tally.values())}")

# Print detailed breakdown
print("\n" + "="*80)
print("DETAILED BREAKDOWN BY CATEGORY")
print("="*80 + "\n")

for cat_num in sorted(categories.keys()):
    print(f"\n{cat_num}. {categories[cat_num]} ({len(tally[cat_num])} tasks)")
    print("-" * 80)
    for task_id in sorted(tally[cat_num]):
        print(f"  - {task_id}")
