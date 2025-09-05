"""
Workout Tracking Module
======================

This module handles all workout-related operations including:
- Adding new workout entries
- Retrieving user workout data
- Managing workout history
- Data persistence using CSV files



import pandas as pd
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional

class WorkoutTracker:
    """
    A class to handle workout tracking and data management.
    
    Features:
    - Multi-user support
    - Persistent CSV storage
    - Workout history retrieval
    - Data validation
    """
    
    def __init__(self, data_file: str = "data/workouts.csv"):
        """
        Initialize the WorkoutTracker.
        
        Args:
            data_file (str): Path to the CSV file for storing workout data
        """
        self.data_file = data_file
        self.workouts_df = self._load_data()
    
    def _load_data(self) -> pd.DataFrame:
        """
        Load workout data from CSV file or create empty DataFrame.
        
        Returns:
            pd.DataFrame: Workout data with required columns
        """
        try:
            if os.path.exists(self.data_file):
                df = pd.read_csv(self.data_file)
                # Ensure all required columns exist
                required_columns = ['user', 'date', 'exercise', 'sets', 'reps', 'weight', 'rpe']
                for col in required_columns:
                    if col not in df.columns:
                        df[col] = None
                return df
            else:
                # Create empty DataFrame with required columns
                return pd.DataFrame(columns=['user', 'date', 'exercise', 'sets', 'reps', 'weight', 'rpe'])
        
        except Exception as e:
            print(f"Error loading workout data: {e}")
            return pd.DataFrame(columns=['user', 'date', 'exercise', 'sets', 'reps', 'weight', 'rpe'])
    
    def _save_data(self) -> bool:
        """
        Save workout data to CSV file.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            
            # Save to CSV
            self.workouts_df.to_csv(self.data_file, index=False)
            return True
        
        except Exception as e:
            print(f"Error saving workout data: {e}")
            return False
    
    def add_workout(self, user: str, date: str, exercise: str, sets: int, 
                   reps: int, weight: float, rpe: int) -> bool:
        """
        Add a new workout entry.
        
        Args:
            user (str): User name
            date (str): Workout date in YYYY-MM-DD format
            exercise (str): Exercise name
            sets (int): Number of sets performed
            reps (int): Number of reps per set
            weight (float): Weight used in kg
            rpe (int): Rate of Perceived Exertion (1-10)
        
        Returns:
            bool: True if workout added successfully
        """
        try:
            # Validate inputs
            if not self._validate_workout_data(user, date, exercise, sets, reps, weight, rpe):
                return False
            
            # Create new workout entry
            new_workout = {
                'user': user.strip(),
                'date': date,
                'exercise': exercise.strip(),
                'sets': int(sets),
                'reps': int(reps),
                'weight': float(weight),
                'rpe': int(rpe),
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Add to DataFrame
            new_row = pd.DataFrame([new_workout])
            self.workouts_df = pd.concat([self.workouts_df, new_row], ignore_index=True)
            
            # Save to file
            return self._save_data()
        
        except Exception as e:
            print(f"Error adding workout: {e}")
            return False
    
    def _validate_workout_data(self, user: str, date: str, exercise: str, 
                              sets: int, reps: int, weight: float, rpe: int) -> bool:
        """
        Validate workout data before adding.
        
        Args:
            user (str): User name
            date (str): Workout date
            exercise (str): Exercise name
            sets (int): Number of sets
            reps (int): Number of reps
            weight (float): Weight used
            rpe (int): RPE value
        
        Returns:
            bool: True if data is valid
        """
        try:
            # Check required fields
            if not user or not exercise:
                print("User and exercise are required")
                return False
            
            # Validate date format
            datetime.strptime(date, "%Y-%m-%d")
            
            # Validate numeric ranges
            if not (1 <= sets <= 20):
                print("Sets must be between 1 and 20")
                return False
            
            if not (1 <= reps <= 50):
                print("Reps must be between 1 and 50")
                return False
            
            if not (0 <= weight <= 1000):
                print("Weight must be between 0 and 1000 kg")
                return False
            
            if not (1 <= rpe <= 10):
                print("RPE must be between 1 and 10")
                return False
            
            return True
        
        except ValueError as e:
            print(f"Invalid date format: {e}")
            return False
        except Exception as e:
            print(f"Validation error: {e}")
            return False
    
    def get_user_workouts(self, user: str) -> pd.DataFrame:
        """
        Get all workouts for a specific user.
        
        Args:
            user (str): User name
        
        Returns:
            pd.DataFrame: User's workout data
        """
        try:
            if self.workouts_df.empty:
                return pd.DataFrame()
            
            user_data = self.workouts_df[self.workouts_df['user'].str.lower() == user.lower()].copy()
            
            if not user_data.empty:
                # Sort by date
                user_data['date'] = pd.to_datetime(user_data['date'])
                user_data = user_data.sort_values('date')
                user_data['date'] = user_data['date'].dt.strftime('%Y-%m-%d')
            
            return user_data
        
        except Exception as e:
            print(f"Error retrieving user workouts: {e}")
            return pd.DataFrame()
    
    def get_exercise_history(self, user: str, exercise: str) -> pd.DataFrame:
        """
        Get workout history for a specific user and exercise.
        
        Args:
            user (str): User name
            exercise (str): Exercise name
        
        Returns:
            pd.DataFrame: Exercise history for the user
        """
        try:
            user_workouts = self.get_user_workouts(user)
            
            if user_workouts.empty:
                return pd.DataFrame()
            
            exercise_data = user_workouts[
                user_workouts['exercise'].str.lower() == exercise.lower()
            ].copy()
            
            return exercise_data.sort_values('date')
        
        except Exception as e:
            print(f"Error retrieving exercise history: {e}")
            return pd.DataFrame()
    
    def get_recent_workouts(self, user: str, days: int = 7) -> pd.DataFrame:
        """
        Get recent workouts for a user within specified days.
        
        Args:
            user (str): User name
            days (int): Number of recent days to retrieve
        
        Returns:
            pd.DataFrame: Recent workout data
        """
        try:
            user_workouts = self.get_user_workouts(user)
            
            if user_workouts.empty:
                return pd.DataFrame()
            
            # Calculate cutoff date
            cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            
            # Filter recent workouts
            user_workouts['date'] = pd.to_datetime(user_workouts['date'])
            recent_workouts = user_workouts[
                user_workouts['date'] >= pd.to_datetime(cutoff_date)
            ].copy()
            
            # Convert date back to string and sort
            recent_workouts['date'] = recent_workouts['date'].dt.strftime('%Y-%m-%d')
            return recent_workouts.sort_values('date', ascending=False)
        
        except Exception as e:
            print(f"Error retrieving recent workouts: {e}")
            return pd.DataFrame()
    
    def get_all_users(self) -> List[str]:
        """
        Get list of all users in the system.
        
        Returns:
            List[str]: List of unique user names
        """
        try:
            if self.workouts_df.empty:
                return []
            
            users = self.workouts_df['user'].unique().tolist()
            return sorted([user for user in users if user and str(user).strip()])
        
        except Exception as e:
            print(f"Error retrieving users: {e}")
            return []
    
    def get_user_exercises(self, user: str) -> List[str]:
        """
        Get list of exercises performed by a specific user.
        
        Args:
            user (str): User name
        
        Returns:
            List[str]: List of unique exercises for the user
        """
        try:
            user_workouts = self.get_user_workouts(user)
            
            if user_workouts.empty:
                return []
            
            exercises = user_workouts['exercise'].unique().tolist()
            return sorted([ex for ex in exercises if ex and str(ex).strip()])
        
        except Exception as e:
            print(f"Error retrieving user exercises: {e}")
            return []
    
    def get_workout_stats(self, user: str) -> Dict:
        """
        Get workout statistics for a user.
        
        Args:
            user (str): User name
        
        Returns:
            Dict: Dictionary containing workout statistics
        """
        try:
            user_workouts = self.get_user_workouts(user)
            
            if user_workouts.empty:
                return {
                    'total_workouts': 0,
                    'unique_exercises': 0,
                    'total_sets': 0,
                    'total_reps': 0,
                    'avg_rpe': 0,
                    'max_weight': 0,
                    'first_workout': None,
                    'last_workout': None
                }
            
            stats = {
                'total_workouts': len(user_workouts),
                'unique_exercises': len(user_workouts['exercise'].unique()),
                'total_sets': user_workouts['sets'].sum(),
                'total_reps': (user_workouts['sets'] * user_workouts['reps']).sum(),
                'avg_rpe': round(user_workouts['rpe'].mean(), 1),
                'max_weight': user_workouts['weight'].max(),
                'first_workout': user_workouts['date'].min(),
                'last_workout': user_workouts['date'].max()
            }
            
            return stats
        
        except Exception as e:
            print(f"Error calculating workout stats: {e}")
            return {}
    
    def get_personal_records(self, user: str) -> Dict:
        """
        Get personal records (PRs) for each exercise.
        
        Args:
            user (str): User name
        
        Returns:
            Dict: Dictionary with exercise names as keys and max weights as values
        """
        try:
            user_workouts = self.get_user_workouts(user)
            
            if user_workouts.empty:
                return {}
            
            # Calculate PRs for each exercise
            prs = user_workouts.groupby('exercise')['weight'].max().to_dict()
            
            return prs
        
        except Exception as e:
            print(f"Error calculating personal records: {e}")
            return {}
    
    def delete_workout(self, user: str, date: str, exercise: str) -> bool:
        """
        Delete a specific workout entry.
        
        Args:
            user (str): User name
            date (str): Workout date
            exercise (str): Exercise name
        
        Returns:
            bool: True if deletion was successful
        """
        try:
            # Find matching workout
            mask = (
                (self.workouts_df['user'].str.lower() == user.lower()) &
                (self.workouts_df['date'] == date) &
                (self.workouts_df['exercise'].str.lower() == exercise.lower())
            )
            
            if not self.workouts_df[mask].empty:
                # Remove the workout
                self.workouts_df = self.workouts_df[~mask]
                return self._save_data()
            else:
                print("Workout not found")
                return False
        
        except Exception as e:
            print(f"Error deleting workout: {e}")
            return False
    
    def update_workout(self, user: str, date: str, exercise: str, 
                      sets: int = None, reps: int = None, 
                      weight: float = None, rpe: int = None) -> bool:
        """
        Update an existing workout entry.
        
        Args:
            user (str): User name
            date (str): Workout date
            exercise (str): Exercise name
            sets (int, optional): New sets value
            reps (int, optional): New reps value
            weight (float, optional): New weight value
            rpe (int, optional): New RPE value
        
        Returns:
            bool: True if update was successful
        """
        try:
            # Find matching workout
            mask = (
                (self.workouts_df['user'].str.lower() == user.lower()) &
                (self.workouts_df['date'] == date) &
                (self.workouts_df['exercise'].str.lower() == exercise.lower())
            )
            
            workout_indices = self.workouts_df[mask].index
            
            if len(workout_indices) == 0:
                print("Workout not found")
                return False
            
            # Update specified fields
            for idx in workout_indices:
                if sets is not None:
                    self.workouts_df.loc[idx, 'sets'] = int(sets)
                if reps is not None:
                    self.workouts_df.loc[idx, 'reps'] = int(reps)
                if weight is not None:
                    self.workouts_df.loc[idx, 'weight'] = float(weight)
                if rpe is not None:
                    self.workouts_df.loc[idx, 'rpe'] = int(rpe)
            
            return self._save_data()
        
        except Exception as e:
            print(f"Error updating workout: {e}")
            return False
    
    def export_user_data(self, user: str, filename: str = None) -> bool:
        """
        Export user's workout data to CSV file.
        
        Args:
            user (str): User name
            filename (str, optional): Output filename
        
        Returns:
            bool: True if export was successful
        """
        try:
            user_workouts = self.get_user_workouts(user)
            
            if user_workouts.empty:
                print(f"No workout data found for user: {user}")
                return False
            
            if filename is None:
                filename = f"data/{user.replace(' ', '_')}_workouts.csv"
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            # Export to CSV
            user_workouts.to_csv(filename, index=False)
            print(f"Data exported to: {filename}")
            return True
        
        except Exception as e:
            print(f"Error exporting user data: {e}")
            return False
    
    def get_workout_volume(self, user: str, days: int = 7) -> Dict:
        """
        Calculate workout volume metrics for a user.
        
        Args:
            user (str): User name
            days (int): Number of recent days to analyze
        
        Returns:
            Dict: Volume metrics including total sets, reps, and tonnage
        """
        try:
            recent_workouts = self.get_recent_workouts(user, days)
            
            if recent_workouts.empty:
                return {
                    'total_sets': 0,
                    'total_reps': 0,
                    'total_tonnage': 0,
                    'avg_intensity': 0,
                    'workout_days': 0
                }
            
            volume_metrics = {
                'total_sets': recent_workouts['sets'].sum(),
                'total_reps': (recent_workouts['sets'] * recent_workouts['reps']).sum(),
                'total_tonnage': (recent_workouts['weight'] * recent_workouts['sets'] * recent_workouts['reps']).sum(),
                'avg_intensity': round(recent_workouts['rpe'].mean(), 1),
                'workout_days': len(recent_workouts['date'].unique())
            }
            
            return volume_metrics
        
        except Exception as e:
            print(f"Error calculating workout volume: {e}")
            return {}
    
    def refresh_data(self) -> bool:
        """
        Refresh workout data from file (useful for concurrent access).
        
        Returns:
            bool: True if refresh was successful
        """
        try:
            self.workouts_df = self._load_data()
            return True
        except Exception as e:
            print(f"Error refreshing data: {e}")
            return False
