# Student Performance Prediction Model

## Overview

This directory contains the Jupyter notebook used to develop the Student Performance Prediction model for our expert system. The model uses a combination of regression techniques and fuzzy logic to predict student academic performance based on demographic factors and study habits.

## Model Details

The model in `student_performance_model.pkl` contains the following components:

- `math_model`: Regression model for predicting math scores
- `reading_model`: Regression model for predicting reading scores
- `writing_model`: Regression model for predicting writing scores
- `fuzzy_effort_simulator`: Fuzzy logic control system simulator for computing effort level
- `compute_effort`: Function to calculate effort level from attendance and study time
- `predict_performance`: Main prediction function for combined predictions
- `predict_from_form`: Function designed specifically for handling Flask form input
- `feature_names`: List of feature names used by the model

## How to Use the Model in Flask

### 1. Loading the Model

```python
import pickle

# Load the model
with open('student_performance_model.pkl', 'rb') as f:
    model_package = pickle.load(f)

# Extract the prediction function for Flask forms
predict_from_form = model_package['predict_from_form']
```

### 2. Using the Prediction Function

The `predict_from_form` function is specifically designed to work with Flask form data. It expects a dictionary with the following keys:

```python
form_data = {
    # Student demographics
    'gender': 'female',                         # string: 'female', 'male', 'other'
    'race_ethnicity': 'group C',                # string: 'group A', 'group B', etc.
    'parental_education': "bachelor's degree",  # string: education level
    'lunch': 'standard',                        # string: 'standard', 'free/reduced'
    'test_preparation': 'completed',            # string: 'completed', 'none'
    
    # Current scores (optional, set to 0 if not available)
    'math_score': 70,                           # float: 0-100
    'reading_score': 75,                        # float: 0-100
    'writing_score': 80,                        # float: 0-100
    
    # Fuzzy inputs
    'attendance': 75,                           # float: 0-100 (percentage)
    'study_time': 20,                           # float: 0-40 (hours per week)
    'motivation': 80                            # float: 0-100 (percentage)
}

# Get prediction
prediction = predict_from_form(form_data)
```

### 3. Prediction Output

The function returns a dictionary with the following keys:

```python
{
    'math_score': 82.5,            # Predicted math score
    'reading_score': 78.3,         # Predicted reading score
    'writing_score': 81.7,         # Predicted writing score
    'average_score': 80.8,         # Average of all three scores
    'effort_level': 65.4,          # Computed effort level (0-100)
    'recommendations': [           # List of personalized recommendations
        "You're doing well overall! Keep up the good work.",
        "Focus on improving your reading skills through regular reading practice."
    ]
}
```

If current scores were provided in the input (non-zero values), the output will also include improvement metrics:

```python
{
    # ... other fields as above ...
    'math_improvement': 12.5,      # Difference between predicted and current math score
    'reading_improvement': 3.3,    # Difference between predicted and current reading score
    'writing_improvement': 1.7,    # Difference between predicted and current writing score
    'average_improvement': 5.8     # Average improvement across all subjects
}
```

### 4. Error Handling

Always wrap your prediction code in a try-except block to handle potential errors:

```python
try:
    prediction = predict_from_form(form_data)
except Exception as e:
    # Handle the error
    print(f"Prediction error: {str(e)}")
    # Provide a fallback or error message
```

## Model Training

The notebook `model_development.ipynb` contains the complete code used to:

- Load and preprocess the student performance dataset
- Perform exploratory data analysis
- Develop the regression models for score prediction
- Implement fuzzy logic for effort level calculation
- Integrate both components into a unified prediction system
- Save the model as a pickle file

If you need to retrain the model with updated data, run all cells in the notebook and ensure the output pickle file is copied to the Flask application directory.

## Additional Notes

- The model was trained on the UCI ML Repository Student Performance dataset and Kaggle's Students Performance in Exams dataset.
- The fuzzy logic component uses the scikit-fuzzy library to model the relationship between attendance, study time, and effort level.
- The model's accuracy metrics (RMSE, R²) are documented in the notebook.