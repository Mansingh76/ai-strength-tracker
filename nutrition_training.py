import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict

class NutritionTracker:
    """
    A class to handle nutrition tracking and data management (in-memory only).
    
    Features:
    - Multi-user support
    - Daily nutrition logging
    - Macronutrient tracking (calories, protein, carbs, fats)
    - Nutrition statistics and trends
    """
    
    def __init__(self):
        """Initialize the NutritionTracker with empty DataFrame (no CSV)."""
        self.nutrition_df = pd.DataFrame(columns=['user', 'date', 'calories', 'protein', 'carbs', 'fats', 'timestamp'])
    
    def add_nutrition_entry(self, user: str, date: str, calories: int, 
                           protein: int, carbs: int, fats: int) -> bool:
        """Add or update a nutrition entry for a specific user and date."""
        try:
            if not self._validate_nutrition_data(user, date, calories, protein, carbs, fats):
                return False
            
            existing_entry = self.nutrition_df[
                (self.nutrition_df['user'].str.lower() == user.lower()) &
                (self.nutrition_df['date'] == date)
            ]
            
            if not existing_entry.empty:
                return self.update_nutrition_entry(user, date, calories, protein, carbs, fats)
            
            new_entry = {
                'user': user.strip(),
                'date': date,
                'calories': int(calories),
                'protein': int(protein),
                'carbs': int(carbs),
                'fats': int(fats),
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            self.nutrition_df = pd.concat([self.nutrition_df, pd.DataFrame([new_entry])], ignore_index=True)
            return True
        except Exception as e:
            print(f"Error adding nutrition entry: {e}")
            return False
    
    def _validate_nutrition_data(self, user: str, date: str, calories: int, 
                                protein: int, carbs: int, fats: int) -> bool:
        """Validate input nutrition data."""
        try:
            if not user:
                print("User is required")
                return False
            datetime.strptime(date, "%Y-%m-%d")
            if not (0 <= calories <= 10000): return False
            if not (0 <= protein <= 1000): return False
            if not (0 <= carbs <= 2000): return False
            if not (0 <= fats <= 500): return False
            return True
        except Exception:
            return False
    
    def get_user_nutrition(self, user: str) -> pd.DataFrame:
        """Retrieve all nutrition data for a user."""
        user_data = self.nutrition_df[self.nutrition_df['user'].str.lower() == user.lower()].copy()
        if not user_data.empty:
            user_data['date'] = pd.to_datetime(user_data['date'])
            user_data = user_data.sort_values('date')
            user_data['date'] = user_data['date'].dt.strftime('%Y-%m-%d')
        return user_data
    
    def get_recent_nutrition(self, user: str, days: int = 7) -> pd.DataFrame:
        """Get last N days of nutrition logs."""
        user_data = self.get_user_nutrition(user)
        if user_data.empty:
            return pd.DataFrame()
        cutoff = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        user_data['date'] = pd.to_datetime(user_data['date'])
        recent = user_data[user_data['date'] >= pd.to_datetime(cutoff)].copy()
        recent['date'] = recent['date'].dt.strftime('%Y-%m-%d')
        return recent.sort_values('date', ascending=False)
    
    def get_nutrition_stats(self, user: str, days: int = 30) -> Dict:
        """Return averages and macro percentages for a given time window."""
        data = self.get_recent_nutrition(user, days)
        if data.empty:
            return {}
        avg_calories = data['calories'].mean()
        avg_protein = data['protein'].mean()
        avg_carbs = data['carbs'].mean()
        avg_fats = data['fats'].mean()
        total_macros = (avg_protein*4) + (avg_carbs*4) + (avg_fats*9)
        return {
            'avg_calories': round(avg_calories, 0),
            'avg_protein': round(avg_protein, 1),
            'avg_carbs': round(avg_carbs, 1),
            'avg_fats': round(avg_fats, 1),
            'days_logged': len(data),
            'protein_pct': round((avg_protein*4)/total_macros*100,1) if total_macros else 0,
            'carbs_pct': round((avg_carbs*4)/total_macros*100,1) if total_macros else 0,
            'fats_pct': round((avg_fats*9)/total_macros*100,1) if total_macros else 0
        }
    
    def update_nutrition_entry(self, user: str, date: str, calories: int = None, 
                              protein: int = None, carbs: int = None, fats: int = None) -> bool:
        """Update existing nutrition entry."""
        mask = (self.nutrition_df['user'].str.lower() == user.lower()) & (self.nutrition_df['date'] == date)
        if not mask.any():
            return False
        idx = self.nutrition_df[mask].index
        if calories is not None: self.nutrition_df.loc[idx, 'calories'] = calories
        if protein is not None: self.nutrition_df.loc[idx, 'protein'] = protein
        if carbs is not None: self.nutrition_df.loc[idx, 'carbs'] = carbs
        if fats is not None: self.nutrition_df.loc[idx, 'fats'] = fats
        self.nutrition_df.loc[idx, 'timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return True
    
    def delete_nutrition_entry(self, user: str, date: str) -> bool:
        """Remove entry for a specific date."""
        mask = (self.nutrition_df['user'].str.lower() == user.lower()) & (self.nutrition_df['date'] == date)
        if not mask.any():
            return False
        self.nutrition_df = self.nutrition_df[~mask]
        return True
    
    def get_all_users(self) -> List[str]:
        """Return all unique users."""
        return sorted(self.nutrition_df['user'].dropna().unique().tolist())
