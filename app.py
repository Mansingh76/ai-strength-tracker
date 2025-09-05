"""
AI Strength Tracker - Main Streamlit Application
===============================================

A comprehensive AI-powered strength tracking system for gym enthusiasts.
Features workout tracking, nutrition monitoring, AI predictions, and fatigue analysis.

Author: Claude AI Assistant
Date: September 2025
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Import custom modules
from workout_tracking import WorkoutTracker
from nutrition_tracking import NutritionTracker
from ai_predictions import AIPredictor
from fatigue_monitor import FatigueMonitor

# Configure Streamlit page
st.set_page_config(
    page_title="AI Strength Tracker",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
.main-header {
    font-size: 3rem;
    color: #FF6B6B;
    text-align: center;
    margin-bottom: 2rem;
}
.metric-card {
    background-color: #f0f2f6;
    padding: 1rem;
    border-radius: 10px;
    margin: 0.5rem 0;
}
.success-box {
    background-color: #d4edda;
    border: 1px solid #c3e6cb;
    border-radius: 5px;
    padding: 1rem;
    margin: 1rem 0;
}
</style>
""", unsafe_allow_html=True)

def initialize_data():
    """Initialize data storage and create dummy data if needed."""
    # Create data directory if it doesn't exist
    if not os.path.exists('data'):
        os.makedirs('data')
    
    # Initialize trackers
    workout_tracker = WorkoutTracker()
    nutrition_tracker = NutritionTracker()
    ai_predictor = AIPredictor()
    fatigue_monitor = FatigueMonitor()
    
    # Create dummy data if files don't exist
    if not os.path.exists('data/workouts.csv'):
        create_dummy_workout_data(workout_tracker)
    
    if not os.path.exists('data/nutrition.csv'):
        create_dummy_nutrition_data(nutrition_tracker)
    
    return workout_tracker, nutrition_tracker, ai_predictor, fatigue_monitor

def create_dummy_workout_data(tracker):
    """Create sample workout data for testing."""
    dummy_workouts = [
        # User 1 - Progressive overload over 4 weeks
        {"user": "John Doe", "date": "2025-08-01", "exercise": "Bench Press", "sets": 3, "reps": 8, "weight": 100, "rpe": 7},
        {"user": "John Doe", "date": "2025-08-03", "exercise": "Squat", "sets": 4, "reps": 6, "weight": 140, "rpe": 8},
        {"user": "John Doe", "date": "2025-08-05", "exercise": "Deadlift", "sets": 3, "reps": 5, "weight": 160, "rpe": 9},
        
        {"user": "John Doe", "date": "2025-08-08", "exercise": "Bench Press", "sets": 3, "reps": 8, "weight": 102.5, "rpe": 7},
        {"user": "John Doe", "date": "2025-08-10", "exercise": "Squat", "sets": 4, "reps": 6, "weight": 142.5, "rpe": 8},
        {"user": "John Doe", "date": "2025-08-12", "exercise": "Deadlift", "sets": 3, "reps": 5, "weight": 165, "rpe": 8},
        
        {"user": "John Doe", "date": "2025-08-15", "exercise": "Bench Press", "sets": 3, "reps": 8, "weight": 105, "rpe": 8},
        {"user": "John Doe", "date": "2025-08-17", "exercise": "Squat", "sets": 4, "reps": 6, "weight": 145, "rpe": 9},
        {"user": "John Doe", "date": "2025-08-19", "exercise": "Deadlift", "sets": 3, "reps": 5, "weight": 170, "rpe": 9},
        
        # User 2 - Different progression pattern
        {"user": "Jane Smith", "date": "2025-08-01", "exercise": "Bench Press", "sets": 4, "reps": 6, "weight": 70, "rpe": 6},
        {"user": "Jane Smith", "date": "2025-08-03", "exercise": "Squat", "sets": 3, "reps": 8, "weight": 80, "rpe": 7},
        {"user": "Jane Smith", "date": "2025-08-05", "exercise": "Deadlift", "sets": 3, "reps": 5, "weight": 100, "rpe": 8},
        
        {"user": "Jane Smith", "date": "2025-08-08", "exercise": "Bench Press", "sets": 4, "reps": 6, "weight": 72.5, "rpe": 7},
        {"user": "Jane Smith", "date": "2025-08-10", "exercise": "Squat", "sets": 3, "reps": 8, "weight": 82.5, "rpe": 7},
        {"user": "Jane Smith", "date": "2025-08-12", "exercise": "Deadlift", "sets": 3, "reps": 5, "weight": 105, "rpe": 8},
    ]
    
    for workout in dummy_workouts:
        tracker.add_workout(**workout)

