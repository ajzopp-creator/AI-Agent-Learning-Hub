In institutional trading, feeding a neural network multiple technical indicators (like an SMA crossover, a Super Trend, and an ATR band) causes a massive statistical headache called **multicollinearity**. Because all these indicators are mathematical derivatives of the exact same underlying price and volume data, they aren't actually giving the AI new information—they are just repeating the same signal in different formats, creating a "feedback loop" of noise.  
**Principal Component Analysis (PCA)** is the mathematical toolkit used to fix this. It is a dimensionality-reduction technique that takes a large set of correlated variables and transforms them into a smaller set of completely uncorrelated variables called **Principal Components (PCs)**.  
Here is a breakdown of how it works conceptually and mathematically for a quantitative trading system.

## **The Conceptual Intuition**

Imagine you are looking at a 3D swarm of data points representing Price, Volume, and Volatility. If you look at it from a random angle, the data looks like a chaotic, noisy cloud.  
PCA rotates the entire dataset in space to find a new perspective. It searches for the specific axis where the data points are stretched out the furthest—this axis captures the **maximum variance** (the most information). That becomes **Principal Component 1 (PC1)**.  
Then, it looks for the next axis, strictly perpendicular (orthogonal) to the first, that captures the next highest amount of remaining variance. That becomes **PC2**. Because they are perpendicular, PC1 and PC2 have a correlation of exactly $0.0$.

## **The Step-by-Step Mathematical Engine**

To transform your collinear technical indicators using PCA, an algorithmic system executes five core steps:

### **1\. Standardization (Z-Score Normalization)**

Indicators have wildly different scales. An SMA is measured in asset price (e.g., $150), Volume is measured in millions, and an RSI ranges from 0 to 100\. PCA is sensitive to variances, so variables with large scales will dominate. We standardize every feature to have a mean of 0 and a standard deviation of 1 using:

$$Z \= \\frac{X \- \\mu}{\\sigma}$$

### **2\. Covariance Matrix Computation**

Next, the system calculates a symmetric matrix that measures how all the standardized indicators move together. If you input 4 indicators, it builds a $4 \\times 4$ covariance matrix. If the values inside are highly positive or negative, it proves severe multicollinearity exists.

### **3\. Eigenvector and Eigenvalue Decomposition**

This is the linear algebra core. The system solves the characteristic equation of the covariance matrix ($\\Sigma$) to find its **Eigenvectors** ($v$) and **Eigenvalues** ($\\lambda$):

$$\\Sigma v \= \\lambda v$$

* **Eigenvectors ($v$):** These dictate the *direction* of the new axes (the Principal Components). They represent the coefficients (loadings) assigned to your original technical indicators.  
* **Eigenvalues ($\\lambda$):** These dictate the *magnitude* or the amount of total market variance carried by that specific component.

### **4\. Sorting and Selecting Components**

If you input 4 indicators, you get 4 Principal Components. However, the system sorts them by their Eigenvalues from highest to lowest. You then compute the **Explained Variance Ratio**:

$$\\text{Explained Variance} \= \\frac{\\lambda\_i}{\\sum \\lambda}$$  
Typically, you will find that **PC1** and **PC2** combined capture $90\\%+$ of the total information, while PC3 and PC4 contain less than $10\\%$ (mostly baseline market noise). You drop PC3 and PC4, successfully compressing your data.

### **5\. Projecting onto the New Feature Space**

Finally, the raw technical indicator data is mathematically multiplied by the selected eigenvectors. This transforms your original, messy, overlapping indicators into brand new, completely uncorrelated data streams.

## **Why this Matters for "Trade the Bounce"**

Instead of feeding your Artificial Neural Network 5 overlapping indicators that blind its predictive accuracy, you feed it **PC1 (which might represent "Trend/Momentum Energy")** and **PC2 (which might represent "Mean Reversion/Volatility Exhaustion")**.  
By eliminating collinearity, your model trains faster, prevents overfitting, and gives you a much cleaner, statistically valid signal when tracking a price bounce.