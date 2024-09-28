from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory, Markup, flash
from flask_session import Session 
import openai
import os
import requests
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
import docx2txt
import markdown
import bleach
from docx import Document
from azure.cosmos import CosmosClient, PartitionKey, exceptions
import uuid
import datetime
import msal
from msal import ConfidentialClientApplication

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_KEY")
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB limit
app.config['VERSION'] = '0.80'

# Initialize Cosmos client
cosmos_endpoint = os.getenv("AZURE_COSMOS_ENDPOINT")
cosmos_key = os.getenv("AZURE_COSMOS_KEY")
cosmos_db_name = os.getenv("AZURE_COSMOS_DB_NAME")
cosmos_results_container_name = os.getenv("AZURE_COSMOS_RESULTS_CONTAINER_NAME")
cosmos_files_container_name = os.getenv("AZURE_COSMOS_FILES_CONTAINER_NAME")

cosmos_client = CosmosClient(cosmos_endpoint, cosmos_key)
cosmos_db = cosmos_client.create_database_if_not_exists(id=cosmos_db_name)
cosmos_results_container = cosmos_db.create_container_if_not_exists(
    id=cosmos_results_container_name,
    partition_key=PartitionKey(path="/id"),
    offer_throughput=400
)
cosmos_files_container = cosmos_db.create_container_if_not_exists(
    id=cosmos_files_container_name,
    partition_key=PartitionKey(path="/id"),
    offer_throughput=400
)


# Configure Azure OpenAI
openai.api_type = os.getenv("AZURE_OPENAI_API_TYPE")  # e.g., "azure"
openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")   # e.g., "https://your-resource-name.openai.azure.com/"
openai.api_version = os.getenv("AZURE_OPENAI_API_VERSION")  # e.g., "2023-05-15"
openai.api_key = os.getenv("AZURE_OPENAI_KEY")
MODEL = os.getenv("AZURE_OPENAI_MODEL")

# Configure Azure Translation Service
TRANSLATION_ENDPOINT = os.getenv("AZURE_TRANSLATION_ENDPOINT")
TRANSLATION_KEY = os.getenv("AZURE_TRANSLATION_KEY")
TRANSLATION_REGION = os.getenv("AZURE_TRANSLATION_REGION")
TRANSLATION_LANGUAGE_URL = os.getenv("AZURE_TRANSLATION_LANGUAGE_URL")

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("MICROSOFT_PROVIDER_AUTHENTICATION_SECRET")
TENANT_ID = os.getenv("TENANT_ID")
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPE = ["User.Read"]  # Adjust scope according to your needs

# Allowed file extensions
ALLOWED_EXTENSIONS = {'txt', 'md', 'docx'}

languages_cache = None

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def fetch_languages():
    try:
        response = requests.get(TRANSLATION_LANGUAGE_URL)
        response.raise_for_status()
        data = response.json()
        translation_languages = data.get('translation', {})
        languages = { code: { 'name': info['name'] } for code, info in translation_languages.items() }
        return languages
    except requests.exceptions.RequestException as e:
        print(f"Error fetching languages: {e}")
        return {}

def get_cached_languages():
    global languages_cache
    if not languages_cache:
        languages_cache = fetch_languages()
    return languages_cache

@app.errorhandler(RequestEntityTooLarge)
def handle_file_too_large(e):
    return render_template('upload_content.html', error="File is too large. Maximum allowed size is 16MB."), 413

# Save results to Cosmos DB
def save_results_to_cosmos(results, topic, body):
    # Get user information from session
    user_info = session.get("user", {})
    user_id = user_info.get("oid", "anonymous")  # Default to 'anonymous' if user ID not found
    user_email = user_info.get("email", "no-email")  # Default to 'no-email' if email not found
    
    result_data = {
        'id': str(uuid.uuid4()),
        'user_id': user_id,  # Save user ID with the result
        'user_email': user_email,  # Save user email with the result
        'topic': topic,
        'body': body,
        'results': results,
        'timestamp': str(datetime.datetime.utcnow())
    }
    
    try:
        cosmos_results_container.create_item(body=result_data)
    except exceptions.CosmosHttpResponseError as e:
        print(f"Error saving to Cosmos DB: {e}")


@app.context_processor
def inject_previous_results():
    # Query Cosmos DB for previous results
    query = "SELECT c.id, c.topic, c.timestamp FROM c"
    previous_results = []
    try:
        previous_results = list(cosmos_results_container.query_items(
            query=query,
            enable_cross_partition_query=True
        ))
    except Exception as e:
        print(f"Error fetching previous results: {e}")
    
    # Inject `previous_results` into the template context for all pages
    return {'previous_results': previous_results}