def create_dummy_nutrition_data(tracker):
    """Create sample nutrition data for testing."""
    dummy_nutrition = [
        # 10 days of nutrition data for John Doe
        {"user": "John Doe", "date": "2025-08-01", "calories": 2800, "protein": 150, "carbs": 350, "fats": 90},
        {"user": "John Doe", "date": "2025-08-02", "calories": 2750, "protein": 145, "carbs": 340, "fats": 88},
        {"user": "John Doe", "date": "2025-08-03", "calories": 2900, "protein": 155, "carbs": 360, "fats": 95},
        {"user": "John Doe", "date": "2025-08-04", "calories": 2650, "protein": 140, "carbs": 330, "fats": 85},
        {"user": "John Doe", "date": "2025-08-05", "calories": 2800, "protein": 150, "carbs": 350, "fats": 90},
        
        # 5 days of nutrition data for Jane Smith
        {"user": "Jane Smith", "date": "2025-08-01", "calories": 2200, "protein": 120, "carbs": 250, "fats": 70},
        {"user": "Jane Smith", "date": "2025-08-02", "calories": 2150, "protein": 115, "carbs": 240, "fats": 68},
        {"user": "Jane Smith", "date": "2025-08-03", "calories": 2300, "protein": 125, "carbs": 260, "fats": 75},
        {"user": "Jane Smith", "date": "2025-08-04", "calories": 2100, "protein": 110, "carbs": 235, "fats": 65},
        {"user": "Jane Smith", "date": "2025-08-05", "calories": 2250, "protein": 120, "carbs": 255, "fats": 72},
    ]
    
    for nutrition in dummy_nutrition:
        tracker.add_nutrition_entry(**nutrition)

def main():
    """Main application function."""
    st.markdown('<h1 class="main-header">💪 AI Strength Tracker</h1>', unsafe_allow_html=True)
    
    # Initialize all components
    workout_tracker, nutrition_tracker, ai_predictor, fatigue_monitor = initialize_data()
    
    # Sidebar for navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page:",
        ["Dashboard", "Log Workout", "Log Nutrition", "AI Predictions", "Progress Charts", "Fatigue Monitor"]
    )
    
    # User selection
    users = workout_tracker.get_all_users()
    if users:
        selected_user = st.sidebar.selectbox("Select User:", users)
    else:
        st.sidebar.warning("No users found. Add some workout data first!")
        selected_user = None
    
    # Page routing
    if page == "Dashboard":
        show_dashboard(selected_user, workout_tracker, nutrition_tracker, fatigue_monitor)
    elif page == "Log Workout":
        log_workout_page(workout_tracker)
    elif page == "Log Nutrition":
        log_nutrition_page(nutrition_tracker)
    elif page == "AI Predictions":
        ai_predictions_page(selected_user, workout_tracker, ai_predictor)
    elif page == "Progress Charts":
        progress_charts_page(selected_user, workout_tracker, ai_predictor)
    elif page == "Fatigue Monitor":
        fatigue_monitor_page(selected_user, workout_tracker, fatigue_monitor)

