"""
Memory Bank - Persistent storage for user data and consultation history

⚠️ DEPRECATED / UNUSED: This service is not currently used in the implementation.

The current implementation uses session.state (in-memory) for sharing data between
agents during a consultation. This MemoryBank provides SQLite-based persistent
storage that could be used for:
- Long-term user profile storage
- Consultation history tracking
- Cross-session data persistence

CURRENT DATA FLOW:
1. Interview agent saves to session.state["user_profile"]
2. Analysis agent retrieves from session.state and saves KBJU to session.state["kbju_calculation"]
3. Compatibility agent retrieves from session.state

FUTURE USE CASES:
This class could be integrated to provide:
- Persistent user profiles across sessions
- Historical KBJU tracking
- Meal plan history
- Long-term nutritional progress tracking

Based on ADK memory patterns (Day 3b - Agent Memory).

This file is kept for future enhancement.
"""

import sqlite3
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
import os


class MemoryBank:
    """
    Memory Bank for storing user nutrition data and consultation history.

    Uses SQLite for local persistence. In production, this could be
    replaced with a cloud database (PostgreSQL, MongoDB, etc.)
    """

    def __init__(self, db_path: str = "nutrition_memory.db"):
        """
        Initialize the Memory Bank with a database connection.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._init_database()

    def _init_database(self):
        """Create database tables if they don't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # User profiles table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_profiles (
                user_id TEXT PRIMARY KEY,
                created_at TEXT,
                updated_at TEXT,
                profile_data TEXT
            )
        """)

        # Consultation history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS consultations (
                consultation_id TEXT PRIMARY KEY,
                user_id TEXT,
                session_id TEXT,
                created_at TEXT,
                completed_at TEXT,
                stage TEXT,
                consultation_data TEXT,
                FOREIGN KEY (user_id) REFERENCES user_profiles(user_id)
            )
        """)

        # KBJU calculations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS kbju_calculations (
                calculation_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                consultation_id TEXT,
                calculated_at TEXT,
                bmr REAL,
                tdee REAL,
                target_calories REAL,
                protein_g REAL,
                fat_g REAL,
                carbs_g REAL,
                goal TEXT,
                calculation_data TEXT,
                FOREIGN KEY (user_id) REFERENCES user_profiles(user_id)
            )
        """)

        # Meal plans table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS meal_plans (
                plan_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                consultation_id TEXT,
                created_at TEXT,
                plan_type TEXT,
                duration_days INTEGER,
                plan_data TEXT,
                FOREIGN KEY (user_id) REFERENCES user_profiles(user_id)
            )
        """)

        conn.commit()
        conn.close()

    # ==================== User Profile Methods ====================

    def save_user_profile(self, user_id: str, profile_data: Dict) -> bool:
        """
        Save or update user profile.

        Args:
            user_id: Unique user identifier
            profile_data: Dictionary containing user information

        Returns:
            True if successful, False otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            now = datetime.utcnow().isoformat()
            profile_json = json.dumps(profile_data)

            # Check if profile exists
            cursor.execute(
                "SELECT user_id FROM user_profiles WHERE user_id = ?",
                (user_id,)
            )
            exists = cursor.fetchone() is not None

            if exists:
                # Update existing profile
                cursor.execute("""
                    UPDATE user_profiles
                    SET updated_at = ?, profile_data = ?
                    WHERE user_id = ?
                """, (now, profile_json, user_id))
            else:
                # Create new profile
                cursor.execute("""
                    INSERT INTO user_profiles (user_id, created_at, updated_at, profile_data)
                    VALUES (?, ?, ?, ?)
                """, (user_id, now, now, profile_json))

            conn.commit()
            conn.close()
            return True

        except Exception as e:
            print(f"Error saving user profile: {e}")
            return False

    def get_user_profile(self, user_id: str) -> Optional[Dict]:
        """
        Retrieve user profile.

        Args:
            user_id: User identifier

        Returns:
            Profile data dictionary or None if not found
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                "SELECT profile_data FROM user_profiles WHERE user_id = ?",
                (user_id,)
            )
            result = cursor.fetchone()
            conn.close()

            if result:
                return json.loads(result[0])
            return None

        except Exception as e:
            print(f"Error retrieving user profile: {e}")
            return None

    # ==================== Consultation Methods ====================

    def save_consultation(
        self,
        consultation_id: str,
        user_id: str,
        session_id: str,
        consultation_data: Dict,
        stage: str = "interview"
    ) -> bool:
        """
        Save consultation data.

        Args:
            consultation_id: Unique consultation identifier
            user_id: User identifier
            session_id: Session identifier
            consultation_data: Consultation information
            stage: Current consultation stage

        Returns:
            True if successful
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            now = datetime.utcnow().isoformat()
            data_json = json.dumps(consultation_data)

            cursor.execute("""
                INSERT OR REPLACE INTO consultations
                (consultation_id, user_id, session_id, created_at, stage, consultation_data)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (consultation_id, user_id, session_id, now, stage, data_json))

            conn.commit()
            conn.close()
            return True

        except Exception as e:
            print(f"Error saving consultation: {e}")
            return False

    def update_consultation_stage(
        self,
        consultation_id: str,
        stage: str,
        data_update: Optional[Dict] = None
    ) -> bool:
        """
        Update consultation stage and optionally merge new data.

        Args:
            consultation_id: Consultation identifier
            stage: New stage
            data_update: Additional data to merge

        Returns:
            True if successful
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            if data_update:
                # Get existing data and merge
                cursor.execute(
                    "SELECT consultation_data FROM consultations WHERE consultation_id = ?",
                    (consultation_id,)
                )
                result = cursor.fetchone()
                if result:
                    existing_data = json.loads(result[0])
                    existing_data.update(data_update)
                    data_json = json.dumps(existing_data)

                    cursor.execute("""
                        UPDATE consultations
                        SET stage = ?, consultation_data = ?
                        WHERE consultation_id = ?
                    """, (stage, data_json, consultation_id))
            else:
                cursor.execute("""
                    UPDATE consultations
                    SET stage = ?
                    WHERE consultation_id = ?
                """, (stage, consultation_id))

            conn.commit()
            conn.close()
            return True

        except Exception as e:
            print(f"Error updating consultation: {e}")
            return False

    def get_consultation(self, consultation_id: str) -> Optional[Dict]:
        """
        Retrieve consultation data.

        Args:
            consultation_id: Consultation identifier

        Returns:
            Consultation data or None
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT user_id, session_id, created_at, stage, consultation_data
                FROM consultations
                WHERE consultation_id = ?
            """, (consultation_id,))

            result = cursor.fetchone()
            conn.close()

            if result:
                return {
                    "user_id": result[0],
                    "session_id": result[1],
                    "created_at": result[2],
                    "stage": result[3],
                    "data": json.loads(result[4])
                }
            return None

        except Exception as e:
            print(f"Error retrieving consultation: {e}")
            return None

    # ==================== KBJU Calculation Methods ====================

    def save_kbju_calculation(
        self,
        user_id: str,
        consultation_id: str,
        calculation_result: Dict
    ) -> bool:
        """
        Save KBJU calculation results.

        Args:
            user_id: User identifier
            consultation_id: Consultation identifier
            calculation_result: Result from calculate_kbju tool

        Returns:
            True if successful
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            now = datetime.utcnow().isoformat()
            calc_json = json.dumps(calculation_result)

            cursor.execute("""
                INSERT INTO kbju_calculations
                (user_id, consultation_id, calculated_at, bmr, tdee, target_calories,
                 protein_g, fat_g, carbs_g, goal, calculation_data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                consultation_id,
                now,
                calculation_result.get("bmr"),
                calculation_result.get("tdee"),
                calculation_result.get("target_calories"),
                calculation_result.get("protein_g"),
                calculation_result.get("fat_g"),
                calculation_result.get("carbs_g"),
                calculation_result.get("goal", "maintenance"),
                calc_json
            ))

            conn.commit()
            conn.close()
            return True

        except Exception as e:
            print(f"Error saving KBJU calculation: {e}")
            return False

    def get_latest_kbju(self, user_id: str) -> Optional[Dict]:
        """
        Get the most recent KBJU calculation for a user.

        Args:
            user_id: User identifier

        Returns:
            Latest KBJU calculation or None
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT calculation_data
                FROM kbju_calculations
                WHERE user_id = ?
                ORDER BY calculated_at DESC
                LIMIT 1
            """, (user_id,))

            result = cursor.fetchone()
            conn.close()

            if result:
                return json.loads(result[0])
            return None

        except Exception as e:
            print(f"Error retrieving KBJU: {e}")
            return None

    # ==================== Meal Plan Methods ====================

    def save_meal_plan(
        self,
        user_id: str,
        consultation_id: str,
        plan_data: Dict,
        plan_type: str = "weekly",
        duration_days: int = 7
    ) -> bool:
        """
        Save a meal plan.

        Args:
            user_id: User identifier
            consultation_id: Consultation identifier
            plan_data: Meal plan data
            plan_type: Type of plan (daily, weekly, custom)
            duration_days: Duration in days

        Returns:
            True if successful
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            now = datetime.utcnow().isoformat()
            plan_json = json.dumps(plan_data)

            cursor.execute("""
                INSERT INTO meal_plans
                (user_id, consultation_id, created_at, plan_type, duration_days, plan_data)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user_id, consultation_id, now, plan_type, duration_days, plan_json))

            conn.commit()
            conn.close()
            return True

        except Exception as e:
            print(f"Error saving meal plan: {e}")
            return False

    def get_latest_meal_plan(self, user_id: str) -> Optional[Dict]:
        """
        Get the most recent meal plan for a user.

        Args:
            user_id: User identifier

        Returns:
            Latest meal plan or None
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT plan_data, plan_type, duration_days, created_at
                FROM meal_plans
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT 1
            """, (user_id,))

            result = cursor.fetchone()
            conn.close()

            if result:
                return {
                    "plan": json.loads(result[0]),
                    "type": result[1],
                    "duration_days": result[2],
                    "created_at": result[3]
                }
            return None

        except Exception as e:
            print(f"Error retrieving meal plan: {e}")
            return None
