# Target Variable Scaling Strategy

This document outlines the current scaling strategy for the PM2.5 target variable and provides recommendations for future improvements.

## Current Strategy (As of May 2024)

The current model (`citywide_stpignn_best.pt`) was trained on a target variable (`station_pm25`) that was scaled using a "MaxAbs" scaling method.

-   **Method**: Every `station_pm25` value was divided by the single maximum value observed across the entire dataset.
-   **Scaling Value**: `342.9356`
-   **Source of Truth**: The scaling value is stored in `gnn/model_weights/target_scaler.json` and is loaded dynamically during evaluation and inference.
-   **Implementation**:
    -   The original training was performed in the `notebooks/cluster_working.ipynb` notebook, where this scaling was applied.
    -   Evaluation scripts like `scripts/evaluate_stpignn_holdout.py` and baseline models like `gnn/persistence_baseline.py` have been updated to load and use this scaler to ensure consistency.

### Assessment

This approach is **scientifically acceptable** because it is applied consistently across training, evaluation, and inference. The results are valid and reproducible.

However, it is **not ideal** because the scaling of the entire dataset is dependent on a single outlier, which can suppress the variance of more common, lower-range values.

## Recommended Future Work (Option B)

For improved model robustness and better alignment with common machine learning practices, the model should be retrained using `StandardScaler`.

### Action Plan

1.  **Calculate New Scaler values (in Notebook)**:
    -   In the training notebook (e.g., a copy of `notebooks/cluster_working.ipynb`), calculate the **mean** and **standard deviation** of the `station_pm25` column.
    -   **Important**: These statistics must be calculated from the **training dataset only** to prevent data leakage from the validation or test sets.

2.  **Update Scaler File (in Repo)**:
    -   Update the `gnn/model_weights/target_scaler.json` file to store the new statistics. The format should be updated to something like:
        ```json
        {
          "type": "standard",
          "mean": <calculated_mean>,
          "std": <calculated_std>
        }
        ```

3.  **Modify Data Loading and Scaling Logic (in Notebook and Repo)**:
    -   Update the data loading process in the training notebook to apply the new scaling: `scaled_value = (raw_value - mean) / std`.
    -   Update all relevant scripts in the repository (e.g., `scripts/evaluate_stpignn_holdout.py`, `gnn/persistence_baseline.py`) to correctly load and apply the mean/std scaling for evaluation and inference.

4.  **Retrain the Model (in Notebook)**:
    -   Retrain the `STPIGNN` model from scratch using the newly scaled data.
    -   Save the new best checkpoint and update the model card.

By following this plan, the project will move to a more robust and standard scaling methodology, likely improving model performance and making the results more defensible.
