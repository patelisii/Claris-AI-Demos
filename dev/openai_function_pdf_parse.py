import os
import json
import openai
from dotenv import load_dotenv
import pdfplumber

load_dotenv()
os.environ['OPENAI_API_KEY'] = os.environ.get("OPENAI_KEY")

w2_function_format = {
    "name": "extract_w2_information",
    "description": "Extract all entities from a W-2 tax form. The name of the entity is indicated by a letter or number, then a space, then the entity name. The corresponding value will be in the table entry below it. I've given you the table in python list form.",
    "parameters": {
        "type": "object",
        "properties": {
            "a Employee's social security number": {
                "type": "string",
                "description": "The employee's social security number"
            },
            "b Employer identification number": {
                "type": "string",
                "description": "The employer's identification number"
            },
            "c Employer's name, address, and ZIP code": {
                "type": "string",
                "description": "The employer's name, address, and ZIP code"
            },
            "d Control number": {
                "type": "string",
                "description": "The control number"
            },
            "e Employee's first name and initial Last name": {
                "type": "string",
                "description": "The employee's first name, middle initial, and last name. Middle initial is optional and may not be present."
            },
            "f Employee's address and ZIP code": {
                "type": "string",
                "description": "The employee's address and ZIP code"
            },
            "1 Wages, tips, other compensation": {
                "type": "string",
                "description": "Total wages, tips, and other compensation received by the employee"
            },
            "2 Federal income tax withheld": {
                "type": "string",
                "description": "Amount of federal income tax withheld from the employee's earnings"
            },
            "3 Social security wages": {
                "type": "string",
                "description": "Total wages subject to social security tax"
            },
            "4 Social security tax withheld": {
                "type": "string",
                "description": "Amount of social security tax withheld from the employee's earnings"
            },
            "5 Medicare wages and tips": {
                "type": "string",
                "description": "Total wages and tips subject to Medicare tax"
            },
            "6 Medicare tax withheld": {
                "type": "string",
                "description": "Amount of Medicare tax withheld from the employee's earnings"
            },
            "7 Social security tips": {
                "type": "string",
                "description": "Total tips subject to social security tax"
            },
            "8 Allocated tips": {
                "type": "string",
                "description": "Total tips allocated to the employee"
            },
            "9 Advance EIC payment": {
                "type": "string",
                "description": "Advance earned income credit payments received by the employee"
            },
            "10 Dependent care benefits": {
                "type": "string",
                "description": "Total dependent care benefits provided to the employee"
            },
            "11 Nonqualified plans": {
                "type": "string",
                "description": "Distributions from nonqualified deferred compensation plans or nongovernmental section 457 plans"
            },
            "12a See instructions for box 12": {
                "type": "string",
                "description": "Codes and amounts for various types of compensation and benefits, as described in the W-2 instructions"
            },
            "12b": {
                "type": "string",
                "description": "Additional codes and amounts as described in the W-2 instructions"
            },
            "12c": {
                "type": "string",
                "description": "Additional codes and amounts as described in the W-2 instructions"
            },
            "12d": {
                "type": "string",
                "description": "Additional codes and amounts as described in the W-2 instructions"
            },
            "13 Statutory employee, Retirement plan, Third-party sick pay": {
                "type": "string",
                "description": "Checkboxes indicating statutory employee status, retirement plan participation, and third-party sick pay"
            },
            "14 Other": {
                "type": "string",
                "description": "Other information, as needed"
            },
            "15 State": {
    "type": "object",
    "properties": {
        "variable1": {
            "type": "string",
            "description": "The state code for the first state where the employee earned wages"
        },
        "variable2": {
            "type": "string",
            "description": "The state code for the second state where the employee earned wages"
        }
    },
    "description": "Object containing state codes where the employee earned wages"
            },
            "Employer's state ID number": {
                "type": "object",
                "properties": {
                    "state1": {
                        "type": "string",
                        "description": "Employer's state identification number for the first state"
                    },
                    "state2": {
                        "type": "string",
                        "description": "Employer's state identification number for the second state"
                    }
                },
                "description": "Object containing employer's state identification numbers"
            },
            "16 State wages, tips, etc.": {
                "type": "object",
                "properties": {
                    "statewages1": {
                        "type": "string",
                        "description": "Amount of state wages, tips, etc., for the first state"
                    },
                    "statewages2": {
                        "type": "string",
                        "description": "Amount of state wages, tips, etc., for the second state"
                    }
                },
                "description": "Object containing amounts of state wages, tips, etc."
            },
            "17 State income tax": {
                "type": "object",
                "properties": {
                    "incometax1": {
                        "type": "string",
                        "description": "Amount of state income tax withheld for the first state"
                    },
                    "incometax2": {
                        "type": "string",
                        "description": "Amount of state income tax withheld for the second state"
                    }
                },
                "description": "Object containing amounts of state income tax withheld"
            },
            "18 Local wages, tips, etc.": {
                "type": "object",
                "properties": {
                    "localwages1": {
                        "type": "string",
                        "description": "Amount of local wages, tips, etc., for the first locality"
                    },
                    "localwages2": {
                        "type": "string",
                        "description": "Amount of local wages, tips, etc., for the second locality"
                    }
                },
                "description": "Object containing amounts of local wages, tips, etc."
            },
            "19 Local income tax": {
                "type": "object",
                "properties": {
                    "localtax1": {
                        "type": "string",
                        "description": "Amount of local income tax withheld for the first locality"
                    },
                    "localtax2": {
                        "type": "string",
                        "description": "Amount of local income tax withheld for the second locality"
                    }
                },
                "description": "Object containing amounts of local income tax withheld"
            },
            "20 Locality name": {
                "type": "object",
                "properties": {
                    "locality1": {
                        "type": "string",
                        "description": "Name of the first locality corresponding to the local income tax amounts"
                    },
                    "locality2": {
                        "type": "string",
                        "description": "Name of the second locality corresponding to the local income tax amounts"
                    }
                },
                "description": "Object containing names of localities corresponding to the local income tax amounts"
            }

        }
    }
}

tools = [{"type":"function", "function":w2_function_format}]

# Path to your PDF file
pdf_path = 'tax_docs/W2_XL_input_clean_1001.pdf'

# Open the PDF
with pdfplumber.open(pdf_path) as pdf:
    for page in pdf.pages:
        # Extract tables from the current page
        tables = page.extract_tables()

response = openai.chat.completions.create(
        model = 'gpt-3.5-turbo',
        messages = [{'role': 'user', 'content': "Can you parse this and return a json with the function I provided?\n" + str(tables[0])}],
        tools=tools,
        tool_choice = 'auto'
    )

print(json.loads(response.choices[0].message.tool_calls[0].function.arguments))