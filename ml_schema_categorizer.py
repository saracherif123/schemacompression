#!/usr/bin/env python3
"""
Machine Learning Approach for Schema Categorization
Automated schema informativeness assessment using ML features
"""

import re
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.preprocessing import StandardScaler
import pickle
import json
from pathlib import Path

class SchemaFeatureExtractor:
    """Extract features from SQL schemas for ML categorization"""
    
    def __init__(self):
        # Define patterns for feature extraction
        self.generic_patterns = [
            r'\b(data|info|record|table|tbl|temp|tmp|log|file)\b',
            r'^\d+$',  # Pure numbers
            r'^[A-Z]{2,}\d+$',  # Abbreviations like AM001, DOC_REF
        ]
        
        self.descriptive_patterns = [
            r'\b(student|customer|order|product|user|account|transaction)\b',
            r'\b(name|id|date|time|email|phone|address)\b',
            r'\b(create|update|delete|insert|select)\b',
        ]
        
        self.technical_patterns = [
            r'\b(config|param|setting|option|flag|status|state)\b',
            r'\b(system|admin|internal|private|public)\b',
            r'\b(api|http|url|endpoint|service)\b',
        ]
    
    def extract_features(self, schema_content):
        """Extract comprehensive features from schema content"""
        features = {}
        
        # Parse schema to extract components
        tables = self._extract_tables(schema_content)
        columns = self._extract_columns(schema_content)
        foreign_keys = self._extract_foreign_keys(schema_content)
        
        # Naming pattern features
        features['descriptiveness_score'] = self._calculate_descriptiveness(tables, columns)
        features['abbreviation_density'] = self._calculate_abbreviation_density(tables, columns)
        features['generic_name_count'] = self._count_generic_names(tables, columns)
        features['technical_term_ratio'] = self._calculate_technical_ratio(tables, columns)
        
        # Structural features
        features['table_count'] = len(tables)
        features['average_column_count'] = len(columns) / len(tables) if tables else 0
        features['schema_size'] = len(schema_content)
        features['foreign_key_density'] = len(foreign_keys) / len(tables) if tables else 0
        
        # Semantic features
        features['domain_coherence'] = self._calculate_domain_coherence(tables)
        features['context_richness'] = self._calculate_context_richness(tables, columns)
        
        return features
    
    def _extract_tables(self, schema_content):
        """Extract table names from CREATE TABLE statements"""
        pattern = r'CREATE\s+TABLE\s+["]?(\w+)["]?\s*\('
        return re.findall(pattern, schema_content, re.IGNORECASE)
    
    def _extract_columns(self, schema_content):
        """Extract column names from schema"""
        pattern = r'CREATE\s+TABLE\s+["]?(\w+)["]?\s*\((.*?)\)\s*;'
        matches = re.findall(pattern, schema_content, re.IGNORECASE | re.DOTALL)
        
        columns = []
        for table_name, column_block in matches:
            # Extract column names from column block
            column_pattern = r'["]?(\w+)["]?\s+'
            table_columns = re.findall(column_pattern, column_block)
            columns.extend(table_columns)
        
        return columns
    
    def _extract_foreign_keys(self, schema_content):
        """Extract foreign key constraints"""
        pattern = r'FOREIGN\s+KEY\s+\([^)]+\)\s+REFERENCES\s+(\w+)'
        return re.findall(pattern, schema_content, re.IGNORECASE)
    
    def _calculate_descriptiveness(self, tables, columns):
        """Calculate descriptiveness score based on naming patterns"""
        all_names = tables + columns
        if not all_names:
            return 0.0
        
        descriptive_count = 0
        for name in all_names:
            if any(re.search(pattern, name, re.IGNORECASE) for pattern in self.descriptive_patterns):
                descriptive_count += 1
        
        return descriptive_count / len(all_names)
    
    def _calculate_abbreviation_density(self, tables, columns):
        """Calculate density of abbreviated names"""
        all_names = tables + columns
        if not all_names:
            return 0.0
        
        abbreviated_count = 0
        for name in all_names:
            if any(re.search(pattern, name, re.IGNORECASE) for pattern in self.generic_patterns):
                abbreviated_count += 1
        
        return abbreviated_count / len(all_names)
    
    def _count_generic_names(self, tables, columns):
        """Count generic names like data, info, record"""
        all_names = tables + columns
        generic_count = 0
        
        for name in all_names:
            if re.search(r'\b(data|info|record|table|tbl|temp|tmp)\b', name, re.IGNORECASE):
                generic_count += 1
        
        return generic_count
    
    def _calculate_technical_ratio(self, tables, columns):
        """Calculate ratio of technical terms"""
        all_names = tables + columns
        if not all_names:
            return 0.0
        
        technical_count = 0
        for name in all_names:
            if any(re.search(pattern, name, re.IGNORECASE) for pattern in self.technical_patterns):
                technical_count += 1
        
        return technical_count / len(all_names)
    
    def _calculate_domain_coherence(self, tables):
        """Calculate domain coherence across tables"""
        if len(tables) < 2:
            return 0.0
        
        # Simple coherence based on common word patterns
        all_words = []
        for table in tables:
            words = re.findall(r'\w+', table.lower())
            all_words.extend(words)
        
        if not all_words:
            return 0.0
        
        # Calculate word frequency
        word_freq = {}
        for word in all_words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Coherence is based on common words across tables
        common_words = sum(1 for freq in word_freq.values() if freq > 1)
        return common_words / len(set(all_words)) if all_words else 0.0
    
    def _calculate_context_richness(self, tables, columns):
        """Calculate context richness of schema"""
        all_names = tables + columns
        if not all_names:
            return 0.0
        
        # Context richness based on word diversity and length
        total_words = 0
        unique_words = set()
        
        for name in all_names:
            words = re.findall(r'\w+', name.lower())
            total_words += len(words)
            unique_words.update(words)
        
        if total_words == 0:
            return 0.0
        
        # Richness = unique words / total words * average word length
        word_diversity = len(unique_words) / total_words
        avg_word_length = sum(len(word) for word in unique_words) / len(unique_words) if unique_words else 0
        
        return word_diversity * (avg_word_length / 10)  # Normalize by 10

