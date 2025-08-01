import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import json

class EmotionAnalyzer:
    def __init__(self, data):
        self.data = data
        self.emotion_types = self._get_emotion_types()
        self.df = self._process_data()

    def _get_emotion_types(self):
        if self.data and "emotion_history_20s" in self.data and self.data["emotion_history_20s"]:
            # Get emotion types from the first entry
            return list(self.data["emotion_history_20s"][0]["emotion_percentage"].keys())
        return []

    def _process_data(self):
        records = []
        for entry in self.data["emotion_history_20s"]:
            timestamp = pd.to_datetime(entry["timestamp"])
            emotions = entry["emotion_percentage"]
            record = {"timestamp": timestamp}
            for emotion_type in self.emotion_types:
                record[emotion_type] = emotions.get(emotion_type, 0) # Use .get to handle missing emotions
            records.append(record)
        return pd.DataFrame(records)

    def get_processed_data(self):
        return self.df

    def get_emotion_statistics(self):
        # Calculate mean percentage for each emotion
        emotion_means = self.df[self.emotion_types].mean().to_dict()

        # Calculate overall percentage of each emotion across all timestamps
        total_percentages = self.df[self.emotion_types].sum().sum()
        emotion_overall_percentages = {}
        for emotion in self.emotion_types:
            emotion_overall_percentages[emotion] = (self.df[emotion].sum() / total_percentages) * 100 if total_percentages > 0 else 0

        # Identify most and least common emotions based on overall percentage
        if emotion_overall_percentages:
            most_common_emotion = max(emotion_overall_percentages, key=emotion_overall_percentages.get)
            least_common_emotion = min(emotion_overall_percentages, key=emotion_overall_percentages.get)
        else:
            most_common_emotion = None
            least_common_emotion = None

        # Calculate standard deviation for each emotion
        emotion_std_dev = self.df[self.emotion_types].std().to_dict()

        return {
            "mean_percentages": emotion_means,
            "overall_percentages": emotion_overall_percentages,
            "most_common_emotion": most_common_emotion,
            "least_common_emotion": least_common_emotion,
            "standard_deviations": emotion_std_dev
        }

    def get_emotion_distribution(self):
        # This method can be used to get the raw distribution for plotting
        return self.df[self.emotion_types]

    def get_temporal_analysis(self):
        # Calculate the rate of change for each emotion
        self.df["time_diff"] = self.df["timestamp"].diff().dt.total_seconds()
        temporal_df = self.df.copy()
        for emotion_type in self.emotion_types:
            temporal_df[f"{emotion_type}_change"] = temporal_df[emotion_type].diff() / temporal_df["time_diff"]

        # Drop the first row which will have NaN for diff calculations
        temporal_df = temporal_df.dropna(subset=["time_diff"])

        return temporal_df[["timestamp"] + [f"{e}_change" for e in self.emotion_types]]

    def plot_emotion_distribution(self, filename="emotion_distribution.png"):
        emotion_data = self.df[self.emotion_types]
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
        for emotion_type in self.emotion_types:
            plt.plot(self.df["timestamp"], self.df[emotion_type], label=emotion_type) # Using emotion_type as label
        plt.title("تغير المشاعر بمرور الوقت", fontname="Noto Sans Arabic")
        plt.xlabel("الوقت", fontname="Noto Sans Arabic")
        plt.ylabel("النسبة المئوية", fontname="Noto Sans Arabic")
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(filename)
        plt.close()
        return filename

    def identify_patterns(self):
        patterns = {}
        for emotion in self.emotion_types:
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
        if not self.df.empty:
            last_entry = self.df.iloc[-1]
            naive_forecast = {emotion: last_entry[emotion] for emotion in self.emotion_types}
            return {
                "naive_forecast": naive_forecast,
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
                    "sad": 10,
                    "angry": 5
                }
            },
            {
                "timestamp": "2025-08-01T15:26:50Z",
                "emotion_percentage": {
                    "happy": 85,
                    "neutral": 10,
                    "sad": 5,
                    "angry": 2
                }
            },
            {
                "timestamp": "2025-08-01T15:27:00Z",
                "emotion_percentage": {
                    "happy": 90,
                    "neutral": 8,
                    "sad": 2,
                    "surprised": 1
                }
            }
        ]
    }

    analyzer = EmotionAnalyzer(sample_data)
    # print(type(analyzer.get_processed_data()))
    # print(type(analyzer.get_emotion_statistics()))
    # print(type(analyzer.get_temporal_analysis()))
    # print(type(analyzer.identify_patterns()))
    # print(type(analyzer.predict_emotions()))
    # analyzer.plot_emotion_distribution()
    # analyzer.plot_temporal_emotions()
    print(analyzer.get_full_analysis_json())