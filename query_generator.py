
from groq import Groq
import json

with open("groq_API_KEY.json", "r") as file:
    PRIVATE = json.load(file)


client = Groq(
    api_key=PRIVATE['key'],
)

def generate_python_code(message, df):
    data = str(df.columns)
    system_message = (
        "You are a coding assistant. Your task is to generate valid Python code based on user input. "
        "The code must:\n"
        "1. Be in the form of a function that can be imported into other Python scripts.\n"
        "The function should be applicable to multiple datasets, so it should have a data parameter.\n"
        "The function should use altair for the visualization and return the altair object.\n"
        "The function should always be called visualize.\n"
        f"Here are the column names in the data:\n{data}\n"
        "make sure to use the correct names of columns.\n"
        "2. Include example tests or demonstrations only inside an `if __name__ == '__main__'` block.\n"
        "3. Be free of any additional text, comments, or metadata outside the Python code.\n\n"
        "The output must be valid Python code and nothing else. It should not include ``` at the top or bottom."

    )

    # print("System Message:\n", system_message)
    # print("User Message:\n", message)

    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": system_message},
            {
                "role": "user",
                "content": f"The task is: {message}. here is some example data as reference: {data}"},
        ],
        response_format={"type": "text"},  # Return plain text
        model="llama3-8b-8192",
    )

    return chat_completion.choices[0].message.content

def prepare_graph(df, message):
    # Sample data for the prompt
    data_sample = str(df.columns)  # Convert to a compact format for display
    system_message = (
        "You are an assistant tasked with generating Python code for data visualization using the Altair library. "
        "You must respond **only** in JSON format with the following structure:\n\n"
        "{\n"
        "  \"code\": \"<Python script to create the visualization>\",\n"
        "  \"other_info\": \"<Optional additional information>\"\n"
        "}\n\n"
        "Rules:\n"
        "1. The 'code' field must contain a Python script as a single valid string.\n"
        "2. The script should be executable in a standalone function and use the provided data sample.\n"
        "3. Do not include any text outside the JSON object.\n"
        "4. Ensure all special characters, such as quotation marks and backslashes, are properly escaped.\n"
        "5. If there are ambiguities in the prompt, include clarifications in the 'other_info' field.\n\n"

    )

    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": message},
        ],
        #response_format={"type": "json_object"},
        model="llama3-8b-8192",
    )

    return chat_completion.choices[0].message.content


def make_query(message):
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You will generate SQL queries for a database with the following tables and columns: " +
                           "1. `customers` with columns: `customer_id`, `customer_unique_id`, `customer_zip_code_prefix`, `customer_city`, `customer_state`." +
                           "2. `order_items` with columns: `order_id`, `order_item_id`, `product_id`, `seller_id`, `shipping_limit_date`, `sales`, `freight_value`." +
                           "3. `payments` with columns: `order_id`, `payment_sequential`, `payment_type`, `payment_installments`, `payment_value`." +
                           "4. `reviews` with columns: `review_id`, `order_id`, `review_score`, `review_comment_title`, `review_comment_message`, `review_creation_date`, `review_answer_timestamp`." +
                           "5. `orders` with columns: `order_id`, `customer_id`, `order_status`, `order_purchase_timestamp`, `order_approved_at`, `order_delivered_carrier_date`, `order_delivered_customer_date`, `order_estimated_delivery_date`." +
                           "6. `products` with columns: `product_id`, `product_category_name`, `product_name_length`, `product_description_length`, `product_photos_qty`, `product_weight_g`, `product_length_cm`, `product_height_cm`, `product_width_cm`." +
                           "7. `sellers` with columns: `seller_id`, `seller_zip_code_prefix`, `seller_city`, `seller_state`." +
                           "8. `category_translation` with columns: `product_category_name`, `product_category_name_english`." +
                           "Create an SQL query based on the prompt the user gives. Only include relevant columns" +
                           "The response should be in JSON format and contain only the query. Do not write anything else. " +
                           'Here is an example response format to follow: {"query":"SELECT * FROM table WHERE condition;"}'+
                           "The query can be all in one line. "


                # "content": "create an SQL query that will work on a database with 1 table called smartphones. " +
                #            "the table has the following columns with these exact names: "
                #            "Smartphone, Brand, Model, RAM, Storage, Color, Free, Final Price." +
                #            "For Final Price specifically, refer to it with `Final Price`. "+
                #            "The response should be nothing but the query. It will be used directly to query the database."+
                #            "respond in json format. Dont write anything else."+
                #             'Here is an example response format to follow: {"query":"select * from table;"}'
                           # "The response should be in json where there is a key called 'query' that " +
                           # "corresponds to the generated SQL code. Then there should be a key called " +
                           # "additional_info where any other comments or summary would be included if needed. "

                # "content": "You are to create SQL queries that work on a database with 3 tables and respond in JSON. " +
                #         "One is customers, with customer_id, cust_name, zip code " +
                #         "The next is products, with product_id, prod_name, price " +
                #         "The last is orders, with order_id, customer_id, product_id, date. " +
                #         "The response should be in json where there is a key called 'query' that " +
                #         "corresponds to the generated SQL code. Then there should be a key called " +
                #         "additional_info where any other comments or summary would be included if needed. "
                #         # "There should be no other text outside of this json format in the response."
            },
            {
                "role": "user",

                "content": message

            }
        ],
        response_format={
                        "type": "json_object"
                        },

        model="llama3-8b-8192",
    )
    #print(chat_completion.choices[0].message.content)
    return chat_completion.choices[0].message.content


if __name__=='__main__':
    example_message = "show the top 5 payment_values and the name of the customer paying for it"

    response = make_query(example_message)
    response_dict = json.loads(response)
    print(response_dict)
    print(type(response_dict))

    print(response_dict['query'])
    print(type(response_dict['query']))
    '''
    import pandas as pd
    df = pd.read_csv('smartphones.csv')
    prompt = 'make a bar chart showing average price by color.'
    graph_response = prepare_graph(df, prompt)
    print('----------')

    #graph_response_dict = json.loads(graph_response)

    code = generate_python_code(prompt, df)
    print(code)

    with open('generated_code.py','w') as f:
        f.write(code)
    
    '''