def show_dashboard(user, workout_tracker, nutrition_tracker, fatigue_monitor):
    """Display the main dashboard with key metrics."""
    st.header("📊 Dashboard")
    
    if not user:
        st.warning("Please select a user from the sidebar.")
        return
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Total workouts
    total_workouts = len(workout_tracker.get_user_workouts(user))
    col1.metric("Total Workouts", total_workouts)
    
    # Recent nutrition average
    recent_nutrition = nutrition_tracker.get_recent_nutrition(user, days=7)
    if not recent_nutrition.empty:
        avg_calories = int(recent_nutrition['calories'].mean())
        col2.metric("Avg Daily Calories (7d)", f"{avg_calories}")
    else:
        col2.metric("Avg Daily Calories (7d)", "No data")
    
    # Current fatigue score
    fatigue_score = fatigue_monitor.calculate_fatigue_score(user)
    col3.metric("Current Fatigue", f"{fatigue_score:.1f}/10")
    
    # Exercises tracked
    user_workouts = workout_tracker.get_user_workouts(user)
    unique_exercises = len(user_workouts['exercise'].unique()) if not user_workouts.empty else 0
    col4.metric("Exercises Tracked", unique_exercises)
    
    # Recent activity
    st.subheader("📈 Recent Activity")
    
    recent_workouts = workout_tracker.get_recent_workouts(user, days=7)
    if not recent_workouts.empty:
        st.write("**Last 7 days of workouts:**")
        display_df = recent_workouts[['date', 'exercise', 'weight', 'sets', 'reps', 'rpe']].copy()
        st.dataframe(display_df, use_container_width=True)
    else:
        st.info("No recent workouts found.")
    
    # Fatigue status
    st.subheader("⚡ Fatigue Status")
    fatigue_status = fatigue_monitor.get_fatigue_status(user)
    if fatigue_status['status'] == 'High':
        st.error(f"🚨 {fatigue_status['message']}")
    elif fatigue_status['status'] == 'Moderate':
        st.warning(f"⚠️ {fatigue_status['message']}")
    else:
        st.success(f"✅ {fatigue_status['message']}")

