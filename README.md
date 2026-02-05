# 🏎️ Formula 1 Strategy Analysis with Game Theory (2021 Abu Dhabi GP)

## 📌 Project Overview
This project analyzes the strategic decision-making process during the controversial **2021 Abu Dhabi Grand Prix** using **Game Theory** and **Python**.

We simulate the "Prisoner's Dilemma" faced by Lewis Hamilton (Mercedes) and Max Verstappen (Red Bull) in the final laps, factoring in:
* **Tyre Performance:** Old Hard vs. New Soft tyres.
* **Safety Car Probability:** Calculated Expected Value based on risk.
* **Nash Equilibrium:** Determining the optimal strategy for both drivers.

## 🛠️ Tech Stack
* **Python 3.10+**
* **FastF1** (Telemetry Data)
* **Pandas & NumPy** (Data Processing)
* **Seaborn & Matplotlib** (Visualization)

## 📊 Results & Analysis
The heatmap below visualizes the **Payoff Matrix**. It shows how the probability of a Safety Car shifts the Nash Equilibrium, making the "PIT" strategy mathematically viable for the follower (Verstappen) despite the time loss.

## 🚀 How to Run
1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
