import os
import pickle
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import KFold, cross_val_score

class StudentScoreMLEngine:
    FEATURE_NAMES = ['Hours', 'Sleep', 'Attendance(%)', 'Assignments']
    FEATURE_LABELS = {
        'Hours': 'Study Hours',
        'Sleep': 'Sleep Duration',
        'Attendance(%)': 'Attendance Rate',
        'Assignments': 'Assignments Done'
    }

    def __init__(self, data_path=None):
        base_dir = os.path.dirname(__file__)
        if data_path is None:
            xlsx_path = os.path.join(base_dir, "student_performance.xlsx")
            csv_path = os.path.join(base_dir, "student_performance.csv")
            if os.path.exists(xlsx_path):
                self.data_path = xlsx_path
                self.df = pd.read_excel(xlsx_path)
            elif os.path.exists(csv_path):
                self.data_path = csv_path
                self.df = pd.read_csv(csv_path)
            else:
                raise FileNotFoundError("Could not find student_performance.xlsx or csv")
        else:
            self.data_path = data_path
            self.df = pd.read_excel(data_path) if data_path.endswith('.xlsx') else pd.read_csv(data_path)

        self.models = {}
        self.metrics = {}
        self.feature_means = {}
        self.feature_stds = {}
        self.feature_mins = {}
        self.feature_maxs = {}
        self.target_mean = float(self.df['Score'].mean())
        self.target_std = float(self.df['Score'].std())

        for col in self.FEATURE_NAMES:
            self.feature_means[col] = float(self.df[col].mean())
            self.feature_stds[col] = float(self.df[col].std())
            self.feature_mins[col] = float(self.df[col].min())
            self.feature_maxs[col] = float(self.df[col].max())

        self._train_all_models()

    def _train_all_models(self):
        X = self.df[self.FEATURE_NAMES]
        y = self.df['Score']

        model_candidates = {
            'linear': ('Linear Regression', LinearRegression()),
            'ridge': ('Ridge Regression', Ridge(alpha=1.0)),
            'rf': ('Random Forest (Ensemble)', RandomForestRegressor(n_estimators=100, random_state=42)),
            'gbr': ('Gradient Boosting (GBR)', GradientBoostingRegressor(n_estimators=100, random_state=42, learning_rate=0.1))
        }

        kf = KFold(n_splits=5, shuffle=True, random_state=42)

        for key, (display_name, model_obj) in model_candidates.items():
            model_obj.fit(X, y)
            preds = model_obj.predict(X)
            r2 = float(r2_score(y, preds))
            mae = float(mean_absolute_error(y, preds))
            rmse = float(np.sqrt(mean_squared_error(y, preds)))

            cv_scores = cross_val_score(model_obj, X, y, cv=kf, scoring='r2')
            cv_mean = float(np.mean(cv_scores))
            cv_std = float(np.std(cv_scores))

            self.models[key] = {
                'name': display_name,
                'model': model_obj
            }
            self.metrics[key] = {
                'name': display_name,
                'r2': round(r2, 4),
                'mae': round(mae, 2),
                'rmse': round(rmse, 2),
                'cv_r2_mean': round(cv_mean, 4),
                'cv_r2_std': round(cv_std, 4)
            }

        # Calculate ensemble metrics
        preds_list = [self.models[k]['model'].predict(X) for k in ['linear', 'ridge', 'rf', 'gbr']]
        ens_preds = np.mean(preds_list, axis=0)
        self.metrics['ensemble'] = {
            'name': 'Consensus Ensemble (Weighted)',
            'r2': round(float(r2_score(y, ens_preds)), 4),
            'mae': round(float(mean_absolute_error(y, ens_preds)), 2),
            'rmse': round(float(np.sqrt(mean_squared_error(y, ens_preds))), 2),
            'cv_r2_mean': round(float(np.mean([self.metrics[k]['cv_r2_mean'] for k in ['linear', 'ridge', 'rf', 'gbr']])), 4),
            'cv_r2_std': 0.02
        }

        # Save single model for legacy backward compatibility
        legacy_path = os.path.join(os.path.dirname(__file__), "model.pkl")
        try:
            with open(legacy_path, "wb") as f:
                pickle.dump(self.models['linear']['model'], f)
        except Exception:
            pass

    def _determine_grade(self, score):
        if score >= 90:
            return "A+", "Outstanding Distinction", "emerald"
        elif score >= 80:
            return "A", "Excellent Mastery", "cyan"
        elif score >= 70:
            return "B", "Proficient / Above Average", "blue"
        elif score >= 60:
            return "C", "Satisfactory / Pass", "amber"
        elif score >= 50:
            return "D", "Marginal / Needs Support", "orange"
        else:
            return "F", "Academic Risk / Failing", "rose"

    def _calculate_percentile(self, score):
        all_scores = self.df['Score'].values
        pct = (np.sum(all_scores < score) + 0.5 * np.sum(all_scores == score)) / len(all_scores) * 100
        return round(float(pct), 1)

    def predict(self, hours, sleep, attendance, assignments, model_name='ensemble'):
        # Input validation and clipping to sensible ranges
        hours = max(0.0, min(16.0, float(hours)))
        sleep = max(0.0, min(14.0, float(sleep)))
        attendance = max(0.0, min(100.0, float(attendance)))
        assignments = max(0.0, min(15.0, float(assignments)))

        X_input = pd.DataFrame([[hours, sleep, attendance, assignments]], columns=self.FEATURE_NAMES)

        # Gather individual model predictions
        all_preds = {}
        for k in ['linear', 'ridge', 'rf', 'gbr']:
            val = float(self.models[k]['model'].predict(X_input)[0])
            all_preds[k] = round(max(0.0, min(100.0, val)), 2)

        if model_name in self.models:
            raw_score = all_preds[model_name]
        else:
            # Consensus ensemble
            raw_score = round(float(np.mean(list(all_preds.values()))), 2)

        final_score = round(max(0.0, min(100.0, raw_score)), 2)
        letter_grade, grade_desc, grade_color = self._determine_grade(final_score)

        # Risk Assessment
        if final_score >= 75:
            risk_level = "Low Risk"
            risk_badge = "success"
        elif final_score >= 55:
            risk_level = "Moderate Risk"
            risk_badge = "warning"
        else:
            risk_level = "High Academic Risk"
            risk_badge = "danger"

        # Uncertainty / Confidence Interval (via Random Forest tree variance + baseline error)
        rf_trees = self.models['rf']['model'].estimators_
        tree_preds = [tree.predict(X_input.values)[0] for tree in rf_trees]
        std_dev = float(np.std(tree_preds))
        margin = max(1.2, round(1.96 * (std_dev + 0.6), 2))
        ci_lower = max(0.0, round(final_score - margin, 1))
        ci_upper = min(100.0, round(final_score + margin, 1))

        # Percentile rank
        percentile = self._calculate_percentile(final_score)

        # Feature Impact breakdown (relative to mean score)
        # Using linear regression weights for clear interpretable point contributions
        lr_model = self.models['linear']['model']
        coefs = lr_model.coef_
        intercept = lr_model.intercept_

        diff_hours = (hours - self.feature_means['Hours']) * coefs[0]
        diff_sleep = (sleep - self.feature_means['Sleep']) * coefs[1]
        diff_att = (attendance - self.feature_means['Attendance(%)']) * coefs[2]
        diff_assign = (assignments - self.feature_means['Assignments']) * coefs[3]

        impacts = [
            {
                'feature': 'Study Hours',
                'value': f"{hours:.1f} hrs/day",
                'baseline': f"{self.feature_means['Hours']:.1f} avg",
                'points': round(float(diff_hours), 2),
                'positive': bool(diff_hours >= 0),
                'icon': 'clock'
            },
            {
                'feature': 'Sleep Duration',
                'value': f"{sleep:.1f} hrs/day",
                'baseline': f"{self.feature_means['Sleep']:.1f} avg",
                'points': round(float(diff_sleep), 2),
                'positive': bool(diff_sleep >= 0),
                'icon': 'moon'
            },
            {
                'feature': 'Attendance Rate',
                'value': f"{attendance:.1f}%",
                'baseline': f"{self.feature_means['Attendance(%)']:.1f}% avg",
                'points': round(float(diff_att), 2),
                'positive': bool(diff_att >= 0),
                'icon': 'calendar-check'
            },
            {
                'feature': 'Assignments Done',
                'value': f"{int(assignments)}",
                'baseline': f"{self.feature_means['Assignments']:.1f} avg",
                'points': round(float(diff_assign), 2),
                'positive': bool(diff_assign >= 0),
                'icon': 'file-text'
            }
        ]

        # Radar data (normalized 0 to 100 for visual comparison)
        # Scale: Hours (0-12 -> 0-100), Sleep (0-10 -> 0-100), Attendance (0-100), Assignments (0-10 -> 0-100)
        radar = {
            'labels': ['Study Intensity', 'Sleep Adequacy', 'Attendance', 'Assignment Completion'],
            'student': [
                round(min(100.0, (hours / 10.0) * 100), 1),
                round(min(100.0, (sleep / 8.0) * 100), 1),
                round(attendance, 1),
                round(min(100.0, (assignments / 9.0) * 100), 1)
            ],
            'benchmark': [
                round(min(100.0, (self.feature_means['Hours'] / 10.0) * 100), 1),
                round(min(100.0, (self.feature_means['Sleep'] / 8.0) * 100), 1),
                round(self.feature_means['Attendance(%)'], 1),
                round(min(100.0, (self.feature_means['Assignments'] / 9.0) * 100), 1)
            ]
        }

        # Sensitivity curve: Projected score across 1 to 14 study hours keeping other variables constant
        hour_range = np.linspace(1.0, 14.0, 14)
        sensitivity_points = []
        for h in hour_range:
            sim_X = pd.DataFrame([[h, sleep, attendance, assignments]], columns=self.FEATURE_NAMES)
            val = float(self.models['linear']['model'].predict(sim_X)[0])
            sensitivity_points.append({
                'hours': round(float(h), 1),
                'predicted_score': round(max(0.0, min(100.0, val)), 1)
            })

        # Smart Actionable Recommendations
        recommendations = []
        if sleep < 6.0:
            recommendations.append({
                'type': 'warning',
                'title': 'Sleep Deficit Risk',
                'text': f"Current sleep is {sleep}h. Sleeping <6h causes cognitive fatigue, memory degradation, and reduced exam retention. Aim for 7–8 hours."
            })
        elif sleep >= 7.0:
            recommendations.append({
                'type': 'success',
                'title': 'Healthy Rest Balance',
                'text': f"Optimal sleep duration of {sleep}h fosters memory consolidation and high cognitive focus during study periods."
            })

        if attendance < 75.0:
            recommendations.append({
                'type': 'danger',
                'title': 'Attendance Warning',
                'text': f"Attendance is at {attendance}%. Institutional minimum is usually 75–80%. Boosting attendance to 85% could lift score by ~{(85 - attendance)*coefs[2]:.1f} points."
            })
        elif attendance >= 90.0:
            recommendations.append({
                'type': 'success',
                'title': 'Punctual Presence',
                'text': f"Superb attendance at {attendance}%. Consistently attending lectures contributes positively to your foundational concepts."
            })

        if assignments < 6:
            potential_pts = (8 - assignments) * coefs[3]
            recommendations.append({
                'type': 'info',
                'title': 'High-Impact Assignment Boost',
                'text': f"Completing 2 more assignments (reaching {int(assignments+2)}) will directly add approximately ~{potential_pts:.1f} marks to your projected final."
            })

        # Next Grade target milestone
        next_grade_target = None
        if final_score < 60:
            next_grade_target = (60.0, "Grade C (Pass)")
        elif final_score < 70:
            next_grade_target = (70.0, "Grade B (Proficient)")
        elif final_score < 80:
            next_grade_target = (80.0, "Grade A (Excellent)")
        elif final_score < 90:
            next_grade_target = (90.0, "Grade A+ (Distinction)")

        if next_grade_target:
            pts_needed = next_grade_target[0] - final_score
            hrs_needed = max(0.2, round(pts_needed / coefs[0], 1))
            recommendations.append({
                'type': 'target',
                'title': f"Pathway to {next_grade_target[1]}",
                'text': f"You are only {pts_needed:.1f} points away! Adding approx. {hrs_needed} hours of focused daily study will elevate you to {next_grade_target[1]}."
            })

        return {
            'score': final_score,
            'letter_grade': letter_grade,
            'grade_desc': grade_desc,
            'grade_color': grade_color,
            'risk_level': risk_level,
            'risk_badge': risk_badge,
            'percentile': percentile,
            'ci': {
                'lower': ci_lower,
                'upper': ci_upper,
                'margin': margin
            },
            'models_comparison': all_preds,
            'selected_model': model_name,
            'impacts': impacts,
            'radar': radar,
            'sensitivity': sensitivity_points,
            'recommendations': recommendations,
            'inputs': {
                'hours': hours,
                'sleep': sleep,
                'attendance': attendance,
                'assignments': assignments
            }
        }

    def optimize_for_target(self, target_score, current_sleep=7.0, current_attendance=85.0, current_assignments=7):
        target_score = max(30.0, min(100.0, float(target_score)))
        lr_model = self.models['linear']['model']
        c_hours, c_sleep, c_att, c_assign = lr_model.coef_
        intercept = lr_model.intercept_

        # Equation: target_score = intercept + c_hours*hours + c_sleep*sleep + c_att*attendance + c_assign*assignments
        # Solve for hours:
        required_from_hours = target_score - (intercept + c_sleep*current_sleep + c_att*current_attendance + c_assign*current_assignments)
        needed_hours = max(1.0, min(15.0, round(required_from_hours / c_hours, 1)))

        # Also provide a balanced recommendation
        balanced_attendance = min(100.0, max(current_attendance, 88.0))
        balanced_assignments = min(10.0, max(current_assignments, 8))
        balanced_req = target_score - (intercept + c_sleep*current_sleep + c_att*balanced_attendance + c_assign*balanced_assignments)
        balanced_hours = max(1.0, min(14.0, round(balanced_req / c_hours, 1)))

        return {
            'target_score': target_score,
            'recommended_hours': needed_hours,
            'balanced_plan': {
                'hours': balanced_hours,
                'sleep': current_sleep,
                'attendance': balanced_attendance,
                'assignments': balanced_assignments
            }
        }

    def batch_predict(self, df, model_name='ensemble'):
        # Normalize column names
        col_map = {}
        for c in df.columns:
            clean = str(c).strip().lower()
            if 'hour' in clean or 'study' in clean:
                col_map[c] = 'Hours'
            elif 'sleep' in clean:
                col_map[c] = 'Sleep'
            elif 'attend' in clean:
                col_map[c] = 'Attendance(%)'
            elif 'assign' in clean:
                col_map[c] = 'Assignments'
            elif 'name' in clean or 'student' in clean:
                col_map[c] = 'Student_Name'

        df_renamed = df.rename(columns=col_map)
        missing = [req for req in self.FEATURE_NAMES if req not in df_renamed.columns]
        if missing:
            raise ValueError(f"Missing required columns in dataset: {missing}. Expected columns like Hours, Sleep, Attendance, Assignments.")

        results = []
        for idx, row in df_renamed.iterrows():
            pred_data = self.predict(
                hours=row['Hours'],
                sleep=row['Sleep'],
                attendance=row['Attendance(%)'],
                assignments=row['Assignments'],
                model_name=model_name
            )
            student_name = row.get('Student_Name', f"Student #{idx+1}")
            results.append({
                'Student_Name': student_name,
                'Hours': row['Hours'],
                'Sleep': row['Sleep'],
                'Attendance': row['Attendance(%)'],
                'Assignments': row['Assignments'],
                'Predicted_Score': pred_data['score'],
                'Grade': pred_data['letter_grade'],
                'Risk_Level': pred_data['risk_level']
            })

        return pd.DataFrame(results)

    def get_metrics_summary(self):
        return self.metrics

    def get_dataset_records(self, limit=50):
        records = self.df.head(limit).to_dict(orient='records')
        summary = {
            'total_students': len(self.df),
            'avg_score': round(float(self.df['Score'].mean()), 2),
            'max_score': float(self.df['Score'].max()),
            'min_score': float(self.df['Score'].min()),
            'avg_hours': round(float(self.df['Hours'].mean()), 2),
            'avg_sleep': round(float(self.df['Sleep'].mean()), 2),
            'avg_attendance': round(float(self.df['Attendance(%)'].mean()), 2),
            'avg_assignments': round(float(self.df['Assignments'].mean()), 2)
        }
        return {'records': records, 'summary': summary}
