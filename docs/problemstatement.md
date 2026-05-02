# Problem Statement: AI-Powered Restaurant Recommendation System (Zomato Use Case)

Build an intelligent restaurant recommendation application inspired by Zomato. The system should combine structured restaurant data with a Large Language Model (LLM) to deliver personalized, explainable recommendations based on user preferences.

## Objective

Design and implement a solution that:

- Accepts user preferences such as location, budget, cuisine, and minimum rating
- Uses a real-world restaurant dataset
- Applies an LLM to generate ranked, natural-language recommendations
- Presents results in a clear, user-friendly format

## Scope and Workflow

### 1) Data Ingestion and Preparation

- Load the Zomato dataset from Hugging Face:  
  <https://huggingface.co/datasets/ManikaSaini/zomato-restaurant-recommendation>
- Clean and preprocess the data
- Extract and normalize key fields such as:
  - Restaurant name
  - Location
  - Cuisines
  - Price/cost range
  - Ratings
  - Any available service attributes

### 2) User Preference Collection

Collect the following inputs from the user:

- Location (for example: Delhi, Bangalore)
- Budget range (low, medium, high)
- Preferred cuisine(s) (for example: Italian, Chinese)
- Minimum acceptable rating
- Optional constraints (for example: family-friendly, quick service)

### 3) Retrieval and LLM Integration

- Filter candidate restaurants using structured logic based on user constraints
- Build an LLM prompt that includes:
  - User preferences
  - Filtered restaurant candidates
  - Ranking criteria and response format instructions
- Ensure prompt design encourages consistent ranking and concise reasoning

### 4) Recommendation Generation

Use the LLM to:

- Rank the best-matching restaurants
- Explain why each recommendation fits the user’s preferences
- Optionally provide a short comparative summary of top choices

### 5) Output Presentation

Display recommendations in an easy-to-read format, including:

- Restaurant name
- Cuisine
- Rating
- Estimated cost
- AI-generated rationale

## Expected Outcome

The final application should help users quickly discover suitable restaurants through a combination of data-driven filtering and human-like AI explanations, improving both relevance and user trust.
