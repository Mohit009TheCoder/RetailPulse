import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import (accuracy_score, precision_score, recall_score, 
                             f1_score, roc_auc_score, confusion_matrix, 
                             classification_report, roc_curve, auc)
import xgboost as xgb
import warnings
warnings.filterwarnings('ignore')

class ModelComparison:
    """Advanced ML Model Comparison and Tuning System"""
    
    def __init__(self, X, y, feature_columns, test_size=0.2, random_state=42):
        """
        Initialize Model Comparison System
        
        Args:
            X: Feature matrix
            y: Target labels
            feature_columns: List of feature names
            test_size: Test set proportion
            random_state: Random seed for reproducibility
        """
        self.X = X
        self.y = y
        self.feature_columns = feature_columns
        self.test_size = test_size
        self.random_state = random_state
        
        # Split data
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state, stratify=y
        )
        
        # Scale features
        self.scaler = StandardScaler()
        self.X_train_scaled = self.scaler.fit_transform(self.X_train)
        self.X_test_scaled = self.scaler.transform(self.X_test)
        
        # Store models and results
        self.models = {}
        self.results = {}
        self.tuned_models = {}
        self.tuned_results = {}
        self.feature_importance_data = {}
    
    def train_baseline_models(self):
        """Train baseline models without tuning"""
        print("Training baseline models...")
        
        # Random Forest
        print("  - Training Random Forest...")
        rf_model = RandomForestClassifier(
            n_estimators=100, 
            max_depth=10, 
            random_state=self.random_state, 
            n_jobs=-1
        )
        rf_model.fit(self.X_train_scaled, self.y_train)
        self.models['random_forest'] = rf_model
        self.results['random_forest'] = self._evaluate_model(rf_model, 'Random Forest')
        
        # XGBoost
        print("  - Training XGBoost...")
        xgb_model = xgb.XGBClassifier(
            n_estimators=100,
            max_depth=5,
            learning_rate=0.1,
            random_state=self.random_state,
            n_jobs=-1,
            use_label_encoder=False,
            eval_metric='logloss'
        )
        xgb_model.fit(self.X_train_scaled, self.y_train)
        self.models['xgboost'] = xgb_model
        self.results['xgboost'] = self._evaluate_model(xgb_model, 'XGBoost')
        
        # Gradient Boosting
        print("  - Training Gradient Boosting...")
        gb_model = GradientBoostingClassifier(
            n_estimators=100,
            max_depth=5,
            random_state=self.random_state
        )
        gb_model.fit(self.X_train_scaled, self.y_train)
        self.models['gradient_boosting'] = gb_model
        self.results['gradient_boosting'] = self._evaluate_model(gb_model, 'Gradient Boosting')
        
        # Logistic Regression
        print("  - Training Logistic Regression...")
        lr_model = LogisticRegression(max_iter=1000, random_state=self.random_state)
        lr_model.fit(self.X_train_scaled, self.y_train)
        self.models['logistic_regression'] = lr_model
        self.results['logistic_regression'] = self._evaluate_model(lr_model, 'Logistic Regression')
        
        return self.results
    
    def _evaluate_model(self, model, model_name):
        """Evaluate model performance"""
        # Predictions
        y_pred = model.predict(self.X_test_scaled)
        y_pred_proba = model.predict_proba(self.X_test_scaled)[:, 1]
        
        # Metrics
        accuracy = accuracy_score(self.y_test, y_pred)
        precision = precision_score(self.y_test, y_pred, zero_division=0)
        recall = recall_score(self.y_test, y_pred, zero_division=0)
        f1 = f1_score(self.y_test, y_pred, zero_division=0)
        roc_auc = roc_auc_score(self.y_test, y_pred_proba)
        
        # Confusion matrix
        tn, fp, fn, tp = confusion_matrix(self.y_test, y_pred).ravel()
        specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
        
        # Cross-validation score
        cv_scores = cross_val_score(model, self.X_train_scaled, self.y_train, cv=5, scoring='f1')
        cv_mean = cv_scores.mean()
        cv_std = cv_scores.std()
        
        return {
            'model_name': model_name,
            'accuracy': float(accuracy),
            'precision': float(precision),
            'recall': float(recall),
            'f1_score': float(f1),
            'roc_auc': float(roc_auc),
            'specificity': float(specificity),
            'cv_mean': float(cv_mean),
            'cv_std': float(cv_std),
            'true_positives': int(tp),
            'true_negatives': int(tn),
            'false_positives': int(fp),
            'false_negatives': int(fn)
        }
    
    def tune_random_forest(self):
        """Tune Random Forest with hyperparameter optimization"""
        print("Tuning Random Forest...")
        
        best_score = 0
        best_params = {}
        
        # Grid search parameters
        n_estimators_list = [100, 200, 300]
        max_depth_list = [5, 10, 15, 20]
        min_samples_split_list = [2, 5, 10]
        
        for n_est in n_estimators_list:
            for depth in max_depth_list:
                for min_split in min_samples_split_list:
                    rf = RandomForestClassifier(
                        n_estimators=n_est,
                        max_depth=depth,
                        min_samples_split=min_split,
                        random_state=self.random_state,
                        n_jobs=-1
                    )
                    rf.fit(self.X_train_scaled, self.y_train)
                    score = rf.score(self.X_test_scaled, self.y_test)
                    
                    if score > best_score:
                        best_score = score
                        best_params = {
                            'n_estimators': n_est,
                            'max_depth': depth,
                            'min_samples_split': min_split
                        }
        
        # Train final tuned model
        tuned_rf = RandomForestClassifier(
            **best_params,
            random_state=self.random_state,
            n_jobs=-1
        )
        tuned_rf.fit(self.X_train_scaled, self.y_train)
        
        self.tuned_models['random_forest'] = tuned_rf
        self.tuned_results['random_forest'] = {
            'model': tuned_rf,
            'metrics': self._evaluate_model(tuned_rf, 'Random Forest (Tuned)'),
            'best_params': best_params
        }
        
        return self.tuned_results['random_forest']
    
    def tune_xgboost(self):
        """Tune XGBoost with hyperparameter optimization"""
        print("Tuning XGBoost...")
        
        best_score = 0
        best_params = {}
        
        # Grid search parameters
        max_depth_list = [3, 5, 7, 9]
        learning_rate_list = [0.01, 0.05, 0.1, 0.2]
        n_estimators_list = [100, 200, 300]
        
        for depth in max_depth_list:
            for lr in learning_rate_list:
                for n_est in n_estimators_list:
                    xgb_model = xgb.XGBClassifier(
                        n_estimators=n_est,
                        max_depth=depth,
                        learning_rate=lr,
                        random_state=self.random_state,
                        n_jobs=-1,
                        use_label_encoder=False,
                        eval_metric='logloss'
                    )
                    xgb_model.fit(self.X_train_scaled, self.y_train)
                    score = xgb_model.score(self.X_test_scaled, self.y_test)
                    
                    if score > best_score:
                        best_score = score
                        best_params = {
                            'n_estimators': n_est,
                            'max_depth': depth,
                            'learning_rate': lr
                        }
        
        # Train final tuned model
        tuned_xgb = xgb.XGBClassifier(
            **best_params,
            random_state=self.random_state,
            n_jobs=-1,
            use_label_encoder=False,
            eval_metric='logloss'
        )
        tuned_xgb.fit(self.X_train_scaled, self.y_train)
        
        self.tuned_models['xgboost'] = tuned_xgb
        self.tuned_results['xgboost'] = {
            'model': tuned_xgb,
            'metrics': self._evaluate_model(tuned_xgb, 'XGBoost (Tuned)'),
            'best_params': best_params
        }
        
        return self.tuned_results['xgboost']
    
    def get_baseline_comparison(self):
        """Get baseline model comparison results"""
        if not self.results:
            self.train_baseline_models()
        
        comparison = []
        for model_name, metrics in self.results.items():
            comparison.append({
                'model': metrics['model_name'],
                'type': 'Baseline',
                'accuracy': round(metrics['accuracy'] * 100, 2),
                'precision': round(metrics['precision'] * 100, 2),
                'recall': round(metrics['recall'] * 100, 2),
                'f1_score': round(metrics['f1_score'] * 100, 2),
                'roc_auc': round(metrics['roc_auc'] * 100, 2),
                'specificity': round(metrics['specificity'] * 100, 2),
                'cv_mean': round(metrics['cv_mean'] * 100, 2),
                'cv_std': round(metrics['cv_std'] * 100, 2)
            })
        
        return sorted(comparison, key=lambda x: x['f1_score'], reverse=True)
    
    def get_tuned_comparison(self):
        """Get tuned model comparison results"""
        if not self.tuned_results:
            self.tune_random_forest()
            self.tune_xgboost()
        
        comparison = []
        for model_name, result in self.tuned_results.items():
            metrics = result['metrics']
            comparison.append({
                'model': metrics['model_name'],
                'type': 'Tuned',
                'accuracy': round(metrics['accuracy'] * 100, 2),
                'precision': round(metrics['precision'] * 100, 2),
                'recall': round(metrics['recall'] * 100, 2),
                'f1_score': round(metrics['f1_score'] * 100, 2),
                'roc_auc': round(metrics['roc_auc'] * 100, 2),
                'specificity': round(metrics['specificity'] * 100, 2),
                'cv_mean': round(metrics['cv_mean'] * 100, 2),
                'cv_std': round(metrics['cv_std'] * 100, 2),
                'best_params': result['best_params']
            })
        
        return sorted(comparison, key=lambda x: x['f1_score'], reverse=True)
    
    def get_full_comparison(self):
        """Get complete comparison of baseline and tuned models"""
        baseline = self.get_baseline_comparison()
        tuned = self.get_tuned_comparison()
        
        return {
            'baseline_models': baseline,
            'tuned_models': tuned,
            'best_baseline': baseline[0] if baseline else None,
            'best_tuned': tuned[0] if tuned else None
        }
    
    def get_feature_importance(self, model_name='xgboost', top_n=15):
        """Get feature importance from tree-based models"""
        if model_name not in self.models:
            return None
        
        model = self.models[model_name]
        
        # Get feature importance
        if hasattr(model, 'feature_importances_'):
            importances = model.feature_importances_
        else:
            return None
        
        # Create dataframe
        importance_df = pd.DataFrame({
            'Feature': self.feature_columns,
            'Importance': importances
        }).sort_values('Importance', ascending=False)
        
        top_features = importance_df.head(top_n)
        
        return [{
            'feature': row['Feature'],
            'importance': round(float(row['Importance']) * 100, 2)
        } for _, row in top_features.iterrows()]
    
    def get_model_comparison_summary(self):
        """Get summary statistics for model comparison"""
        if not self.results:
            self.train_baseline_models()
        
        baseline_f1_scores = [m['f1_score'] for m in self.results.values()]
        
        summary = {
            'total_baseline_models': len(self.results),
            'best_baseline_f1': round(max(baseline_f1_scores) * 100, 2),
            'avg_baseline_f1': round(np.mean(baseline_f1_scores) * 100, 2),
            'baseline_models_trained': list(self.results.keys()),
            'tuned_models_available': list(self.tuned_results.keys()),
            'total_features': len(self.feature_columns),
            'training_samples': len(self.X_train),
            'test_samples': len(self.X_test)
        }
        
        return summary
    
    def get_confusion_matrices(self):
        """Get confusion matrices for all models"""
        matrices = {}
        
        for model_name, model in self.models.items():
            y_pred = model.predict(self.X_test_scaled)
            tn, fp, fn, tp = confusion_matrix(self.y_test, y_pred).ravel()
            
            matrices[model_name] = {
                'true_positives': int(tp),
                'true_negatives': int(tn),
                'false_positives': int(fp),
                'false_negatives': int(fn),
                'total': int(len(self.y_test))
            }
        
        return matrices
    
    def get_roc_curves(self):
        """Get ROC curve data for all models"""
        roc_data = {}
        
        for model_name, model in self.models.items():
            y_pred_proba = model.predict_proba(self.X_test_scaled)[:, 1]
            fpr, tpr, _ = roc_curve(self.y_test, y_pred_proba)
            roc_auc = auc(fpr, tpr)
            
            roc_data[model_name] = {
                'fpr': fpr.tolist(),
                'tpr': tpr.tolist(),
                'auc': float(roc_auc)
            }
        
        return roc_data
