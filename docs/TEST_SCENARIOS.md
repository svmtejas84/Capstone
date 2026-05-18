# Test Scenarios and Outputs

This document contains the output of two test scenarios run on May 18, 2026, to validate the functionality of the toxicity-aware routing engine.

## Scenario 1: Evening Commute

This test simulates a user planning an evening commute.

- **Source:** (13.1295, 77.5877)
- **Destination:** (13.0834, 77.6433)
- **Departure Time:** 2026-05-18 18:30:00

### Jogger

```
--- Testing Commute Mode: JOGGER ---
Recommended Route ID: route_2
Total Cost (Toxicity Dose): 135.491235
Distance Covered: 14484.37 meters

--- Route Explanation ---
Gale-Shapley and A* Scoring (Preference Score):
  - Base Score: 1.164183512
  - Dose Contribution: -0.029021705
  - Distance Contribution: -0.019822283
  - Final Score: 1.115339523
  (This score determines route preference. A lower score is better.)

ST-PIGNN SHAP Explanation not available for this route.

--- Node Analysis & Gale-Shapley Candidates ---
The recommended route (route_2) consists of 174 nodes.
This path was chosen by the A* algorithm using a composite weight of distance and predicted toxicity from the ST-PIGNN model.
The Gale-Shapley algorithm then selected this route from a set of candidates to mitigate herd behavior.

All evaluated candidates:
  - Candidate: route_1
    - Rank: 1
    - Distance: 14479.301m
    - Dose: 135.443816
  - Candidate: route_2 (Recommended)
    - Rank: 2
    - Distance: 14484.37m
    - Dose: 135.491235
  - Candidate: route_0
    - Rank: 3
    - Distance: 16392.379m
    - Dose: 153.33933
```

### Cyclist

```
--- Testing Commute Mode: CYCLIST ---
Recommended Route ID: route_2
Total Cost (Toxicity Dose): 92.209313
Distance Covered: 14484.37 meters

--- Route Explanation ---
Gale-Shapley and A* Scoring (Preference Score):
  - Base Score: 1.309313894
  - Dose Contribution: -0.023217364
  - Distance Contribution: -0.031715652
  - Final Score: 1.254380877
  (This score determines route preference. A lower score is better.)

ST-PIGNN SHAP Explanation not available for this route.

--- Node Analysis & Gale-Shapley Candidates ---
The recommended route (route_2) consists of 174 nodes.
This path was chosen by the A* algorithm using a composite weight of distance and predicted toxicity from the ST-PIGNN model.
The Gale-Shapley algorithm then selected this route from a set of candidates to mitigate herd behavior.

All evaluated candidates:
  - Candidate: route_1
    - Rank: 1
    - Distance: 14479.301m
    - Dose: 92.177041
  - Candidate: route_2 (Recommended)
    - Rank: 2
    - Distance: 14484.37m
    - Dose: 92.209313
  - Candidate: route_0
    - Rank: 3
    - Distance: 16392.379m
    - Dose: 104.355933
```

### Car

```
--- Testing Commute Mode: CAR ---
Recommended Route ID: route_0
Total Cost (Toxicity Dose): 7.155835
Distance Covered: 16392.379 meters

--- Route Explanation ---
Gale-Shapley and A* Scoring (Preference Score):
  - Base Score: 1.551197865
  - Dose Contribution: 0.027195161
  - Distance Contribution: 0.103487747
  - Final Score: 1.681880773
  (This score determines route preference. A lower score is better.)

ST-PIGNN SHAP Explanation not available for this route.

--- Node Analysis & Gale-Shapley Candidates ---
The recommended route (route_0) consists of 151 nodes.
This path was chosen by the A* algorithm using a composite weight of distance and predicted toxicity from the ST-PIGNN model.
The Gale-Shapley algorithm then selected this route from a set of candidates to mitigate herd behavior.

All evaluated candidates:
  - Candidate: route_1
    - Rank: 1
    - Distance: 14479.301m
    - Dose: 6.320711
  - Candidate: route_2
    - Rank: 2
    - Distance: 14484.37m
    - Dose: 6.322924
  - Candidate: route_0 (Recommended)
    - Rank: 3
    - Distance: 16392.379m
    - Dose: 7.155835
```