@app.route('/select_file', methods=['GET', 'POST'])
def select_file():
    if request.method == 'POST':
        selected_file_id = request.form.get('selected_file')
        if selected_file_id:
            try:
                # Fetch the file content from Cosmos DB
                file_item = cosmos_files_container.read_item(item=selected_file_id, partition_key=selected_file_id)

                session['body'] = file_item['content']
                session['topic'] = extract_topic_from_content(file_item['content'])
                
                return redirect(url_for('options'))
            except Exception as e:
                print(f"Error retrieving file: {e}")
                flash("An error occurred while retrieving the file.", "danger")
                return redirect(request.url)
    
    # Get sorting and search parameters from the request
    sort_by = request.args.get('sort_by', 'timestamp')  # Default to sorting by timestamp
    sort_order = request.args.get('sort_order', 'desc')  # Default to descending order
    search_query = request.args.get('search', '').lower()  # Default to empty search query
    
    # Get user_id from session
    user_id = session.get("user", {}).get("oid", "anonymous")

    # Query Cosmos DB for uploaded files
    files_query = f"SELECT c.id, c.filename, c.timestamp FROM c WHERE c.user_id = '{user_id}'"
    files = list(cosmos_files_container.query_items(query=files_query, enable_cross_partition_query=True))

    # Filter results based on the search query
    if search_query:
        files = [file for file in files if search_query in file['filename'].lower()]

    # Sort results based on sort_by and sort_order parameters
    if sort_by == 'filename':
        files.sort(key=lambda x: x['filename'].lower(), reverse=(sort_order == 'desc'))
    else:  # Default to sorting by timestamp
        files.sort(key=lambda x: x['timestamp'], reverse=(sort_order == 'desc'))

    return render_template('select_file.html', files=files, sort_by=sort_by, sort_order=sort_order, search_query=search_query)




# Register the markdown filter
@app.template_filter('markdown')
def markdown_filter(text):
    allowed_tags = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'ul', 'li', 'ol', 'strong', 'em', 'blockquote', 'code', 'pre']
    allowed_attrs = {}
    html = markdown.markdown(text)
    clean_html = bleach.clean(html, tags=allowed_tags, attributes=allowed_attrs, strip=True)
    return Markup(clean_html)

@app.route("/login")
def login():
    # Create a MSAL application object
    msal_app = ConfidentialClientApplication(
        CLIENT_ID, authority=AUTHORITY, client_credential=CLIENT_SECRET,
    )
    # Get the login URL to redirect the user
    result = msal_app.get_authorization_request_url(SCOPE, redirect_uri=url_for("authorized", _external=True, _scheme='https'))
    print("Debug - MSAL auth URL and state:", result)
    #auth_url, session['state'] = result[:2]  # This assumes the first two values are what you need

    return redirect(result)

@app.route("/getAToken")  # Redirect URI
def authorized():
    # Create a MSAL application object
    msal_app = ConfidentialClientApplication(
        CLIENT_ID, authority=AUTHORITY, client_credential=CLIENT_SECRET,
    )
    # Extract the code from the response
    code = request.args.get('code', '')
    result = msal_app.acquire_token_by_authorization_code(
        code,
        scopes=SCOPE,  # Misspelled in MSAL as scope
        redirect_uri=url_for("authorized", _external=True, _scheme='https')
    )
    if "error" in result:
        return f"Login failure: {result.get('error_description', result.get('error'))}"
    session["user"] = result.get("id_token_claims")
    return redirect(url_for("index"))

@app.route("/logout")
def logout():
    session.clear()  # Clear the user session
    flash('You have been successfully logged out.', 'success')  # Optional: Notify the user of logout
    return redirect(url_for('index'))  # Redirect to the homepage or login page

@app.route('/', methods=['GET', 'POST'])
def index():
     # Clear specific keys instead of the whole session
    keys_to_clear = ['selected_options', 'form_data', 'topic', 'body']
    for key in keys_to_clear:
        session.pop(key, None)
    if request.method == 'POST':
        selected_options = request.form.getlist('options')
        session['selected_options'] = selected_options
        return redirect(url_for('content_method'))
    return render_template('index.html')


# Favicon route
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/history')
def history():
    # Get sorting and search parameters from the request
    sort_by = request.args.get('sort_by', 'timestamp')  # Default to sorting by timestamp
    sort_order = request.args.get('sort_order', 'desc')  # Default to descending order
    search_query = request.args.get('search', '').lower()  # Default to empty search query
    
    # Get user_id from session
    user_id = session.get("user", {}).get("oid", "anonymous")
    
    # Query Cosmos DB for user's saved results
    query = f"SELECT c.id, c.topic, c.timestamp FROM c WHERE c.user_id = '{user_id}'"
    results = list(cosmos_results_container.query_items(query=query, enable_cross_partition_query=True))

    # Filter results based on the search query
    if search_query:
        results = [result for result in results if search_query in result['topic'].lower()]

    # Sort results based on sort_by and sort_order parameters
    if sort_by == 'topic':
        results.sort(key=lambda x: x['topic'].lower(), reverse=(sort_order == 'desc'))
    else:  # Default to sorting by timestamp
        results.sort(key=lambda x: x['timestamp'], reverse=(sort_order == 'desc'))

    return render_template('history.html', results=results, sort_by=sort_by, sort_order=sort_order, search_query=search_query)


