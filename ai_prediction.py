"""
AI Predictions Module
====================

This module provides AI-powered predictions for strength training using machine learning.
Features include:
- Linear regression models for weight progression
- Performance prediction based on historical data
- Model accuracy metrics
- Training load optimization



import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error
import warnings
from typing import Dict, List, Optional, Tuple
from workout_tracking import WorkoutTracker

warnings.filterwarnings('ignore')

class AIPredictor:
    """
    A class to provide AI-powered predictions for strength training.
    
    Features:
    - Weight progression predictions using Linear Regression
    - Performance trend analysis
    - Model accuracy assessment
    - Training volume recommendations
    """
    
    def __init__(self, workout_tracker: WorkoutTracker = None):
        """
        Initialize the AIPredictor.
        
        Args:
            workout_tracker (WorkoutTracker, optional): Workout tracker instance
        """
        self.workout_tracker = workout_tracker or WorkoutTracker()
        self.models = {}  # Store trained models for each user-exercise combination
        self.model_metrics = {}  # Store model performance metrics
    
    def predict_next_weight(self, user: str, exercise: str, use_rpe: bool = True) -> Optional[float]:
        """
        Predict the next weight for a specific exercise based on historical data.
        
        Args:
            user (str): User name
            exercise (str): Exercise name
            use_rpe (bool): Whether to include RPE in the prediction model
        
        Returns:
            Optional[float]: Predicted weight in kg, or None if insufficient data
        """
        try:
            # Get exercise history
            exercise_data = self.workout_tracker.get_exercise_history(user, exercise)
            
            if exercise_data.empty or len(exercise_data) < 3:
                return None
            
            # Prepare data for modeling
            exercise_data = exercise_data.sort_values('date').copy()
            exercise_data['date'] = pd.to_datetime(exercise_data['date'])
            
            # Create features
            exercise_data['days_since_start'] = (
                exercise_data['date'] - exercise_data['date'].min()
            ).dt.days
            
            # Select features
            features = ['days_since_start']
            if use_rpe and 'rpe' in exercise_data.columns:
                features.append('rpe')
                # Add interaction term for advanced modeling
                exercise_data['rpe_interaction'] = exercise_data['rpe'] * exercise_data['days_since_start']
                features.append('rpe_interaction')
            
            # Prepare training data
            X = exercise_data[features].values
            y = exercise_data['weight'].values
            
            if len(X) < 3:
                return None
            
            # Train model
            model = LinearRegression()
            model.fit(X, y)
            
            # Store model for future reference
            model_key = f"{user}_{exercise}"
            self.models[model_key] = model
            
            # Calculate model metrics
            y_pred = model.predict(X)
            r2 = r2_score(y, y_pred)
            mae = mean_absolute_error(y, y_pred)
            
            self.model_metrics[model_key] = {
                'r2_score': r2,
                'mean_absolute_error': mae,
                'data_points': len(X),
                'last_updated': datetime.now()
            }
            
            # Predict next weight
            last_row = exercise_data.iloc[-1]
            next_days = last_row['days_since_start'] + 7  # Assume next workout in 7 days
            
            # Prepare features for prediction
            if use_rpe and 'rpe' in exercise_data.columns:
                # Use the average RPE from recent workouts
                recent_rpe = exercise_data.tail(3)['rpe'].mean()
                next_features = [[next_days, recent_rpe, recent_rpe * next_days]]
            else:
                next_features = [[next_days]]
            
            prediction = model.predict(next_features)[0]
            
            # Apply safety constraints
            last_weight = last_row['weight']
            max_increase = last_weight * 0.1  # Maximum 10% increase
            min_increase = 0.5  # Minimum 0.5kg increase
            
            # Conservative progression
            suggested_increase = min(prediction - last_weight, max_increase)
            suggested_increase = max(suggested_increase, min_increase)
            
            predicted_weight = last_weight + suggested_increase
            
            # Round to nearest 0.5kg
            predicted_weight = round(predicted_weight * 2) / 2
            
            return predicted_weight
        
        except Exception as e:
            print(f"Error predicting next weight: {e}")
            return None
    
    def get_model_accuracy(self, user: str, exercise: str) -> Optional[float]:
        """
        Get the accuracy (R² score) of the model for a specific user-exercise combination.
        
        Args:
            user (str): User name
            exercise (str): Exercise name
        
        Returns:
            Optional[float]: R² score or None if model doesn't exist
        """
        try:
            model_key = f"{user}_{exercise}"
            if model_key in self.model_metrics:
                return self.model_metrics[model_key]['r2_score']
            return None
        
        except Exception as e:
            print(f"Error getting model accuracy: {e}")
            return None
    
    def analyze_strength_trends(self, user: str, exercise: str, days: int = 90) -> Dict:
        """
        Analyze strength trends for a specific exercise.
        
        Args:
            user (str): User name
            exercise (str): Exercise name
            days (int): Number of days to analyze
        
        Returns:
            Dict: Trend analysis results
        """
        try:
            exercise_data = self.workout_tracker.get_exercise_history(user, exercise)
            
            if exercise_data.empty:
                return {'status': 'no_data'}
            
            # Filter recent data
            exercise_data = exercise_data.copy()
            exercise_data['date'] = pd.to_datetime(exercise_data['date'])
            cutoff_date = datetime.now() - timedelta(days=days)
            recent_data = exercise_data[exercise_data['date'] >= cutoff_date].copy()
            
            if len(recent_data) < 2:
                return {'status': 'insufficient_data'}
            
            recent_data = recent_data.sort_values('date')
            
            # Calculate trends
            first_weight = recent_data['weight'].iloc[0]
            last_weight = recent_data['weight'].iloc[-1]
            weight_change = last_weight - first_weight
            
            # Calculate percentage change
            if first_weight > 0:
                percentage_change = (weight_change / first_weight) * 100
            else:
                percentage_change = 0
            
            # Determine trend direction
            if abs(percentage_change) < 2:
                trend = 'stable'
            elif percentage_change > 0:
                trend = 'increasing'
            else:
                trend = 'decreasing'
            
            # Calculate average weekly progression
            days_span = (recent_data['date'].max() - recent_data['date'].min()).days
            weeks_span = max(days_span / 7, 1)
            weekly_progression = weight_change / weeks_span
            
            # Analyze RPE trends
            rpe_trend = 'stable'
            if 'rpe' in recent_data.columns and len(recent_data) >= 3:
                first_half_rpe = recent_data.head(len(recent_data)//2)['rpe'].mean()
                second_half_rpe = recent_data.tail(len(recent_data)//2)['rpe'].mean()
                
                rpe_change = second_half_rpe - first_half_rpe
                if rpe_change > 0.5:
                    rpe_trend = 'increasing'
                elif rpe_change < -0.5:
                    rpe_trend = 'decreasing'
            
            return {
                'status': 'success',
                'trend': trend,
                'weight_change': round(weight_change, 1),
                'percentage_change': round(percentage_change, 1),
                'weekly_progression': round(weekly_progression, 2),
                'total_sessions': len(recent_data),
                'days_analyzed': days_span,
                'first_weight': first_weight,
                'last_weight': last_weight,
                'rpe_trend': rpe_trend,
                'avg_rpe': round(recent_data['rpe'].mean(), 1) if 'rpe' in recent_data.columns else None
            }
        
        except Exception as e:
            print(f"Error analyzing strength trends: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def predict_performance_plateau(self, user: str, exercise: str) -> Dict:
        """
        Predict if a user is approaching a performance plateau.
        
        Args:
            user (str): User name
            exercise (str): Exercise name
        
        Returns:
            Dict: Plateau prediction analysis
        """
        try:
            trend_analysis = self.analyze_strength_trends(user, exercise, days=60)
            
            if trend_analysis['status'] != 'success':
                return {'status': 'insufficient_data'}
            
            # Criteria for plateau detection
            plateau_indicators = []
            plateau_score = 0
            
            # Weight progression stalled
            if abs(trend_analysis['weekly_progression']) < 0.5:
                plateau_indicators.append("Minimal weight progression")
                plateau_score += 2
            
            # RPE increasing while weight stagnant
            if (trend_analysis['rpe_trend'] == 'increasing' and 
                trend_analysis['trend'] == 'stable'):
                plateau_indicators.append("RPE increasing without weight progression")
                plateau_score += 3
            
            # Very low percentage change over time
            if abs(trend_analysis['percentage_change']) < 3 and trend_analysis['total_sessions'] > 8:
                plateau_indicators.append("Low overall progression rate")
                plateau_score += 2
            
            # High average RPE
            if trend_analysis['avg_rpe'] and trend_analysis['avg_rpe'] > 8.5:
                plateau_indicators.append("Consistently high RPE")
                plateau_score += 2
            
            # Determine plateau risk
            if plateau_score >= 5:
                risk_level = 'high'
                recommendation = "Consider deload or program change"
            elif plateau_score >= 3:
                risk_level = 'moderate'
                recommendation = "Monitor closely, consider technique work"
            else:
                risk_level = 'low'
                recommendation = "Continue current progression"
            
            return {
                'status': 'success',
                'plateau_risk': risk_level,
                'plateau_score': plateau_score,
                'indicators': plateau_indicators,
                'recommendation': recommendation,
                'trend_data': trend_analysis
            }
        
        except Exception as e:
            print(f"Error predicting performance plateau: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def recommend_training_load(self, user: str, days: int = 14) -> Dict:
        """
        Recommend training load adjustments based on recent performance.
        
        Args:
            user (str): User name
            days (int): Number of recent days to analyze
        
        Returns:
            Dict: Training load recommendations
        """
        try:
            recent_workouts = self.workout_tracker.get_recent_workouts(user, days)
            
            if recent_workouts.empty:
                return {'status': 'no_data'}
            
            # Calculate training metrics
            total_sets = recent_workouts['sets'].sum()
            avg_rpe = recent_workouts['rpe'].mean()
            workout_frequency = len(recent_workouts['date'].unique())
            total_tonnage = (recent_workouts['weight'] * 
                           recent_workouts['sets'] * 
                           recent_workouts['reps']).sum()
            
            recommendations = []
            
            # Analyze training frequency
            if workout_frequency < 2:
                recommendations.append({
                    'category': 'frequency',
                    'message': 'Consider increasing workout frequency',
                    'priority': 'medium'
                })
            elif workout_frequency > 6:
                recommendations.append({
                    'category': 'frequency',
                    'message': 'Consider adding rest days',
                    'priority': 'high'
                })
            
            # Analyze RPE
            if avg_rpe > 9:
                recommendations.append({
                    'category': 'intensity',
                    'message': 'RPE too high, consider reducing intensity',
                    'priority': 'high'
                })
            elif avg_rpe < 6:
                recommendations.append({
                    'category': 'intensity',
                    'message': 'RPE low, room for increased intensity',
                    'priority': 'low'
                })
            
            # Analyze volume
            if total_sets > 100:
                recommendations.append({
                    'category': 'volume',
                    'message': 'High training volume, monitor for overreaching',
                    'priority': 'medium'
                })
            elif total_sets < 20:
                recommendations.append({
                    'category': 'volume',
                    'message': 'Low training volume, consider increasing',
                    'priority': 'medium'
                })
            
            return {
                'status': 'success',
                'metrics': {
                    'total_sets': total_sets,
                    'avg_rpe': round(avg_rpe, 1),
                    'workout_frequency': workout_frequency,
                    'total_tonnage': round(total_tonnage, 0),
                    'days_analyzed': days
                },
                'recommendations': recommendations
            }
        
        except Exception as e:
            print(f"Error recommending training load: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def predict_1rm(self, user: str, exercise: str, reps: int, weight: float, rpe: int) -> Dict:
        """
        Predict 1RM using RPE-based formula.
        
        Args:
            user (str): User name
            exercise (str): Exercise name
            reps (int): Number of reps performed
            weight (float): Weight used
            rpe (int): RPE of the set
        
        Returns:
            Dict: 1RM prediction results
        """
        try:
            # RPE-based 1RM calculation
            # Based on the RPE chart: RPE 10 = 100%, RPE 9 = ~97%, etc.
            rpe_percentages = {
                10: 100, 9: 97, 8: 94, 7: 91, 6: 88, 
                5: 85, 4: 82, 3: 79, 2: 76, 1: 73
            }
            
            if rpe not in rpe_percentages:
                return {'status': 'invalid_rpe'}
            
            # Adjust for rep count (approximate)
            rep_adjustments = {
                1: 0, 2: -3, 3: -6, 4: -9, 5: -12,
                6: -15, 7: -18, 8: -21, 9: -24, 10: -27
            }
            
            base_percentage = rpe_percentages[rpe]
            rep_adjustment = rep_adjustments.get(min(reps, 10), -30)
            
            estimated_percentage = base_percentage + rep_adjustment
            estimated_1rm = weight / (estimated_percentage / 100)
            
            # Get historical data for comparison
            exercise_history = self.workout_tracker.get_exercise_history(user, exercise)
            
            confidence = 'medium'
            if not exercise_history.empty:
                max_weight = exercise_history['weight'].max()
                if estimated_1rm > max_weight * 1.5:
                    confidence = 'low'
                elif abs(estimated_1rm - max_weight) < max_weight * 0.1:
                    confidence = 'high'
            
            return {
                'status': 'success',
                'estimated_1rm': round(estimated_1rm, 1),
                'confidence': confidence,
                'calculation_details': {
                    'weight': weight,
                    'reps': reps,
                    'rpe': rpe,
                    'estimated_percentage': estimated_percentage
                }
            }
        
        except Exception as e:
            print(f"Error predicting 1RM: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def generate_progression_plan(self, user: str, exercise: str, weeks: int = 4) -> Dict:
        """
        Generate a progression plan for the next few weeks.
        
        Args:
            user (str): User name
            exercise (str): Exercise name
            weeks (int): Number of weeks to plan
        
        Returns:
            Dict: Progression plan
        """
        try:
            # Get current performance level
            exercise_data = self.workout_tracker.get_exercise_history(user, exercise)
            
            if exercise_data.empty:
                return {'status': 'no_data'}
            
            # Get most recent workout
            latest_workout = exercise_data.sort_values('date').iloc[-1]
            current_weight = latest_workout['weight']
            current_rpe = latest_workout.get('rpe', 8)
            
            # Analyze recent trend
            trend_analysis = self.analyze_strength_trends(user, exercise)
            
            # Determine progression rate based on trend
            if trend_analysis.get('weekly_progression', 0) > 2:
                # Fast progression
                weekly_increase = 2.5
            elif trend_analysis.get('weekly_progression', 0) > 1:
                # Moderate progression
                weekly_increase = 1.5
            else:
                # Conservative progression
                weekly_increase = 1.0
            
            # Generate weekly plan
            progression_plan = []
            for week in range(1, weeks + 1):
                week_weight = current_weight + (weekly_increase * week)
                week_weight = round(week_weight * 2) / 2  # Round to nearest 0.5kg
                
                # Adjust RPE target based on progression
                if week <= 2:
                    target_rpe = min(current_rpe, 8)
                elif week <= 3:
                    target_rpe = min(current_rpe + 1, 9)
                else:
                    target_rpe = min(current_rpe + 1, 9)
                
                progression_plan.append({
                    'week': week,
                    'target_weight': week_weight,
                    'target_rpe': target_rpe,
                    'notes': self._get_progression_notes(week, target_rpe)
                })
            
            return {
                'status': 'success',
                'current_weight': current_weight,
                'progression_plan': progression_plan,
                'weekly_increase': weekly_increase,
                'notes': 'Plan based on recent performance trends'
            }
        
        except Exception as e:
            print(f"Error generating progression plan: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def _get_progression_notes(self, week: int, rpe: int) -> str:
        """
        Generate notes for progression plan.
        
        Args:
            week (int): Week number
            rpe (int): Target RPE
        
        Returns:
            str: Notes for the week
        """
        if week == 1:
            return "Foundation week - focus on form"
        elif week == 2:
            return "Build week - maintain good technique"
        elif week == 3:
            return "Intensity week - push closer to limits"
        else:
            if rpe >= 9:
                return "Test week - consider deload after this"
            else:
                return "Progressive overload week"
