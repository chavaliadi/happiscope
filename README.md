# HappiScope

**HappiScope** is an interactive research and analytical platform for investigating national subjective well-being using longitudinal panel data from the World Happiness Report (Gallup World Poll). The platform brings together exploratory data analysis, explanatory econometric regression, non-linear machine learning validation, unsupervised clustering, longitudinal cohort tracking, continuous piecewise regression, and well-being literature synthesis into a unified interface.

---

## Table of Contents
- [Why HappiScope?](#why-happiscope)
- [Research Questions](#research-questions)
- [Dataset](#dataset)
- [Data Preparation](#data-preparation)
- [Methodology](#methodology)
  - [Exploratory Data Analysis](#exploratory-data-analysis)
  - [Multiple Linear Regression](#multiple-linear-regression)
  - [Random Forest Validation](#random-forest-validation)
  - [Spearman Rank Correlation](#spearman-rank-correlation)
  - [K-Means Clustering](#k-means-clustering)
  - [Principal Component Analysis (PCA)](#principal-component-analysis-pca)
  - [Longitudinal Cohort Tracking](#longitudinal-cohort-tracking)
  - [Continuous Piecewise Regression](#continuous-piecewise-regression)
- [Application Structure](#application-structure)
- [Research Background](#research-background)
- [From Existing Research to HappiScope](#from-existing-research-to-happiscope)
- [What the Project Produces](#what-the-project-produces)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Installation](#installation)
  - [Windows](#windows)
  - [macOS](#macos)
- [Running the Notebook](#running-the-notebook)
- [Limitations](#limitations)
- [Reproducibility](#reproducibility)
- [References](#references)

---

## Why HappiScope?

National well-being cannot be captured by a single ranking or headline score. While gross domestic product (GDP) has historically served as a standard proxy for national success, modern well-being economics recognizes that subjective quality of life depends on a multidimensional balance of economic prosperity, social support networks, healthy longevity, institutional trust, personal autonomy, and civic generosity.

HappiScope was developed to investigate the empirical nuances behind national well-being:
- Which structural factors correlate most strongly with life satisfaction across nations?
- How stable are these associations across geographical regions and over time?
- Do countries naturally group into distinct clusters based on their structural factor profiles?
- How do these distinct country groups evolve longitudinally over decades?
- Does happiness continue to rise with income, or does the relationship plateau beyond a threshold?
- How do empirical findings from cross-national survey data connect to four decades of well-being literature?

> **Methodological Note:** HappiScope examines empirical associations in observational panel survey data. Findings reflect correlational and statistical patterns; they do not establish direct individual-level causal mechanics.

---

## Research Questions

HappiScope is structured around four primary research questions corresponding to the four application sections:

| Section | Central Research Question |
|---|---|
| **Overview** | What does the global distribution of subjective well-being look like, and how have national happiness scores shifted between 2005 and 2023? |
| **Factor Breakdown** | How strongly are the six standard World Happiness Report factors associated with national life satisfaction, and does a non-linear machine learning model agree with linear econometric weights? |
| **Clusters & Trends** | Can nations be grouped into distinct structural well-being profiles without using happiness scores as an input, and how do those fixed country cohorts progress historically? |
| **The Debate: Does Income Plateau?** | Does the observed relationship between national income (Log GDP per capita) and Life Ladder remain linear, or does an empirical continuous piecewise model provide a superior statistical fit? |

---

## Dataset

HappiScope uses longitudinal panel data derived from the World Happiness Report (Gallup World Poll), spanning 165 countries across 2005–2023. The project repository maintains three local data artifacts in the `data/` directory:

### 1. `data/happiscope_master.csv`
The primary panel dataset containing 2,363 country-year observations across 11 variables:

| Variable | Type | Description |
|---|---|---|
| `Country name` | String | Sovereign nation or territory name (165 unique countries). |
| `year` | Integer | Survey collection year (2005–2023). |
| `Life Ladder` | Float (0–10) | Primary outcome variable: Cantril Self-Anchoring Striving Scale (0 = worst possible life, 10 = best possible life). |
| `Log GDP per capita` | Float | Natural log of purchasing power parity (PPP) GDP per capita (constant 2017 international dollars). |
| `Social support` | Float (0–1) | National average binary response: "If you were in trouble, do you have relatives or friends you can count on?" |
| `Healthy life expectancy at birth` | Float (years) | Estimated healthy life expectancy in years based on World Health Organization (WHO) data. |
| `Freedom to make life choices` | Float (0–1) | National average binary response: "Are you satisfied or dissatisfied with your freedom to choose what you do with your life?" |
| `Generosity` | Float | Residual of regressing national average donations on Log GDP per capita. |
| `Perceptions of corruption` | Float (0–1) | National average binary response regarding corruption in government and businesses. |
| `Positive affect` | Float (0–1) | Average measure of positive affect (happiness, laughter, enjoyment) experienced yesterday. |
| `Negative affect` | Float (0–1) | Average measure of negative affect (worry, sadness, anger) experienced yesterday. |

### 2. `data/country_region.csv`
Geographical reference mapping containing 165 countries mapped to 6 continental regions (`Asia`, `Europe`, `Africa`, `South America`, `North America`, `Oceania`) and standardized ISO-3 country codes for choropleth mapping.

### 3. `data/importance_comparison.csv`
Exported validation table from the project's analytical pipeline comparing standardized Ordinary Least Squares (OLS) regression coefficients against Random Forest permutation feature importances and test-set performance metrics.

---

## Data Preparation

HappiScope enforces a transparent complete-case filtering pipeline tailored to each statistical model. Because survey coverage varies across indicators and years, different analyses use model-specific samples:

- **Multivariate Explanatory Modeling (`Factor Breakdown`):** Requires complete observations across all six WHR explanatory factors plus `Life Ladder`. This complete-case filter yields $N = 2,103$ country-year observations across 2005–2023.
- **Bivariate Income Analysis (`The Debate`):** Requires complete observations only for `Log GDP per capita` and `Life Ladder`. Because observations missing secondary indicators (e.g., corruption or generosity) are retained, the sample size expands to $N = 2,335$ for the pooled panel and $N = 129$ for the cross-sectional 2023 survey year.
- **Cross-Sectional Clustering (`Clusters & Trends`):** Filters for complete observations across the six explanatory factors within a chosen baseline year (e.g., $N = 110$ complete nations in 2023).
- **Longitudinal Cohort Tracking:** Groups established in the baseline clustering year are mapped to fixed cohorts and followed across all available years (2005–2023), averaging all available country scores within that cohort for each year.

---

## Methodology

### Exploratory Data Analysis
The Overview section computes annual descriptive statistics, identifies global happiness leaders and laggards, and renders an interactive world choropleth map color-scaled by Cantril Life Ladder score.

### Multiple Linear Regression
To evaluate the relative explanatory power of the six WHR factors, HappiScope estimates a multivariate Ordinary Least Squares (OLS) regression:

$$\text{Life Ladder}_i = \beta_0 + \sum_{j=1}^{6} \beta_j X_{ij} + \varepsilon_i$$

Because predictor units differ fundamentally (GDP is logarithmic, life expectancy is measured in years, and social support runs from 0 to 1), raw coefficients cannot be directly compared. HappiScope standardizes all six factors ($z$-score standardization: $\mu = 0, \sigma = 1$) to compute standardized regression coefficients ($\beta^*$), enabling fair ranking of relative driver strength.

The model is also evaluated:
- **Year-by-year:** Tracking annual coefficients from 2006 to 2023 (excluding 2005 due to low sample size $N < 30$).
- **By Region:** Estimating regional models for continents meeting a minimum sample threshold of $N \ge 60$.

### Random Forest Validation
To test whether linear regression assumptions obscure complex non-linear interactions or non-linear effects, the project fits a non-linear machine learning model:
- **Algorithm:** `RandomForestRegressor(n_estimators=200, random_state=42)`
- **Evaluation:** Evaluated on a held-out 20% test split ($N = 421$), achieving a test-set $R^2 \approx 0.866$ (compared to linear OLS $R^2 \approx 0.753$).
- **Permutation Importance:** Scored on the unseen test set over 10 repeats to identify true generalization importance without mean-decrease-in-impurity (MDI) cardinality bias.

### Spearman Rank Correlation
To assess structural agreement between the econometric model and machine learning model, HappiScope calculates the Spearman rank correlation ($\rho$) between standardized OLS weights and Random Forest permutation importances:

$$\rho = 0.89 \quad (p = 0.019)$$

This strong positive rank correlation indicates substantial agreement between the relative factor rankings produced by the standardized OLS coefficients and Random Forest permutation importances. In this dataset, economic productivity, social support, and healthy life expectancy represent the strongest empirical associations with national happiness scores.

### K-Means Clustering
To uncover exploratory country groupings based on their six-factor profiles without circularity, HappiScope implements unsupervised K-Means clustering on the six standardized explanatory drivers:
- **Features:** Standardized Log GDP, Social support, Healthy life expectancy, Freedom, Generosity, and Perceptions of corruption.
- **Outcome Exclusion:** `Life Ladder` and geographical identifiers are strictly excluded from the clustering matrix.
- **Hyperparameters:** Evaluates user-selectable cluster counts $K \in [3, 6]$ (default $K = 4$) with `random_state=42` and `n_init=10`.
- **Diagnostics:** Computes Within-Cluster Sum of Squares (Inertia/WCSS) and Silhouette Score for the chosen $K$, accompanied by a diagnostic curve across $K \in [2, 8]$.

### Principal Component Analysis (PCA)
For intuitive visualization of high-dimensional clusters, the 6-dimensional factor space is projected onto 2 orthogonal axes using `PCA(n_components=2, random_state=42)`. The first two principal components capture the majority of factor variance ($\approx 53.6\%$ and $15.5\%$, respectively). 

> **Interpretation Warning:** PCA axes are mathematical dimensions of maximum variance, not standalone real-world traits.

### Longitudinal Cohort Tracking
To avoid "cluster label drift" (where dynamic annual reclustering arbitrarily shuffles cluster IDs), HappiScope implements a fixed-cohort methodology:
1. Clusters are generated once using a selected baseline year (e.g., 2023).
2. Country memberships in each cluster are frozen into permanent cohorts.
3. The average Life Ladder trajectory of these exact cohorts is tracked across all panel years from 2005 to 2023.

### Continuous Piecewise Regression
To investigate whether happiness plateaus at higher income levels, HappiScope fits a continuous piecewise (segmented) regression:

$$Y = \beta_0 + \beta_1 X + \beta_2 \max(0, X - \tau) + \varepsilon$$

where:
- $X = \text{Log GDP per capita}$
- $Y = \text{Life Ladder}$
- $\tau = \text{Breakpoint (income threshold)}$
- **Slope below breakpoint:** $\beta_1$
- **Slope above breakpoint:** $\beta_1 + \beta_2$
- **Continuity constraint:** The hinge function $\max(0, X - \tau)$ guarantees that both linear segments join continuously at $\tau$.

**Breakpoint Estimation:** The optimal threshold $\tau^*$ is discovered via grid search over 80 candidate thresholds spanning the 10th to 90th percentiles of observed Log GDP per capita, selecting the breakpoint that minimizes the Akaike Information Criterion (AIC). An interactive slider also allows users to test counterfactual user-selected breakpoints.

---

## Application Structure

The Streamlit application (`app.py`) provides four navigation routes:

```
HappiScope (app.py)
├── 1. Overview (views/overview.py)
│   ├── Year slider (2005–2023)
│   ├── Global summary metrics (surveyed countries, mean score, top country)
│   ├── Interactive world choropleth map
│   └── Top 10 and Bottom 10 national ranking tables
│
├── 2. Factor Breakdown (views/factor_breakdown.py)
│   ├── Tab 1: Country breakdown (individual country factor profiles)
│   ├── Tab 2: Global drivers (standardized OLS vs Random Forest comparison)
│   ├── Tab 3: Temporal shifts (yearly regression coefficients & pooled sub-periods)
│   └── Tab 4: Regional comparison (standardized coefficients by continent)
│
├── 3. Clusters & Trends (views/clusters_and_trends.py)
│   ├── Clustering controls (base year selector, K slider 3..6)
│   ├── Cluster diagnostics (Silhouette score, Inertia, K=2..8 elbow curve)
│   ├── 2D PCA cluster projection scatter plot
│   ├── Cluster profiles (mean unstandardized factor levels grouped bar chart)
│   ├── Country explorer (individual country vs cluster mean comparison)
│   └── Longitudinal cohort tracking (2005–2023 trajectory of fixed base cohorts)
│
└── 4. The Debate: Does Income Plateau? (views/the_debate.py)
    ├── Sample scope selector (Full Pooled Panel vs Single Year)
    ├── Breakpoint mode selector (Optimal Data-Estimated vs Custom Slider)
    ├── Continuous piecewise regression scatter plot with overlaid OLS fits
    ├── Key slope estimates (slope below tau, slope above tau, delta R-squared)
    ├── Head-to-head statistical comparison table (R², AIC, BIC, RSS)
    ├── Empirical model comparison & causal qualification
    └── Literature expander (Easterlin, Stevenson-Wolfers, Kahneman-Deaton, Killingsworth)
```

---

## Research Background

HappiScope contextualizes its empirical analyses within established literature in well-being economics:

### 1. The Easterlin Paradox (Easterlin, 1974)
Richard Easterlin identified that while wealthier individuals within a country report higher happiness than poorer individuals at a single point in time, long-term national economic growth in developed economies (e.g., post-war United States and Japan) did not produce a corresponding secular rise in average national happiness. Easterlin attributed this to **hedonic adaptation** (the hedonic treadmill) and **relative social comparison**.

### 2. Stevenson & Wolfers (2008): Reassessing the Paradox
Betsey Stevenson and Justin Wolfers analyzed international cross-sectional datasets (including the Gallup World Poll and World Values Survey) across 130+ nations. They concluded that there is no clear satiation point at the national level: the relationship between subjective well-being and log GDP is positive and log-linear across both developing and developed nations.

### 3. Kahneman & Deaton (2010): Emotional Well-Being vs. Life Evaluation
Daniel Kahneman and Angus Deaton analyzed 450,000 Gallup-Healthways responses from US residents, distinguishing two aspects of subjective well-being:
- **Emotional well-being** (day-to-day emotional experiences such as joy, sadness, stress): Plateaus at approximately **$75,000** annual income.
- **Life evaluation** (Cantril Self-Anchoring Ladder): Does **not** plateau; continues to rise log-linearly with income.

Because the World Happiness Report uses the Cantril Life Ladder, cross-national WHR data predominantly captures evaluative life satisfaction rather than day-to-day emotional affect.

### 4. Killingsworth (2021) & Adversarial Collaboration (2023)
Matthew Killingsworth used smartphone experience sampling across 33,000+ US adults, finding that experienced well-being continues to rise above $75,000. In a subsequent adversarial collaboration arbitrated by Barbara Mellers (Kahneman, Killingsworth, & Mellers, 2023), the researchers reconciled their findings: happiness rises continuously with income for the majority of individuals, while an income plateau occurs only for an unhappy minority whose suffering is driven by non-financial distress.

### 5. Diener, Suh, Lucas, & Smith (1999)
Ed Diener and colleagues reviewed three decades of subjective well-being research, emphasizing that external demographic and economic factors account for only a portion of variance in happiness, with social relationships, personality traits, and psychological coping mechanisms explaining substantial individual variation.

---

## From Existing Research to HappiScope

Existing academic literature provides theoretical frameworks, econometric methodologies, and foundational debates. HappiScope operationalizes these theories into an open, interactive analytical workflow:
- Rather than viewing national happiness as an abstract index, users can examine how standardized factor contributions differ across regions.
- Rather than debating the income-happiness relationship in the abstract, users can test empirical piecewise regression breakpoints against cross-national panel data and observe statistical fit metrics in real time.
- Rather than assuming country groups remain constant, users can observe the 20-year historical trajectories of fixed factor cohorts.

---

## What the Project Produces

Key outputs produced by the HappiScope platform include:

| Output | Key Finding / Value |
|---|---|
| **Global OLS Model** | $R^2 \approx 0.753$, $N = 2,103$. All six WHR factors achieve statistical significance ($p < 0.001$). |
| **Top Standardized Drivers** | Log GDP per capita ($\beta^* \approx +0.411$) and Social support ($\beta^* \approx +0.325$) represent the strongest linear associations. |
| **Random Forest Validation** | Test-set $R^2 \approx 0.866$ on held-out 20% test data ($N = 421$). Permutation importance indicates Log GDP as the dominant feature. |
| **Model Agreement** | Spearman rank correlation $\rho = 0.89$ ($p = 0.019$) between standardized OLS weights and Random Forest permutation importances. |
| **K-Means Profiles ($K=4$)** | Identifies distinct exploratory factor groupings (e.g., high-wealth/high-support vs. low-resource/high-autonomy nations) at $N = 110$ complete countries in 2023. |
| **Longitudinal Cohorts** | Demonstrates that structural factor cohorts formed in 2023 maintain parallel, distinct happiness tiers across 2005–2023. |
| **Piecewise Income Model** | Breakpoint estimated at $\tau^* \approx 9.58$ ($\approx \$14,400$ PPP GDP/capita). Below $\tau$: slope $= +0.565$; above $\tau$: slope $= +1.081$ ($\Delta R^2 = +0.0195$, $\text{AIC} = 4811.8$ vs linear $4930.9$). |

---

## Tech Stack

The application is built entirely in Python using stable, industry-standard scientific and visualization libraries:

- **Python** (version 3.10 to 3.13 supported)
- **Streamlit** (interactive web dashboard framework, $\ge 1.50$)
- **pandas** (data manipulation and panel aggregation)
- **NumPy** (vectorized calculations and array transformations)
- **SciPy** (statistical distributions and Spearman rank correlation)
- **statsmodels** (Ordinary Least Squares regression and econometric diagnostics)
- **scikit-learn** (StandardScaler, KMeans, PCA, silhouette scoring, RandomForestRegressor)
- **Plotly** (interactive choropleth maps, scatter plots, grouped bar charts, and trend visualizations)

---

## Project Structure

```
happiscope/
├── app.py                     # Main Streamlit router and sidebar navigation
├── common.py                  # Shared data loaders, constants, and OLS regression helpers
├── requirements.txt           # Project Python dependencies
├── README.md                  # Comprehensive project documentation
├── .gitignore                 # Git ignore rules (cache, virtual environments)
├── happiscope.ipynb           # Localized exploratory Jupyter notebook
├── data/
│   ├── happiscope_master.csv        # WHR panel dataset (165 countries, 2005–2023)
│   ├── country_region.csv           # Country-to-region mapping and ISO-3 codes
│   └── importance_comparison.csv    # Standardized OLS vs Random Forest comparison
└── views/
    ├── __init__.py                  # Views package initialization
    ├── overview.py                  # Page 1: World map and global overview
    ├── factor_breakdown.py          # Page 2: OLS decomposition & RF validation
    ├── clusters_and_trends.py       # Page 3: K-Means clustering, PCA, & cohort trends
    ├── the_debate.py                # Page 4: Piecewise regression on income satiation
    └── coming_soon.py               # Fallback placeholder component
```

---

## Installation

### Windows

#### 1. Prerequisites
Ensure Python 3.10, 3.11, 3.12, or 3.13 is installed. Verify via Command Prompt or PowerShell:
```powershell
python --version
pip --version
```
*(If Python is not recognized, ensure "Add Python to PATH" was checked during installation.)*

#### 2. Clone the Repository
```powershell
git clone https://github.com/chavaliadi/happiscope.git
cd happiscope
```

#### 3. Create and Activate Virtual Environment
```powershell
python -m venv .venv
.venv\Scripts\activate
```

#### 4. Install Dependencies
```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

#### 5. Run the Application
```powershell
streamlit run app.py
```
Streamlit will launch locally in your browser at `http://localhost:8501`.

---

### macOS

#### 1. Prerequisites
Ensure Python 3.10+ is installed. Open Terminal and verify:
```bash
python3 --version
pip3 --version
```

#### 2. Clone the Repository
```bash
git clone https://github.com/chavaliadi/happiscope.git
cd happiscope
```

#### 3. Create and Activate Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate
```

#### 4. Install Dependencies
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

#### 5. Run the Application
```bash
streamlit run app.py
```
Open `http://localhost:8501` in your browser.

#### Troubleshooting
- **Port Conflict:** If port 8501 is occupied, specify an alternative port: `streamlit run app.py --server.port 8502`.
- **Script Execution Blocked (Windows):** If PowerShell prevents script execution, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` prior to activating `.venv`.

---

## Running the Notebook

The project includes `happiscope.ipynb`, which contains the initial exploratory calculations, regression tests, and Random Forest feature importance derivations.

To run the notebook locally:
1. Ensure the virtual environment is activated.
2. Install Jupyter if not already available: `pip install jupyterlab` or `pip install notebook`.
3. Launch Jupyter:
   ```bash
   jupyter lab
   ```
4. Open `happiscope.ipynb`. The notebook references local datasets in `data/` and requires no external downloads or cloud credentials.

---

## Limitations

- **Observational Nature:** All analyses reflect observational cross-national survey data. Coefficients represent statistical associations, not individual causal mechanisms.
- **Ecological Fallacy:** Relationships observed at the aggregate country level (e.g., national average GDP vs. average happiness) cannot be directly mapped to individual persons within those nations.
- **Sample Selection Differences:** Due to survey coverage variations across indicators, different analyses evaluate different complete-case samples ($N = 2,103$ for multivariate OLS, $N = 2,335$ for bivariate income models, and $N = 110$ for 2023 clustering).
- **Cluster Sensitivity:** K-Means clustering depends on feature selection, standardization, and the choice of baseline year; clusters represent exploratory factor groupings rather than fixed sociological taxonomies.
- **PCA Dimensionality:** While the 2D PCA projection explains over $69\%$ of feature variance, approximately $31\%$ of multidimensional information is not captured in the 2D visualization plane.
- **Income Metric Scope:** `Log GDP per capita` captures purchasing-power economic output, but does not measure wealth inequality (Gini coefficient), cost of living spikes, or distribution of social safety benefits.

---

## Reproducibility

The project is designed for reproducible local execution:
- **Random States:** All stochastic algorithms use fixed seeds (`random_state=42` in K-Means, PCA, train/test splitting, Random Forest training, and permutation importance repeats).
- **Deterministic Data Pipelines:** All calculations read from immutable local CSV artifacts in `data/`.
- **Consistent Python Runtime:** The required Python packages are declared in `requirements.txt`, and the application has been validated in a Python 3.13 virtual environment.

---

## References

1. **Easterlin, R. A.** (1974). Does economic growth improve the human lot? Some empirical evidence. In P. A. David & M. W. Reder (Eds.), *Nations and Households in Economic Growth: Essays in Honor of Moses Abramovitz* (pp. 89–125). Academic Press.
2. **Stevenson, B., & Wolfers, J.** (2008). Economic growth and subjective well-being: Reassessing the Easterlin paradox. *Brookings Papers on Economic Activity*, 2008(1), 1–87.
3. **Kahneman, D., & Deaton, A.** (2010). High income improves evaluation of life but not emotional well-being. *Proceedings of the National Academy of Sciences*, 107(38), 16489–16493.
4. **Killingsworth, M. A.** (2021). Experienced well-being rises with income, even above $75,000 per year. *Proceedings of the National Academy of Sciences*, 118(4), e2016976118.
5. **Killingsworth, M. A., Kahneman, D., & Mellers, B.** (2023). Income and emotional well-being: A conflict resolved. *Proceedings of the National Academy of Sciences*, 120(10), e2208661120.
6. **Diener, E., Suh, E. M., Lucas, R. E., & Smith, H. L.** (1999). Subjective well-being: Three decades of progress. *Psychological Bulletin*, 125(2), 276–302.
7. **Helliwell, J. F., Layard, R., Sachs, J. D., De Neve, J.-E., Aknin, L. B., & Wang, S.** (Eds.). (2024). *World Happiness Report 2024*. University of Oxford: Wellbeing Research Centre.