## Scenario 2: Late Night Travel

This test simulates a user traveling late at night.

- **Source:** (12.953, 77.5456)
- **Destination:** (12.9676, 77.5727)
- **Departure Time:** 2026-05-18 02:30:00

### Jogger

```
--- Testing Commute Mode: JOGGER ---
Recommended Route ID: route_2
Total Cost (Toxicity Dose): 113.811408
Distance Covered: 6062.559 meters

--- Route Explanation ---
Gale-Shapley and A* Scoring (Preference Score):
  - Base Score: 0.722302391
  - Dose Contribution: -0.101162324
  - Distance Contribution: 0.014797728
  - Final Score: 0.635937794
  (This score determines route preference. A lower score is better.)

ST-PIGNN SHAP Explanation not available for this route.

--- Node Analysis & Gale-Shapley Candidates ---
The recommended route (route_2) consists of 120 nodes.
This path was chosen by the A* algorithm using a composite weight of distance and predicted toxicity from the ST-PIGNN model.
The Gale-Shapley algorithm then selected this route from a set of candidates to mitigate herd behavior.

All evaluated candidates:
  - Candidate: route_1
    - Rank: 1
    - Distance: 6061.506m
    - Dose: 113.803709
  - Candidate: route_2 (Recommended)
    - Rank: 2
    - Distance: 6062.559m
    - Dose: 113.811408
  - Candidate: route_0
    - Rank: 3
    - Distance: 4643.031m
    - Dose: 191.179932
```

### Cyclist

```
--- Testing Commute Mode: CYCLIST ---
Recommended Route ID: route_2
Total Cost (Toxicity Dose): 77.454986
Distance Covered: 6062.559 meters

--- Route Explanation ---
Gale-Shapley and A* Scoring (Preference Score):
  - Base Score: 0.717567707
  - Dose Contribution: -0.080929859
  - Distance Contribution: 0.023676364
  - Final Score: 0.660314211
  (This score determines route preference. A lower score is better.)

ST-PIGNN SHAP Explanation not available for this route.

--- Node Analysis & Gale-Shapley Candidates ---
The recommended route (route_2) consists of 120 nodes.
This path was chosen by the A* algorithm using a composite weight of distance and predicted toxicity from the ST-PIGNN model.
The Gale-Shapley algorithm then selected this route from a set of candidates to mitigate herd behavior.

All evaluated candidates:
  - Candidate: route_1
    - Rank: 1
    - Distance: 6061.506m
    - Dose: 77.449746
  - Candidate: route_2 (Recommended)
    - Rank: 2
    - Distance: 6062.559m
    - Dose: 77.454986
  - Candidate: route_0
    - Rank: 3
    - Distance: 4643.031m
    - Dose: 130.108565
```

### Car

```
--- Testing Commute Mode: CAR ---
Recommended Route ID: route_2
Total Cost (Toxicity Dose): 5.311199
Distance Covered: 6062.559 meters

--- Route Explanation ---
Gale-Shapley and A* Scoring (Preference Score):
  - Base Score: 0.709676566
  - Dose Contribution: -0.047209085
  - Distance Contribution: 0.038474092
  - Final Score: 0.700941574
  (This score determines route preference. A lower score is better.)

ST-PIGNN SHAP Explanation not available for this route.

--- Node Analysis & Gale-Shapley Candidates ---
The recommended route (route_2) consists of 120 nodes.
This path was chosen by the A* algorithm using a composite weight of distance and predicted toxicity from the ST-PIGNN model.
The Gale-Shapley algorithm then selected this route from a set of candidates to mitigate herd behavior.

All evaluated candidates:
  - Candidate: route_1
    - Rank: 1
    - Distance: 6061.506m
    - Dose: 5.31084
  - Candidate: route_2 (Recommended)
    - Rank: 2
    - Distance: 6062.559m
    - Dose: 5.311199
  - Candidate: route_0
    - Rank: 3
    - Distance: 4643.031m
    - Dose: 8.92173
```
