import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import json

class EmotionAnalyzer:
    def __init__(self, data):
        self.data = data
        self.df = self._process_data()

    def _process_data(self):
        records = []
        for entry in self.data["emotion_history_20s"]:
            timestamp = pd.to_datetime(entry["timestamp"])
            emotions = entry["emotion_percentage"]
            record = {"timestamp": timestamp, **emotions}
            records.append(record)
        return pd.DataFrame(records)

    def get_processed_data(self):
        return self.df

    def get_emotion_statistics(self):
        # Calculate mean percentage for each emotion
        emotion_means = self.df[["happy", "neutral", "sad"]].mean().to_dict()

        # Calculate overall percentage of each emotion across all timestamps
        total_percentages = self.df[["happy", "neutral", "sad"]].sum().sum()
        emotion_overall_percentages = {}
        for emotion in ["happy", "neutral", "sad"]:
            emotion_overall_percentages[emotion] = (self.df[emotion].sum() / total_percentages) * 100 if total_percentages > 0 else 0

        # Identify most and least common emotions based on overall percentage
        most_common_emotion = max(emotion_overall_percentages, key=emotion_overall_percentages.get)
        least_common_emotion = min(emotion_overall_percentages, key=emotion_overall_percentages.get)

        # Calculate standard deviation for each emotion
        emotion_std_dev = self.df[["happy", "neutral", "sad"]].std().to_dict()

        return {
            "mean_percentages": emotion_means,
            "overall_percentages": emotion_overall_percentages,
            "most_common_emotion": most_common_emotion,
            "least_common_emotion": least_common_emotion,
            "standard_deviations": emotion_std_dev
        }

    def get_emotion_distribution(self):
        # This method can be used to get the raw distribution for plotting
        return self.df[["happy", "neutral", "sad"]]

    def get_temporal_analysis(self):
        # Calculate the rate of change for each emotion
        self.df["time_diff"] = self.df["timestamp"].diff().dt.total_seconds()
        self.df["happy_change"] = self.df["happy"].diff() / self.df["time_diff"]
        self.df["neutral_change"] = self.df["neutral"].diff() / self.df["time_diff"]
        self.df["sad_change"] = self.df["sad"].diff() / self.df["time_diff"]

        # Drop the first row which will have NaN for diff calculations
        temporal_df = self.df.dropna(subset=["time_diff"])

        return temporal_df[["timestamp", "happy_change", "neutral_change", "sad_change"]]

    def plot_emotion_distribution(self, filename="emotion_distribution.png"):
        emotion_data = self.df[["happy", "neutral", "sad"]]
        plt.figure(figsize=(10, 6))
        sns.boxplot(data=emotion_data)
        plt.title("توزيع المشاعر", fontname="Noto Sans Arabic")
        plt.xlabel("العاطفة", fontname="Noto Sans Arabic")
        plt.ylabel("النسبة المئوية", fontname="Noto Sans Arabic")
        plt.savefig(filename)
        plt.close()
        return filename

    def plot_temporal_emotions(self, filename="temporal_emotions.png"):
        plt.figure(figsize=(12, 7))
        plt.plot(self.df["timestamp"], self.df["happy"], label="سعيد")
        plt.plot(self.df["timestamp"], self.df["neutral"], label="محايد")
        plt.plot(self.df["timestamp"], self.df["sad"], label="حزين")
        plt.title("تغير المشاعر بمرور الوقت", fontname="Noto Sans Arabic")
        plt.xlabel("الوقت", fontname="Noto Sans Arabic")
        plt.ylabel("النسبة المئوية", fontname="Noto Sans Arabic")
        plt.legend(prop={'family':'Noto Sans Arabic'}) # Set font for legend
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(filename)
        plt.close()
        return filename

    def identify_patterns(self):
        # For simplicity, let\'s identify if any emotion consistently increases or decreases
        # This is a basic pattern identification, more complex patterns would require more data and advanced algorithms
        patterns = {}
        for emotion in ["happy", "neutral", "sad"]:
            # Check for consistent increase
            if all(self.df[emotion].diff().dropna() >= 0):
                patterns[emotion] = "Consistent Increase"
            # Check for consistent decrease
            elif all(self.df[emotion].diff().dropna() <= 0):
                patterns[emotion] = "Consistent Decrease"
            else:
                patterns[emotion] = "No obvious consistent pattern"
        return patterns

    def predict_emotions(self):
        # With very limited data points, building a robust prediction model is not feasible.
        # This function serves as a placeholder to explain what would be needed.
        # For real prediction, you would need:
        # 1. A much larger dataset with more time points.
        # 2. More features (e.g., context, events, user interactions).
        # 3. Advanced time series models (e.g., ARIMA, Prophet, LSTM).
        # 4. Proper training, validation, and testing splits.
        
        # For demonstration, we can just return the last known emotion percentages as a naive forecast.
        if not self.df.empty:
            last_entry = self.df.iloc[-1]
            return {
                "naive_forecast": {
                    "happy": last_entry["happy"],
                    "neutral": last_entry["neutral"],
                    "sad": last_entry["sad"]
                },
                "note": "تنبؤ أولي بناءً على آخر نقطة بيانات بسبب محدودية البيانات. يتطلب نموذجًا أكثر تعقيدًا وبيانات أكبر لتنبؤات دقيقة."
            }
        else:
            return {"note": "لا توجد بيانات للتنبؤ."
            }

    def get_full_analysis_json(self):
        analysis_results = {
            "processed_data": self.get_processed_data().to_dict(orient="records"),
            "emotion_statistics": self.get_emotion_statistics(),
            "temporal_analysis": self.get_temporal_analysis().to_dict(orient="records"),
            "identified_patterns": self.identify_patterns(),
            "predictions": self.predict_emotions()
        }
        return json.dumps(analysis_results, indent=4, default=str)

# Example Usage (for testing purposes)
if __name__ == '__main__':
    sample_data = {
        "emotion_history_20s": [
            {
                "timestamp": "2025-08-01T15:26:40Z",
                "emotion_percentage": {
                    "happy": 75,
                    "neutral": 15,
                    "sad": 10
                }
            },
            {
                "timestamp": "2025-08-01T15:26:50Z",
                "emotion_percentage": {
                    "happy": 85,
                    "neutral": 10,
                    "sad": 5
                }
            },
            {
                "timestamp": "2025-08-01T15:27:00Z",
                "emotion_percentage": {
                    "happy": 90,
                    "neutral": 8,
                    "sad": 2
                }
            }
        ]
    }

    analyzer = EmotionAnalyzer(sample_data)
    print(analyzer.get_processed_data())
    print(analyzer.get_emotion_statistics())
    print(analyzer.get_temporal_analysis())
    print(analyzer.identify_patterns())
    print(analyzer.predict_emotions())
    analyzer.plot_emotion_distribution()
    analyzer.plot_temporal_emotions()
    print(analyzer.get_full_analysis_json())

