from PyPDF2 import PdfReader
from groq import Groq
from docx import Document
import json
from pydantic import BaseModel
from sqlalchemy.sql import text
import uuid
import sqlite3


def get_pdf_text(pdf):
    text = ""
    reader = PdfReader(pdf)
    for page in reader.pages:
        text += page.extract_text() + "/n"
    return text

# def get_docx_text(docx_files):
#     for docx_file in docx_files:
#         document = Document(docx_file)
#         text = ""
#         for para in document.paragraphs:
#             text += para.text + "\n"
#     return text

def query_response(text):
    client = Groq(api_key="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")
    template = { "name" : '',
                 "email" : '',
                 "contact" : '',
                 "skills" : '', 
                 "total_experience_duration" : ''
                }

    chat_completion = client.chat.completions.create(
        messages = [
            {
                "role" : "system",
                "content" : ''' Extract the candidate information data from this Content. Don't comment inside json. Only extract information from this context.Don't generate extra information: . make sure to give only key skills not everything. Give answer in json format. Template Output Example :'''+ json.dumps(template) + '''\n Don't give extra details in template.'''
            },
            {
                "role" : "user",
                "content" : text
            }
        ],
        model = "llama3-70b-8192",
        temperature=0.1,
        response_format={"type" : "json_object"}
    )

    return chat_completion.choices[0].message.content

def save_to_db(conn, cursor, unique_id, response):
    cursor.execute(
        "INSERT INTO resume_data (uid, name, email, contact, skills, experience) VALUES (?,?,?,?,?,?)",
        (unique_id, response['name'], response['email'], response['contact'], response['skills'], response['total_experience_duration'])
    )
    conn.commit()

def fetch_from_db(conn, cursor, unique_id):
    cursor.execute(
        "SELECT name, email, contact, skills, experience FROM resume_data WHERE uid = ?",
        (unique_id,)
    )
    temp = cursor.fetchall()
    conn.commit()
    return temp

def convert(data):
    #given data is list of tuples
    #convert to list of dicts
    new_data = []
    for ele in data:
        temp = {}
        ele = list(ele)
        temp["name"] = ele[0]
        temp["email"] = ele[1]
        temp["contact"] = ele[2]
        temp["skills"] = ele[3]
        temp["experience"] = ele[4]

        new_data.append(temp)

    return new_data