def log_workout_page(workout_tracker):
    """Page for logging new workouts."""
    st.header("💪 Log New Workout")
    
    with st.form("workout_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            user = st.text_input("User Name", placeholder="Enter your name")
            exercise = st.selectbox(
                "Exercise",
                ["Bench Press", "Squat", "Deadlift", "Overhead Press", "Barbell Row", "Other"]
            )
            if exercise == "Other":
                exercise = st.text_input("Custom Exercise Name")
        
        with col2:
            weight = st.number_input("Weight (kg)", min_value=0.0, step=2.5, format="%.1f")
            sets = st.number_input("Sets", min_value=1, max_value=10, value=3)
            reps = st.number_input("Reps", min_value=1, max_value=20, value=8)
            rpe = st.slider("RPE (Rate of Perceived Exertion)", 1, 10, 7)
        
        date = st.date_input("Date", datetime.now())
        
        submitted = st.form_submit_button("Log Workout")
        
        if submitted and user and exercise:
            try:
                workout_tracker.add_workout(
                    user=user,
                    date=date.strftime("%Y-%m-%d"),
                    exercise=exercise,
                    sets=int(sets),
                    reps=int(reps),
                    weight=float(weight),
                    rpe=int(rpe)
                )
                st.success(f"✅ Workout logged successfully for {user}!")
                st.rerun()
            except Exception as e:
                st.error(f"Error logging workout: {str(e)}")
        elif submitted:
            st.error("Please fill in all required fields.")

def log_nutrition_page(nutrition_tracker):
    """Page for logging nutrition data."""
    st.header("🥗 Log Nutrition")
    
    with st.form("nutrition_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            user = st.text_input("User Name", placeholder="Enter your name")
            calories = st.number_input("Calories", min_value=0, max_value=5000, value=2500)
        
        with col2:
            protein = st.number_input("Protein (g)", min_value=0, max_value=300, value=150)
            carbs = st.number_input("Carbs (g)", min_value=0, max_value=500, value=300)
            fats = st.number_input("Fats (g)", min_value=0, max_value=200, value=80)
        
        date = st.date_input("Date", datetime.now())
        
        submitted = st.form_submit_button("Log Nutrition")
        
        if submitted and user:
            try:
                nutrition_tracker.add_nutrition_entry(
                    user=user,
                    date=date.strftime("%Y-%m-%d"),
                    calories=int(calories),
                    protein=int(protein),
                    carbs=int(carbs),
                    fats=int(fats)
                )
                st.success(f"✅ Nutrition logged successfully for {user}!")
                st.rerun()
            except Exception as e:
                st.error(f"Error logging nutrition: {str(e)}")
        elif submitted:
            st.error("Please enter a user name.")

def ai_predictions_page(user, workout_tracker, ai_predictor):
    """Page for AI predictions."""
    st.header("🤖 AI Predictions")
    
    if not user:
        st.warning("Please select a user from the sidebar.")
        return
    
    user_workouts = workout_tracker.get_user_workouts(user)
    if user_workouts.empty:
        st.info("No workout data found for predictions.")
        return
    
    exercises = user_workouts['exercise'].unique()
    selected_exercise = st.selectbox("Select Exercise for Prediction:", exercises)
    
    if st.button("Generate Prediction"):
        try:
            prediction = ai_predictor.predict_next_weight(user, selected_exercise)
            
            if prediction is not None:
                st.success(f"🎯 **Next recommended weight for {selected_exercise}: {prediction:.1f} kg**")
                
                # Show model performance
                accuracy = ai_predictor.get_model_accuracy(user, selected_exercise)
                if accuracy:
                    st.info(f"📊 Model R² Score: {accuracy:.3f}")
                
                # Show recent progression
                exercise_data = user_workouts[user_workouts['exercise'] == selected_exercise].copy()
                exercise_data = exercise_data.sort_values('date').tail(5)
                
                st.subheader("Recent Progress")
                st.dataframe(
                    exercise_data[['date', 'weight', 'sets', 'reps', 'rpe']],
                    use_container_width=True
                )
                
            else:
                st.warning("Not enough data for reliable prediction. Need at least 3 workouts for this exercise.")
        
        except Exception as e:
            st.error(f"Prediction error: {str(e)}")

def progress_charts_page(user, workout_tracker, ai_predictor):
    """Page for displaying progress charts."""
    st.header("📈 Progress Charts")
    
    if not user:
        st.warning("Please select a user from the sidebar.")
        return
    
    user_workouts = workout_tracker.get_user_workouts(user)
    if user_workouts.empty:
        st.info("No workout data found for charts.")
        return
    
    exercises = user_workouts['exercise'].unique()
    selected_exercise = st.selectbox("Select Exercise:", exercises)
    
    # Filter data for selected exercise
    exercise_data = user_workouts[user_workouts['exercise'] == selected_exercise].copy()
    exercise_data = exercise_data.sort_values('date')
    
    # Create progress chart
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Plot actual weights
    exercise_data['date'] = pd.to_datetime(exercise_data['date'])
    ax.plot(exercise_data['date'], exercise_data['weight'], 'bo-', label='Actual Weight', linewidth=2, markersize=6)
    
    # Add predictions if enough data
    if len(exercise_data) >= 3:
        try:
            # Get predictions for recent workouts
            predictions = []
            dates = []
            
            for _, row in exercise_data.tail(5).iterrows():
                pred = ai_predictor.predict_next_weight(user, selected_exercise)
                if pred:
                    predictions.append(pred)
                    dates.append(row['date'])
            
            if predictions:
                ax.plot(dates, predictions, 'ro--', label='AI Predictions', alpha=0.7, linewidth=2)
        
        except Exception as e:
            st.warning(f"Could not generate predictions: {str(e)}")
    
    ax.set_title(f'{selected_exercise} Progress - {user}', fontsize=16, fontweight='bold')
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Weight (kg)', fontsize=12)
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    st.pyplot(fig)
    
    # Show statistics
    st.subheader("📊 Statistics")
    col1, col2, col3, col4 = st.columns(4)
    
    col1.metric("Total Sessions", len(exercise_data))
    col2.metric("Current Max", f"{exercise_data['weight'].max():.1f} kg")
    col3.metric("Average RPE", f"{exercise_data['rpe'].mean():.1f}")
    
    if len(exercise_data) > 1:
        weight_change = exercise_data['weight'].iloc[-1] - exercise_data['weight'].iloc[0]
        col4.metric("Total Progress", f"{weight_change:+.1f} kg")

def fatigue_monitor_page(user, workout_tracker, fatigue_monitor):
    """Page for fatigue monitoring."""
    st.header("⚡ Fatigue Monitor")
    
    if not user:
        st.warning("Please select a user from the sidebar.")
        return
    
    # Current fatigue status
    fatigue_score = fatigue_monitor.calculate_fatigue_score(user)
    fatigue_status = fatigue_monitor.get_fatigue_status(user)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Current Fatigue Score", f"{fatigue_score:.1f}/10")
    
    with col2:
        if fatigue_status['status'] == 'High':
            st.error(f"Status: {fatigue_status['status']}")
        elif fatigue_status['status'] == 'Moderate':
            st.warning(f"Status: {fatigue_status['status']}")
        else:
            st.success(f"Status: {fatigue_status['status']}")
    
    st.write(f"**Recommendation:** {fatigue_status['message']}")
    
    # Deload recommendation
    st.subheader("🔄 Deload Recommendation")
    deload_rec = fatigue_monitor.recommend_deload(user)
    
    if deload_rec['should_deload']:
        st.warning(f"⚠️ **Deload Recommended**: {deload_rec['reason']}")
        st.write(f"**Suggestion:** {deload_rec['suggestion']}")
    else:
        st.success("✅ No deload needed. Keep up the good work!")
    
    # Recent fatigue trend
    st.subheader("📊 Fatigue Trend (Last 14 Days)")
    
    user_workouts = workout_tracker.get_recent_workouts(user, days=14)
    if not user_workouts.empty:
        # Calculate daily fatigue scores
        daily_fatigue = user_workouts.groupby('date').agg({
            'rpe': 'mean',
            'sets': 'sum'
        }).reset_index()
        
        daily_fatigue['fatigue_estimate'] = (daily_fatigue['rpe'] * daily_fatigue['sets']) / 10
        
        fig, ax = plt.subplots(figsize=(12, 4))
        daily_fatigue['date'] = pd.to_datetime(daily_fatigue['date'])
        ax.plot(daily_fatigue['date'], daily_fatigue['fatigue_estimate'], 'ro-', linewidth=2)
        ax.set_title('Daily Fatigue Estimate', fontsize=14)
        ax.set_ylabel('Fatigue Score')
        ax.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        st.pyplot(fig)
    else:
        st.info("No recent workout data for fatigue trend analysis.")

# For ngrok integration in Colab
def setup_ngrok():
    """Setup ngrok for public URL access (useful in Google Colab)."""
    try:
        from pyngrok import ngrok
        import subprocess
        
        # Kill existing ngrok processes
        subprocess.run(['pkill', '-f', 'ngrok'], check=False)
        
        # Setup ngrok tunnel
        public_url = ngrok.connect(8501)
        st.sidebar.success(f"🌐 Public URL: {public_url}")
        return public_url
    except ImportError:
        st.sidebar.info("Install pyngrok for public URL access: pip install pyngrok")
        return None
    except Exception as e:
        st.sidebar.error(f"Ngrok setup failed: {str(e)}")
        return None

if __name__ == "__main__":
    # Uncomment the line below if running in Google Colab
    # setup_ngrok()
    
    main()
