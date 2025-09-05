"""
Nutrition Tracking Module
========================

This module handles all nutrition-related operations including:
- Adding daily nutrition entries
- Retrieving user nutrition data
- Calculating nutrition statistics
- Data persistence using CSV files


import pandas as pd
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional

class NutritionTracker:
    """
    A class to handle nutrition tracking and data management.
    
    Features:
    - Multi-user support
    - Daily nutrition logging
    - Macronutrient tracking (calories, protein, carbs, fats)
    - Persistent CSV storage
    - Nutrition statistics and trends
    """
    
    def __init__(self, data_file: str = "data/nutrition.csv"):
        """
        Initialize the NutritionTracker.
        
        Args:
            data_file (str): Path to the CSV file for storing nutrition data
        """
        self.data_file = data_file
        self.nutrition_df = self._load_data()
    
    def _load_data(self) -> pd.DataFrame:
        """
        Load nutrition data from CSV file or create empty DataFrame.
        
        Returns:
            pd.DataFrame: Nutrition data with required columns
        """
        try:
            if os.path.exists(self.data_file):
                df = pd.read_csv(self.data_file)
                # Ensure all required columns exist
                required_columns = ['user', 'date', 'calories', 'protein', 'carbs', 'fats']
                for col in required_columns:
                    if col not in df.columns:
                        df[col] = 0
                return df
            else:
                # Create empty DataFrame with required columns
                return pd.DataFrame(columns=['user', 'date', 'calories', 'protein', 'carbs', 'fats', 'timestamp'])
        
        except Exception as e:
            print(f"Error loading nutrition data: {e}")
            return pd.DataFrame(columns=['user', 'date', 'calories', 'protein', 'carbs', 'fats', 'timestamp'])
    
    def _save_data(self) -> bool:
        """
        Save nutrition data to CSV file.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            
            # Save to CSV
            self.nutrition_df.to_csv(self.data_file, index=False)
            return True
        
        except Exception as e:
            print(f"Error saving nutrition data: {e}")
            return False
    
    def add_nutrition_entry(self, user: str, date: str, calories: int, 
                           protein: int, carbs: int, fats: int) -> bool:
        """
        Add a new nutrition entry for a specific date.
        
        Args:
            user (str): User name
            date (str): Date in YYYY-MM-DD format
            calories (int): Total calories consumed
            protein (int): Protein in grams
            carbs (int): Carbohydrates in grams
            fats (int): Fats in grams
        
        Returns:
            bool: True if entry added successfully
        """
        try:
            # Validate inputs
            if not self._validate_nutrition_data(user, date, calories, protein, carbs, fats):
                return False
            
            # Check if entry already exists for this user and date
            existing_entry = self.nutrition_df[
                (self.nutrition_df['user'].str.lower() == user.lower()) &
                (self.nutrition_df['date'] == date)
            ]
            
            if not existing_entry.empty:
                # Update existing entry
                return self.update_nutrition_entry(user, date, calories, protein, carbs, fats)
            
            # Create new nutrition entry
            new_entry = {
                'user': user.strip(),
                'date': date,
                'calories': int(calories),
                'protein': int(protein),
                'carbs': int(carbs),
                'fats': int(fats),
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Add to DataFrame
            new_row = pd.DataFrame([new_entry])
            self.nutrition_df = pd.concat([self.nutrition_df, new_row], ignore_index=True)
            
            # Save to file
            return self._save_data()
        
        except Exception as e:
            print(f"Error adding nutrition entry: {e}")
            return False
    
    def _validate_nutrition_data(self, user: str, date: str, calories: int, 
                                protein: int, carbs: int, fats: int) -> bool:
        """
        Validate nutrition data before adding.
        
        Args:
            user (str): User name
            date (str): Date
            calories (int): Calories
            protein (int): Protein in grams
            carbs (int): Carbs in grams
            fats (int): Fats in grams
        
        Returns:
            bool: True if data is valid
        """
        try:
            # Check required fields
            if not user:
                print("User is required")
                return False
            
            # Validate date format
            datetime.strptime(date, "%Y-%m-%d")
            
            # Validate numeric ranges
            if not (0 <= calories <= 10000):
                print("Calories must be between 0 and 10000")
                return False
            
            if not (0 <= protein <= 1000):
                print("Protein must be between 0 and 1000g")
                return False
            
            if not (0 <= carbs <= 2000):
                print("Carbs must be between 0 and 2000g")
                return False
            
            if not (0 <= fats <= 500):
                print("Fats must be between 0 and 500g")
                return False
            
            # Check if macros roughly match calories (allowing for some flexibility)
            calculated_calories = (protein * 4) + (carbs * 4) + (fats * 9)
            if abs(calculated_calories - calories) > calories * 0.2:  # Allow 20% deviation
                print(f"Warning: Macros don't match calories. Calculated: {calculated_calories}, Provided: {calories}")
            
            return True
        
        except ValueError as e:
            print(f"Invalid date format: {e}")
            return False
        except Exception as e:
            print(f"Validation error: {e}")
            return False
    
    def get_user_nutrition(self, user: str) -> pd.DataFrame:
        """
        Get all nutrition entries for a specific user.
        
        Args:
            user (str): User name
        
        Returns:
            pd.DataFrame: User's nutrition data
        """
        try:
            if self.nutrition_df.empty:
                return pd.DataFrame()
            
            user_data = self.nutrition_df[self.nutrition_df['user'].str.lower() == user.lower()].copy()
            
            if not user_data.empty:
                # Sort by date
                user_data['date'] = pd.to_datetime(user_data['date'])
                user_data = user_data.sort_values('date')
                user_data['date'] = user_data['date'].dt.strftime('%Y-%m-%d')
            
            return user_data
        
        except Exception as e:
            print(f"Error retrieving user nutrition: {e}")
            return pd.DataFrame()
    
    def get_recent_nutrition(self, user: str, days: int = 7) -> pd.DataFrame:
        """
        Get recent nutrition entries for a user within specified days.
        
        Args:
            user (str): User name
            days (int): Number of recent days to retrieve
        
        Returns:
            pd.DataFrame: Recent nutrition data
        """
        try:
            user_nutrition = self.get_user_nutrition(user)
            
            if user_nutrition.empty:
                return pd.DataFrame()
            
            # Calculate cutoff date
            cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            
            # Filter recent nutrition
            user_nutrition['date'] = pd.to_datetime(user_nutrition['date'])
            recent_nutrition = user_nutrition[
                user_nutrition['date'] >= pd.to_datetime(cutoff_date)
            ].copy()
            
            # Convert date back to string and sort
            recent_nutrition['date'] = recent_nutrition['date'].dt.strftime('%Y-%m-%d')
            return recent_nutrition.sort_values('date', ascending=False)
        
        except Exception as e:
            print(f"Error retrieving recent nutrition: {e}")
            return pd.DataFrame()
    
    def get_nutrition_stats(self, user: str, days: int = 30) -> Dict:
        """
        Get nutrition statistics for a user over specified period.
        
        Args:
            user (str): User name
            days (int): Number of days to analyze
        
        Returns:
            Dict: Dictionary containing nutrition statistics
        """
        try:
            recent_nutrition = self.get_recent_nutrition(user, days)
            
            if recent_nutrition.empty:
                return {
                    'avg_calories': 0,
                    'avg_protein': 0,
                    'avg_carbs': 0,
                    'avg_fats': 0,
                    'total_days_logged': 0,
                    'calories_range': (0, 0),
                    'protein_percentage': 0,
                    'carbs_percentage': 0,
                    'fats_percentage': 0
                }
            
            # Calculate averages
            avg_calories = recent_nutrition['calories'].mean()
            avg_protein = recent_nutrition['protein'].mean()
            avg_carbs = recent_nutrition['carbs'].mean()
            avg_fats = recent_nutrition['fats'].mean()
            
            # Calculate macro percentages
            total_macros = (avg_protein * 4) + (avg_carbs * 4) + (avg_fats * 9)
            if total_macros > 0:
                protein_percentage = round((avg_protein * 4) / total_macros * 100, 1)
                carbs_percentage = round((avg_carbs * 4) / total_macros * 100, 1)
                fats_percentage = round((avg_fats * 9) / total_macros * 100, 1)
            else:
                protein_percentage = carbs_percentage = fats_percentage = 0
            
            stats = {
                'avg_calories': round(avg_calories, 0),
                'avg_protein': round(avg_protein, 1),
                'avg_carbs': round(avg_carbs, 1),
                'avg_fats': round(avg_fats, 1),
                'total_days_logged': len(recent_nutrition),
                'calories_range': (recent_nutrition['calories'].min(), recent_nutrition['calories'].max()),
                'protein_percentage': protein_percentage,
                'carbs_percentage': carbs_percentage,
                'fats_percentage': fats_percentage
            }
            
            return stats
        
        except Exception as e:
            print(f"Error calculating nutrition stats: {e}")
            return {}
    
    def update_nutrition_entry(self, user: str, date: str, calories: int = None, 
                              protein: int = None, carbs: int = None, fats: int = None) -> bool:
        """
        Update an existing nutrition entry.
        
        Args:
            user (str): User name
            date (str): Date of the entry
            calories (int, optional): New calories value
            protein (int, optional): New protein value
            carbs (int, optional): New carbs value
            fats (int, optional): New fats value
        
        Returns:
            bool: True if update was successful
        """
        try:
            # Find matching entry
            mask = (
                (self.nutrition_df['user'].str.lower() == user.lower()) &
                (self.nutrition_df['date'] == date)
            )
            
            entry_indices = self.nutrition_df[mask].index
            
            if len(entry_indices) == 0:
                print("Nutrition entry not found")
                return False
            
            # Update specified fields
            for idx in entry_indices:
                if calories is not None:
                    self.nutrition_df.loc[idx, 'calories'] = int(calories)
                if protein is not None:
                    self.nutrition_df.loc[idx, 'protein'] = int(protein)
                if carbs is not None:
                    self.nutrition_df.loc[idx, 'carbs'] = int(carbs)
                if fats is not None:
                    self.nutrition_df.loc[idx, 'fats'] = int(fats)
                
                # Update timestamp
                self.nutrition_df.loc[idx, 'timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            return self._save_data()
        
        except Exception as e:
            print(f"Error updating nutrition entry: {e}")
            return False
    
    def delete_nutrition_entry(self, user: str, date: str) -> bool:
        """
        Delete a nutrition entry for a specific date.
        
        Args:
            user (str): User name
            date (str): Date of the entry to delete
        
        Returns:
            bool: True if deletion was successful
        """
        try:
            # Find matching entry
            mask = (
                (self.nutrition_df['user'].str.lower() == user.lower()) &
                (self.nutrition_df['date'] == date)
            )
            
            if not self.nutrition_df[mask].empty:
                # Remove the entry
                self.nutrition_df = self.nutrition_df[~mask]
                return self._save_data()
            else:
                print("Nutrition entry not found")
                return False
        
        except Exception as e:
            print(f"Error deleting nutrition entry: {e}")
            return False
    
    def get_all_users(self) -> List[str]:
        """
        Get list of all users with nutrition data.
        
        Returns:
            List[str]: List of unique user names
        """
        try:
            if self.nutrition_df.empty:
                return []
            
            users = self.nutrition_df['user'].unique().tolist()
            return sorted([user for user in users if user and str(user).strip()])
        
        except Exception as e:
            print(f"Error retrieving users: {e}")
            return []
    
    def get_nutrition_trends(self, user: str, days: int = 30) -> Dict:
        """
        Analyze nutrition trends over time.
        
        Args:
            user (str): User name
            days (int): Number of days to analyze
        
        Returns:
            Dict: Trend analysis data
        """
        try:
            recent_nutrition = self.get_recent_nutrition(user, days)
            
            if len(recent_nutrition) < 3:
                return {'trend': 'insufficient_data', 'message': 'Need at least 3 days of data'}
            
            # Convert date to datetime for trend analysis
            recent_nutrition = recent_nutrition.copy()
            recent_nutrition['date'] = pd.to_datetime(recent_nutrition['date'])
            recent_nutrition = recent_nutrition.sort_values('date')
            
            # Simple trend analysis (comparing first half vs second half)
            mid_point = len(recent_nutrition) // 2
            first_half = recent_nutrition.iloc[:mid_point]
            second_half = recent_nutrition.iloc[mid_point:]
            
            trends = {}
            for column in ['calories', 'protein', 'carbs', 'fats']:
                first_avg = first_half[column].mean()
                second_avg = second_half[column].mean()
                
                if first_avg == 0:
                    change_percent = 0
                else:
                    change_percent = ((second_avg - first_avg) / first_avg) * 100
                
                if abs(change_percent) < 5:
                    trend = 'stable'
                elif change_percent > 0:
                    trend = 'increasing'
                else:
                    trend = 'decreasing'
                
                trends[column] = {
                    'trend': trend,
                    'change_percent': round(change_percent, 1),
                    'first_half_avg': round(first_avg, 1),
                    'second_half_avg': round(second_avg, 1)
                }
            
            return trends
        
        except Exception as e:
            print(f"Error analyzing nutrition trends: {e}")
            return {}
    
    def get_daily_nutrition(self, user: str, date: str) -> Dict:
        """
        Get nutrition data for a specific date.
        
        Args:
            user (str): User name
            date (str): Date in YYYY-MM-DD format
        
        Returns:
            Dict: Nutrition data for the specified date
        """
        try:
            entry = self.nutrition_df[
                (self.nutrition_df['user'].str.lower() == user.lower()) &
                (self.nutrition_df['date'] == date)
            ]
            
            if entry.empty:
                return {}
            
            # Convert to dictionary
            entry_dict = entry.iloc[0].to_dict()
            
            # Remove timestamp if exists
            entry_dict.pop('timestamp', None)
            
            return entry_dict
        
        except Exception as e:
            print(f"Error retrieving daily nutrition: {e}")
            return {}
    
    def calculate_weekly_averages(self, user: str, weeks: int = 4) -> pd.DataFrame:
        """
        Calculate weekly nutrition averages.
        
        Args:
            user (str): User name
            weeks (int): Number of weeks to analyze
        
        Returns:
            pd.DataFrame: Weekly averages
        """
        try:
            days_to_analyze = weeks * 7
            recent_nutrition = self.get_recent_nutrition(user, days_to_analyze)
            
            if recent_nutrition.empty:
                return pd.DataFrame()
            
            # Convert date to datetime and add week column
            recent_nutrition = recent_nutrition.copy()
            recent_nutrition['date'] = pd.to_datetime(recent_nutrition['date'])
            recent_nutrition['week'] = recent_nutrition['date'].dt.isocalendar().week
            recent_nutrition['year_week'] = recent_nutrition['date'].dt.strftime('%Y-W%U')
            
            # Calculate weekly averages
            weekly_averages = recent_nutrition.groupby('year_week').agg({
                'calories': 'mean',
                'protein': 'mean',
                'carbs': 'mean',
                'fats': 'mean'
            }).round(1)
            
            return weekly_averages.reset_index()
        
        except Exception as e:
            print(f"Error calculating weekly averages: {e}")
            return pd.DataFrame()
    
    def export_user_nutrition(self, user: str, filename: str = None) -> bool:
        """
        Export user's nutrition data to CSV file.
        
        Args:
            user (str): User name
            filename (str, optional): Output filename
        
        Returns:
            bool: True if export was successful
        """
        try:
            user_nutrition = self.get_user_nutrition(user)
            
            if user_nutrition.empty:
                print(f"No nutrition data found for user: {user}")
                return False
            
            if filename is None:
                filename = f"data/{user.replace(' ', '_')}_nutrition.csv"
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            # Export to CSV
            user_nutrition.to_csv(filename, index=False)
            print(f"Nutrition data exported to: {filename}")
            return True
        
        except Exception as e:
            print(f"Error exporting nutrition data: {e}")
            return False
    
    def check_nutrition_goals(self, user: str, calorie_goal: int = None, 
                             protein_goal: int = None, days: int = 7) -> Dict:
        """
        Check if user is meeting nutrition goals.
        
        Args:
            user (str): User name
            calorie_goal (int, optional): Daily calorie goal
            protein_goal (int, optional): Daily protein goal in grams
            days (int): Number of recent days to analyze
        
        Returns:
            Dict: Goal achievement analysis
        """
        try:
            recent_nutrition = self.get_recent_nutrition(user, days)
            
            if recent_nutrition.empty:
                return {'status': 'no_data', 'message': 'No nutrition data available'}
            
            results = {
                'days_analyzed': len(recent_nutrition),
                'avg_calories': round(recent_nutrition['calories'].mean(), 0),
                'avg_protein': round(recent_nutrition['protein'].mean(), 1)
            }
            
            if calorie_goal:
                calorie_achievement = (results['avg_calories'] / calorie_goal) * 100
                results['calorie_goal'] = calorie_goal
                results['calorie_achievement'] = round(calorie_achievement, 1)
                results['calorie_status'] = 'on_track' if 90 <= calorie_achievement <= 110 else 'off_track'
            
            if protein_goal:
                protein_achievement = (results['avg_protein'] / protein_goal) * 100
                results['protein_goal'] = protein_goal
                results['protein_achievement'] = round(protein_achievement, 1)
                results['protein_status'] = 'on_track' if protein_achievement >= 90 else 'below_target'
            
            return results
        
        except Exception as e:
            print(f"Error checking nutrition goals: {e}")
            return {}
    
    def get_missing_days(self, user: str, days: int = 30) -> List[str]:
        """
        Find days where nutrition data is missing.
        
        Args:
            user (str): User name
            days (int): Number of recent days to check
        
        Returns:
            List[str]: List of missing dates in YYYY-MM-DD format
        """
        try:
            # Generate list of all dates in the period
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days-1)
            
            all_dates = []
            current_date = start_date
            while current_date <= end_date:
                all_dates.append(current_date.strftime('%Y-%m-%d'))
                current_date += timedelta(days=1)
            
            # Get user's logged dates
            user_nutrition = self.get_user_nutrition(user)
            if user_nutrition.empty:
                return all_dates
            
            logged_dates = set(user_nutrition['date'].tolist())
            
            # Find missing dates
            missing_dates = [date for date in all_dates if date not in logged_dates]
            
            return missing_dates
        
        except Exception as e:
            print(f"Error finding missing days: {e}")
            return []
    
    def refresh_data(self) -> bool:
        """
        Refresh nutrition data from file (useful for concurrent access).
        
        Returns:
            bool: True if refresh was successful
        """
        try:
            self.nutrition_df = self._load_data()
            return True
        except Exception as e:
            print(f"Error refreshing nutrition data: {e}")
            return False
