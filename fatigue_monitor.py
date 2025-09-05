"""
Fatigue Monitor Module
=====================

This module monitors training fatigue and provides recommendations for deload periods.
Features include:
- Fatigue score calculation based on training volume and RPE
- Deload recommendations
- Recovery status assessment
- Training readiness indicators



import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from workout_tracking import WorkoutTracker

class FatigueMonitor:
    """
    A class to monitor training fatigue and provide recovery recommendations.
    
    Features:
    - Multi-factor fatigue assessment
    - Deload period recommendations
    - Recovery status tracking
    - Training readiness indicators
    """
    
    def __init__(self, workout_tracker: WorkoutTracker = None):
        """
        Initialize the FatigueMonitor.
        
        Args:
            workout_tracker (WorkoutTracker, optional): Workout tracker instance
        """
        self.workout_tracker = workout_tracker or WorkoutTracker()
        
        # Fatigue calculation weights
        self.weights = {
            'volume': 0.3,      # Training volume contribution
            'intensity': 0.4,   # RPE/intensity contribution
            'frequency': 0.2,   # Training frequency contribution
            'trend': 0.1        # Recent trend contribution
        }
    
    def calculate_fatigue_score(self, user: str, days: int = 7) -> float:
        """
        Calculate overall fatigue score based on recent training data.
        
        Args:
            user (str): User name
            days (int): Number of recent days to analyze
        
        Returns:
            float: Fatigue score from 0-10 (0 = no fatigue, 10 = extreme fatigue)
        """
        try:
            recent_workouts = self.workout_tracker.get_recent_workouts(user, days)
            
            if recent_workouts.empty:
                return 0.0
            
            # Calculate individual fatigue components
            volume_fatigue = self._calculate_volume_fatigue(recent_workouts)
            intensity_fatigue = self._calculate_intensity_fatigue(recent_workouts)
            frequency_fatigue = self._calculate_frequency_fatigue(recent_workouts, days)
            trend_fatigue = self._calculate_trend_fatigue(user, days)
            
            # Weighted combination
            total_fatigue = (
                volume_fatigue * self.weights['volume'] +
                intensity_fatigue * self.weights['intensity'] +
                frequency_fatigue * self.weights['frequency'] +
                trend_fatigue * self.weights['trend']
            )
            
            # Ensure score is within 0-10 range
            return max(0.0, min(10.0, total_fatigue))
        
        except Exception as e:
            print(f"Error calculating fatigue score: {e}")
            return 0.0
    
    def _calculate_volume_fatigue(self, workouts: pd.DataFrame) -> float:
        """
        Calculate fatigue based on training volume.
        
        Args:
            workouts (pd.DataFrame): Recent workout data
        
        Returns:
            float: Volume-based fatigue score (0-10)
        """
        try:
            if workouts.empty:
                return 0.0
            
            # Calculate total sets and volume
            total_sets = workouts['sets'].sum()
            total_reps = (workouts['sets'] * workouts['reps']).sum()
            total_tonnage = (workouts['weight'] * workouts['sets'] * workouts['reps']).sum()
            
            # Normalize based on typical training volumes
            # These thresholds can be adjusted based on user population
            sets_score = min(total_sets / 50.0, 1.0) * 10  # 50+ sets = high volume
            tonnage_score = min(total_tonnage / 10000.0, 1.0) * 10  # 10,000kg+ = high tonnage
            
            # Combine volume metrics
            volume_fatigue = (sets_score + tonnage_score) / 2
            
            return volume_fatigue
        
        except Exception as e:
            print(f"Error calculating volume fatigue: {e}")
            return 0.0
    
    def _calculate_intensity_fatigue(self, workouts: pd.DataFrame) -> float:
        """
        Calculate fatigue based on training intensity (RPE).
        
        Args:
            workouts (pd.DataFrame): Recent workout data
        
        Returns:
            float: Intensity-based fatigue score (0-10)
        """
        try:
            if workouts.empty or 'rpe' not in workouts.columns:
                return 0.0
            
            # Calculate weighted RPE (more recent workouts weighted higher)
            workouts_sorted = workouts.sort_values('date')
            
            # Create recency weights (more recent = higher weight)
            n_workouts = len(workouts_sorted)
            recency_weights = np.linspace(0.5, 1.0, n_workouts)
            
            # Calculate weighted average RPE
            weighted_rpe = np.average(workouts_sorted['rpe'], weights=recency_weights)
            
            # Convert RPE to fatigue score (RPE 6-10 maps to fatigue 0-10)
            if weighted_rpe <= 6:
                intensity_fatigue = 0.0
            else:
                intensity_fatigue = ((weighted_rpe - 6) / 4) * 10
            
            return min(intensity_fatigue, 10.0)
        
        except Exception as e:
            print(f"Error calculating intensity fatigue: {e}")
            return 0.0
    
    def _calculate_frequency_fatigue(self, workouts: pd.DataFrame, days: int) -> float:
        """
        Calculate fatigue based on training frequency.
        
        Args:
            workouts (pd.DataFrame): Recent workout data
            days (int): Period analyzed
        
        Returns:
            float: Frequency-based fatigue score (0-10)
        """
        try:
            if workouts.empty:
                return 0.0
            
            # Calculate training frequency
            unique_days = len(workouts['date'].unique())
            frequency_ratio = unique_days / days
            
            # Optimal frequency is around 3-4 days per week
            # Too high or too low frequency can indicate issues
            if frequency_ratio <= 0.3:  # Less than 2 days per week
                return 1.0
            elif 0.3 < frequency_ratio <= 0.6:  # 2-4 days per week (optimal)
                return 0.0
            elif 0.6 < frequency_ratio <= 0.8:  # 4-5 days per week
                return 3.0
            else:  # More than 5 days per week
                return 7.0
        
        except Exception as e:
            print(f"Error calculating frequency fatigue: {e}")
            return 0.0
    
    def _calculate_trend_fatigue(self, user: str, days: int) -> float:
        """
        Calculate fatigue based on performance trends.
        
        Args:
            user (str): User name
            days (int): Period to analyze
        
        Returns:
            float: Trend-based fatigue score (0-10)
        """
        try:
            # Compare recent performance to previous period
            recent_workouts = self.workout_tracker.get_recent_workouts(user, days)
            previous_workouts = self.workout_tracker.get_recent_workouts(user, days * 2)
            
            if len(previous_workouts) < days or recent_workouts.empty:
                return 0.0
            
            # Split previous workouts into earlier and recent periods
            previous_workouts['date'] = pd.to_datetime(previous_workouts['date'])
            cutoff_date = previous_workouts['date'].max() - timedelta(days=days)
            earlier_workouts = previous_workouts[previous_workouts['date'] <= cutoff_date]
            
            if earlier_workouts.empty:
                return 0.0
            
            # Compare RPE trends
            recent_avg_rpe = recent_workouts['rpe'].mean()
            earlier_avg_rpe = earlier_workouts['rpe'].mean()
            rpe_increase = recent_avg_rpe - earlier_avg_rpe
            
            # Compare volume trends
            recent_volume = recent_workouts['sets'].sum()
            earlier_volume = earlier_workouts['sets'].sum()
            
            # If RPE is increasing while volume is stable/increasing, indicates fatigue
            trend_fatigue = 0.0
            if rpe_increase > 0.5:  # RPE increased significantly
                trend_fatigue += rpe_increase * 2
            
            if recent_volume >= earlier_volume and rpe_increase > 0:
                trend_fatigue += 2.0  # Volume maintained but RPE up
            
            return min(trend_fatigue, 10.0)
        
        except Exception as e:
            print(f"Error calculating trend fatigue: {e}")
            return 0.0
    
    def get_fatigue_status(self, user: str) -> Dict:
        """
        Get current fatigue status with descriptive message.
        
        Args:
            user (str): User name
        
        Returns:
            Dict: Fatigue status information
        """
        try:
            fatigue_score = self.calculate_fatigue_score(user)
            
            if fatigue_score <= 3:
                status = 'Low'
                message = 'Low fatigue levels. Good recovery status.'
                color = 'green'
            elif fatigue_score <= 6:
                status = 'Moderate'
                message = 'Moderate fatigue. Monitor training load.'
                color = 'yellow'
            elif fatigue_score <= 8:
                status = 'High'
                message = 'High fatigue levels. Consider reducing training load.'
                color = 'orange'
            else:
                status = 'Very High'
                message = 'Very high fatigue. Deload or rest recommended.'
                color = 'red'
            
            return {
                'score': fatigue_score,
                'status': status,
                'message': message,
                'color': color
            }
        
        except Exception as e:
            print(f"Error getting fatigue status: {e}")
            return {
                'score': 0,
                'status': 'Unknown',
                'message': 'Unable to assess fatigue',
                'color': 'gray'
            }
    
    def recommend_deload(self, user: str) -> Dict:
        """
        Recommend whether user should take a deload week.
        
        Args:
            user (str): User name
        
        Returns:
            Dict: Deload recommendation
        """
        try:
            # Analyze multiple factors for deload recommendation
            fatigue_score = self.calculate_fatigue_score(user)
            
            # Check recent workout pattern
            recent_workouts = self.workout_tracker.get_recent_workouts(user, 14)
            
            if recent_workouts.empty:
                return {
                    'should_deload': False,
                    'reason': 'Insufficient data',
                    'suggestion': 'Continue training and monitor fatigue'
                }
            
            deload_indicators = []
            deload_score = 0
            
            # High fatigue score
            if fatigue_score > 7:
                deload_indicators.append('High fatigue levels')
                deload_score += 3
            
            # Consistently high RPE
            if 'rpe' in recent_workouts.columns:
                avg_rpe = recent_workouts['rpe'].mean()
                if avg_rpe > 8.5:
                    deload_indicators.append('Consistently high RPE')
                    deload_score += 2
                
                # Many RPE 9-10 sessions
                high_rpe_sessions = len(recent_workouts[recent_workouts['rpe'] >= 9])
                if high_rpe_sessions >= 3:
                    deload_indicators.append('Multiple very high intensity sessions')
                    deload_score += 2
            
            # High training frequency
            training_days = len(recent_workouts['date'].unique())
            if training_days > 10:  # More than 10 days in 2 weeks
                deload_indicators.append('High training frequency')
                deload_score += 1
            
            # Time since last deload (if we can track it)
            # For now, we'll use a simple heuristic based on total workouts
            total_workouts = len(self.workout_tracker.get_user_workouts(user))
            if total_workouts > 20:  # Assume needs deload every ~20 workouts
                weeks_training = total_workouts // 3  # Assume 3 workouts per week
                if weeks_training >= 4:  # 4+ weeks without deload
                    deload_indicators.append('Extended training period')
                    deload_score += 1
            
            # Make recommendation
            if deload_score >= 4:
                should_deload = True
                suggestion = 'Take a deload week: reduce weight by 20-30% and focus on form'
            elif deload_score >= 2:
                should_deload = True
                suggestion = 'Consider a light deload: reduce volume by 30-40%'
            else:
                should_deload = False
                suggestion = 'Continue current training but monitor fatigue closely'
            
            reason = ', '.join(deload_indicators) if deload_indicators else 'Low deload indicators'
            
            return {
                'should_deload': should_deload,
                'deload_score': deload_score,
                'reason': reason,
                'suggestion': suggestion,
                'indicators': deload_indicators
            }
        
        except Exception as e:
            print(f"Error recommending deload: {e}")
            return {
                'should_deload': False,
                'reason': 'Error in analysis',
                'suggestion': 'Monitor training and consult with coach'
            }
    
    def get_recovery_recommendations(self, user: str) -> List[Dict]:
        """
        Get personalized recovery recommendations based on fatigue analysis.
        
        Args:
            user (str): User name
        
        Returns:
            List[Dict]: List of recovery recommendations
        """
        try:
            fatigue_status = self.get_fatigue_status(user)
            fatigue_score = fatigue_status['score']
            
            recommendations = []
            
            # Base recommendations for all fatigue levels
            recommendations.append({
                'category': 'Sleep',
                'priority': 'high',
                'message': 'Ensure 7-9 hours of quality sleep per night'
            })
            
            recommendations.append({
                'category': 'Nutrition',
                'priority': 'high',
                'message': 'Maintain adequate protein intake (1.6-2.2g/kg bodyweight)'
            })
            
            # Fatigue-specific recommendations
            if fatigue_score <= 3:
                recommendations.append({
                    'category': 'Training',
                    'priority': 'low',
                    'message': 'Good recovery status. Can maintain or slightly increase training load'
                })
            
            elif fatigue_score <= 6:
                recommendations.extend([
                    {
                        'category': 'Training',
                        'priority': 'medium',
                        'message': 'Consider adding extra rest day or reducing intensity'
                    },
                    {
                        'category': 'Recovery',
                        'priority': 'medium',
                        'message': 'Focus on stress management and active recovery'
                    }
                ])
            
            elif fatigue_score <= 8:
                recommendations.extend([
                    {
                        'category': 'Training',
                        'priority': 'high',
                        'message': 'Reduce training volume by 20-30% this week'
                    },
                    {
                        'category': 'Recovery',
                        'priority': 'high',
                        'message': 'Prioritize recovery: massage, stretching, meditation'
                    },
                    {
                        'category': 'Monitoring',
                        'priority': 'medium',
                        'message': 'Monitor morning heart rate and subjective wellness'
                    }
                ])
            
            else:  # Very high fatigue
                recommendations.extend([
                    {
                        'category': 'Training',
                        'priority': 'critical',
                        'message': 'Take complete rest or very light active recovery only'
                    },
                    {
                        'category': 'Health',
                        'priority': 'high',
                        'message': 'Consider consulting healthcare provider if fatigue persists'
                    },
                    {
                        'category': 'Recovery',
                        'priority': 'critical',
                        'message': 'Focus entirely on recovery: sleep, nutrition, stress reduction'
                    }
                ])
            
            return recommendations
        
        except Exception as e:
            print(f"Error getting recovery recommendations: {e}")
            return []
    
    def calculate_training_readiness(self, user: str) -> Dict:
        """
        Calculate training readiness score based on recent performance and fatigue.
        
        Args:
            user (str): User name
        
        Returns:
            Dict: Training readiness assessment
        """
        try:
            fatigue_score = self.calculate_fatigue_score(user)
            recent_workouts = self.workout_tracker.get_recent_workouts(user, 7)
            
            if recent_workouts.empty:
                return {
                    'readiness_score': 5,
                    'status': 'Unknown',
                    'message': 'Insufficient recent data'
                }
            
            # Base readiness from inverse of fatigue (10 - fatigue_score)
            base_readiness = 10 - fatigue_score
            
            # Adjust based on recent performance consistency
            if 'rpe' in recent_workouts.columns:
                rpe_std = recent_workouts['rpe'].std()
                
                # Low RPE variability indicates good consistency
                if rpe_std < 0.5:
                    consistency_bonus = 1
                elif rpe_std < 1:
                    consistency_bonus = 0.5
                else:
                    consistency_bonus = 0
                
                readiness_score = min(10, base_readiness + consistency_bonus)
            else:
                readiness_score = base_readiness
            
            # Determine status
            if readiness_score >= 8:
                status = 'Excellent'
                message = 'Ready for high-intensity training'
            elif readiness_score >= 6:
                status = 'Good'
                message = 'Ready for normal training load'
            elif readiness_score >= 4:
                status = 'Fair'
                message = 'Consider moderate training intensity'
            else:
                status = 'Poor'
                message = 'Focus on recovery, light training only'
            
            return {
                'readiness_score': round(readiness_score, 1),
                'status': status,
                'message': message,
                'fatigue_component': fatigue_score,
                'base_readiness': round(base_readiness, 1)
            }
        
        except Exception as e:
            print(f"Error calculating training readiness: {e}")
            return {
                'readiness_score': 5,
                'status': 'Error',
                'message': 'Unable to calculate readiness'
            }
    
    def get_fatigue_history(self, user: str, days: int = 30) -> List[Dict]:
        """
        Get historical fatigue scores over a period.
        
        Args:
            user (str): User name
            days (int): Number of days to analyze
        
        Returns:
            List[Dict]: Historical fatigue data
        """
        try:
            fatigue_history = []
            
            # Calculate fatigue for each week in the period
            for week in range(days // 7):
                start_day = week * 7
                end_day = start_day + 7
                
                # Get workouts for this week
                week_end = datetime.now() - timedelta(days=start_day)
                week_start = week_end - timedelta(days=7)
                
                all_workouts = self.workout_tracker.get_user_workouts(user)
                if all_workouts.empty:
                    continue
                
                all_workouts['date'] = pd.to_datetime(all_workouts['date'])
                week_workouts = all_workouts[
                    (all_workouts['date'] >= week_start) & 
                    (all_workouts['date'] < week_end)
                ]
                
                if not week_workouts.empty:
                    # Calculate fatigue for this week (simplified)
                    week_fatigue = self._calculate_simple_fatigue(week_workouts)
                    
                    fatigue_history.append({
                        'week_start': week_start.strftime('%Y-%m-%d'),
                        'week_end': week_end.strftime('%Y-%m-%d'),
                        'fatigue_score': round(week_fatigue, 1),
                        'workouts': len(week_workouts)
                    })
            
            return list(reversed(fatigue_history))  # Most recent first
        
        except Exception as e:
            print(f"Error getting fatigue history: {e}")
            return []
    
    def _calculate_simple_fatigue(self, workouts: pd.DataFrame) -> float:
        """
        Calculate a simplified fatigue score for historical analysis.
        
        Args:
            workouts (pd.DataFrame): Workout data for the period
        
        Returns:
            float: Simplified fatigue score
        """
        try:
            if workouts.empty:
                return 0.0
            
            # Simple fatigue based on volume and intensity
            total_sets = workouts['sets'].sum()
            avg_rpe = workouts['rpe'].mean() if 'rpe' in workouts.columns else 7
            
            # Normalize
            volume_factor = min(total_sets / 20.0, 1.0) * 5  # 20 sets = moderate volume
            intensity_factor = max(0, (avg_rpe - 6) / 4 * 5)  # RPE 6-10 maps to 0-5
            
            return volume_factor + intensity_factor
        
        except Exception as e:
            print(f"Error calculating simple fatigue: {e}")
            return 0.0
