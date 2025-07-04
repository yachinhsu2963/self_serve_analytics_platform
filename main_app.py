from try_groq import make_query
import streamlit as st
import json
import mysql.connector
import pandas as pd
from nl4dv import NL4DV
import altair as alt

class Global_var:
    def __init__(self):
        self.query = ''

gb = Global_var()
# print(gb.query, '----------')

@st.cache_resource
def get_connection():
    print('trying to connect')
    with open('db_connect.json', 'r') as f:
        config = json.load(f)
        print(config)

    connection = mysql.connector.connect(
        host=config['host'],
        user=config['username'],
        password=config['password'],
        database=config.get('database')  # Optional key
    )
    if connection is not None:
        print('successfully connected')
    return connection
st.title('Generate a Query')
prompt = st.text_area("Enter your prompt to make a query: (eg. 1.showing the average delivery time across review score \
                      2.show total sales for each product category \
                      3.show freight value and sales across product category)")


if st.button("Generate"):
    out = json.loads(make_query(prompt))['query']
    # print(out)
    # print('------', type(out))
    st.write('results')
    # st.write(out)
    out = out.replace('\\n','')
    gb.query = out
    st.write(out)
    with open('querytext.txt', 'w') as f:
        f.write(out)
st.title("SQL Query App")
# print('------', gb.query)


if st.button("Run Query"):

    try:
        conn = get_connection()
        cursor = conn.cursor()
        with open('querytext.txt', 'r') as f:
            q = f.readline().strip()
        print(f'here is the query {q}')
        cursor.execute(q)
        results = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(results, columns=column_names)
        st.session_state["df"] = df
        st.write("Results:")
        st.dataframe(df.head())
        df.to_csv('raw_data.csv', encoding='utf-8', index=False)

    except Exception as e:
        st.error(f"Error: {e}")


# Title
st.title("Create Your Visualization")

# Initialize session state for queries
if "queries" not in st.session_state:
    st.session_state["queries"] = []  # Store the list of queries

# Button to add a new query input field
st.text("Click button to add your data request")
if st.button("Add one request"):
    st.session_state["queries"].append("")  # Add a new empty query

# Function to handle the visualization generation
def generate_visualization(query):
    try:

        # Load the data
        file_path = "raw_data.csv"
        data = pd.read_csv(file_path)
        # Initialize an instance of NL4DV
        # ToDo: Verify the path to the source data file. Modify it accordingly.
        nl4dv_instance = NL4DV(data_url="raw_data.csv")

        # Use Stanford Core NLP
        # ToDo: Verify the paths to the JAR files. Modify them accordingly.
        dependency_parser_config = {"name":"corenlp", "model":"parsers/stanford-english-corenlp-2018-10-05-models.jar", "parser":"parsers/stanford-parser.jar"}

        # Set the Dependency Parser
        nl4dv_instance.set_dependency_parser(config=dependency_parser_config)
        
        # Execute the query
        output = nl4dv_instance.analyze_query(query)
        print(output)

        if "visList" not in output or len(output["visList"]) == 0:
            st.error("No visualization could be generated for the query.")
            return

        vlSpec = output['visList'][0]['vlSpec']
        # print(vlSpec)

        # Replace URL with embedded data
        vlSpec['data'] = {'values': data.to_dict(orient='records')}

        # Check mark type
        if "type" not in vlSpec.get("mark", {}):
            st.error("The 'type' field is missing in the mark specification.")
        else:
            mark_type = vlSpec["mark"]["type"]
            try:
                chart = getattr(alt.Chart(pd.DataFrame(vlSpec["data"]["values"])), f"mark_{mark_type}")()
            except AttributeError:
                st.warning(f"Unsupported chart type '{mark_type}', defaulting to bar chart.")
                chart = alt.Chart(pd.DataFrame(vlSpec["data"]["values"])).mark_bar()

        # Apply encoding
        for channel, spec in vlSpec["encoding"].items():
            field = spec.get("field", "")
            field_type = spec.get("type", "quantitative")
            encode_func = getattr(alt, channel.capitalize())
            encode_args = {"field": field, "type": field_type}

            # Add additional properties
            for key in ["aggregate", "bin", "axis", "scale", "title", "sort"]:
                if key in spec:
                    encode_args[key] = spec[key]

            chart = chart.encode(**{channel: encode_func(**encode_args)})

        # Set chart properties
        chart = chart.properties(width=600, height=400)

        # Display the chart in Streamlit
        st.altair_chart(chart, use_container_width=True)

        # Check and debug vlSpec
        st.write(vlSpec)

    except Exception as e:
        st.error(f"An error occurred: {e}")

# Render all text inputs for queries and generate visualizations
for i, query in enumerate(st.session_state["queries"]):
    st.session_state["queries"][i] = st.text_input(f"Enter your request {i+1}.  (e.g. 1.Create a line chart showing the average delivery time across review score \
                                                                                      2.Create a bar chart showing total sales across product category\
                                                                                      3.Show the relationship between freight value and sales across product category)",
                                                   query, key=f"query_{i}")
    if query.strip():  # Only process non-empty queries
        generate_visualization(query)