# ContentCatalyst

**ContentCatalyst** is an all-in-one content enhancement tool designed for journalists and content creators. Harness AI to generate engaging titles, craft compelling introductions and summaries, optimize for SEO, create SEO-friendly tags, and seamlessly translate articles into multiple languages.

![home](images\home.png)

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Technologies Used](#technologies-used)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgments](#acknowledgments)

## Features

1. **Article Titles**
   - Generate captivating and SEO-friendly titles.
2. **Introductions & Summaries**
   - Craft compelling introductions and summaries tailored to your audience.
3. **SEO-Friendly Tags**
   - Automatically generate relevant tags to enhance searchability.
4. **Article Translation**
   - Seamlessly translate your articles into multiple languages. *Note: Requires uploading a TXT, MD, or DOCX file.*

## Demo

[Content Catalyst Demo and Walkthrough - YouTube](https://www.youtube.com/watch?v=bPA6tBCflFo)

## Installation

### Prerequisites

- **Python 3.7 or higher**
- **pip** (Python package installer)
- **Git** (to clone the repository)

### Steps

1. **Clone the Repository**

   ```bash
   git clone https://github.com/yourusername/ContentCatalyst.git
   cd ContentCatalyst
   ```

2. **Create a Virtual Environment**

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up Environment Variables**

   Create a `.env` file in the root directory and add the following variables:

   ```env
   # Flask Configuration
   FLASK_KEY=your_flask_secret_key

   # Azure OpenAI Configuration
   AZURE_OPENAI_API_TYPE=azure
   AZURE_OPENAI_ENDPOINT=https://your-azure-openai-endpoint/
   AZURE_OPENAI_API_VERSION=2024-02-15-preview
   AZURE_OPENAI_KEY=your_azure_openai_key
   AZURE_OPENAI_MODEL=gpt-4o

   # Azure Translation Service Configuration
   AZURE_TRANSLATION_KEY=your_translation_subscription_key
   AZURE_TRANSLATION_ENDPOINT=https://api.cognitive.microsofttranslator.com/translate
   AZURE_TRANSLATION_REGION=your_translation_service_region
   AZURE_TRANSLATION_LANGUAGE_URL=https://api.cognitive.microsofttranslator.com/languages?api-version=3.0

   # Azure Cosmos DB Configuration
   AZURE_COSMOS_ENDPOINT=https://your-cosmosdb-endpoint/
   AZURE_COSMOS_KEY=your_cosmos_db_key
   AZURE_COSMOS_DB_NAME=ContentCatalyst
   AZURE_COSMOS_FILES_CONTAINER_NAME=files
   AZURE_COSMOS_RESULTS_CONTAINER_NAME=results

   # Application Insights (Optional)
   APPLICATIONINSIGHTS_CONNECTION_STRING=your_application_insights_connection_string
   ```

5. **Run the Application**

   ```bash
   python app.py
   ```

   The application will be available at `http://127.0.0.1:5000/`.

## Configuration

### Environment Variables

The following environment variables must be set either in your `.env` file or directly in your deployment environment:

- **Flask Configuration:**
  - `FLASK_KEY`: Secret key for Flask sessions.

- **Azure OpenAI Configuration:**
  - `AZURE_OPENAI_API_TYPE`: API type (e.g., "azure").
  - `AZURE_OPENAI_ENDPOINT`: Azure OpenAI endpoint URL.
  - `AZURE_OPENAI_API_VERSION`: API version (e.g., "2024-02-15-preview").
  - `AZURE_OPENAI_KEY`: API key for Azure OpenAI.
  - `AZURE_OPENAI_MODEL`: Deployment name or model identifier (e.g., `gpt-4o`).

- **Azure Translation Service Configuration:**
  - `AZURE_TRANSLATION_ENDPOINT`: Endpoint for the Translator Text API.
  - `AZURE_TRANSLATION_KEY`: API key for translation services.
  - `AZURE_TRANSLATION_REGION`: Azure region for translation services.
  - `AZURE_TRANSLATION_LANGUAGE_URL`: URL to fetch supported languages.

- **Azure Cosmos DB Configuration:**
  - `AZURE_COSMOS_ENDPOINT`: Azure Cosmos DB endpoint.
  - `AZURE_COSMOS_KEY`: API key for Cosmos DB.
  - `AZURE_COSMOS_DB_NAME`: Cosmos DB database name.
  - `AZURE_COSMOS_FILES_CONTAINER_NAME`: Container name for storing files.
  - `AZURE_COSMOS_RESULTS_CONTAINER_NAME`: Container name for storing results.

- **Application Insights (Optional):**
  - `APPLICATIONINSIGHTS_CONNECTION_STRING`: Connection string for Application Insights for logging and monitoring.

### Allowed File Types

ContentCatalyst allows the following file types for translation and processing:

- `.txt`
- `.md`
- `.docx`

Ensure that uploaded files adhere to these formats.

## Usage

### Home Page

1. **Home Page**

   - Visit `http://127.0.0.1:5000/` to access the home page.
   - Select the desired features by checking the corresponding boxes.
   - Click the **Next** button to proceed.

### Content Method

2. **Choose Content Input Method**

   - After selecting features, you'll be presented with multiple options for inputting content:
     - **Provide Text:** Manually enter your topic and article content.
     - **Upload Content:** Upload a TXT, MD, or DOCX file containing your article.
     - **Select File:** Choose from previously uploaded files stored in the system.

### Options Page

3. **Options Page**

   - Based on your selected features, configure additional options:
     - **Article Titles:** Choose the title style and tone, and specify keywords if needed.
     - **Introductions & Summaries:** Select introduction length and tone.
     - **SEO-Friendly Tags:** Set the number of tags to generate.
     - **Article Translation:** Select one or more target languages for translation.

   - For translations, if a file is uploaded, the system will extract content to be translated into the selected languages.

   - Once you have configured the options, click **Generate Content**.

### Viewing Files

4. **Viewing and Selecting Files**

   - If you choose to **Select File** for content input, you'll be able to browse files that were previously uploaded to the system.
   - You can sort files by **filename** or **timestamp** and search through them based on their names.
   - Once a file is selected, the system will extract its content, and you can proceed with further options.

### Viewing History

5. **View Content Generation History**

   - Navigate to the **History** page to view past content generation results.
   - You can search through previously generated results by topic, sort them by **topic** or **timestamp**, and review the content.
   - Clicking on any specific result will allow you to see the full content that was generated in the past.

### Results Page

6. **Results Page**

   - After generating content, you will be redirected to the **Results** page.
   - Here, you can view the generated titles, introductions, summaries, SEO tags, and translations.
   - The results will be saved in the system, and you can access them anytime from the **History** page.

   - Each generated content section includes a **Copy** button for easy copying to the clipboard.

## Technologies Used

### Backend

- **Flask**: Web framework for Python.
- **Azure OpenAI**: AI for generating content.
- **Azure Cosmos DB**: NoSQL database for storing files and results.
- **Azure Translator**: Service for translating content.

### Frontend

- **Bootstrap 5**: Responsive UI design.
- **JavaScript**: Client-side scripting for dynamic interactions.

### Utilities

- **docx2txt**: Extract text from DOCX files.
- **python-dotenv**: Manage environment variables.
- **markdown**: Convert markdown to HTML.
- **bleach**: Sanitize HTML to prevent XSS attacks.
- **requests**: Handle HTTP requests.

### Requirements

From `requirements.txt`, the following dependencies are necessary:

- `Flask`: Web framework for Python.
- `gunicorn`: WSGI HTTP server for production use.
- `Werkzeug`: WSGI utility library.
- `requests`: For making HTTP requests.
- `openai`: OpenAI's official Python client library.
- `docx2txt`: To extract text from DOCX files.
- `python-docx`: For handling DOCX files.
- `Markdown`: To process markdown content.
- `bleach`: To sanitize HTML content.
- `azure-cosmos`: Azure Cosmos DB SDK.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## License

This project is licensed under the [MIT License](LICENSE).

## Acknowledgments

- [OpenAI](https://openai.com/) for AI models.
- [Microsoft Azure](https://azure.microsoft.com/) for translation and storage services.
- [Flask](https://flask.palletsprojects.com/) for the web framework.
- [Bootstrap](https://getbootstrap.com/) for UI design.

---

Feel free to reach out or open an issue if you encounter any problems or have suggestions for improvement.