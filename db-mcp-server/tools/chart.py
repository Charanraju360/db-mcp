import json
import os
import webbrowser
import tempfile
from db.sessions import sessions

# helper to get connection
def get_conn(token):
    if token not in sessions:
        return None, "invalid token. please connect first using connect_db"
    return sessions[token]["conn"], None


# figure out best chart type based on data
def pick_chart_type(columns, rows):
    # if 2 columns and second is a number - bar chart
    # if first column looks like date - line chart
    # if only 2 columns and few rows - pie chart
    
    if len(columns) == 2:
        # check if second column is numeric
        try:
            float(rows[0][1])
            is_numeric = True
        except:
            is_numeric = False

        if is_numeric:
            if len(rows) <= 8:
                return "pie"
            else:
                return "bar"

    # if more than 2 columns and numbers present - bar
    if len(columns) >= 2:
        return "bar"

    return "bar"


# build html with plotly chart
def build_html(chart_type, columns, rows, title):
    # convert rows to lists for json
    data = [list(row) for row in rows]
    labels = [str(row[0]) for row in rows]

    # try to get numeric values from second column
    try:
        values = [float(row[1]) for row in rows]
    except:
        values = list(range(len(rows)))

    if chart_type == "pie":
        chart_data = f"""
        var data = [{{
            type: 'pie',
            labels: {json.dumps(labels)},
            values: {json.dumps(values)},
            textinfo: 'label+percent'
        }}];
        """
    elif chart_type == "bar":
        chart_data = f"""
        var data = [{{
            type: 'bar',
            x: {json.dumps(labels)},
            y: {json.dumps(values)},
            marker: {{ color: '#4f8ef7' }}
        }}];
        """
    elif chart_type == "line":
        chart_data = f"""
        var data = [{{
            type: 'scatter',
            mode: 'lines+markers',
            x: {json.dumps(labels)},
            y: {json.dumps(values)},
            line: {{ color: '#4f8ef7' }}
        }}];
        """
    else:
        chart_data = f"""
        var data = [{{
            type: 'bar',
            x: {json.dumps(labels)},
            y: {json.dumps(values)}
        }}];
        """

    html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>{title}</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {{ font-family: Arial, sans-serif; background: #f9f9f9; }}
        h2 {{ text-align: center; color: #333; }}
        #chart {{ width: 90%; margin: auto; }}
    </style>
</head>
<body>
    <h2>{title}</h2>
    <div id="chart"></div>
    <script>
        {chart_data}
        var layout = {{
            title: '{title}',
            paper_bgcolor: '#f9f9f9',
            plot_bgcolor: '#f9f9f9'
        }};
        Plotly.newPlot('chart', data, layout);
    </script>
</body>
</html>
"""
    return html


# main visualize tool function
def visualize_table(token, query, title="Chart"):
    conn, err = get_conn(token)
    if err:
        return {"success": False, "error": err}

    # only allow select
    if not query.strip().lower().startswith("select"):
        return {"success": False, "error": "only SELECT queries allowed for charts"}

    try:
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]

        if not rows:
            return {"success": False, "error": "query returned no rows, nothing to chart"}

        # pick best chart type
        chart_type = pick_chart_type(columns, rows)

        # build html
        html = build_html(chart_type, columns, rows, title)

        # save to temp file and open in browser
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".html", mode="w", encoding="utf-8")
        tmp.write(html)
        tmp.close()

        webbrowser.open(f"file://{tmp.name}")

        return {
            "success": True,
            "chart_type": chart_type,
            "rows_used": len(rows),
            "file": tmp.name,
            "message": f"chart opened in browser as {chart_type} chart"
        }

    except Exception as e:
        return {"success": False, "error": str(e)}