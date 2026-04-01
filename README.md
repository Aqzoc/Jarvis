# Jarvis: Smart Waste Intelligence

## Problem Statement
In 2026, waste segregation in India has become a legal mandate under the new Solid Waste Management (SWM) Rules. However, communities still struggle with inefficient sorting, specifically regarding hazardous E-waste and sanitary materials. Improper disposal leads to localized environmental crises and missed opportunities for the circular economy.

## Project Description
**Jarvis** is a multimodal AI-powered assistant designed to revolutionize domestic and community waste management. By leveraging high-density spatial reasoning, Jarvis identifies multiple waste items in a single frame, categorizes them according to the **India 2026 Four-Stream Segregation** laws, and provides real-time "Trash-to-Treasure" upcycling suggestions. 

Key features include:
- **Compliance Auditor:** Grades waste disposal against 2026 regulatory standards.
- **Sustainability Tracker:** Estimates CO2 savings and environmental impact.
- **Crisis Protocol:** Identifies hazardous materials (like damaged batteries) and provides immediate safety handling instructions.
- **Circular Economy Engine:** Generates creative engineering ideas for repurposing waste.

## Google AI Usage

### Tools / Models Used
- **Gemini 2.5 Flash:** Used for real-time multimodal image analysis and creative reasoning.
- **Google Cloud Run:** Powers the serverless deployment for global scalability.
- **Google Cloud Build:** Manages the CI/CD pipeline for the Jarvis container image.
- **Google Generative AI SDK:** Integrates the LLM logic into the Python backend.

### How Google AI Was Used
Jarvis utilizes **Gemini 2.5 Flash** to perform dense object detection within "messy" waste photos. The model’s reasoning capabilities allow it to cross-reference identified items with the 2026 SWM legal framework to generate a "Compliance Score." Additionally, the model acts as a creative engine to suggest upcycling projects, moving beyond simple classification into active resource management.

## Proof of Google AI Usage
*Detailed screenshots of the Gemini API integration and GCP Console can be found in the `/proof` folder.*
[AI Proof](./proof/gemini_integration.png)

## Screenshots
![Jarvis Dashboard](./screenshots/dashboard_dark_mode.<img width="1920" height="1080" alt="Screenshot (1)" src="https://github.com/user-attachments/assets/405c1418-c012-4d8a-a97e-9b9fb4e2cfca" />
png)
![Analysis Result](./screenshots/waste_analysis_<img width="1920" height="1080" alt="Screenshot (4)" src="https://github.com/user-attachments/assets/126f61a2-2edf-4447-a83a-d53e03a79d2a" />
ui.png)

## Demo Video
[Watch the Jarvis Demo on Google Drive](PASTE_YOUR_LINK_HERE)

## Installation Steps

```bash
# Clone the repository
git clone [https://github.com/Aqzoc/Jarvis.git](https://github.com/Aqzoc/Jarvis.git)

# Go to project folder
cd Jarvis

# Create a virtual environment (Optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the project
streamlit run app.py
