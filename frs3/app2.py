from flask import Flask, render_template, request
import pandas as pd
import plotly.express as px
import plotly.io as pio
from plotly.subplots import make_subplots
import plotly.graph_objects as go

app = Flask(__name__)

# Load the dataset
data = pd.read_csv('food_data.csv')

# Fill missing values in Health_Issue
data['Health_Issue'] = data['Health_Issue'].fillna('General')

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get user inputs
        name = request.form.get('name')
        age = request.form.get('age')
        weight = request.form.get('weight')
        height = request.form.get('height')
        health_issue = request.form.get('health_issue')

        # Filter the data based on health issue
        filtered_data = data[data['Health_Issue'] == health_issue]

        # Get top 10 food recommendations
        recommendations = filtered_data.head(10)

        # Prepare data for visualizations
        calories = recommendations['Calories'].tolist()
        proteins = recommendations['Protein'].tolist()
        veg_nonveg_counts = recommendations['Veg_Non'].value_counts()
        restaurant_counts = recommendations['Restaurant'].value_counts()

        # Climate categories (keeping the values as lowercase)
        climate_counts = recommendations['Climate'].value_counts()

        # Create visualizations
        pie_fig_calories_proteins = px.pie(
            names=['Calories', 'Proteins'],
            values=[sum(calories), sum(proteins)],
            title='Total Calories vs Proteins for Recommended Foods',
            color_discrete_sequence=['#FF9999', '#66B3FF']
        )

        # New pie chart for restaurant percentages
        restaurant_fig = px.pie(
            names=restaurant_counts.index,
            values=restaurant_counts.values,
            title='Percentage of Food by Restaurant',
            color_discrete_sequence=px.colors.sequential.RdBu
        )

        # New pie chart for climate percentages
        climate_fig = px.pie(
            names=climate_counts.index,
            values=climate_counts.values,
            title='Percentage of Food by Climate',
            color_discrete_sequence=px.colors.sequential.Plasma
        )

        # Create the subplot for pie charts with type='pie'
        fig = make_subplots(rows=2, cols=2,
                            specs=[[{'type': 'pie'}, {'type': 'pie'}],
                                   [{'type': 'pie'}, {'type': 'pie'}]],
                            subplot_titles=('Total Calories vs Proteins', 
                                            'Percentage of Food by Restaurant',
                                            'Percentage of Food by Climate', 
                                            'Percentage of Veg and Non-Veg'))

        # Add the pie charts to the subplot
        fig.add_trace(go.Pie(labels=['Calories', 'Proteins'], values=[sum(calories), sum(proteins)]),
                      row=1, col=1)
        
        fig.add_trace(go.Pie(labels=restaurant_counts.index, values=restaurant_counts.values),
                      row=1, col=2)

        fig.add_trace(go.Pie(labels=climate_counts.index, values=climate_counts.values),
                      row=2, col=1)

        fig.add_trace(go.Pie(labels=veg_nonveg_counts.index, values=veg_nonveg_counts.values),
                      row=2, col=2)

        # Update layout for the pie chart figure
        fig.update_layout(title_text='Food Recommendations Analysis', height=800)

        # Save the combined pie chart
        combined_pie_chart_path = 'static/combined_pie_chart.html'
        pio.write_html(fig, file=combined_pie_chart_path, auto_open=False)

        # Create bar graph for climate conditions with custom colors
        climate_counts_df = climate_counts.reset_index()
        climate_counts_df.columns = ['Climate', 'Count']  # Rename columns

        climate_color_map = {
            'summer': 'orange',  # Color for summer
            'winter': 'blue',    # Color for winter
            'rainy': 'green'     # Color for rainy
        }

        climate_bar_fig = px.bar(
            climate_counts_df,
            x='Climate',
            y='Count',
            title='Food Count by Climate Condition',
            labels={'Climate': 'Climate', 'Count': 'Count'},
            color='Climate',
            color_discrete_map=climate_color_map  # Use custom colors
        )
        climate_bar_chart_path = 'static/climate_bar_chart.html'
        pio.write_html(climate_bar_fig, file=climate_bar_chart_path, auto_open=False)

        # Render results on a new page
        return render_template('results2.html', recommendations=recommendations.to_dict(orient='records'),
                               combined_pie_chart_path=combined_pie_chart_path,
                               climate_bar_chart_path=climate_bar_chart_path)

    # GET request loads the form with health issue options
    health_issues = data['Health_Issue'].unique()
    return render_template('index1.html', health_issues=health_issues)

if __name__ == '__main__':
    app.run(debug=True)