class SchemaCategorizer:
    """Machine learning model for schema categorization"""
    
    def __init__(self):
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            class_weight='balanced'
        )
        self.scaler = StandardScaler()
        self.feature_extractor = SchemaFeatureExtractor()
        self.is_trained = False
    
    def prepare_training_data(self, schema_data):
        """Prepare training data from schema performance data"""
        features_list = []
        labels = []
        
        for schema_name, performance_data in schema_data.items():
            # Extract features
            features = self.feature_extractor.extract_features(performance_data['schema_content'])
            features_list.append(list(features.values()))
            
            # Determine label based on success rate
            success_rate = performance_data['success_rate']
            if success_rate >= 0.6:
                label = 'High'
            elif success_rate >= 0.2:
                label = 'Medium'
            elif success_rate >= 0.05:
                label = 'Low'
            else:
                label = 'Failure'
            
            labels.append(label)
        
        return np.array(features_list), np.array(labels)
    
    def train(self, X, y):
        """Train the categorization model"""
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train model
        self.model.fit(X_scaled, y)
        self.is_trained = True
        
        # Cross-validation
        cv_scores = cross_val_score(self.model, X_scaled, y, cv=5)
        print(f"Cross-validation accuracy: {cv_scores.mean():.3f} (+/- {cv_scores.std() * 2:.3f})")
        
        return cv_scores
    
    def predict(self, schema_content):
        """Predict schema category"""
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")
        
        # Extract features
        features = self.feature_extractor.extract_features(schema_content)
        features_array = np.array([list(features.values())])
        
        # Scale features
        features_scaled = self.scaler.transform(features_array)
        
        # Predict
        prediction = self.model.predict(features_scaled)[0]
        confidence = self.model.predict_proba(features_scaled).max()
        
        return prediction, confidence
    
    def get_feature_importance(self):
        """Get feature importance from trained model"""
        if not self.is_trained:
            raise ValueError("Model must be trained first")
        
        feature_names = [
            'descriptiveness_score', 'abbreviation_density', 'generic_name_count',
            'technical_term_ratio', 'table_count', 'average_column_count',
            'schema_size', 'foreign_key_density', 'domain_coherence', 'context_richness'
        ]
        
        importance = self.model.feature_importances_
        return dict(zip(feature_names, importance))
    
    def save_model(self, filepath):
        """Save trained model"""
        if not self.is_trained:
            raise ValueError("Model must be trained before saving")
        
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_names': [
                'descriptiveness_score', 'abbreviation_density', 'generic_name_count',
                'technical_term_ratio', 'table_count', 'average_column_count',
                'schema_size', 'foreign_key_density', 'domain_coherence', 'context_richness'
            ]
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)
    
    def load_model(self, filepath):
        """Load trained model"""
        with open(filepath, 'rb') as f:
            model_data = pickle.load(f)
        
        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.is_trained = True

def assess_schema_informativeness(schema_file, model_path=None):
    """
    Automatically assess schema informativeness using ML model
    """
    # Load schema content
    with open(schema_file, 'r') as f:
        schema_content = f.read()
    
    # Initialize categorizer
    categorizer = SchemaCategorizer()
    
    if model_path and Path(model_path).exists():
        # Load pre-trained model
        categorizer.load_model(model_path)
    else:
        print("No pre-trained model found. Training new model...")
        # This would require training data - in practice, you'd load this
        raise ValueError("Pre-trained model required for assessment")
    
    # Predict category
    category, confidence = categorizer.predict(schema_content)
    
    # Get recommendations
    recommendations = {
        'High': 'SIMPLE (76.5% token reduction)',
        'Medium': 'GREEDY (35.5% token reduction)', 
        'Low': 'PROMPT (21.7% token reduction)',
        'Failure': 'Full schema or schema redesign'
    }
    
    expected_success = {
        'High': 60.2,
        'Medium': 25.8,
        'Low': 8.4,
        'Failure': 0.0
    }
    
    return {
        'category': category,
        'confidence': confidence,
        'recommended_method': recommendations[category],
        'expected_success_rate': expected_success[category]
    }

def main():
    """Example usage"""
    # Example schema content
    example_schema = """
    CREATE TABLE students (
        student_id INT PRIMARY KEY,
        student_name VARCHAR(100),
        email VARCHAR(100),
        enrollment_date DATE
    );
    
    CREATE TABLE courses (
        course_id INT PRIMARY KEY,
        course_name VARCHAR(100),
        instructor VARCHAR(100),
        credits INT
    );
    
    CREATE TABLE enrollments (
        enrollment_id INT PRIMARY KEY,
        student_id INT,
        course_id INT,
        grade VARCHAR(2),
        FOREIGN KEY (student_id) REFERENCES students(student_id),
        FOREIGN KEY (course_id) REFERENCES courses(course_id)
    );
    """
    
    # Test feature extraction
    extractor = SchemaFeatureExtractor()
    features = extractor.extract_features(example_schema)
    
    print("Schema Features:")
    for feature, value in features.items():
        print(f"  {feature}: {value:.3f}")
    
    print("\nThis schema would likely be categorized as 'High' informativeness")
    print("Recommended method: SIMPLE compression (76.5% token reduction)")
    print("Expected success rate: ~60.2%")

if __name__ == "__main__":
    main()