@app.route('/result/<result_id>')
def view_result(result_id):
    try:
        # Fetch the result from Cosmos DB
        result = cosmos_results_container.read_item(item=result_id, partition_key=result_id)
        print(f"Full Result: {result}")  # Log the entire result object

        # Render the template, log the error if rendering fails
        try:
            return render_template('view_result.html', result=result)
        except Exception as e:
            print(f"Template rendering error: {e}")
            return "Error rendering the template.", 500
    except Exception as e:
        print(f"Error retrieving result: {e}")
        return "Error retrieving result.", 500





@app.route('/content_method', methods=['GET', 'POST'])
def content_method():
    selected_options = session.get('selected_options', [])
    if request.method == 'POST':
        content_option = request.form.get('content_option')
        if content_option == 'provide_text':
            return redirect(url_for('provide_text'))
        elif content_option == 'upload_content':
            return redirect(url_for('upload_content'))
        elif content_option == 'select_file':
            return redirect(url_for('select_file'))
    return render_template('content_method.html')



@app.route('/provide_text', methods=['GET', 'POST'])
def provide_text():
    if request.method == 'POST':
        topic = request.form.get('topic')
        body = request.form.get('body', '')
        session['topic'] = topic
        session['body'] = body
        return redirect(url_for('options'))
    return render_template('provide_text.html')

@app.route('/upload_content', methods=['GET', 'POST'])
def upload_content():
    if request.method == 'POST':
        file = request.files.get('file')
        if file and allowed_file(file.filename):
            try:
                filename = secure_filename(file.filename)
                file_extension = filename.rsplit('.', 1)[1].lower()
                
                # Process content based on the file type
                if file_extension == 'docx':
                    content = docx2txt.process(file)
                elif file_extension in ['txt', 'md']:
                    content = file.read().decode('utf-8', errors='ignore')
                else:
                    content = ''
                
                if not content.strip():
                    flash("The uploaded file is empty or could not be read.", "danger")
                    return redirect(request.url)
                
                # Get user information from session
                user_info = session.get("user", {})
                user_id = user_info.get("oid", "anonymous")  # Default to 'anonymous' if user ID not found
                user_email = user_info.get("email", "no-email")  # Default to 'no-email' if email not found
                            
                # Save the file data to Cosmos DB
                file_data = {
                    'id': str(uuid.uuid4()),
                    'content': content,
                    'filename': filename,
                    'file_content': file.read().decode('utf-8', errors='ignore'),
                    'file_extension': file_extension,
                    'timestamp': str(datetime.datetime.utcnow()),
                    'user_id': user_id,  # Associate with user
                    'user_email': user_email  # Save user email with the result
                }
                cosmos_files_container.create_item(body=file_data)
                
                session['body'] = content
                session['topic'] = extract_topic_from_content(content)
                
                flash("File uploaded successfully!", "success")
                return redirect(url_for('options'))
            except Exception as e:
                print(f"Error processing the uploaded file: {e}")
                flash("An error occurred while processing the uploaded file.", "danger")
                return redirect(request.url)
        else:
            flash("Invalid file type. Please upload a DOCX, TXT, or MD file.", "danger")
            return redirect(request.url)
    
    return render_template('upload_content.html')


def extract_topic_from_content(content):
    # Simple extraction method: Use the first sentence as the topic
    if content:
        return content.strip().split('.')[0]
    else:
        return "Untitled Topic"

@app.route('/options', methods=['GET', 'POST'])
def options():
    selected_options = session.get('selected_options', [])
    body = session.get('body', '')
    languages = {}
    if 'article_translation' in selected_options:
        languages = get_cached_languages()
        if not languages:
            return "Error fetching languages. Please try again later.", 500
        if not body:
            return redirect(url_for('upload_content'))
    if request.method == 'POST':
        form_data = request.form.to_dict(flat=False)
        form_data['target_languages'] = request.form.getlist('target_languages')
        session['form_data'] = form_data
        return redirect(url_for('results'))
    return render_template('options.html', options=selected_options, body=body, languages=languages)



