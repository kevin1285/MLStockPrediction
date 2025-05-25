
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
import numpy as np  
import pandas as pd

def make_line_plot_image(df_segment: pd.DataFrame, out_path="temp_plot.png") -> bool:
    if df_segment is None or df_segment.empty or 'Close' not in df_segment.columns or df_segment['Close'].isnull().all():
        return False
    fig, ax = plt.subplots(figsize=(1.28, 1.28), dpi=100); ax.plot(np.arange(len(df_segment)), df_segment['Close'], color='black', linewidth=2); ax.axis('off')
    ax.set_position([0, 0, 1, 1])
    plt.savefig(out_path, bbox_inches='tight', pad_inches=0)
    plt.close(fig)
    return True


def generate_image(df, window, temp_dir):
    image_path = None
    temp_file_path = None
    try:
        segment = df.iloc[-window:]
        temp_file_path = os.path.join(temp_dir, f"img_{len(df)}.png")
        plot_success = make_line_plot_image(segment[['Close']], out_path=temp_file_path)
        if plot_success:
            image_path = temp_file_path
        else:
            image_path = None
    except Exception as e:
        print(f"Error in image generation: {e}")
        image_path = None
    if not image_path and temp_file_path and os.path.exists(temp_file_path):
         try:
            os.remove(temp_file_path)
         except OSError:
            pass
    return image_path