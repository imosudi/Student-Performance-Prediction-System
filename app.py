# app.py - Main Flask Application
from flask import Flask, render_template, request, jsonify
import pickle
import pandas as pd
import os
import numpy as np
import sys

app = Flask(__name__)

# Define the predict_performance function to prevent unpickling errors
def predict_performance(student_data, attendance=0, study_time=0, motivation=50):
    """
    Predict student performance based on demographic data and effort metrics
    
    Parameters:
    - student_data: DataFrame with demographic information
    - attendance: Attendance percentage (0-100)
    - study_time: Study time in hours per week (0-40)
    - motivation: Motivation level (0-100)
    
    Returns:
    - Dictionary with predicted scores and recommendations
    """
    # This is just a placeholder - the actual function will be loaded from the pickle
    pass

# Load the model with error handling
def load_model(model_path):
    """Load the model safely with proper error handling"""
    try:
        if os.path.exists(model_path):
            with open(model_path, 'rb') as f:
                # Make sure the current module has the required function
                sys.modules['__main__'].predict_performance = predict_performance
                return pickle.load(f)
        else:
            print(f"Warning: Model file {model_path} not found, using fallback")
            return create_fallback_model()
    except Exception as e:
        print(f"Error loading model: {e}")
        return create_fallback_model()

def create_fallback_model():
    """Create a simple fallback model if loading fails"""
    # This is a simple placeholder model
    from sklearn.linear_model import LinearRegression
    math_model = LinearRegression()
    reading_model = LinearRegression()
    writing_model = LinearRegression()
    
    # Create a simple compute_effort function
    def compute_effort(attendance, study_time):
        return (attendance * 0.5 + study_time * 0.5)
    
    return {
        'math_model': math_model,
        'reading_model': reading_model,
        'writing_model': writing_model,
        'compute_effort': compute_effort,
        'predict_from_form': None  # Will use fallback defined below
    }

# Load the model
MODEL_PATH = 'student_performance_model.pkl'
model_package = load_model(MODEL_PATH)

# Extract the prediction function or use fallback
predict_from_form = model_package.get('predict_from_form')

# Handle case where the model doesn't have the prediction function
if not predict_from_form:
    def predict_from_form(form_data):
        """
        Fallback prediction function in case the model doesn't have one
        """
        # Extract basic data
        gender = form_data.get('gender')
        race_ethnicity = form_data.get('race_ethnicity')
        parental_education = form_data.get('parental_education')
        lunch = form_data.get('lunch')
        test_preparation = form_data.get('test_preparation')
        
        # Extract fuzzy inputs
        attendance = float(form_data.get('attendance', 0))
        study_time = float(form_data.get('study_time', 0))
        motivation = float(form_data.get('motivation', 50))
        
        # Create student data dataframe
        student_data = pd.DataFrame({
            'gender': [gender],
            'race/ethnicity': [race_ethnicity],
            'parental level of education': [parental_education],
            'lunch': [lunch],
            'test preparation course': [test_preparation]
        })
        
        # Extract models
        math_model = model_package.get('math_model')
        reading_model = model_package.get('reading_model')
        writing_model = model_package.get('writing_model')
        compute_effort = model_package.get('compute_effort')
        
        # Calculate effort using fuzzy logic or fallback
        if compute_effort:
            effort_level = compute_effort(attendance, study_time)
        else:
            # Simple fallback effort calculation
            effort_level = (attendance * 0.6) + (study_time * 0.4)
        
        # Make predictions if models exist
        try:
            math_score = math_model.predict(student_data)[0] if math_model else 50
            reading_score = reading_model.predict(student_data)[0] if reading_model else 50
            writing_score = writing_model.predict(student_data)[0] if writing_model else 50
        except Exception as e:
            print(f"Prediction error: {e}")
            # Default scores if prediction fails
            math_score = 50
            reading_score = 50
            writing_score = 50
        
        # Adjust based on effort (±10 points max)
        effort_factor = (effort_level - 50) / 50  # -1 to 1 scale
        math_adjusted = math_score + (effort_factor * 10)
        reading_adjusted = reading_score + (effort_factor * 10)
        writing_adjusted = writing_score + (effort_factor * 10)
        
        # Ensure scores are within range
        math_adjusted = max(0, min(100, math_adjusted))
        reading_adjusted = max(0, min(100, reading_adjusted))
        writing_adjusted = max(0, min(100, writing_adjusted))
        
        # Calculate average
        average_score = (math_adjusted + reading_adjusted + writing_adjusted) / 3
        
        # Generate recommendations
        recommendations = []
        
        if effort_level < 40:
            recommendations.append("Consider increasing your attendance and study time to improve performance.")
        
        if math_adjusted < 60:
            recommendations.append("Your math performance needs improvement. Additional practice with problem-solving exercises is recommended.")
        
        if reading_adjusted < 60:
            recommendations.append("Focus on improving your reading skills through regular reading practice.")
        
        if writing_adjusted < 60:
            recommendations.append("Work on enhancing your writing skills through regular practice and feedback.")
        
        if average_score >= 80:
            recommendations.append("You're doing well overall! Keep up the good work.")
        
        # Current scores
        current_math = float(form_data.get('math_score', 0))
        current_reading = float(form_data.get('reading_score', 0))
        current_writing = float(form_data.get('writing_score', 0))
        
        result = {
            'math_score': math_adjusted,
            'reading_score': reading_adjusted,
            'writing_score': writing_adjusted,
            'average_score': average_score,
            'effort_level': effort_level,
            'recommendations': recommendations
        }
        
        # Add improvement calculations if current scores are provided
        if current_math > 0 and current_reading > 0 and current_writing > 0:
            result['math_improvement'] = math_adjusted - current_math
            result['reading_improvement'] = reading_adjusted - current_reading
            result['writing_improvement'] = writing_adjusted - current_writing
            result['average_improvement'] = (result['math_improvement'] + 
                                           result['reading_improvement'] + 
                                           result['writing_improvement']) / 3
        
        return result


@app.route('/', methods=['GET', 'POST'])
def index():
    """Main route for the prediction form and results"""
    prediction = None
    error = None
    
    if request.method == 'POST':
        try:
            # Get form data
            form_data = {
                # Student information
                'gender': request.form.get('gender'),
                'race_ethnicity': request.form.get('race_ethnicity'),
                'parental_education': request.form.get('parental_education'),
                'lunch': request.form.get('lunch'),
                'test_preparation': request.form.get('test_preparation'),
                
                # Current scores
                'math_score': float(request.form.get('math_score', 0)),
                'reading_score': float(request.form.get('reading_score', 0)),
                'writing_score': float(request.form.get('writing_score', 0)),
                
                # Fuzzy inputs
                'attendance': float(request.form.get('attendance', 0)),
                'study_time': float(request.form.get('study_time', 0)),
                'motivation': float(request.form.get('motivation', 0)),
            }
            
            # Get prediction
            prediction = predict_from_form(form_data)
            
        except Exception as e:
            error = f"An error occurred: {str(e)}"
            print(f"Error in prediction: {e}")
    
    return render_template('index.html', prediction=prediction, error=error)


@app.route('/api/predict', methods=['POST'])
def api_predict():
    """API endpoint for predictions"""
    try:
        # Get JSON data
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Make prediction
        result = predict_from_form(data)
        
        # Return prediction as JSON
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/about')
def about():
    """About page with information about the system"""
    return render_template('about.html')


@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors"""
    return render_template('error.html', error='Page not found'), 404


@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors"""
    return render_template('error.html', error='Server error occurred'), 500


if __name__ == '__main__':
    app.run(debug=True)