@app.route('/results')
def results():
    selected_options = session.get('selected_options', [])
    form_data = session.get('form_data', {})
    results = {}
    topic = session.get('topic', '')
    body = session.get('body', '')
    languages = get_cached_languages()

    # Article Titles
    if 'article_titles' in selected_options:
        style = form_data.get('title_style', ['engaging'])[0]
        tone = form_data.get('title_tone', ['neutral'])[0]
        keywords = form_data.get('title_keywords', [''])[0]
        system_prompt = "You are an AI assistant that generates article titles."
        user_prompt = f"Generate five {style} titles with a {tone} tone for an article about '{topic}'."
        if keywords:
            user_prompt += f" Include keywords: {keywords}."
        response = openai.ChatCompletion.create(
            engine=MODEL,  # Replace with your deployment name
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=150,
            temperature=0.7
        )
        titles = response['choices'][0]['message']['content'].strip().split('\n')
        results['article_titles'] = [title.strip('- ') for title in titles if title.strip()]

    # Article Introductions and Summaries
    if 'article_introductions' in selected_options:
        intro_length = form_data.get('intro_length', ['short'])[0]
        include_summary = form_data.get('include_summary', ['no'])[0]
        tone = form_data.get('intro_tone', ['neutral'])[0]
        system_prompt = "You are an AI assistant that writes article introductions and summaries."
        user_prompt = f"Write a {intro_length} introduction with a {tone} tone for an article about '{topic}'."
        if include_summary == 'yes':
            user_prompt += " Also, provide a summary for the article."
        response = openai.ChatCompletion.create(
            engine=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=500,
            temperature=0.7
        )
        introduction = response['choices'][0]['message']['content'].strip()
        results['article_introductions'] = introduction

    # Automated SEO Text
    # This section is not being used in the current version of the app but can be enabled if needed
    if 'automated_seo_text' in selected_options:
        target_keywords = form_data.get('seo_keywords', [''])[0]
        system_prompt = "You are an AI assistant specialized in generating SEO-optimized content."
        user_prompt = f"Generate an SEO-optimized title and introduction for an article about '{topic}'."
        if target_keywords:
            user_prompt += f" Include keywords: {target_keywords}."
        response = openai.ChatCompletion.create(
            engine=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=300,
            temperature=0.7
        )
        seo_text = response['choices'][0]['message']['content'].strip()
        results['automated_seo_text'] = seo_text

    # SEO-Friendly Tags
    if 'seo_friendly_tags' in selected_options:
        num_tags = int(form_data.get('num_tags', ['5'])[0])
        system_prompt = "You are an AI assistant specialized in generating SEO-friendly tags for digital content. Your focus is to create concise, descriptive tags that improve discoverability and search ranking. Each tag should be relevant to the article's topic, structured for readability, and follow standard SEO conventions."
        user_prompt = f"Generate {num_tags} SEO-friendly tags for an article about '{topic}'. Ensure that each tag is relevant, concise, and accurately reflects key themes of the article. Tags will start with a # symbol, will not contain spaces or special characters (other than the #), and should maximize search engine visibility by using common SEO keywords."
        response = openai.ChatCompletion.create(
            engine=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=100,
            temperature=0.7
        )
        tags = response['choices'][0]['message']['content'].strip().split('\n')
        results['seo_friendly_tags'] = [tag.strip('- ') for tag in tags if tag.strip()]

    # Article Translation
    if 'article_translation' in selected_options:
        text_to_translate = body if body else topic
        target_languages = form_data.get('target_languages', [])
        if isinstance(target_languages, str):
            target_languages = [target_languages]
        
        # Debugging: Print target_languages
        print(f"Target languages: {target_languages}")

        translations = {}
        for lang_code in target_languages:
            translated_text = translate_text(text_to_translate, lang_code)
            lang_name = languages.get(lang_code, {}).get('name', lang_code)
            translations[lang_name] = translated_text
        results['article_translation'] = translations

    save_results_to_cosmos(results, topic, body)

    return render_template('results.html', results=results, form_data=form_data, topic=topic, body=body)

def translate_text(text, to_language):
    params = {
        'api-version': '3.0',
        'to': to_language
    }
    headers = {
        'Ocp-Apim-Subscription-Key': TRANSLATION_KEY,
        'Ocp-Apim-Subscription-Region': TRANSLATION_REGION,
        'Content-type': 'application/json'
    }
    body = [{'text': text}]
    try:
        response = requests.post(TRANSLATION_ENDPOINT, params=params, headers=headers, json=body)
        response.raise_for_status()
        result = response.json()
        return result[0]['translations'][0]['text']
    except requests.exceptions.RequestException as e:
        print(f"Error during translation: {e}")
        return "Translation failed due to an error."


if __name__ == '__main__':
    app.run(debug=True)
