import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

ASSETS_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets"))
CLEAN_DATA_PATH = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "cleaned_diabetic_data.csv"))

def generate_visual_assets():
    os.makedirs(ASSETS_DIR, exist_ok=True)
    df = pd.read_csv(CLEAN_DATA_PATH)
    
    # Set Seaborn / Matplotlib dark theme styling
    plt.style.use('dark_background')
    fig, axes = plt.subplots(2, 2, figsize=(16, 11), facecolor='#0f172a')
    fig.suptitle('Hospital Readmission Analytics — 30-Day Risk Drivers\nInnovaccer Healthcare Provider Intelligence', 
                 fontsize=18, fontweight='bold', color='#f8fafc', y=0.98)
    
    # 1. Readmission Rate by Age Group
    age_df = df.groupby('age_clean')['readmitted_30day'].mean().reset_index()
    age_df['pct'] = age_df['readmitted_30day'] * 100
    
    sns.barplot(ax=axes[0,0], data=age_df, x='age_clean', y='pct', palette='viridis')
    axes[0,0].set_title('30-Day Readmission Rate by Age Cohort', fontsize=13, color='#38bdf8', pad=10)
    axes[0,0].set_xlabel('Age Bracket', color='#94a3b8')
    axes[0,0].set_ylabel('Readmission Rate (%)', color='#94a3b8')
    axes[0,0].set_facecolor('#1e293b')
    for p in axes[0,0].patches:
        height = p.get_height()
        if height > 0:
            axes[0,0].annotate(f'{height:.1f}%', (p.get_x() + p.get_width()/2., height/2),
                               ha='center', va='center', fontsize=9, color='white', fontweight='bold')

    # 2. Readmission Rate by Prior Inpatient Visits
    inpatient_order = ['0 Visits', '1 Visit', '2 Visits', '3+ Visits']
    inp_df = df.groupby('prior_inpatient_bucket')['readmitted_30day'].mean().reindex(inpatient_order).reset_index()
    inp_df['pct'] = inp_df['readmitted_30day'] * 100
    
    axes[0,1].plot(inp_df['prior_inpatient_bucket'], inp_df['pct'], marker='o', color='#fbbf24', linewidth=3, markersize=10)
    axes[0,1].fill_between(inp_df['prior_inpatient_bucket'], inp_df['pct'], color='#fbbf24', alpha=0.2)
    axes[0,1].set_title('Readmission Rate vs. Prior Inpatient Visits (Exponential Driver)', fontsize=13, color='#fbbf24', pad=10)
    axes[0,1].set_xlabel('Prior Inpatient Visits', color='#94a3b8')
    axes[0,1].set_ylabel('Readmission Rate (%)', color='#94a3b8')
    axes[0,1].set_facecolor('#1e293b')
    for i, row in inp_df.iterrows():
        axes[0,1].annotate(f"{row['pct']:.1f}%", (row['prior_inpatient_bucket'], row['pct'] + 0.8),
                           ha='center', fontsize=10, color='#ffffff', fontweight='bold')

    # 3. Readmission Rate by HbA1c Test Result
    a1c_df = df.groupby('A1Cresult')['readmitted_30day'].mean().reset_index()
    a1c_df['pct'] = a1c_df['readmitted_30day'] * 100
    a1c_df['A1Cresult'] = a1c_df['A1Cresult'].fillna('Not Tested')
    
    sns.barplot(ax=axes[1,0], data=a1c_df, x='A1Cresult', y='pct', palette='magma')
    axes[1,0].set_title('HbA1c Glycemic Monitoring Impact', fontsize=13, color='#a855f7', pad=10)
    axes[1,0].set_xlabel('HbA1c Test Category', color='#94a3b8')
    axes[1,0].set_ylabel('Readmission Rate (%)', color='#94a3b8')
    axes[1,0].set_facecolor('#1e293b')
    for p in axes[1,0].patches:
        height = p.get_height()
        if height > 0:
            axes[1,0].annotate(f'{height:.1f}%', (p.get_x() + p.get_width()/2., height/2),
                               ha='center', va='center', fontsize=9, color='white', fontweight='bold')

    # 4. Readmission Rate by Discharge Disposition Category
    dc_df = df.groupby('discharge_category')['readmitted_30day'].mean().sort_values(ascending=True).reset_index()
    dc_df['pct'] = dc_df['readmitted_30day'] * 100
    
    sns.barplot(ax=axes[1,1], data=dc_df, y='discharge_category', x='pct', palette='rocket')
    axes[1,1].set_title('Readmission Risk by Discharge Destination', fontsize=13, color='#f43f5e', pad=10)
    axes[1,1].set_xlabel('Readmission Rate (%)', color='#94a3b8')
    axes[1,1].set_ylabel('Discharge Disposition', color='#94a3b8')
    axes[1,1].set_facecolor('#1e293b')
    for p in axes[1,1].patches:
        width = p.get_width()
        if width > 0:
            axes[1,1].annotate(f'{width:.1f}%', (width / 2, p.get_y() + p.get_height()/2.),
                               ha='center', va='center', fontsize=9, color='white', fontweight='bold')

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    
    dashboard_img = os.path.join(ASSETS_DIR, "dashboard_screenshot.png")
    plt.savefig(dashboard_img, dpi=200, bbox_inches='tight')
    plt.close()
    print(f"[SUCCESS] High-resolution analytics visual dashboard saved to: {dashboard_img}")

if __name__ == "__main__":
    generate_visual_assets()
